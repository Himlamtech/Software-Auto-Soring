#!/usr/bin/env python3
"""Setup script for UML Auto Scoring AI development environment."""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """Run a shell command and return success status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up UML Auto Scoring AI development environment\n")
    
    # Check Python version
    if sys.version_info < (3, 12):
        print("❌ Python 3.12+ is required")
        sys.exit(1)
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    steps = [
        ("python -m pip install --upgrade pip", "Upgrading pip"),
        ("pip install uv", "Installing uv package manager"),
        ("uv sync", "Installing project dependencies"),
        ("pre-commit install", "Setting up pre-commit hooks"),
        ("mkdir -p data logs", "Creating data and logs directories"),
    ]
    
    success_count = 0
    for cmd, description in steps:
        if run_command(cmd, description):
            success_count += 1
        print()
    
    if success_count == len(steps):
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your settings")
        print("2. Set your OPENAI_API_KEY in the .env file")
        print("3. Run 'python main.py' to start the development server")
        print("4. Visit http://localhost:8000/docs for API documentation")
    else:
        print(f"⚠️  Setup completed with {len(steps) - success_count} errors")
        print("Please review the error messages above and fix any issues")


if __name__ == "__main__":
    main()
