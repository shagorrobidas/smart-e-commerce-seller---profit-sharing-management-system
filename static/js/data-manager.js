/**
 * Smart E-Commerce System
 * Data Manager - Refactored for Django REST API
 */

class DataManager {
    constructor() {
        this.apiBase = '/api/v1';
    }

    // --- JWT TOKEN HELPERS ---
    getTokens() {
        try {
            return JSON.parse(localStorage.getItem('smartEcoTokens'));
        } catch (e) { return null; }
    }

    getAccessToken() {
        const tokens = this.getTokens();
        return tokens ? tokens.access : null;
    }

    async getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        const token = this.getAccessToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    }

    // --- GENERIC API CALLER ---
    async apiCall(endpoint, method = 'GET', body = null) {
        const url = `${this.apiBase}${endpoint}`;
        const options = {
            method,
            headers: await this.getHeaders(),
        };
        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(url, options);
        
        if (response.status === 401) {
            // Token expired or invalid
            console.warn('Unauthorized. Redirecting to login...');
            // Optional: handle token refresh here
            window.location.href = '/login/';
            return null;
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || error.detail || 'API Call Failed');
        }

        return await response.json();
    }

    // --- HELPERS MAPPED TO OLD METHODS (but now async) ---
    
    // USERS
    async getUsers() { return await this.apiCall('/admin/users/'); }
    async addUser(user) { return await this.apiCall('/admin/users/create/', 'POST', user); }
    async getUserById(id) { return await this.apiCall(`/admin/users/${id}/`); }
    async getStaffUsers() { return await this.apiCall('/staff/users/'); }

    // INVENTORY
    async getInventory(params = '') { return await this.apiCall(`/staff/inventory/${params}`); }
    async addInventoryItem(item) { return await this.apiCall('/staff/inventory/', 'POST', item); }
    async updateInventory(id, updates) { return await this.apiCall(`/staff/inventory/${id}/`, 'PATCH', updates); }
    async getExpenses() { return await this.apiCall('/staff/expenses/'); }

    // ORDERS
    async getOrders() { 
        // Logic depends on role, let's try staff first, then admin reports
        const role = JSON.parse(localStorage.getItem('smartEcoUser'))?.role;
        const endpoint = role === 'admin' ? '/admin/reports/' : '/staff/orders/';
        return await this.apiCall(endpoint);
    }
    async addOrder(order) { return await this.apiCall('/staff/orders/', 'POST', order); }
    async updateOrderStatus(id, status) { return await this.apiCall(`/staff/orders/${id}/`, 'PATCH', { status }); }

    // TASKS
    async getTasks() {
        const role = JSON.parse(localStorage.getItem('smartEcoUser'))?.role;
        const endpoint = role === 'admin' ? '/admin/tasks/' : '/staff/tasks/';
        return await this.apiCall(endpoint);
    }
    async updateTaskStatus(id, status) {
        const role = JSON.parse(localStorage.getItem('smartEcoUser'))?.role;
        const endpoint = role === 'admin' ? `/admin/tasks/${id}/` : `/staff/tasks/${id}/`;
        return await this.apiCall(endpoint, 'PATCH', { status });
    }

    // MESSAGES
    async getMessages() { return await this.apiCall('/staff/messages/'); }
    async sendMessage(msg) { return await this.apiCall('/staff/messages/send/', 'POST', msg); }

    // INVESTOR
    async getInvestorDashboard() { return await this.apiCall('/investor/dashboard/'); }
    async getInvestorReports() { return await this.apiCall('/investor/reports/'); }
    async getInvestorAgreements() { return await this.apiCall('/investor/agreements/'); }

    // INVESTMENTS
    async getInvestments() { return await this.apiCall('/investor/investments/'); }
    async addInvestment(inv) { return await this.apiCall('/investor/investments/', 'POST', inv); }

    // SETTINGS
    async getSettings() { return await this.apiCall('/admin/settings/'); }
    async updateSettings(updates) { return await this.apiCall('/admin/settings/', 'PATCH', updates); }

    // AUTH / PROFILE
    async getProfile() { return await this.apiCall('/auth/profile/'); }
    async updateProfile(data) { return await this.apiCall('/auth/profile/', 'PATCH', data); }
    async getBusinesses() { return await this.apiCall('/auth/businesses/'); }
    
    // PASSWORD RESET
    async forgotPassword(email) { return await this.apiCall('/auth/forgot-password/', 'POST', { email }); }
    async resetPassword(email, password) { return await this.apiCall('/auth/reset-password/', 'POST', { email, password }); }
}

// Global Instance
const DB = new DataManager();
