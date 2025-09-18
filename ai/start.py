#!/usr/bin/env python3
"""Quick start script for UML Auto Scoring AI."""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Main start function."""
    print("🚀 Starting UML Auto Scoring AI...")
    
    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Check if .env exists
    if not Path(".env").exists():
        if Path("env.example").exists():
            print("⚠️  .env file not found. Creating from env.example...")
            subprocess.run(["cp", "env.example", ".env"], check=True)
            print("✅ Created .env file")
            print("💡 Please edit .env file with your API keys before starting")
            print("📝 Required: Set OPENAI_API_KEY or GEMINI_API_KEY")
            return
        else:
            print("❌ Neither .env nor env.example found")
            return
    
    # Check configuration
    print("🔍 Checking configuration...")
    try:
        result = subprocess.run([
            sys.executable, "scripts/check_config.py"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Configuration check failed:")
            print(result.stdout)
            print(result.stderr)
            return
        
        print("✅ Configuration check passed")
    except Exception as e:
        print(f"⚠️  Could not run configuration check: {e}")
    
    # Start the application
    print("🌟 Starting the application...")
    print("📚 API documentation will be available at: http://localhost:2012/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")


if __name__ == "__main__":
    main()

