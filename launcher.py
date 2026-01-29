#!/usr/bin/env python3
"""
Spec Home Analyzer Launcher
Double-click to run the app
"""

import sys
import os
import webbrowser
import threading
import time

# Set up paths for bundled app
if getattr(sys, 'frozen', False):
    # Running as compiled
    bundle_dir = sys._MEIPASS
    os.chdir(bundle_dir)
else:
    # Running as script
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(bundle_dir)

# Add app directory to path
sys.path.insert(0, os.path.join(bundle_dir, 'app'))

def open_browser():
    """Open browser after short delay"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5050')

if __name__ == '__main__':
    # Start browser opener in background
    threading.Thread(target=open_browser, daemon=True).start()

    # Import and run Flask app
    from app import app
    print("\n" + "="*50)
    print("  Spec Home Analyzer is running!")
    print("  Open http://localhost:5050 in your browser")
    print("  Press Ctrl+C to quit")
    print("="*50 + "\n")

    app.run(debug=False, port=5050, use_reloader=False)
