/**
 * Smart E-Commerce System
 * Dashboard Logic - Integrated with DataManager
 */

const Dashboard = {
    // Initial Data Seeding
    initData: () => {
        // Seed Orders if Empty
        if (DB.getOrders().length === 0) {
            const seedOrders = [
                { id: 1, product: 'Wireless Headset', amount: 1200, date: '2024-02-01', type: 'sale', platform: 'Daraz', status: 'delivered' },
                { id: 2, product: 'PowerBank 20k', amount: 2500, date: '2024-02-02', type: 'sale', platform: 'CartUp', status: 'delivered' },
                { id: 3, product: 'Smart Watch', amount: 4500, date: '2024-02-03', type: 'sale', platform: 'Daraz', status: 'pending' },
                { id: 4, product: 'Office Chair', amount: 1500, date: '2024-02-02', type: 'expense', category: 'Ops', status: 'approved' },
                { id: 5, product: 'Gaming Mouse', amount: 3500, date: '2024-02-04', type: 'sale', platform: 'Offline', status: 'delivered' },
            ];
            seedOrders.forEach(o => DB.addOrder(o));
        }

        // Seed Inventory if Empty
        if (DB.getInventory().length === 0) {
            const seedInventory = [
                { id: 1, name: 'Wireless Headset', stock: 45, buyPrice: 800, sellPrice: 1200, category: 'Audio', description: 'High-quality wireless headset.', image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=200&auto=format&fit=crop' },
                { id: 2, name: 'PowerBank 20k', stock: 20, buyPrice: 1500, sellPrice: 2500, category: 'Accessories', description: '20000mAh fast-charging.', image: 'https://images.unsplash.com/photo-1609592424363-233bb4235afb?q=80&w=200&auto=format&fit=crop' },
                { id: 3, name: 'Smart Watch', stock: 12, buyPrice: 3000, sellPrice: 4500, category: 'Wearables', description: 'Fitness tracker.', image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=200&auto=format&fit=crop' },
            ];
            seedInventory.forEach(i => DB.addInventoryItem(i));
        }
    },

    getSales: () => DB.getOrders(), // Alias for compatibility
    getInventory: () => DB.getInventory(),

    // Calculate Totals
    calculateStats: () => {
        const txns = DB.getOrders();
        let totalSales = 0;
        let totalExpenses = 0;
        let totalProfit = 0;

        txns.forEach(t => {
            if (t.type === 'sale') {
                totalSales += Number(t.amount);
                // Simple heuristic logic for demo profit
                totalProfit += (Number(t.amount) * 0.3);
            } else if (t.type === 'expense') {
                totalExpenses += Number(t.amount);
                totalProfit -= Number(t.amount);
            }
        });

        return { totalSales, totalExpenses, totalProfit };
    },

    // Add Record (Sales/Expense)
    addRecord: (record) => {
        // Adapt to Order Schema
        const newOrder = {
            ...record,
            date: new Date().toISOString().split('T')[0],
            status: record.type === 'sale' ? 'pending' : 'approved' // Default status
        };
        DB.addOrder(newOrder);
        window.location.reload();
    },

    // Add Product
    addProduct: (product) => {
        DB.addInventoryItem(product);
        window.location.reload();
    },

    loadStatsUI: () => {
        const stats = Dashboard.calculateStats();
        const elSales = document.getElementById('stat-sales');
        const elProfit = document.getElementById('stat-profit');
        const elExpense = document.getElementById('stat-expense');

        if (elSales) elSales.textContent = App.formatCurrency(stats.totalSales);
        if (elProfit) elProfit.textContent = App.formatCurrency(stats.totalProfit);
        if (elExpense) elExpense.textContent = App.formatCurrency(stats.totalExpenses);
    },

    renderTable: (elementId, data, columns) => {
        const tableBody = document.querySelector(`#৳{elementId} tbody`);
        if (!tableBody) return;

        tableBody.innerHTML = data.map(row => `
            <tr>
                ৳{columns.map(col => `< td >৳{ row[col] || '-' }</td > `).join('')}
            </tr>
        `).join('');
    },

    // Initialize Charts
    initCharts: () => {
        const ctx = document.getElementById('revenueChart');
        if (!ctx) return;

        // Mock Data for Charts (Enhanced logic would aggregate DB data)
        const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const salesData = [1200, 1900, 300, 500, 2000, 3000, 4500];
        const expenseData = [400, 200, 100, 100, 500, 200, 300];

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Revenue',
                    data: salesData,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Expenses',
                    data: expenseData,
                    borderColor: '#f87171',
                    backgroundColor: 'rgba(248, 113, 113, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#a3a3a3' }
                    }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#a3a3a3' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#a3a3a3' }
                    }
                }
            }
        });

        // Other charts logic...
    }
};

// Initialize Logic
document.addEventListener('DOMContentLoaded', () => {
    // Check Auth
    const user = App.checkAuth();
    if (!user) {
        window.location.href = '../login.html';
        return;
    }

    // Set Name
    const userNameEl = document.getElementById('user-name');
    if (userNameEl) userNameEl.textContent = user.name;
    const userRoleEl = document.getElementById('user-role');
    if (userRoleEl) userRoleEl.textContent = user.role.toUpperCase();

    // Data Init
    Dashboard.initData();
    Dashboard.loadStatsUI();
    Dashboard.initCharts();
});
