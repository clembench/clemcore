# from together import Together
# import re
# import os
# import json
#from games.datingsim.utils import load_data
#from clemgame import file_utils
#key_path = "games/datingsim/key.txt"

# with open(key_path, "r", encoding="UTF-8") as file:
#     api_key = file.read()

# # load data
# npc_sheets_path = "./games/datingsim/resources/ex_NPC_sheet.json"
# location_sheets_path = "./games/datingsim/resources/ex_location.json"
#
# # load character and location sheets
# npc_sheets = load_data(npc_sheets_path, randomized=True)
# locations = load_data(location_sheets_path, randomized=True)
#
# num_levels = 2
# max_num_actions = 2
# max_num_subactions = 2


# """
# Here we dump all the gen
# """
#
# folder_path = './examples'
# game_log = {
#     'pc_transcript': pc_transcript,
#     'npc_transcript': npc_transcript,
#     'assistant_transcript': assistant_transcript,
#     'game_transcript': game_transcript,
#     'all_chosen_actions': all_chosen_actions,
#     'npc_reaction_values': npc_reaction_values,
#     'affinity_points': ap
# }
#
# dump_dict_to_json(folder_path, game_log)
#
# # generate transcript for each player
# pc_transcript = list()
# npc_transcript = list()
# assistant_transcript = list()
# game_transcript = list()
#
# # string to keep track of chosen actions
# all_chosen_actions = ""
#
# # list to keep track of replies of NPC
# npc_reaction_values = list()
#
# # count points of PC
# ap = dict()


# def ensure_folder_exists(folder_path):
#     if not os.path.exists(folder_path):
#         os.makedirs(folder_path)
#
#
# def count_files_in_folder(folder_path):
#     if not os.path.exists(folder_path):
#         return 0
#     return len([name for name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, name))])
#
#
# def dump_dict_to_json(folder_path, dictionary):
#     # Ensure the folder exists
#     ensure_folder_exists(folder_path)
#
#     # Count the number of files in the folder
#     file_count = count_files_in_folder(folder_path)
#
#     # Create the file name based on the count
#     file_name = f"{file_count + 1}.json"
#
#     # Create the full file path
#     file_path = os.path.join(folder_path, file_name)
#
#     # Dump the dictionary to a JSON file
#     with open(file_path, 'w') as json_file:
#         json.dump(dictionary, json_file, indent=4)


# make it optional coz it is good only for programmatic answers
# def main():
#     experiments = file_utils.load_json("in/instances.json", "datingsim")
#     instance = experiments["experiments"][0]["game_instances"][0]
#     master = DatingSimGameMaster(instance, ["Llama-3-70B-Together.ai", "Llama-3-70B-Together.ai"])
#     master.setup(**instance)
#     master.play()
#
#
# if __name__ == "__main__":
#     main()