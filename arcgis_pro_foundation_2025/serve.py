#!/usr/bin/env python3
"""
Run a local HTTP server so practice-test.html can load questions.json via fetch.
Usage: python serve.py
Then open http://127.0.0.1:8000/practice-test.html in your browser.
"""
import http.server
import os
import webbrowser
from functools import partial

PORT = 8000
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=SCRIPT_DIR)
    with http.server.HTTPServer(("127.0.0.1", PORT), handler) as httpd:
        url = "http://127.0.0.1:{}/practice-test.html".format(PORT)
        print("Serving at {} (Ctrl+C to stop)".format(url))
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
