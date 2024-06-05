"""
File which beholds helpful functions for generating and fetching data for the game.
"""

import json
import random

def clean_answers_to_prompt():
    pass

def get_random_npcs(npc_sheets):
  """
  Function which fetches the npc sheets
  and returns them shuffled.
  """
    with open(npc_sheets, "r", encoding="UTF-8") as file:
        npcs = json.load(file)
        random.shuffle(npcs)
    return npcs

def get_random_locations(location_sheet):
  """
  Function which fetches the location sheets
  and returns them shuffled.
  """
    with open(location_sheet, "r", encoding="UTF8") as file:
        location_sheets = json.load(file)

    random.shuffle(location_sheets)

    # shuffle all mainactions within the locations
    for location in location_sheets:
        random.shuffle(location["MAIN-ACTIONS"])

    return location_sheets

    



get_random_npcs("./npc_sheets.json")
get_random_locations_actions("./location_sheets.json")
