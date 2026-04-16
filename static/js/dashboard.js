/**
 * Smart E-Commerce System
 * Dashboard Logic - Integrated with Django API (Async)
 */

const Dashboard = {
    init: async () => {
        try {
            const user = App.checkAuth();
            if (!user) {
                window.location.href = '/login/';
                return;
            }

            // Staff dashboard stats & chart are handled inline in dashboard.html
            // to avoid race conditions. Here we only handle admin/investor fallback.
            const role = user.role || 'staff';
            if (role === 'admin') {
                await Dashboard.loadAdminDashboard();
                await Dashboard.loadPendingApprovals();
                await Dashboard.loadPendingInvestments();
            } else if (role === 'staff') {
                // Handled inline in dashboard.html for staff but can be backup here
                // if (!window.staffDashboardInitialized) await Dashboard.loadStaffDashboard();
            } else {
                // Investor
                const stats = await Dashboard.calculateStats();
                Dashboard.loadStatsUI(stats);
                Dashboard.initCharts(stats);
                await Dashboard.loadActivityTable();
            }

        } catch (err) {
            console.error('Dashboard Init Error:', err);
        }
    },

    loadStaffDashboard: async () => {
        try {
            const dash = await DB.getStaffDashboard();

            // Stats cards handled inline in staff/dashboard.html (or here as backup)
            const elSalesToday = document.getElementById('stat-sales-today');
            if (elSalesToday) elSalesToday.textContent = App.formatCurrency(dash.today.sales);

            const elOrdersNew = document.getElementById('stat-orders-new');
            if (elOrdersNew) elOrdersNew.textContent = dash.pending_orders;

            const elMonthlyVal = document.getElementById('stat-monthly-val');
            if (elMonthlyVal) {
                elMonthlyVal.textContent  = App.formatCurrency(dash.month.sales);
                const perc = Math.min(100, Math.round(dash.month.progress));
                document.getElementById('stat-monthly-perc').textContent = perc + '%';
                document.getElementById('stat-monthly-bar').style.width  = perc + '%';
            }

            // Recent activity table
            await Dashboard.loadActivityTable();

        } catch (err) {
            console.error('Staff dashboard load failed:', err);
        }
    },

    loadAdminDashboard: async () => {
        try {
            const dash = await DB.getAdminDashboard();
            const fin = dash.financials;

            // Stats
            const elSales = document.getElementById('stat-sales');
            const elProfit = document.getElementById('stat-profit');
            const elExpense = document.getElementById('stat-expense');

            if (elSales) elSales.textContent = App.formatCurrency(fin.total_sales);
            if (elExpense) elExpense.textContent = App.formatCurrency(fin.total_expenses);
            if (elProfit) elProfit.textContent = App.formatCurrency(fin.net_profit);

            // Charts
            if (dash.monthly_trend) {
                Dashboard.initCharts(dash.monthly_trend);
            }

            // Activity
            const tableBody = document.querySelector('#activity-table tbody');
            if (tableBody && dash.recent_activity) {
                tableBody.innerHTML = dash.recent_activity.map((act, idx) => {
                    const typeColor = act.type === 'expense' ? 'text-red-400' : 'text-emerald-400';
                    const typeBg = act.type === 'expense' ? 'bg-red-500/[0.03]' : 'bg-emerald-500/[0.03]';
                    
                    return `
                        <tr class="${typeBg} hover:bg-white/[0.05] transition-colors">
                            <td class="text-xs text-muted font-medium">${idx + 1}</td>
                            <td class="font-medium ${typeColor}">${act.by_name}</td>
                            <td class="text-xs ${typeColor} opacity-80">${act.date}</td>
                            <td>
                                <div class="flex items-center gap-2">
                                    <iconify-icon icon="${act.type === 'expense' ? 'solar:bill-list-linear' : 'solar:bag-check-linear'}" 
                                        class="${typeColor}"></iconify-icon>
                                    <span class="text-sm font-medium ${typeColor}">${act.description}</span>
                                </div>
                            </td>
                            <td class="font-bold ${typeColor}">
                                ${act.type === 'expense' ? '-' : '+'} ${App.formatCurrency(act.amount)}
                            </td>
                            <td>
                                <span class="status-badge status-${act.status === 'completed' || act.status === 'approved' ? 'success' : 'warning'}">
                                    ${act.status || 'Pending'}
                                </span>
                            </td>
                        </tr>
                    `;
                }).join('');
            }
        } catch (err) {
            console.error('Admin dashboard load failed:', err);
        }
    },

    // ── Charts ────────────────────────────────────────────────────────
    initCharts: (data) => {
        const ctx = document.getElementById('revenueChart');
        if (!ctx) return;

        // Check if data is from Admin API (array of {month, sales, expenses})
        const labels = Array.isArray(data) ? data.map(d => d.month) : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const salesData = Array.isArray(data) ? data.map(d => d.sales) : labels.map(() => 0);
        const expenseData = Array.isArray(data) ? data.map(d => d.expenses) : labels.map(() => 0);

        // Cleanup existing
        const existingChart = Chart.getChart(ctx);
        if (existingChart) existingChart.destroy();

        new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    { 
                        label: 'Revenue', 
                        data: salesData, 
                        borderColor: '#10b981', 
                        backgroundColor: 'rgba(16,185,129,0.1)', 
                        tension: 0.4, 
                        fill: true 
                    },
                    { 
                        label: 'Expenses', 
                        data: expenseData, 
                        borderColor: '#f87171', 
                        backgroundColor: 'rgba(248,113,113,0.1)', 
                        tension: 0.4, 
                        fill: true 
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: ctx => ' ৳' + ctx.parsed.y.toLocaleString()
                        }
                    }
                },
                scales: {
                    y: { 
                        grid: { color: 'rgba(255,255,255,0.05)' }, 
                        ticks: { 
                            color: '#a3a3a3',
                            callback: v => '৳' + v.toLocaleString()
                        } 
                    },
                    x: { 
                        grid: { display: false }, 
                        ticks: { color: '#a3a3a3' } 
                    }
                }
            }
        });
    },

    loadPendingApprovals: async () => {
        const section = document.getElementById('approvals-section');
        const tableBody = document.querySelector('#approvals-table tbody');
        if (!section || !tableBody) return;

        try {
            const data = await DB.getTransactions();
            const txns = (Array.isArray(data) ? data : (data.results || []))
                .filter(t => t.status === 'pending');

            if (txns.length === 0) {
                section.style.display = 'none';
                return;
            }

            section.style.display = 'block';
            document.getElementById('pending-count').textContent = `${txns.length} Pending`;

            tableBody.innerHTML = txns.map(t => `
                <tr id="txn-${t.id}">
                    <td>${t.date}</td>
                    <td>${t.from_user || 'System'}</td>
                    <td>
                        <p class="text-xs font-semibold text-white">${t.note}</p>
                    </td>
                    <td><span style="color: var(--secondary); font-weight: 600;">৳${t.amount.toLocaleString()}</span></td>
                    <td style="text-align: right;">
                        <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
                            <button onclick="Dashboard.handleApprovalAction(${t.id}, 'approve')" class="btn" style="padding: 0.25rem 0.5rem; background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); font-size: 10px;">Approve</button>
                            <button onclick="Dashboard.handleApprovalAction(${t.id}, 'reject')" class="btn" style="padding: 0.25rem 0.5rem; background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); font-size: 10px;">Reject</button>
                        </div>
                    </td>
                </tr>
            `).join('');
        } catch (e) {
            console.error('Approvals load failed', e);
        }
    },

    loadActivityTable: async () => {
        const tableBody = document.querySelector('#activity-table tbody');
        if (!tableBody) return;
        try {
            // Logic for investors/fallback (Admins use loadAdminDashboard which populates activity directly)
            const data = await DB.getOrders();
            const txns = Array.isArray(data) ? data : (data.results || []);
            tableBody.innerHTML = txns.slice(0, 5).map(t => `
                <tr>
                    <td>${new Date(t.created_at || Date.now()).toLocaleDateString()}</td>
                    <td>${t.product_name || t.description || 'System Activity'}</td>
                    <td>${App.formatCurrency(t.amount)}</td>
                    <td><span class="status-badge status-${t.status === 'completed' || t.status === 'approved' ? 'success' : 'warning'}">${t.status}</span></td>
                </tr>
            `).join('');
        } catch (e) {
            console.error('Activity table error:', e);
        }
    },

    calculateStats: async () => {
        try {
            const data = await DB.getOrders();
            let totalSales = 0, totalExpenses = 0, totalProfit = 0;
            const txns = Array.isArray(data) ? data : (data.results || []);

            txns.forEach(t => {
                const amount = Number(t.amount || 0);
                if (t.status === 'completed') {
                    totalSales  += amount;
                    totalProfit += amount * 0.3;
                }
            });
            totalProfit -= totalExpenses;
            return { totalSales, totalExpenses, totalProfit, txns };
        } catch (e) {
            console.error('Stats calculation failed', e);
            return { totalSales: 0, totalExpenses: 0, totalProfit: 0, txns: [] };
        }
    },

    loadStatsUI: (stats) => {
        const elSales   = document.getElementById('stat-sales');
        const elProfit  = document.getElementById('stat-profit');
        const elExpense = document.getElementById('stat-expense');
        if (elSales)   elSales.textContent   = App.formatCurrency(stats.totalSales);
        if (elProfit)  elProfit.textContent  = App.formatCurrency(stats.totalProfit);
        if (elExpense) elExpense.textContent = App.formatCurrency(stats.totalExpenses);
    },

    handleApprovalAction: async (id, action) => {
        const row = document.getElementById(`txn-${id}`);
        if (!row) return;

        try {
            row.innerHTML = `<td colspan="5" style="text-align: center; color: var(--text-muted);">${action === 'approve' ? 'Approving...' : 'Rejecting...'}</td>`;
            
            await DB.approveTransaction(id, action);
            
            row.style.opacity = '0.5';
            row.innerHTML = `<td colspan="5" style="text-align: center; color: ${action === 'approve' ? '#10b981' : '#ef4444'}; font-weight: 600;">Expense ${action === 'approve' ? 'Approved' : 'Rejected'}</td>`;
            
            // Refresh dashboard
            setTimeout(async () => {
                await Dashboard.loadPendingApprovals();
                const user = App.checkAuth();
                if (user && user.role === 'admin') {
                    await Dashboard.loadAdminDashboard();
                } else {
                    const stats = await Dashboard.calculateStats();
                    Dashboard.loadStatsUI(stats);
                }
            }, 1000);

        } catch (e) {
            alert('Action failed: ' + e.message);
            await Dashboard.loadPendingApprovals();
        }
    },

    loadPendingInvestments: async () => {
        const section = document.getElementById('investments-section');
        const tableBody = document.querySelector('#investments-table tbody');
        if (!section || !tableBody) return;

        try {
            const data = await DB.getAdminDashboard();
            const proposals = data.pending_investments || [];

            if (proposals.length === 0) {
                section.style.display = 'none';
                return;
            }

            section.style.display = 'block';
            document.getElementById('invest-count').textContent = `${proposals.length} Pending Proposals`;

            tableBody.innerHTML = proposals.map(p => `
                <tr id="inv-${p.id}">
                    <td>${p.date}</td>
                    <td><span class="font-bold text-white">${p.investor_name}</span></td>
                    <td><span class="font-black text-indigo-400">৳${p.amount.toLocaleString()}</span></td>
                    <td><span class="px-2 py-0.5 bg-indigo-500/10 text-indigo-400 text-[10px] font-bold rounded">${p.equity}% Equity</span></td>
                    <td style="text-align: right;">
                        <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
                            <button onclick="Dashboard.handleInvestmentAction(${p.id}, 'approve')" class="btn" style="padding: 0.25rem 0.5rem; background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); font-size: 10px;">Approve</button>
                            <button onclick="Dashboard.handleInvestmentAction(${p.id}, 'reject')" class="btn" style="padding: 0.25rem 0.5rem; background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); font-size: 10px;">Reject</button>
                        </div>
                    </td>
                </tr>
            `).join('');
        } catch (e) {
            console.error('Investments load failed', e);
        }
    },

    handleInvestmentAction: async (id, action) => {
        const row = document.getElementById(`inv-${id}`);
        if (!row) return;

        try {
            row.style.opacity = '0.5';
            const originalContent = row.innerHTML;
            row.innerHTML = `<td colspan="5" style="text-align: center; color: var(--text-muted);">${action === 'approve' ? 'Approving Investment...' : 'Rejecting Proposal...'}</td>`;
            
            await DB.approveInvestment(id, action);
            
            row.innerHTML = `<td colspan="5" style="text-align: center; color: ${action === 'approve' ? '#10b981' : '#ef4444'}; font-weight: 600;">Investment ${action === 'approve' ? 'Approved & Capital Credited' : 'Rejected'}</td>`;
            
            setTimeout(async () => {
                await Dashboard.loadPendingInvestments();
                await Dashboard.loadAdminDashboard();
            }, 1000);

        } catch (e) {
            alert('Action failed: ' + e.message);
            await Dashboard.loadPendingInvestments();
        }
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    Dashboard.init();
});
