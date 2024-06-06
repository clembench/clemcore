import os
import json
import clemgame
from clemgame.clemgame import GameInstanceGenerator
from utils import get_random_npcs, get_random_locations
import random

GAME_NAME = 'dating_simulator'
# we will create 10 instances for each experiment; vary this as you wish
N_INSTANCES = 10
# if the generation involves randomness, remember to set a random seed
SEED = 42

logger = clemgame.get_logger(__name__)


class DatingSimGameInstanceGenerator(GameInstanceGenerator):

    def __init__(self, name: str):
        super().__init__(GAME_NAME)
        # self.instances = dict(experiments=list())

    def on_generate(self, ):
        # get resources
        npcs = get_random_npcs("./games/dating_simulator/resources/ex_NPC_sheet.json")[:3]
        locations = get_random_locations("./games/dating_simulator/resources/ex_location.json")

        # initial prompts 
        prompt_pc = self.load_template('resources/initial_prompts/pc.template')
        # prompt_npc = self.load_template('resources/initial_prompts/npc.template')
        # prompt_assistant = self.load_template('resources/initial_prompts/assistant.template')

        """
        for mode in ["easy", "normal", "hard"]:
            
        """

        # some fixed details:

        n_levels = 3  # number of levels
        max_mainactions = 4
        max_subactions = 4

        # # TODO: needs to be put where it belongs
        # levels = {1: "first", 2: "second", 3: "third"} # i.e: NOTE: This is their $level date. Here are the actions chosen by PC so far:
        # prompt_npc = prompt_npc.substitute(character_sheet=character_sheet)
        # prompt_assistant = prompt_assistant.substitute(character_sheet=character_sheet, level=current_level,
        #                                                main_action_1=main_action_1, last_npc_response=last_npc_response,
        #                                                last_npc_reaction=last_npc_reaction)

        # define penalty rules
        penalty_rules = {
            'max_unpleasant_actions_in_a_row': 3,
            'penalty_for_unpleasant_actions': -5
        }

        # create an experiment for each playthrough
        # experiments = {}

        experiment = self.add_experiment(f'Playthrough_{"mode"}')

        experiment['initial_prompt_pc'] = prompt_pc
        # experiment['initial_prompt_npc'] = prompt_npc
        # experiment['initial_prompt_assistant'] = prompt_assistant

        experiment['n_levels'] = n_levels
        experiment['max_mainactions'] = max_mainactions
        experiment['max_subactions'] = max_subactions

        experiment['penalty_rules'] = penalty_rules

        for instance in range(N_INSTANCES):  # what do we need to put here? number of levels?
            game_instance = self.add_game_instance(experiment, instance)
            game_instance["location"] = locations[0]
            game_instance["npcs"] = npcs
            # in case we add more locations, for now it's just one
            #game_instance["location"] = random.choice(locations)
            # for index, row in experiments[experiment_name][0].iterrows:
            # # build first instance
            #     instance = self.add_game_instance(experiment, experiment_id)   
            # # get random levels

            # # create a game instance within the experiment
            #     initial_location = locations[0]

            #     # populate the game instance with its parameters
            #     instance['n_levels'] = n_levels
            #     instance['max_mainactions'] = max_mainactions
            #     instance['max_subactions'] = max_subactions

            #     instance['penalty_rules'] = penalty_rules

            #     instance['initial_location'] = initial_location

            #     instance['initial_prompt_pc'] = prompt_pc
            #     instance['initial_prompt_npc'] = prompt_npc
            #     instance['initial_prompt_assistant'] = prompt_assistant


if __name__ == '__main__':
    random.seed(SEED)
    # always call this, which will actually generate and save the JSON file
    DatingSimGameInstanceGenerator(GAME_NAME).generate()
