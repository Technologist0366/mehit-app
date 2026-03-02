#!/usr/bin/env python3
import json

# Load your cookies
with open("facebook_cookies.json", "r") as f:
    cookies = json.load(f)

print(f"Original cookies: {len(cookies)}")
fixed_count = 0

# Fix each cookie
for cookie in cookies:
    if 'sameSite' in cookie:
        original = cookie['sameSite']
        # Convert to proper format
        if original == 'no_restriction':
            cookie['sameSite'] = 'None'
            fixed_count += 1
            print(f"Fixed: {cookie.get('name')} - 'no_restriction' → 'None'")
        elif original == 'lax':
            cookie['sameSite'] = 'Lax'
            fixed_count += 1
            print(f"Fixed: {cookie.get('name')} - 'lax' → 'Lax'")
        elif original == 'unspecified':
            # Remove unspecified as it's invalid
            del cookie['sameSite']
            fixed_count += 1
            print(f"Fixed: {cookie.get('name')} - removed 'unspecified'")
    
    # Ensure secure flag is boolean
    if 'secure' in cookie and not isinstance(cookie['secure'], bool):
        cookie['secure'] = str(cookie['secure']).lower() == 'true'

# Save fixed cookies
with open("facebook_cookies_fixed.json", "w") as f:
    json.dump(cookies, f, indent=2)

print(f"\n✅ Fixed {fixed_count} cookies")
print("💾 Saved to facebook_cookies_fixed.json")
print("\nNow use this file in your scraper.")
