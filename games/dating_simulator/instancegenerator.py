import os
import json
import clemgame
from clemgame.clemgame import GameInstanceGenerator
from utils import get_random_npcs, get_random_locations
import random
from pc_prompts import *


GAME_NAME = 'dating_simulator'
# if the generation involves randomness, remember to set a random seed
SEED = 42

class GameInstanceGenerator(GameResourceLocator):

    # include the self.load_template() and self.load_file() for initial prompt and stuff 
    
    def __init__(self, name: str):
        super().__init__(rizzSims)
        self.instances = dict(experiments=list())
    
    def on_generate(self, npc_sheets, location_sheets):

        # some fixed details:
        
        n_levels = 3 # number of levels
        max_mainactions = 4
        max_subactions = 4

        # get resources
        npcs = get_random_npcs(npc_sheets)
        locations = get_random_locations(location_sheets)

        # initial prompts 
        prompt_pc = self.load_template('resources/initial_prompts/initial_prompt_pc.template')
        prompt_npc = self.load_template('resources/initial_prompts/initial_prompt_npc.template')

        # define penalty rules
        penalty_rules = {
            'max_unpleasant_actions_in_a_row': 3,
            'penalty_for_unpleasant_actions': -5
        }

        # create an experiment for each playthrough
        experiment = self.add_experiment(f'Playthrough_{experiment_id}')

        # build first instance

        # get random levels

        # create a game instance within the experiment
        instance = self.add_game_instance(experiment, experiment_id)

        initial_location = locations[0]

        # populate the game instance with its parameters
        instance['n_levels'] = n_levels
        instance['max_mainactions'] = max_mainactions
        instance['max_subactions'] = max_subactions

        instance['penalty_rules'] = penalty_rules

        instance['initial_location'] = initial_location
        
        instance['initial_prompt_pc'] = prompt_pc
        instance['initial_prompt_npc'] = prompt_npc




if __name__ == '__main__':
    random.seed(SEED)
    # always call this, which will actually generate and save the JSON file
    DatingSimulatorGameInstanceGenerator().generate()
