"""
Simple static file server to serve the debug frontend.
Run this alongside your main RevBot server.
"""
import http.server
import socketserver
import webbrowser
import os
from pathlib import Path


def serve_debug_frontend():
    """Serve the debug frontend on a separate port."""
    PORT = 3000
    DIRECTORY = Path(__file__).parent
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=DIRECTORY, **kwargs)
        
        def end_headers(self):
            # Add CORS headers to allow requests to localhost:8000
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"🌐 Debug Frontend Server running at: http://localhost:{PORT}")
            print(f"📁 Serving files from: {DIRECTORY}")
            print(f"🎯 Debug interface: http://localhost:{PORT}/debug_frontend.html")
            print(f"🔍 Make sure RevBot server is running on http://localhost:8000")
            print("\nPress Ctrl+C to stop the server")
            
            # Try to open browser automatically
            try:
                webbrowser.open(f"http://localhost:{PORT}/debug_frontend.html")
                print("🚀 Opening debug interface in your browser...")
            except:
                print("⚠️  Could not auto-open browser. Navigate to the URL manually.")
            
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Error: Port {PORT} is already in use.")
            print("   Try stopping other servers or use a different port.")
        else:
            print(f"❌ Error starting server: {e}")
    except KeyboardInterrupt:
        print("\n👋 Debug server stopped.")


if __name__ == "__main__":
    serve_debug_frontend()