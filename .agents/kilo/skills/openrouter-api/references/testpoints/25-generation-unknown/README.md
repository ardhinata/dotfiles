# Testpoint: /generation with unknown id

Not-found probe: 'GET /generation?id=gen-doesnotexist12345' returns **404** with 'error.{message:"Generation ... not found", code:404}'. Use this to distinguish a missing-id 400 from a real not-found 404.

Expected status: '404'.
Expected body shape: 'object{keys=1,error}'.
Required keys: 'error'.
Last verified: 2026-08-25.
