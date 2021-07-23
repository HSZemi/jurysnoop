#! /usr/bin/env python3

from pathlib import Path
import sys
import json
import math
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
    #return
    styles = mpatch.BoxStyle.get_styles()
    spacing = 1.2
    figheight = (spacing * len(final) + 1.5)
    fig = plt.figure(figsize=(10, figheight / 1.5))
    plt.axis('off')
    plt.gca().set_ylim(-0.1, 1)
    plt.title(title)
    fontsize = 0.3 * 72
    
    lines = {}

    plt.text(0.27, (spacing * (len(semi_final)) - 0.5) / figheight, 'Halbfinale',
                ha="right",
                size=fontsize*0.8)
    for i, key in enumerate(semi_final):
        plt.text(0.27, (spacing * (len(semi_final) - (i+1)) - 0.5) / figheight, f"{key} {semi_final[key]}",
                ha="right",
                size=fontsize,
                bbox=dict(boxstyle='square', fc="w", ec="k"))
        lines[key] = [(0.3, (spacing * (len(semi_final) - (i+1)) - 0.5) / figheight)]
    
    plt.text(0.73, (spacing * (len(final)) - 0.5) / figheight, 'Finale',
                ha="left",
                size=fontsize*0.8)
    for i, key in enumerate(final):
        plt.text(0.73, (spacing * (len(final) - (i+1)) - 0.5) / figheight, f"{key} {final[key]}",
                ha="left",
                size=fontsize,
                bbox=dict(boxstyle='square', fc="w", ec="k"))
        lines[key].append((0.7, (spacing * (len(final) - (i+1)) - 0.5) / figheight))
    
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
    plt.close()


def main():
    votingstats = json.loads((Path(__file__).parent / 'voting-stats.json').read_text())
    values = {}
    equal_from_front = [0 for i in range(10)]
    equal_from_back = [0 for i in range(10)]
    total = 0
    difference_values = []
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
        for value in difference_vector.values():
            difference_values.append(abs(value))
        
        for index in range(len(sorted_filtered_semi_final)):
            if list(sorted_filtered_semi_final.keys())[index] == list(sorted_filtered_final.keys())[index]:
                equal_from_front[index] += 1
            if list(sorted_filtered_semi_final.keys())[-1-index] == list(sorted_filtered_final.keys())[-1-index]:
                equal_from_back[index] += 1
        total += 1
            
        
        if vector_value >= 30 or vector_value <= 0 or juror == 'stockholm-2016|denmark|D':
            create_diagram(f"{juror.replace('|','_')}", sorted_filtered_semi_final, sorted_filtered_final)
            create_diagram(f"{juror.replace('|','_')}_inverse", reverse_sorted_filtered_semi_final, sorted_filtered_final)
        
        values[juror] = (vector_value, reverse_vector_value)
    sorted_values = dict(sorted(values.items(), key=lambda item: item[1][0]))
    for key, value in sorted_values.items():
        print(value[0], value[1], key)
    
    for i in range(10):
        print(i, equal_from_front[i], math.floor(equal_from_front[i] / total * 100))
    for i in range(10):
        print(i, equal_from_back[i], math.floor(equal_from_back[i] / total * 100))
    print(total)
    print('average difference', sum(difference_values) / len(difference_values))

if __name__ == "__main__":
    main()
