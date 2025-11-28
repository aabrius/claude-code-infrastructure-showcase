#!/usr/bin/env python3
"""
Setup Real GAM Credentials for Journey Testing

This script helps you configure and validate real Google Ad Manager credentials
for comprehensive journey testing.

Usage:
    python setup_real_credentials.py --check      # Check current configuration
    python setup_real_credentials.py --setup      # Interactive setup guide
    python setup_real_credentials.py --validate   # Validate credentials
    python setup_real_credentials.py --test       # Run real credential tests
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess

def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a required file exists."""
    path = Path(filepath)
    if path.exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (NOT FOUND)")
        return False

def validate_googleads_yaml() -> Dict[str, Any]:
    """Validate googleads.yaml configuration."""
    print("\n🔍 Validating googleads.yaml configuration...")
    
    config_path = Path("googleads.yaml")
    if not config_path.exists():
        print("❌ googleads.yaml not found")
        return {"valid": False, "error": "File not found"}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        ad_manager_config = config.get('ad_manager', {})
        
        # Check required fields
        required_fields = {
            'client_id': 'OAuth2 Client ID',
            'client_secret': 'OAuth2 Client Secret', 
            'refresh_token': 'OAuth2 Refresh Token',
            'network_code': 'GAM Network Code'
        }
        
        validation_result = {"valid": True, "issues": [], "config": ad_manager_config}
        
        for field, description in required_fields.items():
            value = ad_manager_config.get(field, '')
            
            if not value:
                validation_result["issues"].append(f"Missing {description} ({field})")
                validation_result["valid"] = False
            elif value.startswith('INSERT_'):
                validation_result["issues"].append(f"Placeholder value for {description} ({field})")
                validation_result["valid"] = False
            else:
                print(f"✅ {description}: {'*' * 8}{value[-4:] if len(value) > 4 else '****'}")
        
        # Check application name
        app_name = ad_manager_config.get('application_name', 'Ad Manager Data Extractor')
        print(f"✅ Application Name: {app_name}")
        
        if validation_result["issues"]:
            print("\n⚠️  Issues found:")
            for issue in validation_result["issues"]:
                print(f"   - {issue}")
        else:
            print("\n✅ googleads.yaml configuration is valid!")
        
        return validation_result
        
    except Exception as e:
        print(f"❌ Error reading googleads.yaml: {e}")
        return {"valid": False, "error": str(e)}

def check_oauth_client_secret() -> bool:
    """Check for OAuth client secret JSON file."""
    print("\n🔍 Checking OAuth client secret file...")
    
    # First check for the specific file mentioned in generate_new_token.py
    specific_client_secret = 'client_secret_640670014752-u5lnbkslujd482j3rs8jvm6fng4q1nbf.apps.googleusercontent.com.json'
    
    if Path(specific_client_secret).exists():
        client_secret_file = Path(specific_client_secret)
        print(f"✅ Found OAuth client secret: {client_secret_file.name}")
    else:
        # Look for client secret file pattern
        json_files = list(Path(".").glob("client_secret_*.json"))
        
        if not json_files:
            print("❌ OAuth client secret JSON file not found")
            print(f"   Expected: {specific_client_secret}")
            print("   Or pattern: client_secret_*.apps.googleusercontent.com.json")
            return False
        
        client_secret_file = json_files[0]
        print(f"✅ Found OAuth client secret: {client_secret_file.name}")
    
    try:
        with open(client_secret_file, 'r') as f:
            client_config = json.load(f)
        
        if 'web' in client_config:
            web_config = client_config['web']
            client_id = web_config.get('client_id', '')
            redirect_uris = web_config.get('redirect_uris', [])
            
            print(f"   Client ID: {client_id[:20]}...")
            print(f"   Redirect URIs: {len(redirect_uris)} configured")
            
            return True
        else:
            print("❌ Client secret file is not configured for web application")
            return False
            
    except Exception as e:
        print(f"❌ Error reading client secret file: {e}")
        return False

def check_environment_setup() -> Dict[str, bool]:
    """Check development environment setup."""
    print("\n🔍 Checking development environment...")
    
    checks = {}
    
    # Check Python packages
    required_packages = [
        'google-auth-oauthlib',
        'google-auth',
        'googleads',
        'pyyaml',
        'pytest'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ Python package: {package}")
            checks[f"package_{package}"] = True
        except ImportError:
            print(f"❌ Python package: {package} (NOT INSTALLED)")
            checks[f"package_{package}"] = False
    
    # Check project structure
    required_dirs = [
        "packages/core/src",
        "packages/shared/src", 
        "tests/journeys",
        "src"
    ]
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ Directory: {dir_path}")
            checks[f"dir_{dir_path.replace('/', '_')}"] = True
        else:
            print(f"❌ Directory: {dir_path} (NOT FOUND)")
            checks[f"dir_{dir_path.replace('/', '_')}"] = False
    
    return checks

def interactive_setup_guide():
    """Interactive guide to set up real credentials."""
    print("\n🚀 Interactive GAM Credentials Setup")
    print("=" * 50)
    
    print("\nThis guide will help you set up real Google Ad Manager credentials")
    print("for comprehensive journey testing.")
    
    # Step 1: Check current status
    print("\n📋 STEP 1: Current Configuration Status")
    print("-" * 35)
    
    yaml_validation = validate_googleads_yaml()
    oauth_file_exists = check_oauth_client_secret()
    env_checks = check_environment_setup()
    
    if yaml_validation["valid"]:
        print("\n✅ Your credentials are already configured!")
        print("You can proceed to run tests with:")
        print("   export USE_REAL_GAM_CREDENTIALS=true")
        print("   python tests/journeys/real_credentials_test.py")
        return
    
    # Step 2: Setup instructions
    print("\n📋 STEP 2: Setup Instructions")
    print("-" * 30)
    
    if not oauth_file_exists:
        print("\n🔑 OAuth Client Setup Required:")
        print("1. Go to Google Cloud Console (https://console.cloud.google.com)")
        print("2. Create or select a project")
        print("3. Enable Google Ad Manager API")
        print("4. Create OAuth 2.0 credentials (Web application)")
        print("5. Download the client secret JSON file")
        print("6. Place it in this directory")
        print("\nThen run this setup again.")
        return
    
    if not yaml_validation["valid"]:
        print("\n🔧 Credential Configuration Required:")
        print("1. Your googleads.yaml needs to be configured")
        print("2. Run the OAuth token generation:")
        print("   python generate_new_token.py")
        print("3. Follow the OAuth flow to get your refresh token")
        print("4. The script will automatically update googleads.yaml")
        print("\nThen run this setup again.")
        return
    
    print("\n✅ Setup complete! You can now run real credential tests.")

def run_credential_validation():
    """Run credential validation tests."""
    print("\n🧪 Running Credential Validation Tests")
    print("=" * 45)
    
    # First check configuration
    yaml_validation = validate_googleads_yaml()
    if not yaml_validation["valid"]:
        print("❌ Configuration validation failed")
        print("Run setup first: python setup_real_credentials.py --setup")
        return False
    
    # Set environment variable for real credentials
    os.environ["USE_REAL_GAM_CREDENTIALS"] = "true"
    
    try:
        # Import and run the real credentials test
        sys.path.append(str(Path("tests/journeys")))
        from real_credentials_test import RealCredentialsJourneyTests
        
        import asyncio
        
        async def run_validation():
            test_runner = RealCredentialsJourneyTests()
            return await test_runner.run_real_credential_tests()
        
        result = asyncio.run(run_validation())
        
        if "error" in result:
            print(f"❌ Validation failed: {result['error']}")
            return False
        
        success_rate = result.get("success_rate", 0)
        print(f"\n📊 Validation Results:")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Tests: {result.get('total_tests', 0)}")
        print(f"   Duration: {result.get('total_duration', 0):.2f}s")
        
        if success_rate == 100:
            print("\n✅ ALL VALIDATIONS PASSED!")
            print("Your credentials are working perfectly.")
            return True
        else:
            print(f"\n⚠️  Some validations failed ({success_rate:.1f}% success)")
            print("Check the detailed output above for specific issues.")
            return False
            
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def run_journey_tests():
    """Run the full journey test suite with real credentials."""
    print("\n🎯 Running Full Journey Tests with Real Credentials")
    print("=" * 55)
    
    # Set environment variable
    os.environ["USE_REAL_GAM_CREDENTIALS"] = "true"
    
    try:
        # Run the real credentials test
        result = subprocess.run([
            sys.executable, 
            "tests/journeys/real_credentials_test.py"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ Journey tests completed successfully!")
        else:
            print(f"\n❌ Journey tests failed (exit code: {result.returncode})")
            
    except Exception as e:
        print(f"❌ Failed to run journey tests: {e}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Setup and validate real GAM credentials for journey testing"
    )
    
    parser.add_argument(
        "--check", 
        action="store_true", 
        help="Check current configuration status"
    )
    parser.add_argument(
        "--setup", 
        action="store_true", 
        help="Interactive setup guide"
    )
    parser.add_argument(
        "--validate", 
        action="store_true", 
        help="Validate credentials with test API calls"
    )
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Run full journey test suite"
    )
    
    args = parser.parse_args()
    
    print("🔐 GAM Credentials Setup and Validation")
    print("=" * 45)
    
    if args.check:
        print("\n📋 Configuration Status Check")
        print("-" * 35)
        
        # Check all components
        yaml_valid = validate_googleads_yaml()
        oauth_exists = check_oauth_client_secret()
        env_ok = check_environment_setup()
        
        print(f"\n📊 Summary:")
        print(f"   Configuration: {'✅' if yaml_valid['valid'] else '❌'}")
        print(f"   OAuth Setup: {'✅' if oauth_exists else '❌'}")
        print(f"   Environment: {'✅' if all(env_ok.values()) else '❌'}")
        
        if yaml_valid['valid'] and oauth_exists and all(env_ok.values()):
            print("\n🎉 Everything looks good! You can run:")
            print("   python setup_real_credentials.py --validate")
        else:
            print("\n🔧 Setup needed. Run:")
            print("   python setup_real_credentials.py --setup")
    
    elif args.setup:
        interactive_setup_guide()
    
    elif args.validate:
        success = run_credential_validation()
        if success:
            print("\n🎯 Ready for journey testing! Run:")
            print("   python setup_real_credentials.py --test")
        else:
            print("\n🔧 Fix validation issues before proceeding")
    
    elif args.test:
        run_journey_tests()
    
    else:
        # Default: show current status and options
        print("\n📋 Quick Status Check:")
        yaml_validation = validate_googleads_yaml()
        
        if yaml_validation["valid"]:
            print("✅ Credentials configured - ready for testing!")
            print("\nAvailable commands:")
            print("   --validate  : Test credentials with API calls")
            print("   --test      : Run full journey test suite")
        else:
            print("❌ Credentials need setup")
            print("\nAvailable commands:")
            print("   --check     : Detailed configuration check")
            print("   --setup     : Interactive setup guide")
        
        print("\nFor help: python setup_real_credentials.py --help")

if __name__ == "__main__":
    main()