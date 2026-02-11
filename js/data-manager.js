/**
 * Smart E-Commerce System
 * Data Manager - Centralized LocalStorage Handler
 */

class DataManager {
    constructor() {
        this.init();
    }

    init() {
        // Initialize Collections if they don't exist
        this.initializeCollection('smartEcoUsers', []);
        this.initializeCollection('smartEcoOrders', []); // Formerly Sales
        this.initializeCollection('smartEcoInventory', []);
        this.initializeCollection('smartEcoTransactions', []);
        this.initializeCollection('smartEcoTasks', []);
        this.initializeCollection('smartEcoMessages', []);
        this.initializeCollection('smartEcoInvestments', []);
        this.initializeCollection('smartEcoSettings', {
            businessName: 'SmartSeller.sys',
            currency: 'BDT',
            taxRate: 5,
            announcement: 'Welcome to the new system!',
            logo: ''
        });
    }

    initializeCollection(key, defaultValue) {
        if (!localStorage.getItem(key)) {
            localStorage.setItem(key, JSON.stringify(defaultValue));
        }
    }

    // --- GENERIC HELPERS ---
    get(key) {
        return JSON.parse(localStorage.getItem(key) || '[]');
    }

    set(key, data) {
        localStorage.setItem(key, JSON.stringify(data));
    }

    add(key, item) {
        const data = this.get(key);
        item.id = item.id || Date.now() + Math.random().toString(36).substr(2, 9);
        item.createdAt = new Date().toISOString();
        data.unshift(item); // Add to top
        this.set(key, data);
        return item;
    }

    update(key, id, updates) {
        const data = this.get(key);
        const index = data.findIndex(item => item.id === id);
        if (index !== -1) {
            data[index] = { ...data[index], ...updates, updatedAt: new Date().toISOString() };
            this.set(key, data);
            return data[index];
        }
        return null;
    }

    delete(key, id) {
        const data = this.get(key);
        const newData = data.filter(item => item.id !== id);
        this.set(key, newData);
    }

    // --- USERS ---
    getUsers() { return this.get('smartEcoUsers'); }
    addUser(user) {
        // Ensure balance is init
        user.balance = user.balance || 0;
        return this.add('smartEcoUsers', user);
    }
    updateUser(id, updates) { return this.update('smartEcoUsers', id, updates); }
    getUserById(id) { return this.getUsers().find(u => u.id === id); }

    // --- INVENTORY ---
    getInventory() { return this.get('smartEcoInventory'); }
    addInventoryItem(item) { return this.add('smartEcoInventory', item); }
    updateInventory(id, updates) { return this.update('smartEcoInventory', id, updates); }

    // --- ORDERS / SALES ---
    // Unifying 'Sales' from dashboard.js into 'Orders'
    getOrders() { return this.get('smartEcoOrders'); }
    addOrder(order) { return this.add('smartEcoOrders', order); }
    updateOrderStatus(id, status) { return this.update('smartEcoOrders', id, { status }); }

    // Legacy support for dashboard.js 'smartEcoSales' if needed, 
    // but better to migrate dashboard.js to use 'smartEcoOrders'.
    // We will assume dashboard.js will be refactored to use getOrders().

    // --- TRANSACTIONS ---
    // Types: 'transfer', 'expense', 'income', 'profit_share', 'loan'
    getTransactions() { return this.get('smartEcoTransactions'); }
    addTransaction(txn) {
        // txn: { type, amount, fromUser, toUser, status (pending/approved), note }
        const newTxn = this.add('smartEcoTransactions', txn);

        // If approved instantly (e.g. expense), update balances
        if (txn.status === 'approved') {
            this.executeTransactionBalanceUpdate(newTxn);
        }
        return newTxn;
    }

    executeTransactionBalanceUpdate(txn) {
        if (txn.fromUser) {
            const sender = this.getUserById(txn.fromUser);
            if (sender) this.updateUser(sender.id, { balance: Number(sender.balance) - Number(txn.amount) });
        }
        if (txn.toUser) {
            const receiver = this.getUserById(txn.toUser);
            if (receiver) this.updateUser(receiver.id, { balance: Number(receiver.balance) + Number(txn.amount) });
        }
    }

    // --- TASKS ---
    getTasks() { return this.get('smartEcoTasks'); }
    addTask(task) { return this.add('smartEcoTasks', task); }
    updateTaskStatus(id, status) { return this.update('smartEcoTasks', id, { status }); }

    // --- MESSAGES ---
    getMessages() { return this.get('smartEcoMessages'); }
    sendMessage(msg) { return this.add('smartEcoMessages', msg); }

    // --- INVESTMENTS ---
    getInvestments() { return this.get('smartEcoInvestments'); }
    addInvestment(inv) { return this.add('smartEcoInvestments', inv); }

    // --- SETTINGS ---
    getSettings() { return JSON.parse(localStorage.getItem('smartEcoSettings')); }
    updateSettings(updates) {
        const current = this.getSettings();
        const updated = { ...current, ...updates };
        localStorage.setItem('smartEcoSettings', JSON.stringify(updated));
        return updated;
    }
}

// Global Instance
const DB = new DataManager();
