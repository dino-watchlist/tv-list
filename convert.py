import json
import os
import urllib.request

def update_playlist():
    # 1. Get the JSON URL from Environment Variables (for security)
    # We will set this up in GitHub Settings later.
    json_url = os.environ.get('JSON_SOURCE_URL')
    
    if not json_url:
        print("Error: JSON_SOURCE_URL environment variable not found.")
        return

    output_file = 'list.m3u'

    try:
        # 2. Fetch JSON data from the web
        print(f"Fetching data from {json_url}...")
        with urllib.request.urlopen(json_url) as response:
            data = json.loads(response.read().decode())

        # Ensure data is a list
        if isinstance(data, dict):
            data = [data]

        # 3. Write M3U8 Playlist
        with open(output_file, 'w', encoding='utf-8') as m3u:
            m3u.write('#EXTM3U\n')

            for channel in data:
                name = channel.get('name', 'Unknown')
                logo = channel.get('logo', '')
                link = channel.get('link', '')
                drm_scheme = channel.get('drmScheme', '')
                drm_license = channel.get('drmLicense', '')
                cookie = channel.get('cookie', '')

                # KODIPROP Tags
                if drm_scheme and drm_scheme.lower() == 'clearkey':
                    m3u.write('#KODIPROP:inputstream.adaptive.license_type=com.clearkey.alpha\n')
                
                if drm_license:
                    m3u.write(f'#KODIPROP:inputstream.adaptive.license_key={drm_license}\n')

                # Cookie Tag
                if cookie:
                    header_str = json.dumps({"cookie": cookie})
                    m3u.write(f'#EXTHTTP:{header_str}\n')

                # Info and Link
                m3u.write(f'#EXTINF:-1 tvg-logo="{logo}" ,{name}\n')
                m3u.write(f'{link}\n')

        print(f"Success! Updated {output_file}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_playlist()
