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

    // Global Dashboard UI updates
    if (user) {
        const userNameEl = document.getElementById('user-name');
        if (userNameEl) userNameEl.textContent = user.name || 'User';

        const userRoleEl = document.getElementById('user-role');
        if (userRoleEl && user.role) userRoleEl.textContent = user.role.toUpperCase();
        
        const userCompanyEl = document.getElementById('user-company');
        if (userCompanyEl && user.company) userCompanyEl.textContent = user.company;

        const userInitialEl = document.getElementById('user-initial');
        if (userInitialEl && user.name) userInitialEl.textContent = user.name.charAt(0).toUpperCase();

        // Initialize Notifications
        App.startNotificationPolling();
    }
});

// Notification System
App.unreadCount = parseInt(sessionStorage.getItem('smartEcoUnreadCount')) || 0;

App.fetchUnreadCount = async () => {
    try {
        if (typeof DB === 'undefined') return;
        const data = await DB.getUnreadCount();
        const count = data.unread_count || 0;
        
        // Only show toast if count has INCREASED
        if (count > App.unreadCount && window.location.pathname.indexOf('/messages/') === -1) {
            App.showToast(`You have ${count} unread messages.`);
        }
        
        App.unreadCount = count;
        sessionStorage.setItem('smartEcoUnreadCount', count);
        App.updateBadges(count);
    } catch (e) {
        console.warn('Notification fetch failed', e);
    }
};

App.updateBadges = (count) => {
    const badges = document.querySelectorAll('.msg-badge');
    badges.forEach(b => {
        if (count > 0) {
            b.textContent = count > 9 ? '9+' : count;
            b.classList.remove('hidden');
        } else {
            b.classList.add('hidden');
        }
    });
};

App.showToast = (msg) => {
    const existing = document.getElementById('global-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'global-toast';
    // Use inline styles for compatibility where Tailwind is missing
    toast.style.cssText = `
        position: fixed; top: 1.5rem; right: 1.5rem; z-index: 9999;
        background: rgba(79, 70, 229, 0.95); backdrop-filter: blur(8px);
        color: white; padding: 1rem 1.5rem; border-radius: 1rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
        display: flex; align-items: center; gap: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-family: 'Inter', sans-serif;
    `;
    toast.className = 'animate-slide-in';
    
    toast.innerHTML = `
        <div style="width: 2.5rem; height: 2.5rem; border-radius: 0.75rem; background: rgba(255, 255, 255, 0.2); display: flex; align-items: center; justify-content: center;">
            <iconify-icon icon="solar:chat-round-dots-bold" width="24"></iconify-icon>
        </div>
        <div style="flex: 1;">
            <p style="margin: 0; font-size: 10px; font-weight: 700; text-transform: uppercase; opacity: 0.7; letter-spacing: 0.1em;">New Message</p>
            <p style="margin: 0; font-size: 13px; font-weight: 600;">${msg}</p>
        </div>
        <button onclick="this.parentElement.remove()" style="background: none; border: none; color: white; opacity: 0.5; cursor: pointer; display: flex; align-items: center;">
            <iconify-icon icon="solar:close-circle-linear" width="20"></iconify-icon>
        </button>
    `;

    document.body.appendChild(toast);
    setTimeout(() => {
        if (toast.parentElement) {
            toast.classList.add('animate-slide-out');
            setTimeout(() => toast.remove(), 500);
        }
    }, 5000);
};

App.refreshNotifications = () => {
    App.fetchUnreadCount();
};

App.startNotificationPolling = () => {
    App.fetchUnreadCount();
    setInterval(App.fetchUnreadCount, 10000); // 10 seconds
};
