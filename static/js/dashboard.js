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
                await Dashboard.loadCompanyProducts();
                await Dashboard.loadStaffApprovals();
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
            if (dash.recent_activity) {
                Dashboard.allActivity = dash.recent_activity;
                Dashboard.renderActivityRows(dash.recent_activity);
            }
        } catch (err) {
            console.error('Admin dashboard load failed:', err);
        }
    },

    filterActivity: (type) => {
        // Update tab UI
        document.querySelectorAll('.activity-tab').forEach(tab => tab.classList.remove('active'));
        const activeTab = document.getElementById(`tab-${type}`);
        if (activeTab) activeTab.classList.add('active');

        if (!Dashboard.allActivity) return;

        let filtered = Dashboard.allActivity;
        if (type === 'finance') {
            filtered = Dashboard.allActivity.filter(a => a.type === 'sale' || a.type === 'expense');
        } else if (type === 'user') {
            filtered = Dashboard.allActivity.filter(a => a.type === 'user');
        } else if (type === 'investment') {
            filtered = Dashboard.allActivity.filter(a => a.type === 'investment');
        } else if (type === 'product') {
            filtered = Dashboard.allActivity.filter(a => a.type === 'product');
        }

        Dashboard.renderActivityRows(filtered);
    },

    renderActivityRows: (activities) => {
        const tableBody = document.querySelector('#activity-table tbody');
        if (!tableBody) return;

        if (activities.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="6" class="text-center py-8 text-muted">No activity records found for this category.</td></tr>`;
            return;
        }

        tableBody.innerHTML = activities.map((act, idx) => {
            let typeColor = 'text-emerald-400';
            let typeBg = 'bg-emerald-500/[0.03]';
            let icon = 'solar:bag-check-linear';
            let amountPrefix = '+';

            if (act.type === 'expense') {
                typeColor = 'text-red-400';
                typeBg = 'bg-red-500/[0.03]';
                icon = 'solar:bill-list-linear';
                amountPrefix = '-';
            } else if (act.type === 'user') {
                typeColor = 'text-blue-400';
                typeBg = 'bg-blue-500/[0.03]';
                icon = 'solar:users-group-rounded-linear';
                amountPrefix = '';
            } else if (act.type === 'task') {
                typeColor = 'text-amber-400';
                typeBg = 'bg-amber-500/[0.03]';
                icon = 'solar:checklist-minimalistic-linear';
                amountPrefix = '';
            } else if (act.type === 'investment') {
                typeColor = 'text-indigo-400';
                typeBg = 'bg-indigo-500/[0.03]';
                icon = 'solar:hand-money-linear';
                amountPrefix = '+';
            } else if (act.type === 'product') {
                typeColor = 'text-purple-400';
                typeBg = 'bg-purple-500/[0.03]';
                icon = 'solar:box-linear';
                amountPrefix = '';
            }
            
            return `
                <tr class="${typeBg} hover:bg-white/[0.05] transition-colors">
                    <td class="text-xs text-muted font-medium">${idx + 1}</td>
                    <td class="font-medium ${typeColor}">${act.by_name}</td>
                    <td class="text-xs ${typeColor} opacity-80">${act.date}</td>
                    <td>
                        <div class="flex items-center gap-2">
                            <iconify-icon icon="${icon}" class="${typeColor}"></iconify-icon>
                            <span class="text-sm font-medium ${typeColor}">${act.description}</span>
                        </div>
                    </td>
                    <td class="font-bold ${typeColor}">
                        ${amountPrefix} ${act.amount > 0 ? App.formatCurrency(act.amount) : '–'}
                    </td>
                    <td>
                        <span class="status-badge status-${act.status === 'completed' || act.status === 'approved' || act.status === 'active' || act.status === 'in_stock' ? 'success' : 'warning'}">
                            ${act.status || 'Pending'}
                        </span>
                    </td>
                </tr>
            `;
        }).join('');
    },

    loadCompanyProducts: async () => {
        const tableBody = document.querySelector('#dashboard-products-table tbody');
        if (!tableBody) return;
        try {
            const data = await DB.getAdminProducts();
            const products = Array.isArray(data) ? data : (data.results || []);
            
            if (products.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">No products found in the company.</td></tr>`;
                return;
            }

            tableBody.innerHTML = products.slice(0, 5).map(p => {
                const stockClass = p.stock === 0 ? 'stock-zero' : p.is_low_stock ? 'stock-low' : 'stock-ok';
                const stockLabel = p.stock === 0 ? 'Out of Stock' : p.is_low_stock ? `Low (${p.stock})` : p.stock;
                const staffName  = (p.added_by && p.added_by.name) ? p.added_by.name : 'Unknown';
                
                return `
                    <tr>
                        <td class="font-medium text-white">${p.name}</td>
                        <td class="text-xs text-muted">${p.category}</td>
                        <td><span class="stock-badge ${stockClass}">${stockLabel}</span></td>
                        <td class="font-medium text-white">৳${p.sell_price.toLocaleString()}</td>
                        <td>
                            <div class="flex items-center gap-2">
                                <div class="avatar-xs" style="width: 20px; height: 20px; border-radius: 50%; background: var(--primary); display: flex; align-items: center; justify-content: center; font-size: 10px; color: white;">
                                    ${staffName.charAt(0).toUpperCase()}
                                </div>
                                <span class="text-xs text-indigo-200">${staffName}</span>
                            </div>
                        </td>
                    </tr>
                `;
            }).join('');
        } catch (err) {
            console.error('Failed to load company products:', err);
            tableBody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #ef4444; padding: 1.5rem;">Failed to load products.</td></tr>`;
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
    },

    loadStaffApprovals: async () => {
        const section = document.getElementById('staff-approvals-section');
        const tableBody = document.querySelector('#staff-approvals-table tbody');
        if (!section || !tableBody) return;

        try {
            const data = await DB.getAdminDashboard();
            const staff = data.pending_staff || [];

            if (staff.length === 0) {
                section.style.display = 'none';
                return;
            }

            section.style.display = 'block';
            document.getElementById('staff-pending-count').textContent = `${staff.length} Pending`;

            tableBody.innerHTML = staff.map(s => `
                <tr id="staff-${s.id}">
                    <td class="text-xs text-muted">${s.date}</td>
                    <td><span class="font-bold text-white">${s.name}</span></td>
                    <td><span class="text-xs text-indigo-200">${s.email}</span></td>
                    <td style="text-align: right;">
                        <div style="display: flex; gap: 0.5rem; justify-content: flex-end;">
                            <button onclick="Dashboard.handleStaffApproval(${s.id}, 'approve')" class="btn" style="padding: 0.25rem 0.5rem; background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); font-size: 10px;">Approve</button>
                            <button onclick="Dashboard.handleStaffApproval(${s.id}, 'reject')" class="btn" style="padding: 0.25rem 0.5rem; background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); font-size: 10px;">Reject</button>
                        </div>
                    </td>
                </tr>
            `).join('');
        } catch (e) {
            console.error('Staff approvals load failed', e);
        }
    },

    handleStaffApproval: async (id, action) => {
        const row = document.getElementById(`staff-${id}`);
        if (!row) return;

        try {
            row.style.opacity = '0.5';
            const originalContent = row.innerHTML;
            row.innerHTML = `<td colspan="4" style="text-align: center; color: var(--text-muted);">${action === 'approve' ? 'Approving Staff...' : 'Rejecting...'}</td>`;
            
            await DB.approveStaff(id, action);
            
            row.innerHTML = `<td colspan="4" style="text-align: center; color: ${action === 'approve' ? '#10b981' : '#ef4444'}; font-weight: 600;">Staff ${action === 'approve' ? 'Approved & Verified' : 'Rejected'}</td>`;
            
            setTimeout(async () => {
                await Dashboard.loadStaffApprovals();
                const user = App.checkAuth();
                if (user && user.role === 'admin') {
                    await Dashboard.loadAdminDashboard();
                }
            }, 1000);

        } catch (e) {
            alert('Action failed: ' + e.message);
            await Dashboard.loadStaffApprovals();
        }
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    Dashboard.init();
});
