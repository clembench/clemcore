import json
import random


def load_data(path_to_file, randomized=False):
    with open(path_to_file, "r", encoding="UTF-8") as file:
        content = json.load(file)

    # shuffle the data
    if randomized:
        random.shuffle(content)

    # if it's about locations, also shuffle actions
    if "location" in path_to_file:
        for location in content:
            random.shuffle(location["MAIN-ACTIONS"])

    return content

