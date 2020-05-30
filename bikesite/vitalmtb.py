import os
import csv

from bs4 import BeautifulSoup
import requests

from bikesite.config import PROJECT_DIR


import argparse


def url_raw_filename(url):
    return url.split('/')[-1]

def bike_from_raw_filename(raw_filename):
    return raw_filename.split(',')[0]

def get_bike_name(url):
    raw_filename = url_raw_filename(url)
    return bike_from_raw_filename(raw_filename)

def save_to_html_cache_dir(response, bike_name):
    html_cache_dir = os.path.join(PROJECT_DIR, 'html')
    with open(os.path.join(html_cache_dir, f'{bike_name}.html'), 'w') as f:
        f.write(response.content.decode())

def get_content(attr):
    return getattr(row, attr).text.strip()

def trim_content(attr):
    return getattr(row, attr).text.strip().replace(' ', '').replace('\n', '')


def main(args):
    # params
    url = args.url

    # save response to HTML cach edir
    response = requests.get(url=url)
    bike = get_bike_name(url)
    save_to_html_cache_dir(response, bike)

    # parse response content to CSV
    soup = BeautifulSoup(response.content)
    html = soup.find(id="specs")
    table = html.contents[3]
    rows = table.findAll(lambda tag: tag.name=='tr')

    attr = 'td'
    vitalmtb_dir = os.path.join(PROJECT_DIR, 'vitalmtb')

    with open(os.path.join(vitalmtb_dir, f'{bike}.csv'), 'w', newline='') as f:
        fieldnames = ['Key', 'Value']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, row in enumerate(rows):
            if hasattr(row, attr) and hasattr(row.th, 'text'):
                key, value = get_content('th'), trim_content('td')
                writer.writerow({'Key': key, 'Value': value})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('url', type='str',
                        help='full url vitalmtb bike specs page')
    args = parser.parse_args()

    main(args)
