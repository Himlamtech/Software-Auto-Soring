#!/usr/bin/env python3
"""Configuration checker for UML Auto Scoring AI."""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.settings import get_settings


def check_environment_file():
    """Check if .env file exists."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    print("🔍 Checking environment configuration...")
    
    if env_file.exists():
        print("✅ .env file found")
        return True
    elif env_example.exists():
        print("⚠️  .env file not found, but env.example exists")
        print("💡 Please copy env.example to .env and configure your settings:")
        print("   cp env.example .env")
        return False
    else:
        print("❌ Neither .env nor env.example found")
        return False


def check_llm_configuration():
    """Check LLM provider configuration."""
    print("\n🤖 Checking LLM configuration...")
    
    try:
        settings = get_settings()
        
        print(f"📋 Selected LLM Provider: {settings.llm_provider}")
        
        if settings.llm_provider == "openai":
            if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
                print("✅ OpenAI API key is configured")
                print(f"📋 OpenAI Model: {settings.llm_model}")
                return True
            else:
                print("❌ OpenAI API key is not configured or still using placeholder")
                print("💡 Please set OPENAI_API_KEY in your .env file")
                return False
                
        elif settings.llm_provider == "gemini":
            if settings.gemini_api_key and settings.gemini_api_key != "your_gemini_api_key_here":
                print("✅ Gemini API key is configured")
                print(f"📋 Gemini Model: {settings.gemini_model}")
                return True
            else:
                print("❌ Gemini API key is not configured or still using placeholder")
                print("💡 Please set GEMINI_API_KEY in your .env file")
                return False
        else:
            print(f"❌ Unknown LLM provider: {settings.llm_provider}")
            return False
            
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return False


def check_directories():
    """Check required directories."""
    print("\n📁 Checking directories...")
    
    required_dirs = ["data", "logs"]
    all_good = True
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"⚠️  {dir_name}/ directory missing, creating...")
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created {dir_name}/ directory")
            except Exception as e:
                print(f"❌ Failed to create {dir_name}/ directory: {e}")
                all_good = False
    
    return all_good


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n📦 Checking dependencies...")
    
    required_imports = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("openai", "openai"),
        ("google-generativeai", "google.generativeai"),
        ("python-dotenv", "dotenv")
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_imports:
        try:
            __import__(import_name)
            print(f"✅ {package_name} is installed")
        except ImportError:
            print(f"❌ {package_name} is missing")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n💡 Install missing packages with:")
        print(f"   uv add {' '.join(missing_packages)}")
        return False
    
    return True


def check_api_connectivity():
    """Check API connectivity (basic test)."""
    print("\n🌐 Checking API connectivity...")
    
    try:
        settings = get_settings()
        
        if settings.llm_provider == "openai" and settings.openai_api_key:
            print("🔧 OpenAI client configuration looks good")
            print("💡 Run a test request to verify API connectivity")
            
        elif settings.llm_provider == "gemini" and settings.gemini_api_key:
            print("🔧 Gemini client configuration looks good")
            print("💡 Run a test request to verify API connectivity")
            
        else:
            print("⚠️  No valid API key found for testing")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking API connectivity: {e}")
        return False


def main():
    """Main configuration check function."""
    print("🚀 UML Auto Scoring AI - Configuration Checker\n")
    
    # Change to project root
    os.chdir(Path(__file__).parent.parent)
    
    checks = [
        ("Environment File", check_environment_file),
        ("LLM Configuration", check_llm_configuration),
        ("Directories", check_directories),
        ("Dependencies", check_dependencies),
        ("API Connectivity", check_api_connectivity),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        if check_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Configuration Check Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All checks passed! Your system is ready to run.")
        print("\n🚀 Start the application with:")
        print("   python main.py")
        print("\n📚 API documentation will be available at:")
        print("   http://localhost:8000/docs")
    else:
        print("⚠️  Some checks failed. Please fix the issues above before running the application.")
        
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
