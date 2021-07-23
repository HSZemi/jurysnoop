#! /usr/bin/env python3

from bs4 import BeautifulSoup
from pathlib import Path
import requests
import sys
import json
import time

EVENTS = [
    'stockholm-2016',
    'kyiv-2017',
    'lisbon-2018',
    'tel-aviv-2019',
    'rotterdam-2021',
    ]

SEMI_FINALS = ['first-semi-final','second-semi-final']

FINAL = 'grand-final'


def download_country_result(url, event, part, country):
    time.sleep(1)
    response = requests.get(url, headers = {'User-Agent': 'ESC Fansite 9'})
    target_path = Path(__file__).parent / 'event' / event / country / part
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(response.content.decode('utf-8'))


def download_tables(event, part, index):
    results_url = f'https://eurovision.tv/event/{event}/{part}/results'
    print(results_url)
    time.sleep(1)
    response = requests.get(results_url, headers = {'User-Agent': 'ESC Fansite'})
    soup = BeautifulSoup(response.content, 'html.parser')
    for option in soup.find('select', {"class": "form-select"}).find_all('option'):
        if option.has_attr('value'):
            country_url = option['value']
            country = country_url.split('/')[-1]
            download_country_result(country_url, event, part, country)
            if country not in index[event]:
                index[event][country] = []
            index[event][country].append(part)
    


def main():
    index = {}
    for event in EVENTS:
        index[event] = {}
        for semifinal in SEMI_FINALS:
            download_tables(event, semifinal, index)
        download_tables(event, FINAL, index)
    (Path(__file__).parent / 'event' / 'index.json').write_text(json.dumps(index, sort_keys=True, indent=4))
if __name__ == "__main__":
    main() 
