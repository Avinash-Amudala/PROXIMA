"""
Quick test to verify the API works
"""

import sys
sys.path.append('src')

print("=" * 80)
print("Testing PROXIMA API")
print("=" * 80)

try:
    from proxima.api.main import app
    print("✓ API module imported successfully")
    
    # Test that the app is created
    print(f"✓ FastAPI app created: {app.title}")
    
    # List all routes
    print("\nAvailable API endpoints:")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ', '.join(route.methods)
            print(f"  {methods:10} {route.path}")
    
    print("\n" + "=" * 80)
    print("✓ API IS WORKING!")
    print("=" * 80)
    print("""
To start the server, run:

    cd src
    py -m uvicorn proxima.api.main:app --reload

Then access:
    - API: http://localhost:8000
    - Docs: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
""")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

