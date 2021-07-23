#! /usr/bin/env python3

from bs4 import BeautifulSoup
from pathlib import Path
import requests
import sys
import json

EVENTS = [
    'stockholm-2016',
    'kyiv-2017',
    'lisbon-2018',
    'tel-aviv-2019',
    'rotterdam-2021',
    ]

SEMI_FINALS = ['first-semi-final','second-semi-final']

FINAL = 'grand-final'


def main():
    index = json.loads((Path(__file__).parent / 'event' / 'index.json').read_text())
    jury_scores = {}
    for event in index:
        for country in index[event]:
            for show in index[event][country]:
                file_ = Path(__file__).parent / 'event' / event / country / show
                soup = BeautifulSoup(file_.read_text(), 'html.parser')
                jurylink = soup.find('a', string='View the jury members')
                if not jurylink:
                    print(event, country, show)
                    sys.exit(1)
                table = jurylink.find_next('table')
                
                output_rows = []
                for table_row in table.findAll('tr'):
                    output_row = []
                    columns = table_row.findAll('th')
                    for column in columns:
                        output_row.append(column.text.strip().replace('\n', '_').replace('_ _', '__'))
                    columns = table_row.findAll('td')
                    for column in columns:
                        output_row.append(column.text.strip().replace('\n', '_').replace('_ _', '__'))
                    output_rows.append(output_row)
                
                for row in output_rows[1:]:
                    for jury_letter, position in zip(('A','B','C','D','E'), row[2:7]):
                        country_receiving_points = row[0]
                        jury_member_id = f'{event}|{country}|{jury_letter}'
                        if jury_member_id == 'stockholm-2016|russia|E': # disqualified
                            continue
                        if jury_member_id not in jury_scores:
                            jury_scores[jury_member_id] = {}
                        if show not in jury_scores[jury_member_id]:
                            jury_scores[jury_member_id][show] = {}
                        jury_scores[jury_member_id][show][country_receiving_points] = int(position)
    print(json.dumps(jury_scores, indent=4, sort_keys=True))
    
    
if __name__ == "__main__":
    main() 
