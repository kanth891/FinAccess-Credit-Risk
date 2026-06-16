/* ===================================================
   FinAccess – API Client & UI Utilities
   Used by all static HTML pages (no Jinja2)
   =================================================== */

// ── Auth Helpers ─────────────────────────────────────
const Auth = {
    getToken()       { return localStorage.getItem('fa_token'); },
    getUser()        { const u = localStorage.getItem('fa_user'); return u ? JSON.parse(u) : null; },
    setSession(token, user) {
        localStorage.setItem('fa_token', token);
        localStorage.setItem('fa_user', JSON.stringify(user));
    },
    clearSession()   { localStorage.removeItem('fa_token'); localStorage.removeItem('fa_user'); },
    isLoggedIn()     { return !!this.getToken(); },
    isAdmin()        { const u = this.getUser(); return u && u.is_admin; },

    requireAuth()    {
        if (!this.isLoggedIn()) { window.location.href = '/login'; return false; }
        return true;
    },
    requireAdmin()   {
        if (!this.isLoggedIn() || !this.isAdmin()) { window.location.href = '/login'; return false; }
        return true;
    },
    requireGuest()   {
        if (this.isLoggedIn()) {
            window.location.href = this.isAdmin() ? '/admin' : '/dashboard';
            return false;
        }
        return true;
    }
};

// ── API Client ────────────────────────────────────────
const API = {
    async request(method, url, body = null) {
        const headers = { 'Content-Type': 'application/json' };
        const token = Auth.getToken();
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const opts = { method, headers };
        if (body) opts.body = JSON.stringify(body);

        const res = await fetch(url, opts);
        const data = await res.json().catch(() => ({}));

        if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
        return data;
    },
    get(url)          { return this.request('GET', url); },
    post(url, body)   { return this.request('POST', url, body); }
};

// ── Flash Messages ────────────────────────────────────
const Flash = {
    show(message, type = 'error') {
        let container = document.getElementById('flashContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'flashContainer';
            container.className = 'flash-container';
            document.body.appendChild(container);
        }
        const el = document.createElement('div');
        el.className = `flash flash-${type}`;
        el.innerHTML = `<span>${message}</span><button class="flash-close" onclick="this.parentElement.remove()">×</button>`;
        container.appendChild(el);
        setTimeout(() => { el.style.opacity='0'; el.style.transform='translateX(110%)'; setTimeout(() => el.remove(), 400); }, 5000);
    },
    success(msg) { this.show(msg, 'success'); },
    error(msg)   { this.show(msg, 'error'); }
};

// ── UI Utilities ──────────────────────────────────────
const UI = {
    // Render navbar based on auth state
    renderNavbar(activePage = '') {
        const user = Auth.getUser();
        const isAdmin = Auth.isAdmin();
        const brandHtml = `<a href="/" class="nav-brand"><span class="brand-icon">⬡</span><span class="brand-text">Fin<span class="brand-accent">Access</span></span></a>`;

        let links = '';
        if (user) {
            if (isAdmin) {
                links = `<a href="/admin" class="nav-link ${activePage==='admin'?'nav-link-active':''}">Admin Panel</a>`;
            } else {
                links = `
                    <a href="/dashboard" class="nav-link ${activePage==='dashboard'?'nav-link-active':''}">Dashboard</a>
                    <a href="/apply"     class="nav-link ${activePage==='apply'?'nav-link-active':''}">Apply</a>
                    <a href="/history"   class="nav-link ${activePage==='history'?'nav-link-active':''}">History</a>`;
            }
            links += `<span class="nav-user">${user.name}</span>
                      <button onclick="logout()" class="btn btn-outline btn-sm">Logout</button>`;
        } else {
            links = `<a href="/login" class="nav-link">Login</a>
                     <a href="/register" class="btn btn-primary btn-sm">Get Started</a>`;
        }

        const nav = document.getElementById('navbar');
        if (nav) nav.innerHTML = `<div class="nav-container">${brandHtml}<div class="nav-links">${links}</div></div>`;
    },

    // Progress bar animation
    animateProgressBars() {
        document.querySelectorAll('.progress-fill, .avg-risk-bar').forEach(el => {
            const w = el.style.width; el.style.width = '0';
            setTimeout(() => { el.style.transition = 'width 0.9s ease'; el.style.width = w; }, 80);
        });
    },

    // Count-up animation
    animateCounters() {
        document.querySelectorAll('[data-count]').forEach(el => {
            const target = parseFloat(el.dataset.count);
            const suffix = el.dataset.suffix || '';
            const prefix = el.dataset.prefix || '';
            if (isNaN(target)) return;
            let current = 0;
            const step = target / 40;
            const timer = setInterval(() => {
                current = Math.min(current + step, target);
                el.textContent = prefix + (Number.isInteger(target) ? Math.round(current) : current.toFixed(1)) + suffix;
                if (current >= target) clearInterval(timer);
            }, 20);
        });
    },

    // Render a decision badge
    badge(decision) {
        const cls = decision === 'Approved' ? 'badge-approved' : 'badge-rejected';
        return `<span class="badge ${cls}">${decision}</span>`;
    },

    // Render credit score chip
    creditChip(score) {
        let cls = 'chip-poor';
        if (score >= 750) cls = 'chip-excellent';
        else if (score >= 700) cls = 'chip-good';
        else if (score >= 650) cls = 'chip-fair';
        return `<span class="credit-chip ${cls}">${score}</span>`;
    },

    // Render risk score progress bar
    riskBar(score) {
        let cls = score >= 70 ? 'progress-green' : score >= 50 ? 'progress-yellow' : 'progress-red';
        return `<div class="progress-wrap">
            <div class="progress-track"><div class="progress-fill ${cls}" style="width:${score}%"></div></div>
            <span class="progress-val">${score}</span>
        </div>`;
    },

    // Format currency
    currency(n) { return '$' + Number(n).toLocaleString(); },

    // Format date
    date(str) {
        return new Date(str).toLocaleDateString('en-US', { month:'short', day:'numeric', year:'numeric' });
    }
};

// ── Global logout ─────────────────────────────────────
function logout() {
    Auth.clearSession();
    window.location.href = '/';
}

// ── Toggle password visibility ────────────────────────
function togglePassword(id) {
    const f = document.getElementById(id);
    if (f) f.type = f.type === 'password' ? 'text' : 'password';
}

// ── Animate progress bars on DOM ready ───────────────
document.addEventListener('DOMContentLoaded', () => UI.animateProgressBars());
