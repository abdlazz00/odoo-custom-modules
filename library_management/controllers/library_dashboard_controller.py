# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class LibraryDashboardController(http.Controller):

    @http.route('/library/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self):
        env = request.env

        # =====================================================
        # 🔹 KPI SECTION
        # =====================================================
        books = env['library.book'].sudo().search([])
        total_books = len(books)
        total_stock_books = sum(books.mapped('stock'))
        available_books = sum(books.mapped('remaining_stock'))
        borrowed_books = sum(books.mapped('borrowed_stock'))

        borrows = env['library.borrow'].sudo().search([])
        total_fine_paid = sum(borrows.mapped('fine_paid'))
        total_fine_balance = sum(borrows.mapped('fine_balance'))

        # =====================================================
        # 🔹 CHART DATA (optional, tetap dipakai)
        # =====================================================
        borrow_chart = env['library.borrow'].sudo().read_group(
            [('state', '!=', 'draft')],
            ['id:count'],
            ['borrow_date:month'],
        )

        category_chart = env['library.book'].sudo().read_group(
            [], ['id:count'], ['category_id']
        )

        fine_chart = [
            {"label": "Denda Dibayar", "value": total_fine_paid},
            {"label": "Belum Dibayar", "value": total_fine_balance},
        ]

        top_books = env['library.borrow.lines'].sudo().read_group(
            [], ['id:count'], ['book_id']
        )
        top_books_sorted = sorted(top_books, key=lambda x: x.get('id_count', 0), reverse=True)[:5]

        top_members = env['library.borrow'].sudo().read_group(
            [], ['id:count'], ['member_id']
        )
        top_members_sorted = sorted(top_members, key=lambda x: x.get('id_count', 0), reverse=True)[:5]

        # =====================================================
        # 🔹 RETURN STRUCTURE
        # =====================================================
        return {
            "kpi": {
                "total_books": total_books,
                "total_stock_books": total_stock_books,
                "available_books": available_books,
                "borrowed_books": borrowed_books,
                "total_fines_paid": total_fine_paid,
                "total_fines_balance": total_fine_balance,
            },
            "borrow_chart": borrow_chart,
            "category_chart": category_chart,
            "fine_chart": fine_chart,
            "top_books": top_books_sorted,
            "top_members": top_members_sorted,
        }
