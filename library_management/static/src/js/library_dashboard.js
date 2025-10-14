/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted } from "@odoo/owl";

class LibraryDashboard extends Component {
    static props = {
        action: { type: Object, optional: true },
        actionId: { type: Number, optional: true },
        updateActionState: { type: Function, optional: true },
        className: { type: String, optional: true },
    };

    setup() {
        this.state = useState({
            loading: true,
            kpis: {},
            book_stock_list: [],
            top_members_list: [],
        });

        onMounted(() => {
            console.log("📚 Library Dashboard mounted");
            this.loadAll();
            this._startAutoRefresh();
        });
    }

    // ======================================================
    // AUTO REFRESH
    // ======================================================
    _startAutoRefresh() {
        setInterval(() => this.loadAll(false), 300000); // Refresh setiap 5 menit
    }

    // ======================================================
    // LOAD DATA DARI CONTROLLER
    // ======================================================
    async loadAll(showSpinner = true) {
        try {
            if (showSpinner) this.state.loading = true;
            console.log("⚡ Memuat data dashboard via endpoint /library/dashboard/data ...");

            const response = await fetch("/library/dashboard/data", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({}),
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const result = await response.json();
            if (!result || !result.result) throw new Error("Invalid JSON-RPC response format");

            const data = result.result;
            console.log("📦 Data dashboard diterima:", data);

            // ======================================================
            // KPI
            // ======================================================
            const k = data.kpi || {};
            this.state.kpis = {
                total_books: k.total_books || 0,
                total_stock_books: k.total_stock_books || 0,
                available_books: k.available_books || 0,
                borrowed_books: k.borrowed_books || 0,
                total_fines_paid: this._formatCurrency(k.total_fines_paid || 0),
                total_fines_balance: this._formatCurrency(k.total_fines_balance || 0),
            };

            // ======================================================
            // TOP DATA
            // ======================================================
            this.state.book_stock_list = data.book_stock_list || [];

            this.state.top_members_list = data.top_members_list || [];

            // ======================================================
            // RENDER CHART
            // ======================================================
            setTimeout(() => {
                this._renderBorrowChart(data.borrow_chart);
                this._renderCategoryChart(data.category_chart);
                this._renderFineChart(data.fine_chart);
            }, 250);

            console.log("✅ Dashboard berhasil dimuat & chart dirender.");
        } catch (error) {
            console.error("❌ Gagal memuat data dashboard:", error);
            alert("Terjadi kesalahan saat memuat data dashboard. Cek console untuk detail.");
        } finally {
            this.state.loading = false;
        }
    }

    // ======================================================
    // UTIL: FORMAT RUPIAH
    // ======================================================
    _formatCurrency(value) {
        return new Intl.NumberFormat("id-ID", {
            style: "currency",
            currency: "IDR",
            minimumFractionDigits: 0,
        }).format(value);
    }

    // ======================================================
    // CHART RENDERERS
    // ======================================================

    _renderBorrowChart(data) {
        console.log("📊 Borrow chart data:", data);
        if (!data?.length) data = [{ "borrow_date:month": "Tidak Ada", "borrow_date_count": 0 }];

        const canvas = document.getElementById("chartBorrow");
        const labels = data.map(r => r["borrow_date:month"] || "Tidak diketahui");
        const values = data.map(r => r["borrow_date_count"] || 0);

        this._renderChart(canvas, "bar", labels, values, "Jumlah Peminjaman");
    }

    _renderCategoryChart(data) {
        console.log("📈 Category chart data:", data);
        if (!data?.length) data = [{ "category_id": [false, "Tidak Ada"], "category_id_count": 0 }];

        const canvas = document.getElementById("chartCategory");
        const labels = data.map(r => r["category_id"]?.[1] || "Tanpa Kategori");
        const values = data.map(r => r["category_id_count"] || 0);

        this._renderChart(canvas, "pie", labels, values, "Distribusi Buku per Kategori");
    }

    _renderFineChart(data) {
        console.log("💰 Fine chart data:", data);
        if (!data?.length) return;

        const canvas = document.getElementById("chartFine");
        const labels = data.map(r => r.label);
        const values = data.map(r => r.value);

        this._renderChart(canvas, "doughnut", labels, values, "Status Pembayaran Denda");
    }

    // ======================================================
    // GENERIC CHART RENDERER
    // ======================================================
    _renderChart(canvasEl, type, labels, values, label = "") {
        if (!canvasEl) {
            console.warn("⏳ Canvas belum siap untuk chart:", label);
            return;
        }
        if (typeof window.Chart === "undefined") {
            console.warn("⚠️ Chart.js belum dimuat, skip render:", label);
            return;
        }

        const ctx = canvasEl.getContext("2d");
        if (!ctx) return;

        const old = window.Chart?.getChart(canvasEl);
        if (old) old.destroy();

        new window.Chart(ctx, {
            type,
            data: {
                labels,
                datasets: [{
                    label,
                    data: values,
                    backgroundColor: [
                        "#007bff", "#28a745", "#ffc107", "#dc3545", "#17a2b8",
                        "#6610f2", "#fd7e14", "#20c997", "#6f42c1", "#198754"
                    ],
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: type !== "bar" },
                    datalabels: {
                        color: "#fff",
                        font: { weight: "bold", size: 10 },
                        formatter: value => value,
                    },
                },
                scales: type === "bar" ? {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } },
                } : {},
            },
        });
    }
}

// ======================================================
// REGISTER DASHBOARD ACTION
// ======================================================
LibraryDashboard.template = "library_management.Dashboard";
registry.category("actions").add("library_management.dashboard", LibraryDashboard);
