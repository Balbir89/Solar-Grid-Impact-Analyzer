import http.server
import socketserver
import os

# Set the port for the server to listen on. Using a very high port to avoid conflicts.
PORT = 50000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    # Override the guess_type method to ensure .html and .csv files are served
    # with the correct MIME types, so the browser interprets them properly.
    def guess_type(self, path):
        if path.endswith('.html'):
            return 'text/html'
        elif path.endswith('.csv'):
            return 'text/csv'
        # For all other file types, use the default behavior of the base class.
        return super().guess_type(path)

# Create the TCP server instance.
# It listens on all available interfaces (empty string "") and the specified PORT.
# MyHandler is used to process incoming HTTP requests.
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    # Print a message to the console indicating that the server has started
    # and which port it is listening on. This is important for the user to know.
    print(f"Serving at port {PORT}")
    
    # This method starts the server and keeps it running indefinitely.
    # It will continuously listen for and handle incoming HTTP requests.
    # The server will only stop when a KeyboardInterrupt (e.g., Ctrl+C) is received
    # in the terminal where this script is running. It is crucial to keep this
    # terminal window open and the server running for the web page to be accessible.
    httpd.serve_forever()
