/**
 * Smart E-Commerce System
 * Main JavaScript File
 */

// Global State Management (Simulation)
const App = {
    // Check if user is logged in
    checkAuth: () => {
        const user = localStorage.getItem('smartEcoUser');
        if (user) {
            return JSON.parse(user);
        }
        return null;
    },

    // Mock Login
    login: (email, password, role) => {
        // In a real app, this would be an API call
        const user = {
            id: 'u_' + Date.now(),
            email: email,
            role: role,
            name: email.split('@')[0]
        };
        localStorage.setItem('smartEcoUser', JSON.stringify(user));
        return user;
    },

    // Logout
    logout: () => {
        localStorage.removeItem('smartEcoUser');

        // Handle path navigation relative to current location
        const path = window.location.pathname;
        let redirect = 'pages/logout.html'; // Default if from root

        if (path.includes('/pages/admin/') || path.includes('/pages/staff/') || path.includes('/pages/investor/')) {
            redirect = '../../pages/logout.html'; // Up two levels
        } else if (path.includes('/pages/') && !path.includes('/pages/logout.html')) {
            redirect = 'logout.html'; // Same level
        }

        window.location.href = redirect;
    },

    // Delete Account
    deleteAccount: () => {
        if (confirm('Are you sure you want to PERMANENTLY delete your account? This cannot be undone.')) {
            const user = App.checkAuth();
            if (user) {
                // Remove from DB
                const allUsers = JSON.parse(localStorage.getItem('smartEcoUsers') || '[]');
                const newUsers = allUsers.filter(u => u.email !== user.email);
                localStorage.setItem('smartEcoUsers', JSON.stringify(newUsers));
            }
            App.logout();
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

        // Update icon if exists
        const icon = document.getElementById('theme-icon');
        if (icon) {
            icon.setAttribute('icon', next === 'light' ? 'solar:moon-linear' : 'solar:sun-linear');
        }
    },

    initTheme: () => {
        const saved = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', saved);

        // Create Floating Toggle Button if it doesn't exist
        if (!document.getElementById('theme-toggle')) {
            const btn = document.createElement('button');
            btn.id = 'theme-toggle';
            btn.className = 'btn glass-card';
            btn.style.position = 'fixed';
            btn.style.bottom = '20px';
            btn.style.right = '20px';
            btn.style.padding = '0.75rem';
            btn.style.zIndex = '1000';
            btn.style.borderRadius = '50%';
            btn.style.width = '48px';
            btn.style.height = '48px';
            btn.style.display = 'flex';
            btn.style.alignItems = 'center';
            btn.style.justifyContent = 'center';
            btn.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';

            // Icon
            const isLight = saved === 'light';
            btn.innerHTML = `<iconify-icon id="theme-icon" icon="৳{isLight ? 'solar:moon-linear' : 'solar:sun-linear'}" style="font-size: 24px; color: var(--text-main);"></iconify-icon>`;

            btn.onclick = App.toggleTheme;
            document.body.appendChild(btn);
        }
    }
};

// UI Interactions
document.addEventListener('DOMContentLoaded', () => {
    // Init Theme
    App.initTheme();

    // Dynamic Header State
    const user = App.checkAuth();
    const navAuthSection = document.getElementById('nav-auth');

    if (user && navAuthSection) {
        // If logged in, show Dashboard link instead of Login
        navAuthSection.innerHTML = `
            <a href="pages/৳{user.role}/dashboard.html" class="text-xs font-medium hover:text-white transition-colors">Dashboard</a>
            <button onclick="App.logout()" class="bg-white text-black text-xs font-medium px-4 py-2 rounded-full hover:bg-gray-200 transition-colors">
                Logout
            </button>
        `;
    }
});
