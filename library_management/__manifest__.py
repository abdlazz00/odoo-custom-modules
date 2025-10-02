{
    "name": "Library Management",
    "version": "1.0",
    "summary": "Library Management",
    "description": """
        This module for manage Library sistem
    """,
    "category": "Sales",
    "author": "Abdul Aziz",
    "maintainer": "Abdul Aziz",
    "website": "https://github.com/abdlazz00",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/library_security.xml",
        "data/ir_sequence.xml",
        "data/library_scheduler.xml",
        "data/partner_data.xml",
        "views/library_book_views.xml",
        "views/library_support_views.xml",
        "views/library_transaction_views.xml",
        "views/library_settings_views.xml",
        "views/menus.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "auto_install": False,
}
# -*- coding: utf-8 -*-
