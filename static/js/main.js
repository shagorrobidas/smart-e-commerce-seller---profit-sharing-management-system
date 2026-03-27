/**
 * Smart E-Commerce System
 * Main JavaScript File - Refactored for Django
 */

const App = {
    // Check if user is logged in
    checkAuth: () => {
        const user = localStorage.getItem('smartEcoUser');
        const tokens = localStorage.getItem('smartEcoTokens');
        if (user && tokens) {
            return JSON.parse(user);
        }
        return null;
    },

    // Logout handled in auth.js
    logout: () => {
        if (window.App && window.App.logout) {
            window.App.logout();
        } else {
            localStorage.clear();
            window.location.href = '/login/';
        }
    },

    // Format Currency
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('en-BD', {
            style: 'currency',
            currency: 'BDT',
            minimumFractionDigits: 2
        }).format(amount).replace('BDT', '৳');
    },

    // Theme Management
    toggleTheme: () => {
        const html = document.documentElement;
        const current = html.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';

        html.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);

        const icon = document.getElementById('theme-icon');
        if (icon) {
            icon.setAttribute('icon', next === 'light' ? 'solar:moon-linear' : 'solar:sun-linear');
        }
    },

    initTheme: () => {
        const saved = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', saved);

        if (!document.getElementById('theme-toggle')) {
            const btn = document.createElement('button');
            btn.id = 'theme-toggle';
            btn.className = 'btn glass-card';
            btn.style.cssText = `
                position: fixed; bottom: 20px; right: 20px; padding: 0.75rem;
                z-index: 1000; border-radius: 50%; width: 48px; height: 48px;
                display: flex; align-items: center; justify-content: center;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            `;

            const isLight = saved === 'light';
            btn.innerHTML = `<iconify-icon id="theme-icon" icon="${isLight ? 'solar:moon-linear' : 'solar:sun-linear'}" style="font-size: 24px; color: var(--text-main);"></iconify-icon>`;

            btn.onclick = App.toggleTheme;
            document.body.appendChild(btn);
        }
    }
};

// UI Interactions
document.addEventListener('DOMContentLoaded', () => {
    App.initTheme();

    // Dynamic Header State for Landing Page
    const user = App.checkAuth();
    const navAuthSection = document.getElementById('nav-auth');

    if (user && navAuthSection) {
        navAuthSection.innerHTML = `
            <a href="/${user.role}/dashboard/" class="text-xs font-medium hover:text-white transition-colors">Dashboard</a>
            <button onclick="App.logout();" class="bg-white text-black text-xs font-medium px-4 py-2 rounded-full hover:bg-gray-200 transition-colors">
                Logout
            </button>
        `;
    }
});
