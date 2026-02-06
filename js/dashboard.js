/**
 * Smart E-Commerce System
 * Dashboard Logic
 */

const Dashboard = {
    // Initial Data Seeding
    initData: () => {
        if (!localStorage.getItem('smartEcoSales')) {
            const seedSales = [
                { id: 1, product: 'Wireless Headset', amount: 1200, date: '2024-02-01', type: 'sale', platform: 'Daraz' },
                { id: 2, product: 'PowerBank 20k', amount: 2500, date: '2024-02-02', type: 'sale', platform: 'CartUp' },
                { id: 3, product: 'Smart Watch', amount: 4500, date: '2024-02-03', type: 'sale', platform: 'Daraz' },
                { id: 4, product: 'Office Chair', amount: 1500, date: '2024-02-02', type: 'expense', category: 'Ops' },
                { id: 5, product: 'Gaming Mouse', amount: 3500, date: '2024-02-04', type: 'sale', platform: 'Offline' },
                { id: 6, product: 'Mechanical Keyboard', amount: 6000, date: '2024-02-04', type: 'sale', platform: 'Daraz' },
                { id: 7, product: 'Shipping Labels', amount: 200, date: '2024-02-04', type: 'expense', category: 'Logistics' },
                { id: 8, product: 'Facebook Ads', amount: 5000, date: '2024-02-05', type: 'expense', category: 'Marketing' },
                { id: 9, product: 'Laptop Stand', amount: 1800, date: '2024-02-05', type: 'sale', platform: 'CartUp' },
                { id: 10, product: 'USB Hub', amount: 1200, date: '2024-02-06', type: 'sale', platform: 'Offline' },
            ];
            localStorage.setItem('smartEcoSales', JSON.stringify(seedSales));
        }

        if (!localStorage.getItem('smartEcoInventory')) {
            const seedInventory = [
                { id: 1, name: 'Wireless Headset', stock: 45, buyPrice: 800, sellPrice: 1200, category: 'Audio', description: 'High-quality wireless headset with noise cancellation and 20h battery life.', image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=200&auto=format&fit=crop' },
                { id: 2, name: 'PowerBank 20k', stock: 20, buyPrice: 1500, sellPrice: 2500, category: 'Accessories', description: '20000mAh fast-charging power bank with dual USB-C output.', image: 'https://images.unsplash.com/photo-1609592424363-233bb4235afb?q=80&w=200&auto=format&fit=crop' },
                { id: 3, name: 'Smart Watch', stock: 12, buyPrice: 3000, sellPrice: 4500, category: 'Wearables', description: 'Fitness tracker with heart rate monitor, GPS, and waterproof design.', image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=200&auto=format&fit=crop' },
                { id: 4, name: 'Gaming Mouse', stock: 8, buyPrice: 2000, sellPrice: 3500, category: 'Gaming', description: 'RGB gaming mouse with 16000 DPI sensor and programmable buttons.', image: 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?q=80&w=200&auto=format&fit=crop' },
                { id: 5, name: 'Mech Keyboard', stock: 15, buyPrice: 4000, sellPrice: 6000, category: 'Gaming', description: 'Mechanical keyboard with Blue switches and customizable RGB backlight.', image: 'https://images.unsplash.com/photo-1587829741301-3231756c515c?q=80&w=200&auto=format&fit=crop' },
                { id: 6, name: '24" Monitor', stock: 5, buyPrice: 12000, sellPrice: 15500, category: 'Electronics', description: '1080p IPS monitor with 144Hz refresh rate for smooth gaming.', image: 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?q=80&w=200&auto=format&fit=crop' },
                { id: 7, name: 'Laptop Stand', stock: 30, buyPrice: 1000, sellPrice: 1800, category: 'Accessories', description: 'Ergonomic aluminum laptop stand, adjustable height and angle.', image: 'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?q=80&w=200&auto=format&fit=crop' },
                { id: 8, name: 'USB-C Cable', stock: 50, buyPrice: 200, sellPrice: 450, category: 'Accessories', description: 'Braided 2m USB-C to USB-C cable supporting 100W PD charging.', image: 'https://images.unsplash.com/photo-1625961332771-3f40b0e2bdcf?q=80&w=200&auto=format&fit=crop' },
            ];
            localStorage.setItem('smartEcoInventory', JSON.stringify(seedInventory));
        }
    },

    getSales: () => JSON.parse(localStorage.getItem('smartEcoSales') || '[]'),
    getInventory: () => JSON.parse(localStorage.getItem('smartEcoInventory') || '[]'),

    // Calculate Totals
    calculateStats: () => {
        const txns = Dashboard.getSales();
        let totalSales = 0;
        let totalExpenses = 0;
        let totalProfit = 0; // Simplified profit (Revenue - Expense) for demo, 
        // Real profit needs referencing buyPrice.

        // Advanced Profit Calc: Revenue - (BuyPrice * Qty) - Expenses
        // For this demo 'sale' entries are just revenue.

        txns.forEach(t => {
            if (t.type === 'sale') {
                totalSales += t.amount;
                // Heuristic: Assume 30% margin for demo if COGS not linked directly here
                totalProfit += (t.amount * 0.3);
            } else if (t.type === 'expense') {
                totalExpenses += t.amount;
                totalProfit -= t.amount;
            }
        });

        return { totalSales, totalExpenses, totalProfit };
    },

    // Add Record
    addRecord: (record) => {
        const data = Dashboard.getSales();
        record.id = Date.now();
        record.date = new Date().toISOString().split('T')[0];
        data.unshift(record); // Add to top
        localStorage.setItem('smartEcoSales', JSON.stringify(data));
        window.location.reload();
    },

    // Add Product
    addProduct: (product) => {
        const data = Dashboard.getInventory();
        product.id = Date.now();
        data.push(product);
        localStorage.setItem('smartEcoInventory', JSON.stringify(data));
        window.location.reload();
    },

    loadStatsUI: () => {
        const stats = Dashboard.calculateStats();
        // Update DOM elements if they exist
        const elSales = document.getElementById('stat-sales');
        const elProfit = document.getElementById('stat-profit');
        const elExpense = document.getElementById('stat-expense');

        if (elSales) elSales.textContent = App.formatCurrency(stats.totalSales);
        if (elProfit) elProfit.textContent = App.formatCurrency(stats.totalProfit);
        if (elExpense) elExpense.textContent = App.formatCurrency(stats.totalExpenses);
    },

    renderTable: (elementId, data, columns) => {
        const tableBody = document.querySelector(`#${elementId} tbody`);
        if (!tableBody) return;

        tableBody.innerHTML = data.map(row => `
            <tr>
                ${columns.map(col => `<td>${row[col] || '-'}</td>`).join('')}
            </tr>
        `).join('');
    },

    // Initialize Charts
    initCharts: () => {
        const ctx = document.getElementById('revenueChart');
        if (!ctx) return;

        // Process Data for Chart
        const txns = Dashboard.getSales();
        // Group by Date (last 7 days logic simulated)
        const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const salesData = [1200, 1900, 300, 500, 2000, 3000, 4500]; // Mock
        const expenseData = [400, 200, 100, 100, 500, 200, 300]; // Mock

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
                        labels: { color: getComputedStyle(document.body).getPropertyValue('--text-main') }
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

        // Initialize Staff Chart if exists
        const ctxStaff = document.getElementById('staffChart');
        if (ctxStaff) {
            new Chart(ctxStaff, {
                type: 'bar',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'My Sales',
                        data: [500, 800, 450, 1200, 1500, 900, 2000],
                        backgroundColor: '#6366f1',
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
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
        });
    }

        // Investor Allocation Chart
        const ctxAlloc = document.getElementById('allocationChart');
    if(ctxAlloc) {
        new Chart(ctxAlloc, {
            type: 'doughnut',
            data: {
                labels: ['Inventory', 'Marketing', 'Ops', 'Reserves'],
                datasets: [{
                    data: [45, 30, 15, 10],
                    backgroundColor: [
                        '#10b981', // Emerald
                        '#6366f1', // Indigo
                        '#f59e0b', // Amber
                        '#64748b'  // Slate
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#a3a3a3' }
                    }
                }
            }
        });
    }
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
    Dashboard.initData();
    Dashboard.loadStatsUI();
    Dashboard.initCharts();
});
