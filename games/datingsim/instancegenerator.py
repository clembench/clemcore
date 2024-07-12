"""
Generate instances for the dating simulator game.

Creates files in ./instances
"""
import random
import os
import json
from string import Template
# import tqdm

import clemgame
from clemgame.clemgame import GameInstanceGenerator

from utils import *

GAME_NAME = 'datingsim'
# we will create 10 instances for each experiment; vary this as you wish
N_INSTANCES = 10
# if the generation involves randomness, remember to set a random seed
SEED = 42
ASSISTANT_MODEL = "meta-llama/Llama-3-70b-chat-hf"

logger = clemgame.get_logger(__name__)


class DatingSimInstanceGenerator(GameInstanceGenerator):

    def __init__(self, name: str):
        super().__init__(GAME_NAME)
        # self.instances = dict(experiments=list())

    def load_instances(self):
        return self.load_json("in/instances")

    def on_generate(self):
        # get resources
        # load character sheets which will be our experiments
        # aka need to change the resources where we 
        # predefine the character sheet mash ups
        # example: one where both players are male,
        # one where both players are female, etc.
        # TO DO: prepare the datasets 
        char_sheets = get_random_npcs("games/datingsim/resources/testfile.json")
        # pre define location to keep it open for an experimeent 
        locations = None
        # predefine actions in case that we include them
        actions = None  # number of how often each player can say sth
        n_turns = 25

        # initial prompts for player A and player B
        # TO-DO: Change prompts
        initial_prompt_a = "test1"  # self.load_template('C:/Users/imgey/Desktop/MASTER_POTSDAM/SoSe24/PM2/project/rizzSim/rizzSim/games/datingsim/resources/resources/initial_prompts/initial_pc_prompt.template')
        initial_prompt_b = "test2"  # self.load_template('C:/Users/imgey/Desktop/MASTER_POTSDAM/SoSe24/PM2/project/rizzSim/rizzSim/games/datingsim/resources/resources/initial_prompts/initial_npc_prompt.template')

        """
        maybe we can still leave this in and generate more experiments with
        the amount of character information they get 

        for mode in ["easy", "normal", "hard"]:
        """

        # build th file, one experiment at a time
        for index, experiment in enumerate(char_sheets):
            # create experiment, name is (WILL BE) in the char sheet
            experiment = self.add_experiment(f"Playthrough_{experiment['exp_name']}")
            experiment["n_turns"] = n_turns
            # build n instances for each experiment 
            for game_id in range(N_INSTANCES):
                # set parameters
                # give players the characters - for now random
                charsheet_a = random.choice(char_sheets[index]["chars"])
                charsheet_b = random.choice(char_sheets[index]["chars"])

                if locations is not None:
                    location = random.choice(locations)
                else:
                    location = None

                if actions is not None:
                    set_of_actions = random.choice(actions)
                else:
                    set_of_actions = None

                instance = self.add_game_instance(experiment, game_id)

                # populate game with parameters
                instance["char_a"] = charsheet_a
                instance["char_b"] = charsheet_b
                instance["location"] = location
                instance["set_of_actions"] = set_of_actions

                instance["initial_prompt_player_a"] = initial_prompt_a
                instance["initial_prompt_player_b"] = initial_prompt_b

        # experiment['penalty_rules'] = penalty_rules

        # regex patterns
        # TODO: maybe we can go over these patterns later
        # experiment["pattern_sex_age"] = r"^SEX:\s*(\w+)\s*AGE:\s*(\d\d)$"
        # experiment["pattern_f_number"] = r"^NUMBER:\s*(.+?)$"
        # experiment["pattern_num_r"] = r"^NUMBER: (\d)$"
        # experiment["pattern_num_reason"] = r"NUMBER:\s*(.+?)\s*REASON:\s*(.+)$"
        # experiment["pattern_num_rea_res"] = r"NUMBER:\s*(.+?)\s*REASON:\s*(.+)\s*RESPONSE:\s*(.+)$"
        # experiment["pattern_response"] = r"RESPONSE:\s*(.+)$"

        # THIS is the new pattern basically
        # experiment["pattern_response_players"] = r"REASON:\s*(.+?)\s*SENTIMENT:\s*(.+)\s*RESPONSE:\s*(.+)$"


if __name__ == '__main__':
    random.seed(SEED)
    # always call this, which will actually generate and save the JSON file
    DatingSimInstanceGenerator(GAME_NAME).generate()
