import http.server
import socketserver
import os

PORT = 8000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def guess_type(self, path):
        # Override guess_type to always serve .html files as text/html
        # And .csv files as text/csv
        if path.endswith('.html'):
            return 'text/html'
        elif path.endswith('.csv'):
            return 'text/csv'
        return super().guess_type(path)

    def do_GET(self):
        # This method handles GET requests
        # We need to make sure the path is correctly interpreted relative to the current directory
        # The base path for the server is the directory where simple_server.py is run

        # Construct the full path to the requested file
        requested_path = self.path.lstrip('/') # Remove leading slash
        full_path = os.path.join(os.getcwd(), requested_path)

        # If the requested path is for the HTML file, explicitly set content type
        if requested_path == '4_Deployment_App.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(full_path, 'rb') as file:
                self.wfile.write(file.read())
        # If the requested path is for the CSV file, explicitly set content type
        elif requested_path == 'simulated_eon_grid_data.csv':
            self.send_response(200)
            self.send_header('Content-type', 'text/csv')
            self.end_headers()
            with open(full_path, 'rb') as file:
                self.wfile.write(file.read())
        else:
            # For all other files, use the default SimpleHTTPRequestHandler behavior
            super().do_GET()

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"serving at port {PORT}")
    httpd.serve_forever()
