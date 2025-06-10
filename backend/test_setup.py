"""
Cross-platform setup verification script.
Run this to verify your installation works correctly.
"""
import sys
import os
import platform
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 8):
        print("❌ Error: Python 3.8+ required")
        return False
    elif version < (3, 11):
        print("⚠️  Warning: Python 3.11+ recommended for best performance")
    
    return True


def check_virtual_environment():
    """Check if running in virtual environment."""
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if in_venv:
        print(f"✓ Virtual environment active: {sys.prefix}")
        return True
    else:
        print("⚠️  Warning: Not running in virtual environment")
        print("   Recommended: Create and activate 'revbot' virtual environment")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'fastapi',
        'uvicorn',
        'anthropic',
        'pydantic',
        'structlog'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def check_env_file():
    """Check if .env file exists and has API key."""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found")
        print("   Run: cp .env.example .env (or copy .env.example .env on Windows)")
        return False
    
    print("✓ .env file exists")
    
    # Check if API key is set
    with open(env_path, 'r') as f:
        content = f.read()
        if 'your_anthropic_api_key_here' in content:
            print("⚠️  Warning: API key not configured in .env file")
            print("   Edit .env and add your Anthropic API key")
            return False
        elif 'ANTHROPIC_API_KEY=' in content:
            print("✓ API key configured")
            return True
    
    return False


def check_platform_specific():
    """Check platform-specific requirements."""
    system = platform.system()
    print(f"✓ Platform: {system} {platform.release()}")
    
    if system == "Windows":
        # Check if running in proper terminal
        if os.environ.get('TERM') == 'xterm':
            print("⚠️  Running in Git Bash - consider using Command Prompt or PowerShell")
        
        # Check if Python is in PATH
        try:
            result = subprocess.run(['python', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Python accessible via 'python' command")
            else:
                print("⚠️  Try 'py' instead of 'python' command")
        except FileNotFoundError:
            print("❌ Python not found in PATH")
            return False
    
    elif system == "Darwin":  # macOS
        # Check if Xcode Command Line Tools are installed
        try:
            subprocess.run(['xcode-select', '--print-path'], 
                          capture_output=True, check=True)
            print("✓ Xcode Command Line Tools installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Consider installing Xcode Command Line Tools: xcode-select --install")
    
    return True


def main():
    """Run all setup checks."""
    print("RevBot Setup Verification")
    print("=" * 30)
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Platform", check_platform_specific)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(False)
    
    print("\n" + "=" * 30)
    print("Summary:")
    
    if all(results):
        print("🎉 All checks passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. python test_claude.py  # Test API connection")
        print("2. python main.py         # Start the server")
        print("3. python example_usage.py # Test full functionality")
    else:
        print("❌ Some issues found. Please resolve them before continuing.")
        failed_count = len([r for r in results if not r])
        print(f"   {failed_count} out of {len(checks)} checks failed.")
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)