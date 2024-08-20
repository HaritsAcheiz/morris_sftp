import ast
import os
from urllib.parse import unquote, quote
from httpx import Client, HTTPError
import pandas as pd
from dataclasses import dataclass

@dataclass
class Downloader:
    client: Client() = None
    base_url: str = 'https://www.morriscostumes.com'

    def create_session(self):
        print('Creating session...')
        headers = {
            'Host': 's7.orientaltrading.com',
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
        self.client = Client(timeout=30)
        self.client.get(self.base_url)
        self.client.headers.update(headers)

    def fetch(self, url, proxy=None, output_dir='data/images', filename=''):
        print(f'Downloading {filename}...')
        encoded_url = quote(url, safe=':/?&=')
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{filename}.jpeg")

        try:
            response = self.client.get(encoded_url)
            response.raise_for_status()

            with open(filepath, 'wb') as file:
                file.write(response.content)

            return filepath
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")

        return None

    def extract_url(self, x):
        image_urls = ast.literal_eval(x)
        image_url = image_urls[0]

        return image_url

if __name__ == '__main__':
    downloader = Downloader()
    downloader.create_session()

    df = pd.read_csv('./data/create_products.csv')[0:5]
    df['url'] = df['Image Src'].apply(downloader.extract_url)
    df.apply(lambda x: downloader.fetch(x['url'], filename=x['Handle']), axis=1)
    downloader.client.close()
