import json
import os
import urllib.request
import urllib.parse
import sys

def update_playlist():
    # 1. Get the Source URL from GitHub Secrets
    json_url = os.environ.get('JSON_SOURCE_URL')

    if not json_url:
        print("Error: JSON_SOURCE_URL is missing.")
        sys.exit(1)

    output_file = 'list.m3u'
    
    # 2. Define a TiviMate-friendly User-Agent
    # "Mozilla/5.0" pretends to be a PC browser, which usually passes server checks.
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"

    try:
        # Fetch the JSON data
        req = urllib.request.Request(json_url)
        req.add_header('User-Agent', user_agent)
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        # Ensure data is a list
        if isinstance(data, dict):
            data = [data]

        with open(output_file, 'w', encoding='utf-8') as m3u:
            m3u.write('#EXTM3U\n')

            for channel in data:
                # Extract fields safely
                name = channel.get('name', 'Unknown')
                logo = channel.get('logo', '')
                link = channel.get('link', '')
                drm_scheme = channel.get('drmScheme', '')
                drm_license = channel.get('drmLicense', '')
                cookie = channel.get('cookie', '')

                # --- STEP 1: DRM CONFIGURATION (KODIPROP) ---
                # TiviMate looks here to find the decryption key
                if drm_scheme and drm_scheme.lower() == 'clearkey':
                    m3u.write('#KODIPROP:inputstream.adaptive.license_type=com.clearkey.alpha\n')
                
                if drm_license:
                    m3u.write(f'#KODIPROP:inputstream.adaptive.license_key={drm_license}\n')

                # --- STEP 2: CHANNEL INFO ---
                m3u.write(f'#EXTINF:-1 tvg-logo="{logo}" ,{name}\n')

                # --- STEP 3: HEADERS VIA PIPE (|) ---
                # TiviMate requires headers appended to the URL. 
                # We MUST URL-encode values to handle spaces or special characters in the cookie.
                
                headers_dict = {
                    "User-Agent": user_agent
                }

                if cookie:
                    headers_dict["Cookie"] = cookie

                # Build the header string: &Key=Value
                header_string = ""
                for key, value in headers_dict.items():
                    encoded_val = urllib.parse.quote(value) # Crucial: Encodes spaces to %20, etc.
                    header_string += f"&{key}={encoded_val}"

                # Remove the very first '&'
                header_string = header_string[1:]

                # Write the final URL
                # Format: https://link.mpd|Cookie=...&User-Agent=...
                m3u.write(f'{link}|{header_string}\n')

        print("Success: Playlist generated for TiviMate.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_playlist()
