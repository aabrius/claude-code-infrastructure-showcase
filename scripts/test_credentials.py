#!/usr/bin/env python3
"""
Quick test script to verify Google Ad Manager credentials are valid.
"""

import sys
import yaml
from datetime import datetime

def test_credentials():
    """Test GAM authentication with current credentials."""
    print("=" * 60)
    print("Google Ad Manager Credential Test")
    print("=" * 60)
    print()

    # Load credentials from googleads.yaml
    try:
        print("📄 Loading credentials from googleads.yaml...")
        with open('googleads.yaml', 'r') as f:
            config = yaml.safe_load(f)

        ad_manager_config = config.get('ad_manager', {})

        # Display configuration (redacted)
        print("✓ Configuration loaded:")
        print(f"  - Network Code: {ad_manager_config.get('network_code')}")
        print(f"  - Application: {ad_manager_config.get('application_name')}")
        print(f"  - Client ID: {ad_manager_config.get('client_id', '')[:20]}...")
        print(f"  - Client Secret: {ad_manager_config.get('client_secret', '')[:10]}...")
        print(f"  - Refresh Token: {ad_manager_config.get('refresh_token', '')[:20]}...")
        print()

    except FileNotFoundError:
        print("❌ Error: googleads.yaml not found")
        return False
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False

    # Test authentication with Google Ads API
    try:
        print("🔐 Testing OAuth2 authentication...")
        from google.ads.googleads.client import GoogleAdsClient

        # Create client
        client = GoogleAdsClient.load_from_dict(config)

        print("✓ OAuth2 client created successfully")
        print()

    except ImportError:
        print("⚠️  google-ads library not installed")
        print("   Run: pip install google-ads")
        return False
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print()
        print("Possible issues:")
        print("  1. Refresh token expired - run: python generate_new_token.py")
        print("  2. Invalid credentials")
        print("  3. Network code incorrect")
        return False

    # Test Ad Manager specific access
    try:
        print("🎯 Testing Ad Manager API access...")
        from googleads import ad_manager

        # Create Ad Manager client
        ad_manager_client = ad_manager.AdManagerClient.LoadFromString(yaml.dump(config))

        # Try to get network service
        network_service = ad_manager_client.GetService('NetworkService', version='v202311')

        # Make a test API call
        current_network = network_service.getCurrentNetwork()

        print("✅ Ad Manager API access successful!")
        print()
        print("Network Information:")
        print(f"  - Display Name: {current_network['displayName']}")
        print(f"  - Network Code: {current_network['networkCode']}")
        print(f"  - Network ID: {current_network['id']}")
        if 'timeZone' in current_network:
            print(f"  - Time Zone: {current_network['timeZone']}")
        print()

        return True

    except ImportError:
        print("⚠️  googleads library not installed")
        print("   Run: pip install googleads")
        return False
    except Exception as e:
        print(f"❌ Ad Manager API call failed: {e}")
        print()
        print("Possible issues:")
        print("  1. Refresh token expired - run: python generate_new_token.py")
        print("  2. Network code incorrect")
        print("  3. User doesn't have access to this network")
        return False


if __name__ == "__main__":
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    success = test_credentials()

    print()
    print("=" * 60)
    if success:
        print("✅ CREDENTIALS ARE VALID AND WORKING")
        print("=" * 60)
        print()
        print("Your MCP server should work with these credentials!")
        sys.exit(0)
    else:
        print("❌ CREDENTIAL TEST FAILED")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Run: python generate_new_token.py")
        print("  2. Install missing packages: pip install -r requirements.txt")
        print("  3. Check your network code is correct")
        sys.exit(1)
