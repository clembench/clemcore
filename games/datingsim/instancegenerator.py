"""
Generate instances for the dating simulator game.

Creates files in ./instances
"""
import random
import os
import json
from string import Template
import tqdm

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
        npcs = get_random_npcs("./games/dating_simulator/resources/ex_NPC_sheet.json")[:3]
        locations = get_random_locations("./games/dating_simulator/resources/ex_location.json")

        # initial prompts 
        prompt_pc = self.load_template('./resources/initial_prompts/initial_pc_prompt.template')
        prompt_npc = self.load_template('./resources/initial_prompts/initial_npc_prompt.template')
        prompt_assistant = self.load_template('./resources/initial_prompts/initial_assistant_prompt.template')
        
        """
        for mode in ["easy", "normal", "hard"]:
            
        """

        # some fixed details:
        n_levels = 2  # number of levels
        max_mainactions = 2
        max_subactions = 2

        # # TODO: work on these levels
        # levels = {1: "first", 2: "second", 3: "third"} # i.e: NOTE: This is their $level date. Here are the actions chosen by PC so far:
        
        # TODO: put these in the game-flow as the variables need to be replaced according to the PC and NPC decisions
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
        mode = "easy"
        experiment = self.add_experiment(f'Playthrough_{mode}')

        experiment['initial_prompt_pc'] = prompt_pc
        experiment['initial_prompt_npc'] = prompt_npc
        experiment['initial_prompt_assistant'] = prompt_assistant

        # TODO: add regex patterns here I guess?

        experiment['n_levels'] = n_levels
        experiment['max_mainactions'] = max_mainactions
        experiment['max_subactions'] = max_subactions

        experiment['penalty_rules'] = penalty_rules

        # regex patterns
        # TODO: maybe we can go over these patterns later
        experiment["pattern_sex_age"] = "SEX:\\s*(\\w+)\\s*AGE:\\s*(\\d\\d)"
        experiment["pattern_f_number"] = "NUMBER:\\s*(.+?)"
        experiment["pattern_num_r"] = "NUMBER: (\\d)"
        experiment["pattern_num_reason"] = "NUMBER:\\s*(.+?)\\s*REASON:\\s*(.+)"
        experiment["pattern_num_rea_res"] = "NUMBER:\\s*(.+?)\\s*REASON:\\s*(.+)\\s*RESPONSE:\\s*(.+)"
        experiment["pattern_response"] = "'RESPONSE:\\s*(.+)"
        
        experiment["location"] = locations[0]
        experiment["npcs"] = npcs

        main_actions = experiment["location"]["MAIN-ACTIONS"]

        main_actions_data = []

        for main_action in tqdm.tqdm(main_actions, desc="Generating subactions"):
            main_action_data = {
                "main_action": main_action,
                "npc_subactions": {}
                }

            for npc in experiment["npcs"]:
                npc_name = npc["NAME"]
                character_sheet = prompt_char_sheets(npc)
                prompt_assistant_modified = prompt_assistant.replace('$character_sheet', character_sheet)\
                                                    .replace('$main_action', main_action)
                subactions = get_correct_subactions(ASSISTANT_MODEL, prompt_assistant_modified)
                main_action_data["npc_subactions"][npc_name] = subactions
            
            main_actions_data.append(main_action_data)
        
        experiment["location"]["MAIN-ACTIONS"] = main_actions_data

        for instance in range(N_INSTANCES):  # what do we need to put here? number of levels?
            game_instance = self.add_game_instance(experiment, instance)

            # !! realized we do not have anything game_instance specific as npcs and locations are the same for every instance

            # in case we add more locations, for now it's just one
            #game_instance["location"] = random.choice(locations)

if __name__ == '__main__':
    random.seed(SEED)
    # always call this, which will actually generate and save the JSON file
    DatingSimInstanceGenerator(GAME_NAME).generate()
