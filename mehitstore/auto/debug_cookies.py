#!/usr/bin/env python3
import json
import os

print("🐞 Cookie File Debugger")
print("=" * 50)

# Check if file exists
if not os.path.exists("facebook_cookies.json"):
    print("❌ facebook_cookies.json not found!")
    exit(1)

# Read and examine the file
try:
    with open("facebook_cookies.json", "r") as f:
        content = f.read()
        print(f"📄 File size: {len(content)} bytes")
        print(f"\n📋 First 200 characters:")
        print("-" * 40)
        print(content[:200])
        print("-" * 40)
        
        # Try to parse JSON
        cookies = json.loads(content)
        print(f"\n✅ JSON parsed successfully!")
        print(f"📊 Type: {type(cookies)}")
        
        if isinstance(cookies, list):
            print(f"📊 List with {len(cookies)} items")
            
            # Show structure of first cookie
            if len(cookies) > 0:
                print("\n📝 First cookie structure:")
                first = cookies[0]
                print(f"Type: {type(first)}")
                print("Keys:", list(first.keys()) if isinstance(first, dict) else "Not a dictionary")
                
                # Check for None values
                if isinstance(first, dict):
                    for key, value in first.items():
                        print(f"  {key}: {type(value)} = {value}")
                        
        elif isinstance(cookies, dict):
            print(f"📊 Dictionary with keys: {list(cookies.keys())}")
            
            # If it's a dict with a cookies key, that's common
            if 'cookies' in cookies:
                print("Found 'cookies' key - likely need to extract from there")
                print(f"Contains {len(cookies['cookies'])} cookies")
        
        # Check for common Facebook cookie issues
        print("\n🔍 Checking for required Facebook cookies:")
        required_cookies = ['c_user', 'xs', 'datr']
        found_cookies = []
        
        if isinstance(cookies, list):
            for cookie in cookies:
                if isinstance(cookie, dict) and 'name' in cookie:
                    found_cookies.append(cookie['name'])
        elif isinstance(cookies, dict) and 'cookies' in cookies:
            for cookie in cookies['cookies']:
                if isinstance(cookie, dict) and 'name' in cookie:
                    found_cookies.append(cookie['name'])
        
        for req in required_cookies:
            if req in found_cookies:
                print(f"✅ {req} - Found")
            else:
                print(f"❌ {req} - Missing")
                
except json.JSONDecodeError as e:
    print(f"❌ JSON Decode Error: {e}")
    print("Line {}, Column {}".format(e.lineno, e.colno))
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e)}")
