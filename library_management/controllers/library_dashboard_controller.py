# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class LibraryDashboardController(http.Controller):

    @http.route("/library/dashboard/data", type="json", auth="user")
    def get_dashboard_data(self):
        env = request.env

        books = env["library.book"].sudo().search([])
        total_books = len(books)
        total_stock_books = sum(books.mapped("stock"))
        available_books = sum(books.mapped("remaining_stock"))
        borrowed_books = sum(books.mapped("borrowed_stock"))

        borrows = env["library.borrow"].sudo().search([])
        total_fine_paid = sum(borrows.mapped("fine_paid"))
        total_fine_balance = sum(borrows.mapped("fine_balance"))

        borrow_chart = (
            env["library.borrow"]
            .sudo()
            .read_group(
                [("state", "!=", "draft")],
                ["id:count"],
                ["borrow_date:month"],
            )
        )
        category_chart = (
            env["library.book"].sudo().read_group([], ["id:count"], ["category_id"])
        )
        fine_chart = [
            {"label": "Denda Dibayar", "value": total_fine_paid},
            {"label": "Belum Dibayar", "value": total_fine_balance},
        ]

        book_stock_list = (
            env["library.book"]
            .sudo()
            .search_read(
                [],
                ["name", "stock", "borrowed_stock", "remaining_stock"],
                limit=10,
                order="remaining_stock asc",
            )
        )

        top_members_query = (
            env["library.borrow"]
            .sudo()
            .read_group(
                [("state", "!=", "draft")],
                ["id:count"],
                ["member_id"],
                limit=10,
                orderby="member_id_count DESC",
            )
        )

        top_members_list = []
        for m in top_members_query:
            if m.get("member_id"):
                top_members_list.append(
                    {
                        "id": m["member_id"][0],
                        "name": m["member_id"][1],
                        "borrow_count": m["member_id_count"],
                    }
                )
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
            "book_stock_list": book_stock_list,
            "top_members_list": top_members_list,
        }
