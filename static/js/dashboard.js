/**
 * Smart E-Commerce System
 * Dashboard Logic - Integrated with Django API (Async)
 */

const Dashboard = {
    // Initial Data Fetching
    init: async () => {
        try {
            // Check Auth
            const user = App.checkAuth();
            if (!user) {
                window.location.href = '/login/';
                return;
            }

            // Set UI Names
            const userNameEl = document.getElementById('user-name');
            if (userNameEl) userNameEl.textContent = user.name;
            const userRoleEl = document.getElementById('user-role');
            if (userRoleEl) userRoleEl.textContent = user.role.toUpperCase();

            // Fetch Data
            const stats = await Dashboard.calculateStats();
            Dashboard.loadStatsUI(stats);
            Dashboard.initCharts(stats);
            
            // Load activity table
            await Dashboard.loadActivityTable();

            // Staff specific UI updates
            const elSalesToday = document.getElementById('stat-sales-today');
            if (elSalesToday) elSalesToday.textContent = App.formatCurrency(stats.totalSales); // For demo, using total

            const elOrdersNew = document.getElementById('stat-orders-new');
            if (elOrdersNew) elOrdersNew.textContent = stats.txns.filter(t => t.status === 'pending').length;

            const elMonthlyVal = document.getElementById('stat-monthly-val');
            if (elMonthlyVal) {
                elMonthlyVal.textContent = App.formatCurrency(stats.totalSales);
                const perc = Math.min(100, Math.round((stats.totalSales / 50000) * 100));
                document.getElementById('stat-monthly-perc').textContent = perc + '%';
                document.getElementById('stat-monthly-bar').style.width = perc + '%';
            }

        } catch (err) {
            console.error('Dashboard Init Error:', err);
        }
    },

    // Calculate Totals from API
    calculateStats: async () => {
        try {
            // For Admin dashboard, we use the analytics endpoint if possible, 
            // or aggregate multiple calls. Let's use the reports endpoint.
            const data = await DB.getOrders(); // Returns orders/transactions
            
            let totalSales = 0;
            let totalExpenses = 0;
            let totalProfit = 0;

            const txns = Array.isArray(data) ? data : (data.results || []);

            txns.forEach(t => {
                const amount = Number(t.amount || t.total_amount || 0);
                if (t.type === 'sale' || t.status === 'delivered') {
                    totalSales += amount;
                    // Mock profit logic or use backend profit if available
                    totalProfit += (amount * 0.3);
                } else if (t.type === 'expense') {
                    totalExpenses += amount;
                }
            });

            // Adjust profit
            totalProfit -= totalExpenses;

            return { totalSales, totalExpenses, totalProfit, txns };
        } catch (e) {
            console.error('Stats calculation failed', e);
            return { totalSales: 0, totalExpenses: 0, totalProfit: 0, txns: [] };
        }
    },

    loadStatsUI: (stats) => {
        const elSales = document.getElementById('stat-sales');
        const elProfit = document.getElementById('stat-profit');
        const elExpense = document.getElementById('stat-expense');

        if (elSales) elSales.textContent = App.formatCurrency(stats.totalSales);
        if (elProfit) elProfit.textContent = App.formatCurrency(stats.totalProfit);
        if (elExpense) elExpense.textContent = App.formatCurrency(stats.totalExpenses);
    },

    loadActivityTable: async () => {
        const tableBody = document.querySelector('#activity-table tbody');
        if (!tableBody) return;

        const data = await DB.getOrders();
        const txns = Array.isArray(data) ? data : (data.results || []);

        tableBody.innerHTML = txns.slice(0, 5).map(t => `
            <tr>
                <td>${new Date(t.created_at || Date.now()).toLocaleDateString()}</td>
                <td>${t.product_name || t.description || 'System Activity'}</td>
                <td>${App.formatCurrency(t.amount || t.total_amount)}</td>
                <td><span class="status-badge status-${t.status === 'delivered' || t.status === 'approved' ? 'success' : 'warning'}">${t.status}</span></td>
            </tr>
        `).join('');
    },

    // Initialize Charts
    initCharts: (stats) => {
        const ctx = document.getElementById('revenueChart');
        const sCtx = document.getElementById('staffChart');
        if (!ctx && !sCtx) return;

        const currentCtx = ctx || sCtx;
        const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const salesData = [stats.totalSales * 0.1, stats.totalSales * 0.15, stats.totalSales * 0.05, stats.totalSales * 0.2, stats.totalSales * 0.25, stats.totalSales * 0.1, stats.totalSales * 0.15];
        const expenseData = [stats.totalExpenses * 0.2, stats.totalExpenses * 0.1, stats.totalExpenses * 0.3, stats.totalExpenses * 0.1, stats.totalExpenses * 0.1, stats.totalExpenses * 0.1, stats.totalExpenses * 0.1];

        new Chart(currentCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: ctx ? 'Revenue' : 'Sales Recorded',
                    data: salesData,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: ctx ? 'Expenses' : 'Expenses Submitted',
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
                scales: {
                    y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#a3a3a3' } },
                    x: { grid: { display: false }, ticks: { color: '#a3a3a3' } }
                }
            }
        });
    }
};

// Initialize Logic
document.addEventListener('DOMContentLoaded', () => {
    Dashboard.init();
});
