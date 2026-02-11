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

            if (email && password) {
                // Check DB
                const users = DB.getUsers();
                let user = users.find(u => u.email === email && u.password === password);

                if (user) {
                    // Update Last Login
                    DB.updateUser(user.id, { lastLogin: new Date().toISOString() });
                    // Store Session
                    localStorage.setItem('smartEcoUser', JSON.stringify(user));
                    window.location.href = `৳{user.role}/dashboard.html`;
                } else if (email === 'admin@demo.com' && password === 'admin') {
                    // Create Admin if not exists
                    if (!users.find(u => u.email === 'admin@demo.com')) {
                        const newAdmin = {
                            id: 'admin_001',
                            name: 'Demo Admin',
                            email: 'admin@demo.com',
                            password: 'admin',
                            role: 'admin',
                            company: 'Smart System',
                            balance: 100000 // Initial Business Capital
                        };
                        DB.addUser(newAdmin);
                        localStorage.setItem('smartEcoUser', JSON.stringify(newAdmin));
                        window.location.href = 'admin/dashboard.html';
                    } else {
                        // Retry login to catch newly created admin
                        const existingAdmin = users.find(u => u.email === 'admin@demo.com');
                        localStorage.setItem('smartEcoUser', JSON.stringify(existingAdmin));
                        window.location.href = 'admin/dashboard.html';
                    }
                } else if (email === 'staff@demo.com' && password === 'staff') {
                    // Create Staff if not exists
                    if (!users.find(u => u.email === 'staff@demo.com')) {
                        const newStaff = {
                            id: 'staff_001',
                            name: 'Demo Staff',
                            email: 'staff@demo.com',
                            password: 'staff',
                            role: 'staff',
                            company: 'Smart System',
                            balance: 0
                        };
                        DB.addUser(newStaff);
                        localStorage.setItem('smartEcoUser', JSON.stringify(newStaff));
                        window.location.href = 'staff/dashboard.html';
                    } else {
                        const existingStaff = users.find(u => u.email === 'staff@demo.com');
                        localStorage.setItem('smartEcoUser', JSON.stringify(existingStaff));
                        window.location.href = 'staff/dashboard.html';
                    }
                } else if (email === 'investor@demo.com' && password === 'investor') {
                    // Create Investor if not exists
                    if (!users.find(u => u.email === 'investor@demo.com')) {
                        const newInvestor = {
                            id: 'investor_001',
                            name: 'Demo Investor',
                            email: 'investor@demo.com',
                            password: 'investor',
                            role: 'investor',
                            company: 'Smart System',
                            balance: 50000 // Initial Investment Value
                        };
                        DB.addUser(newInvestor);
                        localStorage.setItem('smartEcoUser', JSON.stringify(newInvestor));
                        window.location.href = 'investor/dashboard.html';
                    } else {
                        const existingInvestor = users.find(u => u.email === 'investor@demo.com');
                        localStorage.setItem('smartEcoUser', JSON.stringify(existingInvestor));
                        window.location.href = 'investor/dashboard.html';
                    }
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
                // Check if email exists
                const users = DB.getUsers();
                if (users.find(u => u.email === email)) {
                    alert('Email already registered!');
                    return;
                }

                const newUser = {
                    company,
                    name,
                    email,
                    role,
                    password,
                    balance: 0,
                    status: 'active'
                };

                DB.addUser(newUser);

                // Auto login
                const createdUser = DB.getUsers().find(u => u.email === email);
                localStorage.setItem('smartEcoUser', JSON.stringify(createdUser));

                alert('Registration Successful!');
                window.location.href = `৳{role}/dashboard.html`;
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
                alert(`Password reset link sent to ৳{email}`);
                window.location.href = 'login.html';
            }
        });
    }

});
