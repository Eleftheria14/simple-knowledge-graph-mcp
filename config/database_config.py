"""
Database Configuration for Scientific Paper Analyzer

This module provides configuration options for PostgreSQL database connections.
"""

import os
from typing import Dict, Optional

# Default database configuration
DEFAULT_CONFIG = {
    'host': 'localhost',
    'database': 'scientific_papers',
    'user': 'postgres',
    'password': 'password',
    'port': 5432
}

def get_database_config() -> Dict[str, str]:
    """
    Get database configuration from environment variables or defaults
    
    Environment variables:
    - DATABASE_URL: Full PostgreSQL connection string
    - DB_HOST: Database host (default: localhost)
    - DB_NAME: Database name (default: scientific_papers)
    - DB_USER: Database user (default: postgres)
    - DB_PASSWORD: Database password (default: password)
    - DB_PORT: Database port (default: 5432)
    
    Returns:
        Dictionary with database connection parameters
    """
    
    # Check for full DATABASE_URL first
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return {'database_url': database_url}
    
    # Build config from individual environment variables
    config = {
        'host': os.getenv('DB_HOST', DEFAULT_CONFIG['host']),
        'database': os.getenv('DB_NAME', DEFAULT_CONFIG['database']),
        'user': os.getenv('DB_USER', DEFAULT_CONFIG['user']),
        'password': os.getenv('DB_PASSWORD', DEFAULT_CONFIG['password']),
        'port': int(os.getenv('DB_PORT', str(DEFAULT_CONFIG['port'])))
    }
    
    return config

def get_database_url() -> str:
    """
    Get database URL for connection
    
    Returns:
        PostgreSQL connection URL
    """
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url
    
    config = get_database_config()
    return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

# Example .env file content
EXAMPLE_ENV = """
# Database Configuration Options

# Option 1: Full connection URL
DATABASE_URL=postgresql://postgres:password@localhost:5432/scientific_papers

# Option 2: Individual parameters
DB_HOST=localhost
DB_NAME=scientific_papers
DB_USER=postgres
DB_PASSWORD=password
DB_PORT=5432

# For Docker setup
# DATABASE_URL=postgresql://postgres:password@localhost:5432/scientific_papers

# For cloud databases (example with Railway)
# DATABASE_URL=postgresql://user:pass@host.railway.app:5432/railway
"""

if __name__ == "__main__":
    print("Database Configuration:")
    print("=" * 30)
    
    config = get_database_config()
    for key, value in config.items():
        if key == 'password':
            print(f"{key}: {'*' * len(str(value))}")
        else:
            print(f"{key}: {value}")
    
    print(f"\nConnection URL: {get_database_url()}")
    
    print("\nExample .env file:")
    print(EXAMPLE_ENV)