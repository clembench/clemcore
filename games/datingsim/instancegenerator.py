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
# from rizzSim.games.datingsim.utils import *

GAME_NAME = 'datingsim'
# we will create 10 instances for each experiment; vary this as you wish
N_INSTANCES = 3
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
        max_retries = 3

        # initial prompts for player A and player B
        # TO-DO: Change prompts
        initial_prompt_a = self.load_template('resources/initial_prompts/initialprompt_playerA.template') 
        initial_prompt_b = self.load_template('resources/initial_prompts/initialprompt_playerB.template')

        further_prompts = self.load_template('resources/prompts/further_prompts.template')
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
            experiment["max_retries"] = max_retries
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

                instance["initial_prompt_player_a"] = initial_prompt_a.replace("$charsheet_a", str(instance["char_a"])).replace("charsheet_b", str(instance["char_b"]))
                instance["initial_prompt_player_b"] = initial_prompt_b.replace("$charsheet_a", str(instance["char_a"])).replace("charsheet_b", str(instance["char_b"]))
                instance["further_prompts"] = further_prompts


        # THIS is the new pattern basically
        # experiment["pattern_response_players"] = r"REASON:\s*(.+?)\s*SENTIMENT:\s*(.+)\s*RESPONSE:\s*(.+)$"


if __name__ == '__main__':
    random.seed(SEED)
    # always call this, which will actually generate and save the JSON file
    DatingSimInstanceGenerator(GAME_NAME).generate()
