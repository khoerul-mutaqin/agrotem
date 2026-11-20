# -*- coding: utf-8 -*-
{
    "name": "CDP Agrotem chatter display size specific user",
    "version": "17.0.0.0.5",
    "license": "OPL-1",
    "summary": "chatter move to buttom for specific user",
    "category": "Custom",
    "author": "CLuedoo",
    "website": "https://cluedoo.com",
    "support": "support@cluedoo.com",
    "depends": ["base","web","mail"],
    'data': [
        'views/res_users_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cdp_agrotem_chatter_display_specific_user/static/src/scss/chatter_adjustment.scss',
            'cdp_agrotem_chatter_display_specific_user/static/src/js/chatter_patch.js',
        ],
    },
}
