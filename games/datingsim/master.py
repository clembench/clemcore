# start the game by creating folder for game
# load the data
# have a master, a player and the llm
# start the conversation between them
# include point counter
# include constraints that there are no several fails after each other allowed
import copy
from typing import Dict, List

##########################################################
##########################################################
##########################################################

from together import Together
import re
import os
import json
import numpy as np

from backends import Model
from clemgame import get_logger, file_utils
from clemgame.metrics import METRIC_ABORTED, METRIC_SUCCESS, METRIC_LOSE, METRIC_REQUEST_COUNT, \
    METRIC_REQUEST_COUNT_VIOLATED, METRIC_REQUEST_COUNT_PARSED, METRIC_REQUEST_SUCCESS, BENCH_SCORE
from clemgame.clemgame import GameMaster, GameBenchmark, GameScorer, Player

from games.datingsim.utils import load_data
from games.datingsim.resources.initial_prompts.initial_pc import give_rules
from games.datingsim.resources.prompts.pc_prompts import *
from games.datingsim.resources.prompts.npc_prompts import *
from games.datingsim.resources.prompts.assistant_prompts import *


GAME_NAME = "datingsim"
logger = get_logger(__name__)
key_path = "games/datingsim/key.txt"
##########################################################
##########################################################


class DatingSimGameMaster(GameMaster):
    def __init__(self, game_name: str, experiment: Dict, player_models: List[Model]):
        super().__init__(game_name, experiment, player_models)
        self.config = experiment
        self.initial_prompt_pc = experiment['initial_prompt_pc']
        self.max_mainactions = experiment['max_mainactions']
       #continue this
        # "max_mainactions": 4,
        # "max_subactions": 4,
        # "n_levels": 3,
        # "name": "Playthrough_mode",
        # "penalty_rules": {
        #     "max_unpleasant_actions_in_a_row": 3,
        #     "penalty_for_unpleasant_actions": -5
        # }
        self.current_turn = 0
        self.model_pc = player_models[0]
        self.model_npc = player_models[1]
        #self.model_ass = player_models[2]
        self.player_model_names = [
            player_model.get_name() for player_model in player_models
        ]

    def add_player(self, player: Player):
        idx = len(self.player_model_names)
        #player pc and npc here
        player.descriptor = f"PC"
        self.player_model_names[str(player)] = player.descriptor

    def add_message(self, player: Player, utterance: str, role="user")-> None:
    # write function
        player.history.append({'role': role, 'content': utterance})
        action = {'type': 'send message', 'content': utterance}
        self.log_event(from_='GM', to=str(self.player_model_names[str(player)]), action=action)

    def get_answer(self, player: Player) -> str:

        prompt, raw_answer, answer = player(player.history, self.current_turn)
        action = {'type': 'get message', 'content': answer}
        self.log_event(from_=str(self.player_model_names[str(player)]), to="GM", action=action, call=(copy.deepcopy(prompt), raw_answer))
        player.history = []
        return answer


    def _custom_response(self, messages, turn_idx):
        # mock response
        return f'PC: This should never happen.'

    def setup(self, **game_instance) -> None:
        logger.info("setup")
        # self.game_instance = game_instance
        # self.ap = dict()
        #put everything for the game instance

        #create player here
        #self.add_player(self.dupa)


    def play(self):
        for i in range(self.num_levels):
            self.current_turn += 1
            self.log_next_turn()
            self.add_message(self.dupa, "HI")
            answer = self.get_answer(self.dupa)
            print(answer)
            #self.add_message(self.playermodel, next_prompt)
            affinity_points = 0
            instance_index = f"{i + 1}.0.0"

            try:
                if game_status == "abort":
                    break
            except:
                pass

            # randomize level for first level
            if i == 0:
                location = locations[i]

                # prompt
                pc_initial_prompt = give_rules()
                prompting(pc_initial_prompt, game_transcript, pc_transcript)

                pattern = r'SEX:\s*(\w+)\s*AGE:\s*(\d\d)'
                response, game_status = enforce_template(pattern, game_transcript, pc_transcript)

                # end the game
                if game_status == "abort":
                    break

                choose_npc_prompt = choose_date(npc_sheets)

                prompting(choose_npc_prompt, game_transcript, pc_transcript)

                # check if generated response is in the correct format
                # Define the expected template pattern
                pattern = r'NUMBER:\s*(.+?)'
                response, game_status = enforce_template(pattern, game_transcript, pc_transcript)
                if game_status == "abort":
                    break

                # clean the response

                # regex to match the number and reason
                number_pattern = r"NUMBER: (\d)"

                # get matches
                number_match = re.search(number_pattern, response)

                # Extract matched groups if they exist
                if number_match:
                    number = number_match.group(1)
                else:
                    number = None

                cleaned_response = {"cleaned response": {
                    "NUMBER": int(number)}
                }

                game_transcript[-1].update(cleaned_response)
                pc_transcript[-1].update(cleaned_response)

                chosen_npc = npc_sheets[int(number) - 1]

            #################################################
            # here starts what is applicable to every level
            #################################################

            for j in range(max_num_actions):
                try:
                    if game_status == "abort":
                        break
                except:
                    pass
                instance_index = f"{i + 1}.{j + 1}.0"

                if j == 0:
                    # if it is the first main-action of the instance,
                    # first give a location description and
                    # immediatly after that the action options
                    prompt, actions = start_level(location, j)

                    # give prompt to pc
                    prompting(prompt, game_transcript, pc_transcript)

                    pattern = r'NUMBER:\s*(.+?)\s*REASON:\s*(.+)'
                    response, game_status = enforce_template(pattern, game_transcript, pc_transcript)
                    if game_status == "abort":
                        break

                    get_number_and_reason(game_transcript, pc_transcript)

                    # give NPC rules and get their reaction
                    chosen_main_action = actions[int(game_transcript[-1]["cleaned response"]["NUMBER"]) - 1]
                    prompt = npc_initial_prompt(chosen_npc, chosen_main_action)

                else:
                    prompt = choose_further_mainaction(npc_transcript, location, j)
                    prompting(prompt, game_transcript, pc_transcript)
                    pattern = r'NUMBER:\s*(.+?)\s*REASON:\s*(.+)'
                    response, game_status = enforce_template(pattern, game_transcript, pc_transcript)
                    if game_status == "abort":
                        break

                    # get number and reason
                    get_number_and_reason(game_transcript, pc_transcript)

                    chosen_main_action = actions[int(pc_transcript[-1]["cleaned response"]["NUMBER"]) - 1]
                    prompt = get_npc_response(chosen_main_action)

                all_chosen_actions += instance_index + "\t" + chosen_main_action + "\n"

                # prompt to npc
                prompting(prompt, game_transcript, npc_transcript)
                pattern = r'NUMBER:\s*(.+?)\s*REASON:\s*(.+)\s*RESPONSE:\s*(.+)'
                response, game_status = enforce_template(pattern, game_transcript, npc_transcript)
                if game_status == "abort":
                    break

                npc_reaction_value = get_npc_reaction(game_transcript, npc_transcript)
                npc_reaction_values.append(npc_reaction_value)

                affinity_points += npc_reaction_value
                if affinity_points < 0:
                    affinity_points = 0

                # check if game continues
                num_neg_values = check_if_continue_game(npc_reaction_values)
                if num_neg_values >= 2:
                    break

                # generate sub-actions
                for k in range(max_num_subactions):
                    try:
                        if game_status == "abort":
                            break
                    except:
                        pass

                    instance_index = f"{i + 1}.{j + 1}.{k + 1}"

                    # generate prompt for assistant

                    if k == 0:
                        # initial prompt to assistent
                        prompt = assistant_initial_prompt(i, all_chosen_actions, instance_index, npc_transcript,
                                                          chosen_npc,
                                                          location)

                    else:
                        prompt = assistant_further_subactions(i, all_chosen_actions, instance_index, npc_transcript,
                                                              chosen_npc,
                                                              location)

                    prompting(prompt, game_transcript, assistant_transcript)
                    check_output_assistant(game_transcript, assistant_transcript)
                    if game_status == "abort":
                        break

                    # sub_actions = game_transcript[-1]["content"]
                    sub_actions = response

                    # give generated options to pc
                    prompt = choose_further_subactions(sub_actions, npc_transcript)
                    prompting(prompt, game_transcript, pc_transcript)
                    pattern = r'NUMBER:\s*(.+?)\s*REASON:\s*(.+)'
                    response, game_status = enforce_template(pattern, game_transcript, pc_transcript)
                    if game_status == "abort":
                        break

                    # get number and reason
                    get_number_and_reason(game_transcript, pc_transcript)

                    # get npc response
                    chosen_sub_action = sub_actions[int(pc_transcript[-1]["cleaned response"]["NUMBER"]) - 1]
                    all_chosen_actions += instance_index + "\t" + chosen_main_action + "\n"

                    prompt = get_npc_response(chosen_sub_action)
                    # prompt to npc
                    prompting(prompt, game_transcript, npc_transcript)
                    pattern = r'NUMBER:\s*(.+?)\s*REASON:\s*(.+)\s*RESPONSE:\s*(.+)'
                    response, game_status = enforce_template(pattern, game_transcript, npc_transcript)
                    if game_status == "abort":
                        break

                    npc_reaction_value = get_npc_reaction(game_transcript, npc_transcript)
                    npc_reaction_values.append(npc_reaction_value)

                    affinity_points += npc_reaction_value
                    if affinity_points < 0:
                        affinity_points = 0

                    # check if game continues
                    num_neg_values = check_if_continue_game(npc_reaction_values)
                    if num_neg_values >= 2:
                        break

            if i < self.num_levels:
                try:
                    if game_status == "abort":
                        break
                except:
                    pass
                # if all main and sub actions are through
                # or game is disturbed by penalty,
                # let PC chose the next location
                prompt = choose_next_location(self.locations, i)
                prompting(prompt, game_transcript, pc_transcript)
                pattern = r'NUMBER:\s*(.+?)\s*REASON:\s*(.+)'
                response, game_status = enforce_template(pattern, game_transcript, pc_transcript)
                if game_status == "abort":
                    break

                get_number_and_reason(game_transcript, pc_transcript)

                # let npc decide if they like the suggested location
                location = locations[game_transcript[-1]["cleaned response"]["NUMBER"]]
                prompt = next_date(location)
                prompting(prompt, game_transcript, npc_transcript)
                pattern = r'NUMBER:\s*(.+?)\s*REASON:\s*(.+)\s*RESPONSE:\s*(.+)'
                response, game_status = enforce_template(pattern, game_transcript, npc_transcript)
                if game_status == "abort":
                    break

                npc_reaction_value = get_npc_reaction(game_transcript, npc_transcript)
                npc_reaction_values.append(npc_reaction_value)

                affinity_points += npc_reaction_value
                if affinity_points < 0:
                    affinity_points = 0

                ap.update({f"lv{i}": affinity_points})

                # check if PC has chance for a next date
                number_of_accessed_actions = len(npc_reaction_values)
                threshold, _ = scoring_sytem(self.max_num_actions, self.max_num_subactions, i)

                neg_prompt = False  # quick solution
                if affinity_points >= threshold:
                    # if so, prompt NPC to give positive response
                    pos_prompt = grant_next_date()
                    prompting(pos_prompt, game_transcript, npc_transcript)
                    pattern = r'RESPONSE:\s*(.+)'
                    response, game_status = enforce_template(pattern, game_transcript, npc_transcript)
                    if game_status == "abort":
                        break

                    # if not, prompt NPC to give negative response
                else:
                    neg_prompt = decline_next_date()
                    prompting(neg_prompt, game_transcript, npc_transcript)
                    pattern = r'RESPONSE:\s*(.+)'
                    response, game_status = enforce_template(pattern, game_transcript, npc_transcript)
                    if game_status == "abort":
                        break

                # clean the response
                response = game_transcript[-1]["content"]
                # regex to match the number and reason
                response_pattern = r"RESPONSE: (.+)"
                # get matches
                response_match = re.search(response_pattern, response)
                # Extract matched groups if they exist
                if response_match:
                    res = response_match.group(1)
                else:
                    res = None
                cleaned_response = {"cleaned response": {
                    "RESPONSE": res}
                }

                game_transcript[-1].update(cleaned_response)
                npc_transcript[-1].update(cleaned_response)

                # if date ends the date, end the whole game
                if neg_prompt:
                    # tell NPC to abort mission
                    prompt = aborted_game_bc_of_npc(location, game_transcript, ap)
                    prompting(prompt, game_transcript, pc_transcript)

                    break

            else:
                # if we reached end of last level, PC asks NPC if they
                # want to become an official pair

                # get threshold
                number_of_accessed_actions = len(npc_reaction_values)
                threshold, _ = scoring_sytem(self.max_num_actions, self.max_num_subactions, i)

                if affinity_points >= threshold:
                    answer = "YES"
                else:
                    answer = "NO"

                # prompt to NPC with the pre-defined question of going out
                # generate answer of NPC
                prompt = become_couple(answer)
                prompting(prompt, game_transcript, npc_transcript)
                pattern = r'RESPONSE:\s*(.+)'
                response, game_status = enforce_template(pattern, game_transcript, pc_transcript)
                if game_status == "abort":
                    break

                # clean the response
                response = game_transcript[-1]["content"]
                # regex to match the number and reason
                response_pattern = r"RESPONSE: (.+)"
                # get matches
                response_match = re.search(response_pattern, response)
                # Extract matched groups if they exist
                if response_match:
                    res = response_match.group(1)
                else:
                    res = None
                cleaned_response = {"cleaned response": {
                    "RESPONSE": res}
                }

                game_transcript[-1].update(cleaned_response)
                npc_transcript[-1].update(cleaned_response)

                # prompt to PC that they have asked NPC to become an
                # official pair and give it the response of the NPC to
                # the asked question
                prompt = end_game(game_transcript, answer, ap)

                prompting(prompt, game_transcript, pc_transcript)


def prompting(prompt, general_transcript, specific_transcript, ):
    # 1. prepare prompt with
    # previous prompts, responses and new prompt
    new_prompt = {"role": "user", "content": prompt}

    specific_transcript.append(new_prompt)

    # 2. prompt to LLM
    client = Together(api_key=api_key)
    response_raw = client.chat.completions.create(
        model="meta-llama/Llama-3-8b-chat-hf",
        messages=specific_transcript,
    )

    response = response_raw.choices[0].message.content

    # generate new entry in transcript with response
    response_entry = {"role": "assistant",
                      "content": response,
                      }

    general_transcript.append(new_prompt)
    general_transcript.append(response_entry)
    specific_transcript.append(response_entry)

    # return general_transcript, specific_transcript


def enforce_template(pattern, game_transcript, specific_transcript):
    """
    Function which checks the given answer of the LLMS.
    If they follow the given template, all gucci.
    If not, generate new prompt where we enforce the
    usage of the template
    """

    tries_to_genrate_correct_output = 0

    while True:

        response = game_transcript[-1]["content"]

        # Search for the pattern in the output
        match = re.search(pattern, response, re.DOTALL)

        if match:
            game_status = "ongoing"
            break
        elif tries_to_genrate_correct_output > 2:
            game_status = "abort"
            print(game_status)
            break
        elif not match:
            # Handle cases where the output doesn't match the template
            prompt = f"""ERROR: Your given ANSWER does not follow the given TEMPLATE. Try again. Use the following TEMPLATE: {pattern}

DO NOT APOLOGIZE OR WHATEVER. JUST USE THE PATTERN"""
            tries_to_genrate_correct_output += 1
            prompting(prompt, game_transcript, specific_transcript)

    return response, game_status


def check_output_assistant(game_transcript, specific_transcript):
    tries_to_genrate_correct_output = 0

    pattern = r'<OPT>.*?<OPT>'

    while True:
        response = game_transcript[-1]["content"]

        mm = re.search(pattern, response, re.DOTALL)

        if mm:
            match = mm.group()
        else:
            match = None
        if match == response:
            game_status = "ongoing"
            break
        elif tries_to_genrate_correct_output > 2:
            game_status = "abort"
            print(game_status)
            break
        elif match != response:
            # Handle cases where the output doesn't match the template
            prompt = f"""ERROR: Your given ANSWER does not follow the given TEMPLATE. Try again.
List the possible SUB-ACTIONS as follows:
<OPT>1) SUB ACTION: "DIALOGUE"
2) SUB ACTION: "DIALOGUE"
3) SUB ACTION: "DIALOGUE"
4) SUB ACTION: "DIALOGUE"
<OPT>

Don't forget to include the special symbols <OPT> and <OPT>

Do NOT add any other text."""
            tries_to_genrate_correct_output += 1
            prompting(prompt, game_transcript, specific_transcript)

    return response, game_status


def save_prompt_response(prompt, response, transcript):
    current_context = {
        "master": prompt,
        "pc": response
    }
    transcript.append(current_context)


def prompt_char_sheets(character_sheet):
    prompt = f"""GENDER: {character_sheet["GENDER"]}
    AGE: {character_sheet["AGE"]}
    APPEARANCE: {character_sheet["APPEARANCE"]}
    LIKES: {character_sheet["LIKES"]}
    DISLIKES: {character_sheet["DISLIKES"]}
    HOBBIES: {character_sheet["HOBBIES"]}
    SUMMARY: {character_sheet["SUMMARY"]}
    """
    return prompt


def choose_date(npc_sheets):
    #####################
    # prompt npc sheets #
    #####################

    npc1 = prompt_char_sheets(npc_sheets[0])
    npc2 = prompt_char_sheets(npc_sheets[1])
    npc3 = prompt_char_sheets(npc_sheets[2])

    choose_npc_prompt = f"""CHOOSE YOUR DATE: From the following list choose the NPC you want to date. Respond with the number of the chosen character with: NUMBER: 
1) {npc1}
2) {npc2}
3) {npc3}

Use the following template to answer and nothing more or less.
NUMBER:
"""
    return choose_npc_prompt


def check_if_continue_game(npc_reaction_values):
    """
    Function which checks the number of negative
    responses of the NPC in a row. 
    """
    if len(npc_reaction_values) >= 2:

        # count negative values:
        num_neg_values = 0
        for value in npc_reaction_values[-1:-3]:
            if value < 0:
                num_neg_values += 1
        return num_neg_values

    else:
        num_neg_values = 0
        return num_neg_values


def get_number_and_reason(game_transcript, specific_transcript):
    # clean the response
    response = game_transcript[-1]["content"]

    # regex to match the number and reason
    number_pattern = r"NUMBER: (\d)"
    reason_pattern = r"REASON: (.+)"

    # get matches
    number_match = re.search(number_pattern, response)
    reason_match = re.search(reason_pattern, response)

    # Extract matched groups if they exist
    if number_match:
        number = number_match.group(1)
    else:
        number = None

    if reason_match:
        reason = reason_match.group(1)
    else:
        reason = None

    cleaned_response = {"cleaned response": {
        "NUMBER": int(number),
        "REASON": reason}
    }

    game_transcript[-1].update(cleaned_response)
    specific_transcript[-1].update(cleaned_response)


def get_npc_reaction(game_transcript, specific_transcript):
    # clean the response
    response = game_transcript[-1]["content"]

    # regex to match the number and reason
    number_pattern = r"NUMBER: (\d)"
    reason_pattern = r"REASON: (.+)"
    answer_pattern = r"RESPONSE: (.+)"

    # get matches
    number_match = re.search(number_pattern, response)
    reason_match = re.search(reason_pattern, response)
    answer_match = re.search(answer_pattern, response)

    # Extract matched groups if they exist
    if number_match:
        number = number_match.group(1)
    else:
        number = None

    if reason_match:
        reason = reason_match.group(1)
    else:
        reason = None

    if answer_match:
        answer = answer_match.group(1)
    else:
        answer = None

    cleaned_response = {"cleaned response": {
        "NUMBER": int(number),
        "REASON": reason,
        "ANSWER": answer}
    }

    # cleaned_response = {
    #     "NUMBER": number,
    #     "REASON": reason,
    #     "ANSWER": answer}

    game_transcript[-1].update(cleaned_response)
    specific_transcript[-1].update(cleaned_response)

    num = cleaned_response["cleaned response"]["NUMBER"]

    point_scaling = {1: -5, 2: -3, 3: 0, 4: 3, 5: 5}

    value = point_scaling[int(num)]
    return value


def get_assistant_sub_actions(game_transcript, specific_transcript):
    """
    For this version, there is no need for it
    since the options will be forwarded as they
    are produces
    """

    # clean the response
    response = game_transcript[-1]["content"]

    # regex to match the number and reason
    pattern = r"NUMBER\) (\d+) SUB ACTION: (.+?) '(.*?)'"

    # Extract and print matches
    for subaction in response:
        match = re.search(pattern, response)
        if match:
            number = match.group(1)
            action = match.group(2)
            dialogue = match.group(3)

    cleaned_response = {"cleaned response": {
        "NUMBER": int(number)}
    }

    game_transcript[-1].update(cleaned_response)
    specific_transcript[-1].update(cleaned_response)

    num = cleaned_response["NUMBER"]

    point_scaling = {1: -5, 2: -3, 3: 0, 4: 3, 5: 5}

    value = point_scaling[num]
    return value


def scoring_sytem(max_num_actions, max_num_subactions, level):
    max_poss = max_num_actions * max_num_subactions
    max_points = 5 * max_poss  # bc 17 possibilities to get points

    if level == 0:
        threshold = 0.25 * max_points
    elif level == 1:
        threshold = 0.50 * max_points
    elif level == 2:
        threshold = 0.75 * max_points

    return threshold, max_points


def ensure_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def count_files_in_folder(folder_path):
    if not os.path.exists(folder_path):
        return 0
    return len([name for name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, name))])


def dump_dict_to_json(folder_path, dictionary):
    # Ensure the folder exists
    ensure_folder_exists(folder_path)

    # Count the number of files in the folder
    file_count = count_files_in_folder(folder_path)

    # Create the file name based on the count
    file_name = f"{file_count + 1}.json"

    # Create the full file path
    file_path = os.path.join(folder_path, file_name)

    # Dump the dictionary to a JSON file
    with open(file_path, 'w') as json_file:
        json.dump(dictionary, json_file, indent=4)


##########################################################
##########################################################

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

# generate transcript for each player
pc_transcript = list()
npc_transcript = list()
assistant_transcript = list()
game_transcript = list()

# string to keep track of chosen actions
all_chosen_actions = ""

# list to keep track of replies of NPC
npc_reaction_values = list()

# count points of PC
ap = dict()


"""
Here we dump all the gen
"""

folder_path = './examples'
game_log = {
    'pc_transcript': pc_transcript,
    'npc_transcript': npc_transcript,
    'assistant_transcript': assistant_transcript,
    'game_transcript': game_transcript,
    'all_chosen_actions': all_chosen_actions,
    'npc_reaction_values': npc_reaction_values,
    'affinity_points': ap
}

dump_dict_to_json(folder_path, game_log)

class DatingSimGameScorer(GameScorer):
    def __init__(self, experiment: Dict, game_instance: Dict):
         super().__init__(GAME_NAME, experiment, game_instance)
    
    def compute_scores(self, episode_interactions: Dict) -> None:
        """Episode level scores"""
        # implement the penalty for unpleasant actions in the scoring system here
        # not sure if we need to count current_unpleasant_actions_in_a_row here maybe GM is better so it can already abort the game?
        # pc_successful is True if it reaches certain level_threshold but 
        # find a way to reach instances file here. why can't I reach experiment variables here?
        turn_scores = []
        current_unpleasant_actions_in_a_row = 0
        #max_unpleasant_actions_in_a_row = experiment[max_unpleasant_actions_in_a_row]
        #penalty_for_unpleasant_actions = experiment[penalty_for_unpleasant_actions]
        accumulated_points = 0
        level_threshold, max_points = scoring_sytem(max_num_actions, max_num_subactions)

        invalid_response = False 
        pc_successful = False
        # maybe add num_sub/main_actions ?

        for turn_idx, turn in enumerate(episode_interactions["turns"]):
             turn_score = {"last_choice": None, "current_point": 0, "request_count": 1}
             
             for event in turn:
                action = event["action"]
                if action["type"] == "invalid format":
                    invalid_response = True
                if action["type"] == "current_point":
                    turn_score["current_point"] = action["content"]
                if action["type"] == "non-affirmative response":
                    current_unpleasant_actions_in_a_row += current_unpleasant_actions_in_a_row + action["content"]
                if action["type"] == "affirmative response":
                    pc_successful = True
                    accumulated_points += accumulated_points + turn_score["current_point"]
        
             if invalid_response:
                turn_score["violated_request_count"] = 1
                turn_score["parsed_request_count"] = 0
             else:
                turn_score["violated_request_count"] = 0
                turn_score["parsed_request_count"] = 1
            
             self.log_turn_score(turn_idx, 'Accuracy', 1 if pc_successful else 0)
             self.log_turn_score(turn_idx, 'Affinity Points', turn_score["current_point"])
             self.log_turn_score(turn_idx, METRIC_REQUEST_COUNT_VIOLATED, turn_score["violated_request_count"])
             self.log_turn_score(turn_idx, METRIC_REQUEST_COUNT_PARSED, turn_score["parsed_request_count"])
             self.log_turn_score(turn_idx, METRIC_REQUEST_COUNT, turn_score["request_count"])
             turn_scores.append(turn_score)
        
        violated_request_count = sum([turn["violated_request_count"] for turn in turn_scores])
        self.log_episode_score(METRIC_REQUEST_COUNT_VIOLATED, violated_request_count)

        parsed_request_count = sum([turn["parsed_request_count"] for turn in turn_scores])
        self.log_episode_score(METRIC_REQUEST_COUNT_PARSED, parsed_request_count)

        request_count = sum([turn["request_count"] for turn in turn_scores])
        self.log_episode_score(METRIC_REQUEST_COUNT, request_count)

        self.log_episode_score(METRIC_REQUEST_SUCCESS, parsed_request_count / request_count)

        total_affinity_points = sum([turn["affinity_points"] for turn in turn_scores])
        self.log_episode_score('Accumulated Affinity Points', total_affinity_points)

        pc_successful = False # need to reset it for calculating episode success
        if total_affinity_points > level_threshold:
            pc_successful =  True
             
        # Common metrics
        if invalid_response:  # whether a violation of the game rules happened (response not parsable)
            self.log_episode_score(METRIC_ABORTED, 1)
            self.log_episode_score(METRIC_SUCCESS, 0)
            self.log_episode_score(METRIC_LOSE, 0)
            # Game-specific metrics 
            self.log_episode_score(BENCH_SCORE, np.nan)  # metric not applicable
        else:
            self.log_episode_score(METRIC_ABORTED, 0)
            if pc_successful:
                self.log_episode_score(METRIC_SUCCESS, 1)
                self.log_episode_score(METRIC_LOSE, 0)
                self.log_episode_score(BENCH_SCORE, 100 / total_affinity_points / max_points * 100 )
            else:
                self.log_episode_score(METRIC_SUCCESS, 0)
                self.log_episode_score(METRIC_LOSE, 1)
                self.log_episode_score(BENCH_SCORE, 0) # 0 or the same formula as above?
    

class DatingSimGameBenchmark(GameBenchmark):

    def __init__(self):
        super().__init__(GAME_NAME)

    # defines whether the game is single player or not
    def is_single_player(self):
        return True

    # add a description of your game
    def get_description(self):
        return "A game where LLM has to seduce the chosen NPC"

    def create_game_master(
        self, experiment: Dict, player_models: List[Model]
    ) -> GameMaster:
        return DatingSimGameMaster(experiment, player_models)

    def create_game_scorer(self, experiment: Dict, game_instance: Dict) -> GameScorer:
        return DatingSimGameScorer(experiment, game_instance)

#make it optional coz it is good only for programatic answers
def main():
    experiments = file_utils.load_json("in/instances.json", "datingsim")
    instance = experiments["experiments"][0]["game_instances"][0]
    master = DatingSimGameMaster(instance, ["Llama-3-70B-Together.ai", "Llama-3-70B-Together.ai"])
    master.setup(**instance)
    master.play()


if __name__ == "__main__":
    main()
