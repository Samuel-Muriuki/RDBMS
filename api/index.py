"""
Vercel serverless function entry point.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webapp.app import app

# Export for Vercel
handler = app
