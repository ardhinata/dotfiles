# Testpoint: /models?page=2

Negative pagination probe: 'page=2' is silently ignored. Response is the same 690KB payload as no-param. Use 'limit' instead.

Expected status: '200'.
Expected body shape: 'object{keys=3}'.
Required keys: 'data,links,total_count'.
Last verified: 2026-08-25.
