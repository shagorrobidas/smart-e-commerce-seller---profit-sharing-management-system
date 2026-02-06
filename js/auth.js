/**
 * Smart E-Commerce System
 * Authentication Logic
 */

document.addEventListener('DOMContentLoaded', () => {

    // Login Form Handling
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            // Simple mock validation
            if (email && password) {
                // Determine role based on email for demo purposes if not found in localstorage
                // In real app, backend would validate and return role

                // Check if user exists in our mock DB
                let user = null;
                const storedUsers = JSON.parse(localStorage.getItem('smartEcoUsers') || '[]');
                user = storedUsers.find(u => u.email === email && u.password === password);

                if (user) {
                    localStorage.setItem('smartEcoUser', JSON.stringify(user));
                    window.location.href = `${user.role}/dashboard.html`;
                } else if (email === 'admin@demo.com' && password === 'admin') {
                    // Backdoor for demo admin
                    const demoUser = { name: 'Demo Admin', email: 'admin@demo.com', role: 'admin' };
                    localStorage.setItem('smartEcoUser', JSON.stringify(demoUser));
                    window.location.href = 'admin/dashboard.html';
                } else if (email === 'staff@demo.com' && password === 'staff') {
                    // Backdoor for demo staff
                    const demoStaff = { name: 'Demo Staff', email: 'staff@demo.com', role: 'staff', company: 'Smart Eco' };
                    localStorage.setItem('smartEcoUser', JSON.stringify(demoStaff));
                    window.location.href = 'staff/dashboard.html';
                } else if (email === 'investor@demo.com' && password === 'investor') {
                    // Backdoor for demo investor
                    const demoInvestor = { name: 'Demo Investor', email: 'investor@demo.com', role: 'investor', company: 'Angel VC' };
                    localStorage.setItem('smartEcoUser', JSON.stringify(demoInvestor));
                    window.location.href = 'investor/dashboard.html';
                } else {
                    alert('Invalid credentials. Try admin@demo.com / admin');
                }
            }
        });
    }

    // Register Form Handling
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const company = document.getElementById('company').value;
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const role = document.getElementById('role').value;
            const password = document.getElementById('password').value;

            if (company && name && email && role && password) {
                const newUser = {
                    id: 'u_' + Date.now(),
                    company,
                    name,
                    email,
                    role,
                    password // In a real app, never store plain text passwords
                };

                // Store in mock DB
                const storedUsers = JSON.parse(localStorage.getItem('smartEcoUsers') || '[]');
                storedUsers.push(newUser);
                localStorage.setItem('smartEcoUsers', JSON.stringify(storedUsers));

                // Auto login
                localStorage.setItem('smartEcoUser', JSON.stringify(newUser));

                alert('Registration Successful!');
                window.location.href = `${role}/dashboard.html`;
            }
        });
    }

    // Forgot Password Handling
    const forgotForm = document.getElementById('forgotForm');
    if (forgotForm) {
        forgotForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            if (email) {
                alert(`Password reset link sent to ${email}`);
                window.location.href = 'login.html';
            }
        });
    }

});
