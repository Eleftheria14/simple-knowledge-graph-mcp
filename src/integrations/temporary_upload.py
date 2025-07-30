"""
Temporary file upload service for LlamaParse integration
Uploads files to temporary cloud storage and returns public URLs
"""

import os
import uuid
import boto3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError


class TemporaryUploadService:
    """Upload files to temporary cloud storage for LlamaParse access"""
    
    def __init__(self):
        # Configure your cloud storage (AWS S3, Google Cloud, etc.)
        self.s3_client = boto3.client('s3') if os.getenv('AWS_ACCESS_KEY_ID') else None
        self.bucket_name = os.getenv('TEMP_STORAGE_BUCKET', 'docsgpt-temp-files')
        
    def upload_for_llamaparse(self, file_path: str, filename: str) -> str:
        """
        Upload file to temporary storage and return public URL
        
        Args:
            file_path: Local path to file
            filename: Original filename
            
        Returns:
            Public URL accessible to LlamaParse
        """
        if not self.s3_client:
            raise Exception("AWS credentials not configured")
            
        # Generate unique key with expiration
        unique_id = str(uuid.uuid4())
        temp_key = f"temp/{unique_id}/{filename}"
        
        try:
            # Upload file
            self.s3_client.upload_file(file_path, self.bucket_name, temp_key)
            
            # Generate presigned URL (expires in 1 hour)
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': temp_key},
                ExpiresIn=3600  # 1 hour
            )
            
            # Schedule deletion after processing
            self._schedule_deletion(temp_key, hours=24)
            
            return url
            
        except ClientError as e:
            raise Exception(f"Upload failed: {e}")
    
    def _schedule_deletion(self, key: str, hours: int = 24):
        """Schedule file deletion after specified hours"""
        # In production, use a job queue or scheduled function
        # For now, we'll rely on S3 lifecycle policies
        pass


# Alternative: Simple HTTP file server
class SimpleFileServer:
    """Temporary HTTP server for file access"""
    
    @staticmethod
    def create_temp_endpoint(file_path: str, port: int = 8000) -> str:
        """
        Start temporary HTTP server and return URL
        WARNING: Only for development/testing
        """
        import http.server
        import socketserver
        import threading
        from pathlib import Path
        
        directory = Path(file_path).parent
        filename = Path(file_path).name
        
        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)
        
        # Start server in background thread
        httpd = socketserver.TCPServer(("", port), Handler)
        thread = threading.Thread(target=httpd.serve_forever)
        thread.daemon = True
        thread.start()
        
        return f"http://localhost:{port}/{filename}"