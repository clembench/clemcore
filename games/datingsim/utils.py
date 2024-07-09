import json
import random

def get_random_npcs(npc_sheets):
  """
  Function which fetches the npc sheets
  and returns them shuffled.
  """
  with open(npc_sheets, "r", encoding="UTF-8") as file:
    npcs = json.load(file)
    random.shuffle(npcs)
    return npcs
      
# import string
# # from together import Together # TODO: if there is a way to directy load via clembench. it'd have been better
# import re

# from utils import *

# with open("./key.txt", "r", encoding="UTF-8") as file: # better with clem prob, TODO: check a function using key.json
#     api_key = file.read()
# # client = Together(api_key=api_key)

# # Function to load the template from a file
# def load_template(file_path):
#     with open(file_path, 'r') as file:
#         template_content = file.read()
#     return string.Template(template_content)

# def load_data(path_to_file, randomized=False):
#     with open(path_to_file, "r", encoding="UTF-8") as file:
#         content = json.load(file)

#     # shuffle the data
#     if randomized:
#         random.shuffle(content)

#     # if it's about locations, also shuffle actions
#     if "location" in path_to_file:
#         for location in content:
#             random.shuffle(location["MAIN-ACTIONS"])

#     return content



# def get_random_locations(location_sheet):
#   """
#   Function which fetches the location sheets
#   and returns them shuffled.
#   """
#   with open(location_sheet, "r", encoding="UTF8") as file:
#     location_sheets = json.load(file)
    
#     random.shuffle(location_sheets)

#     # shuffle all mainactions within the locations
#     for location in location_sheets:
#         random.shuffle(location["MAIN-ACTIONS"])

#     return location_sheets

# def prompt_char_sheets(character_sheet):
#     prompt = f"""
#     GENDER: {character_sheet["GENDER"]}
#     AGE: {character_sheet["AGE"]}
#     APPEARANCE: {character_sheet["APPEARANCE"]}
#     LIKES: {character_sheet["LIKES"]}
#     DISLIKES: {character_sheet["DISLIKES"]}
#     HOBBIES: {character_sheet["HOBBIES"]}
#     SUMMARY: {character_sheet["SUMMARY"]}
#     """
#     return prompt

# # Function to extract subactions from the given string
# def extract_subactions(subactions_string):
#     pattern = r'\d+\)\s(.*?):\s"(.*?)"'
#     matches = re.findall(pattern, subactions_string)
#     return [f'{action}: "{dialogue}"' for action, dialogue in matches]

# # def generate_subactions(ASSISTANT_MODEL, prompt_assistant):
# #     response = client.chat.completions.create(
# #     model=ASSISTANT_MODEL,
# #     messages=[{"role": "user", "content": prompt_assistant}],
# #                )
# #     subactions = response.choices[0].message.content
# #     subactions = extract_subactions(subactions)

# #     return subactions

# # Function to check if the subactions are correct
# def check_subactions(subactions_string):
#     # Define the special token to check
#     special_token = "<OPT>"
    
#     # Check if the subactions string starts and ends with the special token
#     if not (subactions_string.startswith(special_token)):
#         return False
    
#     # Extract subactions and check their count
#     subactions = extract_subactions(subactions_string)
#     if len(subactions) != 4:
#         return False
    
#     return True

# # Function to ensure correct subactions are generated
# # def get_correct_subactions(ASSISTANT_MODEL, prompt_assistant):
# #     while True:
# #         response = client.chat.completions.create(
# #             model=ASSISTANT_MODEL,
# #             messages=[{"role": "user", "content": prompt_assistant}],
# #             )
# #         subactions = response.choices[0].message.content
        
# #         if check_subactions(subactions):
# #             subactions = extract_subactions(subactions)
# #             return subactions
# #         else:
# #             print("Subactions are incorrect or not exactly 4. Retrying...")
# #             # Retry by asking the model the same question again
# #             continue

# #get_random_npcs("./npc_sheets.json")
# #get_random_locations("./location_sheets.json")

