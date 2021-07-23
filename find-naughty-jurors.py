#! /usr/bin/env python3

from pathlib import Path
import sys
import json
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import matplotlib.patches as mpatch
from matplotlib.patches import FancyBboxPatch

SEMI_FINALS = ['first-semi-final','second-semi-final']

FINAL = 'grand-final'


def extract_common_countries(placements):
    sets = []
    for value in placements.values():
        sets.append(set(value.keys()))
    return set.intersection(*sets)


def get_semi_final_key(placements):
    for key in placements:
        if key in SEMI_FINALS:
            return key
    raise ValueError("No semi final found")


def calculate_difference_vector(semi_final, final):
    result = {}
    for key in final:
        final_index = list(final.keys()).index(key)
        semi_final_index = list(semi_final.keys()).index(key)
        result[key] = semi_final_index - final_index
    return result


def measure(vector):
    return sum([abs(value) for value in vector.values()])


def create_diagram(title, semi_final, final):
    styles = mpatch.BoxStyle.get_styles()
    spacing = 1.2
    figheight = (spacing * len(final) + .5)
    fig = plt.figure(figsize=(10, figheight / 1.5))
    plt.axis('off')
    plt.title(title)
    fontsize = 0.3 * 72
    
    lines = {}

    for i, key in enumerate(semi_final):
        plt.text(0.27, (spacing * (len(semi_final) - i) - 0.5) / figheight, f"{key} {semi_final[key]}",
                ha="right",
                size=fontsize,
                bbox=dict(boxstyle='square', fc="w", ec="k"))
        lines[key] = [(0.3, (spacing * (len(semi_final) - i) - 0.5) / figheight)]
        
    for i, key in enumerate(final):
        plt.text(0.73, (spacing * (len(final) - i) - 0.5) / figheight, f"{key} {final[key]}",
                ha="left",
                size=fontsize,
                bbox=dict(boxstyle='square', fc="w", ec="k"))
        lines[key].append((0.7, (spacing * (len(final) - i) - 0.5) / figheight))
    
    for key, coords in lines.items():
        plt.annotate("",
              xy=coords[0], xycoords='data',
              xytext= coords[1], textcoords='data',
              arrowprops=dict(arrowstyle="-",
                              edgecolor = "blue",
                              linewidth=5,
                              alpha=0.65,
                              connectionstyle="arc3,rad=0."), 
              )
    plt.savefig(f'{title}.png')


def main():
    votingstats = json.loads((Path(__file__).parent / 'voting-stats.json').read_text())
    values = {}
    for juror, placements in votingstats.items():
        common_countries = extract_common_countries(placements)
        semi_final_key = get_semi_final_key(placements)
        
        filtered_semi_final = { key:value for (key,value) in placements[semi_final_key].items() if key in common_countries }
        filtered_final = { key:value for (key,value) in placements[FINAL].items() if key in common_countries }
        
        sorted_filtered_final = dict(sorted(filtered_final.items(), key=lambda item: item[1]))
        sorted_filtered_semi_final = dict(sorted(filtered_semi_final.items(), key=lambda item: item[1]))
        reverse_sorted_filtered_semi_final = dict(sorted(filtered_semi_final.items(), key=lambda item: item[1], reverse=True))
        
        difference_vector = calculate_difference_vector(sorted_filtered_semi_final, sorted_filtered_final)
        reverse_difference_vector = calculate_difference_vector(reverse_sorted_filtered_semi_final, sorted_filtered_final)
        vector_value = measure(difference_vector)
        reverse_vector_value = measure(reverse_difference_vector)
        
        if vector_value >= 40:
            create_diagram(f"{juror.replace('|','_')}", sorted_filtered_semi_final, sorted_filtered_final)
            create_diagram(f"{juror.replace('|','_')}_inverse", reverse_sorted_filtered_semi_final, sorted_filtered_final)
        
        values[juror] = (vector_value, reverse_vector_value)
    sorted_values = dict(sorted(values.items(), key=lambda item: item[1][0]))
    for key, value in sorted_values.items():
        print(value[0], value[1], key)
    
    
def debug_diagram():
    id_ = 'stockholm-2016|denmark|B'.replace('|','_')
    sf = {
    "Moldova": 2,
    "Armenia": 3,
    "Azerbaijan": 5,
    "Sweden": 7,
    "Australia": 8,
    "Greece": 9,
    "Poland": 10,
    "Cyprus": 13,
    "Belgium": 16
    }
    f = {
    "Poland": 9,
    "Greece": 12,
    "Cyprus": 13,
    "Belgium": 14,
    "Armenia": 16,
    "Australia": 17,
    "Sweden": 18,
    "Azerbaijan": 21,
    "Moldova": 22
    }
    
    create_diagram(id_, sf,f)
    
if __name__ == "__main__":
    main()
    #debug_diagram()
