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



#this we need to change a lot since this is pretty much done by clembench automatically,
#I will remove it once i make sure it's safe
#
# def prompting(prompt, general_transcript, specific_transcript, ):
#     # 1. prepare prompt with
#     # previous prompts, responses and new prompt
#     new_prompt = {"role": "user", "content": prompt}
#
#     specific_transcript.append(new_prompt)
#
#     # 2. prompt to LLM
#     client = Together(api_key=api_key)
#     response_raw = client.chat.completions.create(
#         model="meta-llama/Llama-3-8b-chat-hf",
#         messages=specific_transcript,
#     )
#
#     response = response_raw.choices[0].message.content
#
#     # generate new entry in transcript with response
#     response_entry = {"role": "assistant",
#                       "content": response,
#                       }
#
#     general_transcript.append(new_prompt)
#     general_transcript.append(response_entry)
#     specific_transcript.append(response_entry)
#
#     # return general_transcript, specific_transcript

# # Step 3: GM asks PC again
#         # Who do you wanna date?
#         # further addition enforcing template and parsin mess on those actions is required
#         self.add_message(self.pc, utterance=self.load_template('resources/prompts/choose_date.template'))
#
#         # Step 4: PC replies to GM
#         # I wanna date number 3
#         # further addition enforcing template and parsin mess on those actions is required
#         self.get_answer(self.pc)
#
#         # Step 5: GM writes to NPC
#         # You are now this person, reply ready if u got it
#         # further addition enforcing template and parsin mess on those actions is required
#
#         # this template is more tricky
#         gm_to_npc_message = self.load_template('resources/initial_prompts/very_initial_npc_prompt.template')
#         self.add_message(self.pc, gm_to_npc_message)
#
#         # Step 6: NPC responds to GM
#         # ready
#         # further addition enforcing template and parsin mess on those actions is required
#         self.get_answer(self.npc)
#         # the start (all code before) is only for one game-play
#
#         # for 1,2,3 (range doesn't include last number so we add 1)
#         # range = main_actions
#         for level in range(1, self.n_levels + 1):
#             try:
#                 if game_status == "abort":
#                     break
#             except:
#                 pass
#             self.log_next_turn()
#
#             if level == 1:
#                 # here we set the initial location
#                 location = self.location
#
#             else:
#                 "oh u passed the previous (1st, 2nd) lvl bla bla"
#                 # Step in between: GM asks PC
#                 # What location do u want?
#                 gm_to_pc_message = self.load_template('resources/prompts/choose_next_location.template')
#                 self.add_message(self.pc, gm_to_pc_message)
#
#                 # Step in between answer: PC to GM
#                 # I wanna go to park
#                 self.get_answer(self.pc)
#
#                 # Step X: GM asks NPC
#                 # Your date chose this location, judge it
#                 gm_to_npc_message = self.load_template('resources/prompts/get_npc_location_reaction.template')
#                 self.add_message(self.pc, gm_to_npc_message)
#
#                 # Step X1: NPC to GM
#                 # I like park
#                 self.get_answer(self.npc)
#                 self.score[self.current_turn] = get_npc_reaction()
#
#             # here we make a while loop for game_status = True
#             # we should have a function check if game ends imo
#             for main_action in range(self.max_mainactions):
#
#                 if main_action == 0:
#                     # Step 7: GM asks PC
#                     # Description of location + What main action u wanna?
#                     gm_to_pc_message = self.load_template('resources/prompts/start_level.template')
#                     self.add_message(self.pc, gm_to_pc_message)
#
#                     # this should be a while loop over all of this code but maybe not for first lvl generation which
#                     # should be in setup
#                     try:
#                         if game_status == "abort":
#                             break
#                     except:
#                         pass
#
#                 # I think i messed this instance_index up, sorry for that
#                 # instance_index = f"{main_action + 1}.{subaction + 1}.0"
#
#                 else:
#                     # Step 7: GM asks PC
#                     #  What main action u wanna?
#                     gm_to_pc_message = self.load_template('resources/questions/gm_to_pc3.template')
#                     self.add_message(self.pc, gm_to_pc_message)
#
#                 # all from here is repeatable for any main action and any lvl
#
#                 # Step 8: PC replies to GM
#                 # I wanna do yoga
#                 self.get_answer(self.npc)
#
#                 # Step 9: GM writes to NPC
#                 # your partner wanna do yoga, judge them
#                 gm_to_npc_message = self.load_template('resources/prompts/get_npc_response.template')
#                 self.add_message(self.pc, gm_to_npc_message)
#
#                 # Step 10: NPC replies to GM
#                 # i judge them like this
#                 self.get_answer(self.npc)
#
#                 # GM makes a decision
#                 # Ok do i continue main action, change main action or end game?
#                 # check if game continues:
#
#                 self.score[self.current_turn] = get_npc_reaction()
#                 # total_sum = sum(self.score.values())
#                 # if total_sum < 0:
#                 # total_sum and stuff
#                 # theoretically we should not make score go to zero wtf
#
#                 # this should be a while loop over all of this code but maybe not for first lvl generation which
#                 try:
#                     if game_status == "abort":
#                         break
#                 except:
#                     pass
#
#                 # we should have a function check if game ends imo
#                 # this should work on self.score and last two turns
#                 num_neg_values = check_if_continue_game(self.score)
#                 if num_neg_values >= 2:
#                     break
#
#                 # generate sub-actions
#                 # not only, it also prompts it (assistant creation) to PC, NPC and gets their reactions
#                 # we should have a function check if game ends imo
#                 for subaction in range(0, self.max_subactions):
#                     try:
#                         if game_status == "abort":
#                             break
#                     except:
#                         pass
#
#                     instance_index = f"{level + 1}.{main_action + 1}.{subaction + 1}"
#
#                     if subaction == 0:
#                         # initial prompt to assistant
#                         # Step 11a: GM writes to ASSISTANT
#                         # Gimme subactions for this main action yoga
#                         gm_to_assistant_message = self.load_template(
#                             'resources/initial_prompts/initial_assistant_prompt.template')
#                         self.add_message(self.assistant, gm_to_assistant_message)
#
#                         # prompt = assistant_initial_prompt(level, all_chosen_actions, instance_index, npc_transcript,
#                         #                                   chosen_npc,
#                         #                                   location)
#
#                     else:
#                         # Step 11b: GM writes to ASSISTANT
#                         # Gimme more subactions for this main action yoga
#                         gm_to_assistant_message = self.load_template(
#                             'resources/prompts/assistant_further_subactions.template')
#                         self.add_message(self.assistant, gm_to_assistant_message)
#
#                         #
#                         # prompt = assistant_further_subactions(level, all_chosen_actions, instance_index, npc_transcript,
#                         #                                       chosen_npc,
#                         #                                       location)
#
#                     # Step 12: ASSISTANT replies to GM
#                     # Ok here u have 4 subactions
#                     self.get_answer(self.assistant)
#
#                     if game_status == "abort":
#                         break
#
#                     # give generated options to pc
#                     # Step 13: GM asks PC
#                     # What subaction u wanna do?
#                     gm_to_pc_message = self.load_template('resources/prompts/choose_further_subaction.template')
#                     self.add_message(self.pc, gm_to_pc_message)
#
#                     # again we should have a function check if game ends imo
#                     if game_status == "abort":
#                         break
#
#                     # Step 14: PC replies to GM
#                     # I wanna make a backflip
#                     self.get_answer(self.pc)
#
#                     # Step 15: GM writes to NPC
#                     # Your date made a backflip, judge them
#                     gm_to_npc_message = self.load_template('resources/prompts/get_npc_response.template')
#                     self.add_message(self.pc, gm_to_npc_message)
#
#                     # same as above we should have a function check if game ends imo
#                     if game_status == "abort":
#                         break
#
#                     # Step 16: NPC responds to GM
#                     # This is my judgment
#                     self.get_answer(self.npc)
#                     self.score[self.current_turn] = get_npc_reaction()
#
#                     # total_sum = sum(self.score.values())
#                     # if total_sum < 0:
#                     # total_sum and stuff
#                     # theoretically we should not make score go to zero wtf
#
#                     # this should work on self.score
#                     # fix it to put everything in check_if_cont_game
#                     num_neg_values = check_if_continue_game(self.score)
#                     if num_neg_values >= 2:
#                         break
#
#             # again this should be in game_status true or not, or
#             # we should have a function check if game ends imo
#
#             # not last lvl
#             if level < self.n_levels:
#                 try:
#                     if game_status == "abort":
#                         break
#                 except:
#                     pass
#
#                 # if all main and sub actions are through
#                 # or game is disturbed by penalty ????????
#                 if game_status == "abort":
#                     break
#
#                 # #we dont use it for now and it's in the wrong indentation place too
#                 # # # let npc decide if they like the suggested location
#                 # # this is happening way above
#                 # location = locations[game_transcript[-1]["cleaned response"]["NUMBER"]]
#                 # prompt = next_date(location)
#                 # prompting(prompt, game_transcript, npc_transcript)
#                 # pattern = self.pattern_num_rea_res
#                 # response, game_status = enforce_template(pattern, game_transcript, npc_transcript)
#                 # if game_status == "abort":
#                 #     break
#
#                 # npc_reaction_value = get_npc_reaction(game_transcript, npc_transcript)
#                 # npc_reaction_values.append(npc_reaction_value)
#
#                 # self.score[self.current_turn] = get_npc_reaction()
#                 # total_sum = sum(self.score.values())
#                 # if total_sum < 0:
#                 # total_sum and stuff
#                 # theoretically we should not make score go to zero wtf
#
#                 # update the score dict for level
#                 # ap.update({f"lv{level}": affinity_points})
#
#                 # check if PC has chance for a next date
#                 current_ap = len(self.score)
#                 threshold, _ = scoring_sytem(self.max_mainactions, self.max_subactions, level)
#
#                 if current_ap >= threshold:
#                     # Step NEXT DATE YES: GM to NPC
#                     # You wanna go on next date, react please!
#                     gm_to_npc_message = self.load_template('resources/prompts/next_date.template')
#                     self.add_message(self.npc, gm_to_npc_message)
#                     if game_status == "abort":
#                         break
#
#                 else:
#                     # Step NEXT DATE NO: GM to NPC
#                     # You dont wanna go on next date, react please!
#                     gm_to_npc_message = self.load_template('resources/prompts/decline_next_date.template')
#                     self.add_message(self.npc, gm_to_npc_message)
#
#                     # Step NEXT DATE NO: NPC to GM
#                     # I'm dumping u bro
#                     self.get_answer(self.npc)
#
#                     # Step END GAME: NPC to GM
#                     # Your date dump you, game over
#                     gm_to_pc_message = self.load_template('resources/prompts/aborted_game_bc_of_npc.template')
#                     self.add_message(self.npc, gm_to_pc_message)
#                     break
#
#             else:
#                 # if we reached end of last level, PC asks NPC if they
#                 # want to become an official pair
#
#                 # get threshold
#                 number_of_accessed_actions = len(self.score)
#                 threshold, _ = scoring_sytem(self.max_mainactions, self.max_subactions, level)
#                 sum_from_whole_game = sum(self.score.values())
#
#                 if sum_from_whole_game >= threshold:
#
#                     # Step END YES: GM to NPC
#                     # You're happy with dates, what do you say?
#                     gm_to_npc_message = self.load_template('resources/prompts/become_couple_yes.template')
#                     self.add_message(self.pc, gm_to_npc_message)
#
#                     # Step END YES: NPC to GM
#                     # Yes, I wanna date them! I'm super happy
#                     self.get_answer(self.npc)
#
#                     # Step END YES: GM to PC
#                     # You finished the game and have a cute date, thanks for playin!
#                     gm_to_pc_message = self.load_template('resources/prompts/game_end_win.template')
#                     self.add_message(self.pc, gm_to_pc_message)
#
#                 else:
#
#                     # Step END NO: GM to NPC
#                     # You're unhappy with date! Dump them! What do you say?
#                     gm_to_npc_message = self.load_template('resources/prompts/become_couple_no.template')
#                     self.add_message(self.pc, gm_to_npc_message)
#
#                     # Step END NO: NPC to GM
#                     # No, I wanna dump them, they are the worst!
#                     self.get_answer(self.npc)
#
#                     # Step END NO: GM to PC
#                     # You finished the game but messed up bruv, thanks for playin tho
#                     gm_to_pc_message = self.load_template('resources/prompts/game_end_lose.template')
#                     self.add_message(self.pc, gm_to_pc_message)
#
#                 if game_status == "abort":
#                     break
# def check_output_assistant(game_transcript, specific_transcript):
#     tries_to_genrate_correct_output = 0
#
#     pattern = r'<OPT>.*?<OPT>'
#
#     while True:
#         response = game_transcript[-1]["content"]
#
#         mm = re.search(pattern, response, re.DOTALL)
#
#         if mm:
#             match = mm.group()
#         else:
#             match = None
#         if match == response:
#             game_status = "ongoing"
#             break
#         elif tries_to_genrate_correct_output > 2:
#             game_status = "abort"
#             print(game_status)
#             break
#         elif match != response:
#             # Handle cases where the output doesn't match the template
#             prompt = f"""ERROR: Your given ANSWER does not follow the given TEMPLATE. Try again.
# List the possible SUB-ACTIONS as follows:
# <OPT>1) SUB ACTION: "DIALOGUE"
# 2) SUB ACTION: "DIALOGUE"
# 3) SUB ACTION: "DIALOGUE"
# 4) SUB ACTION: "DIALOGUE"
# <OPT>
#
# Don't forget to include the special symbols <OPT> and <OPT>
#
# Do NOT add any other text."""
#             tries_to_genrate_correct_output += 1
#             prompting(prompt, game_transcript, specific_transcript)
#
#     return response, game_status

# def choose_date(npc_sheets):
#     #####################
#     # prompt npc sheets #
#     #####################
#
#     npc1 = prompt_char_sheets(npc_sheets[0])
#     npc2 = prompt_char_sheets(npc_sheets[1])
#     npc3 = prompt_char_sheets(npc_sheets[2])
#
#     choose_npc_prompt = f"""CHOOSE YOUR DATE: From the following list choose the NPC you want to date. Respond with the number of the chosen character with: NUMBER:
# 1) {npc1}
# 2) {npc2}
# 3) {npc3}
#
# Use the following template to answer and nothing more or less.
# NUMBER:
# """
#     return choose_npc_prompt

# def get_assistant_sub_actions(game_transcript, specific_transcript):
#     """
#     For this version, there is no need for it
#     since the options will be forwarded as they
#     are produces
#     """
#
#     # clean the response
#     response = game_transcript[-1]["content"]
#
#     # regex to match the number and reason
#     pattern = r"NUMBER\) (\d+) SUB ACTION: (.+?) '(.*?)'"
#
#     # Extract and print matches
#     for subaction in response:
#         match = re.search(pattern, response)
#         if match:
#             number = match.group(1)
#             action = match.group(2)
#             dialogue = match.group(3)
#
#     cleaned_response = {"cleaned response": {
#         "NUMBER": int(number)}
#     }
#
#     game_transcript[-1].update(cleaned_response)
#     specific_transcript[-1].update(cleaned_response)
#
#     num = cleaned_response["NUMBER"]
#
#     point_scaling = {1: -5, 2: -3, 3: 0, 4: 3, 5: 5}
#
#     value = point_scaling[num]
#     return value
#
#
# def scoring_sytem(max_num_actions, max_num_subactions, level):
#     max_poss = max_num_actions * max_num_subactions
#     max_points = 5 * max_poss  # bc 17 possibilities to get points
#     threshold = 0
#     if level == 0:
#         threshold = 0.25 * max_points
#     elif level == 1:
#         threshold = 0.50 * max_points
#     elif level == 2:
#         threshold = 0.75 * max_points

#    return threshold, max_points


# def get_npc_reaction(game_transcript, specific_transcript):
#     # clean the response
#     response = game_transcript[-1]["content"]
#
#     # regex to match the number and reason
#     number_pattern = r"NUMBER: (\d)"
#     reason_pattern = r"REASON: (.+)"
#     answer_pattern = r"RESPONSE: (.+)"
#
#     # get matches
#     number_match = re.search(number_pattern, response)
#     reason_match = re.search(reason_pattern, response)
#     answer_match = re.search(answer_pattern, response)
#
#     # Extract matched groups if they exist
#     if number_match:
#         number = number_match.group(1)
#     else:
#         number = None
#
#     if reason_match:
#         reason = reason_match.group(1)
#     else:
#         reason = None
#
#     if answer_match:
#         answer = answer_match.group(1)
#     else:
#         answer = None
#
#     cleaned_response = {"cleaned response": {
#         "NUMBER": int(number),
#         "REASON": reason,
#         "ANSWER": answer}
#     }
#
#     # cleaned_response = {
#     #     "NUMBER": number,
#     #     "REASON": reason,
#     #     "ANSWER": answer}
#
#     game_transcript[-1].update(cleaned_response)
#     specific_transcript[-1].update(cleaned_response)
#
#     num = cleaned_response["cleaned response"]["NUMBER"]
#
#     point_scaling = {1: -5, 2: -3, 3: 0, 4: 3, 5: 5}
#
#     value = point_scaling[int(num)]
#     return value

# def save_prompt_response(prompt, response, transcript):
#     current_context = {
#         "master": prompt,
#         "pc": response
#     }
#     transcript.append(current_context)

# def get_number_and_reason(game_transcript, specific_transcript):
#     # clean the response
#     response = game_transcript[-1]["content"]
#
#     # regex to match the number and reason
#     number_pattern = r"NUMBER: (\d)"
#     reason_pattern = r"REASON: (.+)"
#
#     # get matches
#     number_match = re.search(number_pattern, response)
#     reason_match = re.search(reason_pattern, response)
#
#     # Extract matched groups if they exist
#     if number_match:
#         number = number_match.group(1)
#     else:
#         number = None
#
#     if reason_match:
#         reason = reason_match.group(1)
#     else:
#         reason = None
#
#     cleaned_response = {"cleaned response": {
#         "NUMBER": int(number),
#         "REASON": reason}
#     }
#
#     game_transcript[-1].update(cleaned_response)
#     specific_transcript[-1].update(cleaned_response)



# Patterns:
# self.pattern_sex_age = experiment["pattern_sex_age"]
# self.pattern_f_number = experiment["pattern_f_number"]
# self.pattern_num_r = experiment["pattern_num_r"]
# self.pattern_num_reason = experiment["pattern_num_reason"]
# self.pattern_num_rea_res = experiment["pattern_num_rea_res"]
# self.pattern_response = experiment["pattern_response"]


# def prompt_char_sheets(character_sheet):
#     prompt = f"""GENDER: {character_sheet["GENDER"]}
#     AGE: {character_sheet["AGE"]}
#     APPEARANCE: {character_sheet["APPEARANCE"]}
#     LIKES: {character_sheet["LIKES"]}
#     DISLIKES: {character_sheet["DISLIKES"]}
#     HOBBIES: {character_sheet["HOBBIES"]}
#     SUMMARY: {character_sheet["SUMMARY"]}
#     """
#     return prompt