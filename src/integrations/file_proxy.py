"""
Local file proxy service for secure LlamaParse integration
Creates temporary authenticated URLs for internal files
"""

import os
import uuid
import time
from flask import Flask, send_file, request, abort
from threading import Thread, Timer


class FileProxyService:
    """Secure file proxy for LlamaParse access"""
    
    def __init__(self, port=8080):
        self.app = Flask(__name__)
        self.port = port
        self.temp_tokens = {}  # {token: {file_path, expires}}
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/file/<token>')
        def serve_file(token):
            # Validate token
            if token not in self.temp_tokens:
                abort(404)
            
            file_info = self.temp_tokens[token]
            
            # Check expiration
            if time.time() > file_info['expires']:
                del self.temp_tokens[token]
                abort(404)
            
            # Serve file
            return send_file(file_info['file_path'])
    
    def create_temp_url(self, file_path: str, expires_in: int = 3600) -> str:
        """
        Create temporary URL for file access
        
        Args:
            file_path: Path to file
            expires_in: Expiration time in seconds (default 1 hour)
            
        Returns:
            Temporary URL accessible to LlamaParse
        """
        token = str(uuid.uuid4())
        expires = time.time() + expires_in
        
        self.temp_tokens[token] = {
            'file_path': file_path,
            'expires': expires
        }
        
        # Auto-cleanup after expiration
        Timer(expires_in, lambda: self.temp_tokens.pop(token, None)).start()
        
        return f"http://localhost:{self.port}/file/{token}"
    
    def start_server(self):
        """Start the proxy server in background thread"""
        def run():
            self.app.run(host='0.0.0.0', port=self.port, debug=False)
        
        thread = Thread(target=run, daemon=True)
        thread.start()
        return thread


# Usage in n8n workflow:
# 1. Start proxy service on container startup
# 2. Create temp URL for file
# 3. Use temp URL with LlamaParse
# 4. URL expires automatically