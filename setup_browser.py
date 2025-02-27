import os
import subprocess
from pathlib import Path

def setup_crawl4ai_dependencies():
    # Install Playwright
    subprocess.run(["pip", "install", "playwright"], check=True)
    # Install only Chromium browser (faster than installing all browsers)
    subprocess.run(["playwright", "install", "chromium"], check=True)
    
    print("Playwright and Chromium installed successfully")

if __name__ == "__main__":
    setup_crawl4ai_dependencies()
