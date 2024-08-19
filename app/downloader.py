import os
from urllib.parse import unquote, quote
from httpx import Client, HTTPError

def fetch(url, proxy=None, output_dir='data'):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0'
    }

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Extract filename from URL and sanitize it
    filename = unquote(url.split("/")[-1])
    filename = "".join([c for c in filename if c.isalnum() or c in (' ', '-', '_')]).rstrip()
    filepath = os.path.join(output_dir, f"{filename}.jpeg")

    try:
        with Client(headers=headers, proxies={'http://': proxy, 'https://': proxy} if proxy else None, timeout=30) as client:
            response = client.get(url)
            response.raise_for_status()

            with open(filepath, 'wb') as file:
                file.write(response.content)

        return filepath
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

    return None

if __name__ == '__main__':
    url = 'https://s7.orientaltrading.com/is/image/OrientalTrading/VIEWER_ZOOM/10  skeleton gargoyle decoration~sew81858'
    encoded_url = quote(url, safe=':/?&=')
    response = fetch(encoded_url,
        # proxy='http://47.251.70.179:80'
    )
    if response:
        print(f"Image downloaded successfully: {response}")
    else:
        print("Failed to download image")
