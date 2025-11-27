import json
import os
import urllib.request
import sys

def update_playlist():
    # 1. Get Secret URL
    json_url = os.environ.get('JSON_SOURCE_URL')

    if not json_url:
        print("Error: JSON_SOURCE_URL secret is missing.")
        sys.exit(1)

    output_file = 'list.m3u'
    
    # We force a Browser User-Agent so the server doesn't block us
    browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    try:
        # Fetch the JSON
        req = urllib.request.Request(json_url)
        req.add_header('User-Agent', browser_ua)
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        if isinstance(data, dict):
            data = [data]

        with open(output_file, 'w', encoding='utf-8') as m3u:
            m3u.write('#EXTM3U\n')

            for channel in data:
                name = channel.get('name', 'Unknown')
                logo = channel.get('logo', '')
                link = channel.get('link', '')
                drm_scheme = channel.get('drmScheme', '')
                drm_license = channel.get('drmLicense', '')
                cookie = channel.get('cookie', '')

                # --- 1. DRM TAGS (KODIPROP) ---
                # TiviMate reads these for the License Key
                if drm_scheme and drm_scheme.lower() == 'clearkey':
                    m3u.write('#KODIPROP:inputstream.adaptive.license_type=com.clearkey.alpha\n')
                
                if drm_license:
                    m3u.write(f'#KODIPROP:inputstream.adaptive.license_key={drm_license}\n')

                # --- 2. EXTINF INFO ---
                m3u.write(f'#EXTINF:-1 tvg-logo="{logo}" ,{name}\n')

                # --- 3. URL WITH HEADERS (The TiviMate Fix) ---
                # We append headers with a pipe "|" instead of using #EXTHTTP
                headers = ""
                
                if cookie:
                    headers += f"Cookie={cookie}"
                
                # Always add User-Agent to trick the server
                if headers:
                    headers += f"&User-Agent={browser_ua}"
                else:
                    headers += f"User-Agent={browser_ua}"

                # Write the final link
                m3u.write(f'{link}|{headers}\n')

        print(f"Success. Optimized.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_playlist()
