import http.server
import socketserver
import os

# Changed the port to 8002 to avoid "Address already in use" error
PORT = 8002

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def guess_type(self, path):
        # Override guess_type to always serve .html files as text/html
        # and .csv files as text/csv.
        # This will apply to any .html or .csv file requested.
        if path.endswith('.html'):
            return 'text/html'
        elif path.endswith('.csv'):
            return 'text/csv'
        # For all other file types, use the default behavior
        return super().guess_type(path)

    # We can remove the custom do_GET if guess_type handles the MIME types correctly,
    # as SimpleHTTPRequestHandler's default do_GET will use guess_type.
    # If you need specific custom logic for certain paths (e.g., dynamic content),
    # then a custom do_GET would be necessary, but for serving static files
    # with custom MIME types, overriding guess_type is often sufficient.
    # For now, let's rely on the default do_GET which uses guess_type.
    # If you later need more complex routing or dynamic responses, we can add it back.

# Create the server
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    # This line will keep the server running indefinitely until you stop it manually
    # by pressing Ctrl+C in the terminal.
    httpd.serve_forever()
