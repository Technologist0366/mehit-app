#!/usr/bin/env python3
import json

# Read your current cookies
with open("facebook_cookies.json", "r") as f:
    firefox_cookies = json.load(f)

print("Your current cookies:")
for cookie in firefox_cookies:
    print(f"  - {cookie.get('Name raw')}")

print("\n✅ You need to export cookies from Chrome or use a proper extension")
print("   The current Firefox export format is not compatible with Crawl4AI")
print("\n📋 Required Facebook cookies:")
print("   - c_user (your user ID)")
print("   - xs (session token)")
print("   - datr (browser identifier)")
print("   - fr (facebook identifier)")
print("   - sb (security badge)")
