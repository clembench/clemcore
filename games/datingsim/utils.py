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

def prompt_char_sheets(character_sheet):
    prompt = f"""
    GENDER: {character_sheet["GENDER"]}
    AGE: {character_sheet["AGE"]}
    APPEARANCE: {character_sheet["APPEARANCE"]}
    LIKES: {character_sheet["LIKES"]}
    DISLIKES: {character_sheet["DISLIKES"]}
    HOBBIES: {character_sheet["HOBBIES"]}
    SUMMARY: {character_sheet["SUMMARY"]}
    """
    return prompt



#get_random_npcs("./npc_sheets.json")
#get_random_locations("./location_sheets.json")

