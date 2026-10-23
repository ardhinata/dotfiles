# Testpoint: /models?limit=10

Pagination probe: 'limit=10' returns ~13KB. 'per_page=10/50/500' and 'page=2/5/999' are silently ignored (~690KB identical payload).

Expected status: '200'.
Expected body shape: 'object{keys=3}'.
Required keys: 'data,links,total_count'.
Last verified: 2026-08-25.
