/**
 * Smart E-Commerce System
 * Authentication Logic Refactored for JWT Backend
 */

document.addEventListener('DOMContentLoaded', () => {

    // Login Form Handling
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            if (email && password) {
                try {
                    const response = await fetch('/api/v1/auth/login/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        // Store Auth Data
                        localStorage.setItem('smartEcoTokens', JSON.stringify(data.tokens));
                        localStorage.setItem('smartEcoUser', JSON.stringify(data.user));
                        
                        // Redirect based on role
                        const role = data.user.role;
                        window.location.href = `/${role}/dashboard/`;
                    } else {
                        const error = await response.json();
                        const msg = error.error || 'Login failed. Check your credentials.';
                        if (window.showAuthError) {
                            window.showAuthError(msg);
                        } else {
                            alert(msg);
                        }
                    }
                } catch (err) {
                    console.error('Login Error:', err);
                    const msg = 'Server error. Please try again later.';
                    if (window.showAuthError) {
                        window.showAuthError(msg, "Error");
                    } else {
                        alert(msg);
                    }
                }
            }
        });
    }

    // Register Form Handling
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const role = document.getElementById('role').value;
            const company = document.getElementById('company').value;

            try {
                const response = await fetch('/api/v1/auth/register/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password, role, company })
                });

                if (response.ok) {
                    const data = await response.json();
                    // Registration Successful -> Show Modal
                    if (window.showSuccessModal) {
                        window.showSuccessModal(data.message, data.debug_verification_link);
                    } else {
                        alert('Registration Successful! Please check your email for verification.');
                        window.location.href = '/login/';
                    }
                } else {
                    const error = await response.json();
                    const msg = error.error || (typeof error === 'object' ? JSON.stringify(error) : error);
                    if (window.showErrorModal) {
                        window.showErrorModal(msg);
                    } else {
                        // alert(msg);
                        window.showAuthError(msg, "Error");
                    }
                }
            } catch (err) {
                console.error('Registration Error:', err);
                alert('Server error during registration.');
            }
        });
    }

    // Global App Object for Logout
    window.App = {
        logout: async () => {
            const tokens = JSON.parse(localStorage.getItem('smartEcoTokens'));
            if (tokens) {
                try {
                    await fetch('/api/v1/auth/logout/', {
                        method: 'POST',
                        headers: { 
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${tokens.access}`
                        },
                        body: JSON.stringify({ refresh: tokens.refresh })
                    });
                } catch (e) { console.error('Logout error', e); }
            }
            localStorage.clear();
            window.location.href = '/login/';
        }
    };
});
