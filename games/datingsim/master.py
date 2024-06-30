import copy
import re
from typing import Dict, List
from string import Template
import numpy as np

from backends import Model
from clemgame import get_logger
from clemgame.metrics import METRIC_ABORTED, METRIC_SUCCESS, METRIC_LOSE, METRIC_REQUEST_COUNT, \
    METRIC_REQUEST_COUNT_VIOLATED, METRIC_REQUEST_COUNT_PARSED, METRIC_REQUEST_SUCCESS, BENCH_SCORE
from clemgame.clemgame import GameMaster, GameBenchmark, GameScorer
from games.datingsim.player import *

GAME_NAME = "datingsim"
logger = get_logger(__name__)


class DatingSimGameMaster(GameMaster):
    def __init__(self, game_name: str, experiment: Dict, player_models: List[Model]):
        super().__init__(game_name, experiment, player_models)
        self.initial_prompt_pc = experiment['initial_prompt_pc']
        self.prompt_npc = experiment['initial_prompt_npc']
        self.prompt_assistant = experiment['initial_prompt_assistant']

        # regex patterns
        self.pattern_sex_age = experiment["pattern_sex_age"]
        self.pattern_f_number = experiment["pattern_f_number"]
        self.pattern_num_r = experiment["pattern_num_r"]
        self.pattern_num_reason = experiment["pattern_num_reason"]
        self.pattern_num_rea_res = experiment["pattern_num_rea_res"]
        self.pattern_response = experiment["pattern_response"]

        self.max_mainactions = experiment['max_mainactions']
        self.max_subactions = experiment['max_subactions']
        self.n_levels = experiment['n_levels']
        self.name = experiment['name']
        self.penalty_rules = experiment['penalty_rules']
        self.current_turn = 0

        # boolean to see game status
        self.game_status = True 
        # check for invalid responses 
        self.invalid_response = False
        self.score = {}  # affinity points

        # this may cause problems because of clembench max 2 player problem
        # but there is a chance we can force clembench to ignore scoring for npc and ass then it should work imo
        self.model_pc = player_models[0]
        self.model_npc = player_models[1]
        self.model_ass = player_models[2]

        self.player_model_names = [
            player_model.get_name() for player_model in player_models
        ]

    def add_player(self, player: Player) -> None:
        idx = len(self.player_model_names)
        # player pc and npc here
        if idx == 0:
            player.descriptor = f"PC"
        elif idx == 1:
            player.descriptor = f"NPC"
        else:
            player.descriptor = f"Assistant"
        self.player_model_names[str(player)] = player.descriptor

    def add_message(self, player: Player, utterance: str, role="user") -> None:
        # write function, this needs to be merged with what is in GameMaster of dating_simulator/master.py
        player.history.append({'role': role, 'content': utterance})
        action = {'type': 'send message', 'content': utterance}
        self.log_event(from_='GM', to=str(self.player_model_names[str(player)]), action=action)

    def get_answer(self, player: Player, restart_history=True) -> str:
        # this needs to be merged with what is in GameMaster of dating_simulator/master.py
        prompt, raw_answer, answer = player(player.history, self.current_turn)
        action = {'type': 'get message', 'content': answer}
        self.log_event(from_=str(self.player_model_names[str(player)]), to="GM", action=action,
                       call=(copy.deepcopy(prompt), raw_answer))
        # figure out how to add to history after parsing
        if restart_history == True:
            player.history = []
        return answer

    def setup(self, **game_instance) -> None:
        """
        The function sets up the game with the given game instance configuration.
        """
        logger.info("Setup")

        # import game instances
        self.game_instance = game_instance
        self.game_id = self.game_instance["game_id"]
        self.location = game_instance["location"]
        self.npc_candidates = game_instance["npcs"]

        # create player/s here
        self.pc = PC(self.model_a, "Player")
        self.npc = NPC(self.model_b, "Date")
        self.assistant = Assistant(self.model_c, "Assistant")
        self.add_player(self.pc)
        self.add_player(self.npc)
        self.add_player(self.assistant)

        def does_game_continue(self): # XXmod
        """
        Proceed until player
        - finishes game successfully or
        - doesn't meet the threshold to continue or
        - has too many negative actions in a row.
        """
        if self.invalid_response:
            self.log_to_self("invalid format", "abort game") # message from GM to GM
            return False
        elif self.count_bad_choices > 2:
            self.log_to_self("too many bad choices", "failed game")
            return False
        elif self.became_pair == True:
            self.log_to_self("became a pair", "end game")
            return False
        else:
            return True
        
    def validate_response(self, player: Player, utterance: str, pattern: str, repetition: False) -> bool: # XXmod
        """
        Function to check if the given answer is in the valid
        format. 
        If yes, the game continues.
        If no, the game is aborted.
        If repetitions are allowed, the role can re-try n times.
        If it fails again, the game will be aborted.
        """
        match = re.search(pattern, utterance)

        if repetition == False:
            if match:
                self.game_status = True
            else:
                self.game_status = False

        else:
            tries_to_genrate_correct_output = 0
            while True:
                if match:
                    self.game_status = True
                    break
                elif tries_to_genrate_correct_output > 2:
                    self.game_status = False
                    break
                elif not match:
                    # Handle cases where the output doesn't match the template
                    tries_to_genrate_correct_output += 1
                    # need to include reprompt here, not sure if this is the
                    # correct method though
                    DialogueGameMaster.prompt(player=player, is_reprompt=True)
                    break
                    
        
    def play(self):
        # this is our main pain
        # all the message patterns should be made in instance_generator
        # location and 3 NPC options should probably be provided in instance gen as well, but it depends on choice
        # we should make game_status True/False (according to Nick) which makes sense
        # Initial interaction sequence (steps 1 to 6)

        # TO ALL STEPS ADD MESSAGE PARSING WHICH SHOULD BE A METHOD INSIDE GAME MASTER (?) FOR NOW

        # added beginning of the game according to dating_simulator/master.py
        # part of it is already updated to show how to change from the earlier code to add_mess and get_answ
        # further addition enforcing template and parsin mess on those actions is required
        self.log_next_turn()

        self.current_turn += 1
        self.log_next_turn()

        # "i" should be level number, idk i think i misplaced it since i changed the loops ;-;
        # instance_index = f"{i + 1}.0.0"

        # Step 1: GM asks PC
        # What is your age, gender?
        # further addition enforcing template and parsin mess on those actions is required
        self.add_message(self.pc, utterance=self.load_template('resources/initial_prompts/initial_pc_prompt.template'))
        # prompt GM -> PC
        # validate answer with
        # validate_response
        # check if game continues with 
        # does_game_continue

        # Step 2: PC replies to GM
        # Im 666 year old mekanik
        # further addition enforcing template and parsin mess on those actions is required
        self.get_answer(self.pc)

        # Step 3: GM asks PC again
        # Who do you wanna date?
        # further addition enforcing template and parsin mess on those actions is required
        self.add_message(self.pc, utterance=self.load_template('resources/prompts/choose_date.template'))

        # Step 4: PC replies to GM
        # I wanna date number 3
        # further addition enforcing template and parsin mess on those actions is required
        self.get_answer(self.pc)

        # Step 5: GM writes to NPC
        # You are now this person, reply ready if u got it
        # further addition enforcing template and parsin mess on those actions is required

        # this template is more tricky
        gm_to_npc_message = self.load_template('resources/initial_prompts/very_initial_npc_prompt.template')
        self.add_message(self.pc, gm_to_npc_message)

        # Step 6: NPC responds to GM
        # ready
        # further addition enforcing template and parsin mess on those actions is required
        self.get_answer(self.npc)
        # the start (all code before) is only for one game-play

        # for 1,2,3 (range doesn't include last number so we add 1)
        # range = main_actions
        for level in range(1, self.n_levels + 1):
            try:
                if game_status == "abort":
                    break
            except:
                pass
            self.log_next_turn()

            if level == 1:
                # here we set the initial location
                location = self.location

            else:
                "oh u passed the previous (1st, 2nd) lvl bla bla"
                # Step in between: GM asks PC
                # What location do u want?
                gm_to_pc_message = self.load_template('resources/prompts/choose_next_location.template')
                self.add_message(self.pc, gm_to_pc_message)

                # Step in between answer: PC to GM
                # I wanna go to park
                self.get_answer(self.pc)

                # Step X: GM asks NPC
                # Your date chose this location, judge it
                gm_to_npc_message = self.load_template('resources/prompts/get_npc_location_reaction.template')
                self.add_message(self.pc, gm_to_npc_message)

                # Step X1: NPC to GM
                # I like park
                self.get_answer(self.npc)
                self.score[self.current_turn] = get_npc_reaction()

            # here we make a while loop for game_status = True
            # we should have a function check if game ends imo
            for main_action in range(self.max_mainactions):

                if main_action == 0:
                    # Step 7: GM asks PC
                    # Description of location + What main action u wanna?
                    gm_to_pc_message = self.load_template('resources/prompts/start_level.template')
                    self.add_message(self.pc, gm_to_pc_message)

                    # this should be a while loop over all of this code but maybe not for first lvl generation which
                    # should be in setup
                    try:
                        if game_status == "abort":
                            break
                    except:
                        pass

                # I think i messed this instance_index up, sorry for that
                # instance_index = f"{main_action + 1}.{subaction + 1}.0"

                else:
                    # Step 7: GM asks PC
                    #  What main action u wanna?
                    gm_to_pc_message = self.load_template('resources/questions/gm_to_pc3.template')
                    self.add_message(self.pc, gm_to_pc_message)

                # all from here is repeatable for any main action and any lvl

                # Step 8: PC replies to GM
                # I wanna do yoga
                self.get_answer(self.npc)

                # Step 9: GM writes to NPC
                # your partner wanna do yoga, judge them
                gm_to_npc_message = self.load_template('resources/prompts/get_npc_response.template')
                self.add_message(self.pc, gm_to_npc_message)

                # Step 10: NPC replies to GM
                # i judge them like this
                self.get_answer(self.npc)

                # GM makes a decision
                # Ok do i continue main action, change main action or end game?
                # check if game continues:

                self.score[self.current_turn] = get_npc_reaction()
                # total_sum = sum(self.score.values())
                # if total_sum < 0:
                # total_sum and stuff
                # theoretically we should not make score go to zero wtf

                # this should be a while loop over all of this code but maybe not for first lvl generation which
                try:
                    if game_status == "abort":
                        break
                except:
                    pass

                # we should have a function check if game ends imo
                # this should work on self.score and last two turns
                num_neg_values = check_if_continue_game(self.score)
                if num_neg_values >= 2:
                    break

                # generate sub-actions
                # not only, it also prompts it (assistant creation) to PC, NPC and gets their reactions
                # we should have a function check if game ends imo
                for subaction in range(0, self.max_subactions):
                    try:
                        if game_status == "abort":
                            break
                    except:
                        pass

                    instance_index = f"{level + 1}.{main_action + 1}.{subaction + 1}"

                    if subaction == 0:
                        # initial prompt to assistant
                        # Step 11a: GM writes to ASSISTANT
                        # Gimme subactions for this main action yoga
                        gm_to_assistant_message = self.load_template(
                            'resources/initial_prompts/initial_assistant_prompt.template')
                        self.add_message(self.assistant, gm_to_assistant_message)

                        # prompt = assistant_initial_prompt(level, all_chosen_actions, instance_index, npc_transcript,
                        #                                   chosen_npc,
                        #                                   location)

                    else:
                        # Step 11b: GM writes to ASSISTANT
                        # Gimme more subactions for this main action yoga
                        gm_to_assistant_message = self.load_template(
                            'resources/prompts/assistant_further_subactions.template')
                        self.add_message(self.assistant, gm_to_assistant_message)

                        #
                        # prompt = assistant_further_subactions(level, all_chosen_actions, instance_index, npc_transcript,
                        #                                       chosen_npc,
                        #                                       location)

                    # Step 12: ASSISTANT replies to GM
                    # Ok here u have 4 subactions
                    self.get_answer(self.assistant)

                    if game_status == "abort":
                        break

                    # give generated options to pc
                    # Step 13: GM asks PC
                    # What subaction u wanna do?
                    gm_to_pc_message = self.load_template('resources/prompts/choose_further_subaction.template')
                    self.add_message(self.pc, gm_to_pc_message)

                    # again we should have a function check if game ends imo
                    if game_status == "abort":
                        break

                    # Step 14: PC replies to GM
                    # I wanna make a backflip
                    self.get_answer(self.pc)

                    # Step 15: GM writes to NPC
                    # Your date made a backflip, judge them
                    gm_to_npc_message = self.load_template('resources/prompts/get_npc_response.template')
                    self.add_message(self.pc, gm_to_npc_message)

                    # same as above we should have a function check if game ends imo
                    if game_status == "abort":
                        break

                    # Step 16: NPC responds to GM
                    # This is my judgment
                    self.get_answer(self.npc)
                    self.score[self.current_turn] = get_npc_reaction()

                    # total_sum = sum(self.score.values())
                    # if total_sum < 0:
                    # total_sum and stuff
                    # theoretically we should not make score go to zero wtf

                    # this should work on self.score
                    # fix it to put everything in check_if_cont_game
                    num_neg_values = check_if_continue_game(self.score)
                    if num_neg_values >= 2:
                        break

            # again this should be in game_status true or not, or
            # we should have a function check if game ends imo

            # not last lvl
            if level < self.n_levels:
                try:
                    if game_status == "abort":
                        break
                except:
                    pass

                # if all main and sub actions are through
                # or game is disturbed by penalty ????????
                if game_status == "abort":
                    break

                # #we dont use it for now and it's in the wrong indentation place too
                # # # let npc decide if they like the suggested location
                # # this is happening way above
                # location = locations[game_transcript[-1]["cleaned response"]["NUMBER"]]
                # prompt = next_date(location)
                # prompting(prompt, game_transcript, npc_transcript)
                # pattern = self.pattern_num_rea_res
                # response, game_status = enforce_template(pattern, game_transcript, npc_transcript)
                # if game_status == "abort":
                #     break

                # npc_reaction_value = get_npc_reaction(game_transcript, npc_transcript)
                # npc_reaction_values.append(npc_reaction_value)

                # self.score[self.current_turn] = get_npc_reaction()
                # total_sum = sum(self.score.values())
                # if total_sum < 0:
                # total_sum and stuff
                # theoretically we should not make score go to zero wtf

                # update the score dict for level
                # ap.update({f"lv{level}": affinity_points})

                # check if PC has chance for a next date
                current_ap = len(self.score)
                threshold, _ = scoring_sytem(self.max_mainactions, self.max_subactions, level)

                if current_ap >= threshold:
                    # Step NEXT DATE YES: GM to NPC
                    # You wanna go on next date, react please!
                    gm_to_npc_message = self.load_template('resources/prompts/next_date.template')
                    self.add_message(self.npc, gm_to_npc_message)
                    if game_status == "abort":
                        break

                else:
                    # Step NEXT DATE NO: GM to NPC
                    # You dont wanna go on next date, react please!
                    gm_to_npc_message = self.load_template('resources/prompts/decline_next_date.template')
                    self.add_message(self.npc, gm_to_npc_message)

                    # Step NEXT DATE NO: NPC to GM
                    # I'm dumping u bro
                    self.get_answer(self.npc)

                    # Step END GAME: NPC to GM
                    # Your date dump you, game over
                    gm_to_pc_message = self.load_template('resources/prompts/aborted_game_bc_of_npc.template')
                    self.add_message(self.npc, gm_to_pc_message)
                    break

            else:
                # if we reached end of last level, PC asks NPC if they
                # want to become an official pair

                # get threshold
                number_of_accessed_actions = len(self.score)
                threshold, _ = scoring_sytem(self.max_mainactions, self.max_subactions, level)
                sum_from_whole_game = sum(self.score.values())

                if sum_from_whole_game >= threshold:

                    # Step END YES: GM to NPC
                    # You're happy with dates, what do you say?
                    gm_to_npc_message = self.load_template('resources/prompts/become_couple_yes.template')
                    self.add_message(self.pc, gm_to_npc_message)

                    # Step END YES: NPC to GM
                    # Yes, I wanna date them! I'm super happy
                    self.get_answer(self.npc)

                    # Step END YES: GM to PC
                    # You finished the game and have a cute date, thanks for playin!
                    gm_to_pc_message = self.load_template('resources/prompts/game_end_win.template')
                    self.add_message(self.pc, gm_to_pc_message)

                else:

                    # Step END NO: GM to NPC
                    # You're unhappy with date! Dump them! What do you say?
                    gm_to_npc_message = self.load_template('resources/prompts/become_couple_no.template')
                    self.add_message(self.pc, gm_to_npc_message)

                    # Step END NO: NPC to GM
                    # No, I wanna dump them, they are the worst!
                    self.get_answer(self.npc)

                    # Step END NO: GM to PC
                    # You finished the game but messed up bruv, thanks for playin tho
                    gm_to_pc_message = self.load_template('resources/prompts/game_end_lose.template')
                    self.add_message(self.pc, gm_to_pc_message)

                if game_status == "abort":
                    break


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
            prompt = f"""ERROR: Your given ANSWER doess not follow the given TEMPLATE. Try again. Use the following TEMPLATE: {pattern}

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
    threshold = 0
    if level == 0:
        threshold = 0.25 * max_points
    elif level == 1:
        threshold = 0.50 * max_points
    elif level == 2:
        threshold = 0.75 * max_points

    return threshold, max_points


##########################################################
##########################################################


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
        # max_unpleasant_actions_in_a_row = experiment[max_unpleasant_actions_in_a_row]
        # penalty_for_unpleasant_actions = experiment[penalty_for_unpleasant_actions]
        accumulated_points = 0
        level_threshold, max_points = scoring_sytem(self.max_num_actions, self.max_num_subactions)

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

        pc_successful = False  # need to reset it for calculating episode success
        if total_affinity_points > level_threshold:
            pc_successful = True

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
                self.log_episode_score(BENCH_SCORE, 100 / total_affinity_points / max_points * 100)
            else:
                self.log_episode_score(METRIC_SUCCESS, 0)
                self.log_episode_score(METRIC_LOSE, 1)
                self.log_episode_score(BENCH_SCORE, 0)  # 0 or the same formula as above?


# This is literally all done, we just need to adjust the "players" if single_player or not,
# which it is, but it's a bigger discussion, leave it for now
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
