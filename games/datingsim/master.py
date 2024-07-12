import copy
import re
from typing import Dict, List
from string import Template
import numpy as np

from backends import Model
from clemgame import get_logger
from clemgame.metrics import METRIC_ABORTED, METRIC_SUCCESS, METRIC_LOSE, METRIC_REQUEST_COUNT, \
    METRIC_REQUEST_COUNT_VIOLATED, METRIC_REQUEST_COUNT_PARSED, METRIC_REQUEST_SUCCESS, BENCH_SCORE
from clemgame.clemgame import GameMaster, GameBenchmark, GameScorer, DialogueGameMaster
from games.datingsim.player import *

GAME_NAME = "datingsim"
logger = get_logger(__name__)


class DatingSimGameMaster(GameMaster):
    def __init__(self, game_name: str, experiment: Dict, player_models: List[Model]):
        super().__init__(game_name, experiment, player_models)

        # regex patterns here

        self.name = experiment['name']
        # self.penalty_rules = experiment['penalty_rules']
        self.current_turn = 0
        self.n_turns = experiment['n_turns']

        # boolean to see game status
        self.game_status = True
        # check for invalid responses 
        self.invalid_response = False
        # self.score = {}  # this was affinity points

        self.model_a = player_models[0]
        self.model_b = player_models[1]

        self.player_model_names = [
            player_model.get_name() for player_model in player_models
        ]

    def add_player(self, player: Player) -> None:
        idx = len(self.player_model_names)
        # player writer and responder
        if idx == 0:
            player.descriptor = f"Writer"
            self.player_model_names[idx] = player.descriptor
        elif idx == 1:
            player.descriptor = f"Responder"
            self.player_model_names[idx] = player.descriptor

    def add_message(self, player: Player, utterance: str, role="user") -> None:
        # write function, this needs to be merged with what is in GameMaster of dating_simulator/master.py
        player.history.append({'role': role, 'content': utterance})
        action = {'type': 'send message', 'content': utterance}
        self.log_event(from_='GM', to=str(player), action=action)

    def get_answer(self, player: Player, restart_history=True) -> str:
        # this needs to be merged with what is in GameMaster of dating_simulator/master.py
        prompt, raw_answer, answer = player(player.history, self.current_turn)
        action = {'type': 'get message', 'content': answer}
        self.log_event(from_=str(player), to="GM", action=action,
                       call=(copy.deepcopy(prompt), raw_answer))
        # figure out how to add to history after parsing
        # this is a suggestion from Nic, not sure how to solve it yet
        # if restart_history == True:
        #     player.history = []
        return answer

    # def get_answer(self, player: Player, restart_history=False) -> str:
    #     # this needs to be merged with what is in GameMaster of dating_simulator/master.py
    #     print(f"Debug: player.history before generating response: {player.history}")
    #     if not player.history:
    #         print("Error: player history is empty!")
    #         return ""
    #
    #     prompt, raw_answer, answer = player(player.history, self.current_turn)
    #     action = {'type': 'get message', 'content': answer}
    #     self.log_event(from_=str(player), to="GM", action=action,
    #                    call=(copy.deepcopy(prompt), raw_answer))
    #     # figure out how to add to history after parsing
    #     # this is a suggestion from Nic, not sure how to solve it yet
    #     # if restart_history:
    #     #     player.history = []
    #     return answer

    def setup(self, **game_instance) -> None:
        """
        The function sets up the game with the given game instance configuration.
        """
        logger.info("Setup")

        # import game instances
        self.game_instance = game_instance
        self.game_id = self.game_instance["game_id"]

        # create player/s here
        self.player_a = Dater(self.model_a, "Writer")
        self.player_b = Dater(self.model_b, "Responder")

        self.add_player(self.player_a)
        self.add_player(self.player_b)
        self.initial_prompt_player_a = self.game_instance["initial_prompt_player_a"]
        self.initial_prompt_player_b = self.game_instance["initial_prompt_player_b"]
        self.location = self.game_instance['location']
        self.log_players({
            "GM": "Game master for datingsim",
            "Player_1": self.player_models[0].get_name(),
            "Player_2": self.player_models[1].get_name()}
        )

    # This needs to be revised again
    # def validate_response(self, player: Player, utterance: str, pattern: str, repetition: False) -> bool:
    #     """
    #     Function to check if the given answer is in the valid
    #     format.
    #     If yes, the game continues.
    #     If no, the game is aborted.
    #     If repetitions are allowed, the role can re-try n times.
    #     If it fails again, the game will be aborted.
    #     """
    #     match = re.search(pattern, utterance)
    #
    #     if not repetition:
    #         if match:
    #             self.game_status = True
    #         else:
    #             self.game_status = False
    #
    #     else:
    #         tries_to_genrate_correct_output = 0
    #         while True:
    #             if match:
    #                 self.game_status = True
    #                 break
    #             elif tries_to_genrate_correct_output > 2:
    #                 self.game_status = False
    #                 break
    #             elif not match:
    #                 # Handle cases where the output doesn't match the template
    #                 tries_to_genrate_correct_output += 1
    #                 # need to include reprompt here, not sure if this is the
    #                 # correct method though
    #                 DialogueGameMaster.prompt(player=player, is_reprompt=True)
    #                 break

    # TO DO: include checking every response of LLMs if they are following the pattern
    def play(self):

        self.log_next_turn()


        # Step 1a
        # GM to P1
        # Provides character sheet
        # initial prompt is (same for both): game description, goal, game rules, char-sheet
        # write first ("you are this person (char sheet A) and you write to another person (char sheet B)")
        self.add_message(self.player_a, utterance=self.initial_prompt_player_a)

        # P1 to GM
        # Writes a beginning message to P2
        self.get_answer(self.player_a)

        self.log_next_turn()
        self.current_turn += 1

        # Step 1b
        # GM to P2
        # Provides character sheet
        # initial prompt is (same for both): game description, goal, game rules, char-sheet
        # get written to ("you are this person (char sheet B) and another person (char sheet A) writes to you this *mess*")
        # + reply to P1
        self.add_message(self.player_b, utterance=self.initial_prompt_player_b)

        # P2 to GM
        # Answers begin message to P1
        self.get_answer(self.player_b)

        self.log_next_turn()
        self.current_turn += 1

        while self.current_turn - 2 < self.n_turns:
            # Step 2,4,6...n-1
            # GM to P1
            # Gives message from P2 to P1
            self.add_message(self.player_a, utterance=self.player_b.history[-1])

            # P1 to GM
            # Answers to P2's message
            self.get_answer(self.player_a)
            self.log_next_turn()
            self.current_turn += 1

            # Step 3,5,7...n
            # GM to P2
            # Gives message from P1 to P2
            self.add_message(self.player_b, utterance=self.player_a.history[-1])

            # P2 to GM
            # Answers to P1's message
            self.get_answer(self.player_b)
            self.log_next_turn()
            self.current_turn += 1

    print("end")


# This needs to be adjusted or removed completely (replaced)
# def enforce_template(pattern, game_transcript, specific_transcript):
#     """
#     Function which checks the given answer of the LLMS.
#     If they follow the given template, all gucci.
#     If not, generate new prompt where we enforce the
#     usage of the template
#     """
#
#     tries_to_genrate_correct_output = 0
#
#     while True:
#
#         response = game_transcript[-1]["content"]
#
#         # Search for the pattern in the output
#         match = re.search(pattern, response, re.DOTALL)
#
#         if match:
#             game_status = "ongoing"
#             break
#         elif tries_to_genrate_correct_output > 2:
#             game_status = "abort"
#             print(game_status)
#             break
#         elif not match:
#             # Handle cases where the output doesn't match the template
#             prompt = f"""ERROR: Your given ANSWER doess not follow the given TEMPLATE. Try again. Use the following TEMPLATE: {pattern}
#
# DO NOT APOLOGIZE OR WHATEVER. JUST USE THE PATTERN"""
#             tries_to_genrate_correct_output += 1
#             prompting(prompt, game_transcript, specific_transcript)
#
#     return response, game_status


# this needs to be completely changed according to our new rules when the game ends
# def check_if_continue_game(npc_reaction_values):
#     """
#     Function which checks the number of negative
#     responses of the NPC in a row.
#     """
#     if len(npc_reaction_values) >= 2:
#
#         # count negative values:
#         num_neg_values = 0
#         for value in npc_reaction_values[-1:-3]:
#             if value < 0:
#                 num_neg_values += 1
#         return num_neg_values
#
#     else:
#         num_neg_values = 0
#         return num_neg_values


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
        # level_threshold, max_points = scoring_sytem(self.max_num_actions, self.max_num_subactions)
        level_threshold = 1
        max_points = 5
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


##########################################################
##########################################################


class DatingSimGameBenchmark(GameBenchmark):

    def __init__(self):
        super().__init__(GAME_NAME)

    # defines whether the game is single player or not
    def is_single_player(self):
        return False

    # add a description of your game
    def get_description(self):
        return "A game where LLMs date"

    def create_game_master(
            self, experiment: Dict, player_models: List[Model]
    ) -> GameMaster:
        return DatingSimGameMaster(game_name="datingsim", experiment=experiment, player_models=player_models)

    def create_game_scorer(self, experiment: Dict, game_instance: Dict) -> GameScorer:
        return DatingSimGameScorer(experiment, game_instance)
