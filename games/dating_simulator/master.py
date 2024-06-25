# start the game by creating folder for game
# load the data
# have a master, a player and the llm
# start the conversation between them
# include point counter
# include constraints that there are no several fails after each other allowed
from typing import Dict, List

##########################################################
##########################################################
##########################################################

from together import Together
import re
import os
import json

from backends import Model
from clemgame import get_logger
from clemgame import metrics
from clemgame.clemgame import GameMaster, GameBenchmark, GameScorer, Player
from games.dating_simulator.utils import load_data
from games.dating_simulator.resources.initial_prompts.initial_pc import give_rules
from games.dating_simulator.resources.prompts.pc_prompts import *
from games.dating_simulator.resources.prompts.npc_prompts import *
from games.dating_simulator.resources.prompts.assistant_prompts import *


GAME_NAME = "Dating Simulator"
key_path = "games/dating_simulator/key.txt"
logger = get_logger(__name__)
##########################################################
##########################################################


class DatingSimGameMaster(GameMaster):
    def __init__(self, game_name: str, experiment: Dict, player_models: List[Model]):
        super().__init__(game_name, experiment, player_models)
        self.config = experiment
        self.player_model_names = [
            player_model.get_name() for player_model in player_models
        ]
    def _custom_response(self, messages, turn_idx):
        # mock response
        return f'PC: This should never happen.'



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

    return threshold


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

with open(key_path, "r", encoding="UTF-8") as file:
    api_key = file.read()

# load data
npc_sheets_path = "games/dating_simulator/resources/ex_NPC_sheet.json"
location_sheets_path = "games/dating_simulator/resources/ex_location.json"

# load character and location sheets
npc_sheets = load_data(npc_sheets_path, randomized=True)
locations = load_data(location_sheets_path, randomized=True)

num_levels = 2
max_num_actions = 2
max_num_subactions = 2

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

for i in range(num_levels):
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
                prompt = assistant_initial_prompt(i, all_chosen_actions, instance_index, npc_transcript, chosen_npc,
                                                  location)

            else:
                prompt = assistant_further_subactions(i, all_chosen_actions, instance_index, npc_transcript, chosen_npc,
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

    if i < num_levels:
        try:
            if game_status == "abort":
                break
        except:
            pass
        # if all main and sub actions are through
        # or game is disturbed by penalty,
        # let PC chose the next location
        prompt = choose_next_location(locations, i)
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
        threshold = scoring_sytem(max_num_actions, max_num_subactions, i)

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
        threshold = scoring_sytem(max_num_actions, max_num_subactions, i)

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
    # def __init__(self, experiment: Dict, game_instance: Dict):
    #     super().__init__(GAME_NAME, experiment, game_instance)
    #     self.target_grid_name = game_instance["target_grid_name"]
    #     self.player_2_response_pattern = game_instance["player_2_response_pattern"]
    #     self.player_1_response_pattern = game_instance["player_1_response_pattern"]
    #
    # def compute_scores(self, episode_interactions: Dict) -> None:
    #     '''
    #     Compute and log scores for one episode of referencegame.
    #     :param episode_interactions: the game episode interactions log
    #     '''
    """ Episode level scores"""
    turn_scores = []
    prev_guess = None
    prev_guess_counter = 0
    prev_clue = None
    prev_clue_counter = 0
    invalid_response = False  # Note: This only takes into consideration that both players were compliant or not
    guesser_won = False
    # checking the last guess (could be None) is ok,
    # b.c. the game ends only successfully, when there is a correct guess


class DatingSimGameBenchmark(GameBenchmark):
    """Integrate the game into the benchmark run."""
    def __init__(self):
        super().__init__(GAME_NAME)

    # defines whether the game is single player or not
    def is_single_player(self):
        return True

    # add a description of your game
    def get_description(self):
        return "A game where LLM has to seduce the chosen NPC"

    # copy this, replacing the name of the game master in the return statement
    def create_game_master(
        self, experiment: Dict, player_models: List[Model]
    ) -> GameMaster:
        return DatingSimGameMaster(self.name, experiment, player_models)

    def create_game_scorer(self, experiment: Dict, game_instance: Dict) -> GameScorer:
        return DatingSimGameScorer(self.name, experiment, game_instance)


def main(dry_run):
    # master = WordleGameMaster(dry_run)
    # master.setup()
    # master.play()
    bm = DatingSimGameBenchmark(dry_run)
    master = bm.create_game_master({}, dry_run)
    master.setup()
    master.play()


if __name__ == "__main__":
    main(dry_run=True)
