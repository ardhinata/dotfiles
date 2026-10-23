# Testpoint: /benchmarks?source=artificial-analysis

Query-param probe: source filter. 'data' shrinks (~33KB vs ~500KB default). Confirms 'source' query param is honored.

Expected status: '200'.
Expected body shape: 'object{keys=2}'.
Required keys: 'data,meta'.
Last verified: 2026-08-25.
