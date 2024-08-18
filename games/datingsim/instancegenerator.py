"""
Generate instances for the dating simulator game.

Creates files in ./instances
"""
import random
from copy import deepcopy
import os
import json
from string import Template
# import tqdm

import clemgame
from clemgame.clemgame import GameInstanceGenerator

# from utils import *
from games.datingsim.utils import *

GAME_NAME = 'datingsim'
# we will create 10 instances for each experiment; vary this as you wish
N_INSTANCES = 13
# if the generation involves randomness, remember to set a random seed
SEED = 42

# EXPERIMENTS = ["easy", 
#                "medium", 
#                "difficult", 
#                "easy-reprompt",
#                "medium-reprompt", 
#                "difficult-reprompt",
#                "easy-themselves",
#                "medium-themselves",
#                "difficult-themselves",
#                "easy-same_gender",
#                "medium-same_gender",
#                "difficult-same_gender",
#                "easy-more_turns",
#                "medium-more_turns",
#                "difficult-more_turns",
#                "easy-less_turns",
#                "medium-less_turns",
#                "difficult-less_turns"]

EXPERIMENTS = ["easy", 
               "medium", 
               "difficult", 
               "medium-themselves",
               "medium-same_gender",
               "medium-more_turns",
               "medium-less_turns"]

logger = clemgame.get_logger(__name__)


class DatingSimInstanceGenerator(GameInstanceGenerator):

    def __init__(self):
        super().__init__(GAME_NAME)

    def load_instances(self):
        return self.load_json("in/instances")

    def on_generate(self):
        
        # get resources
        char_sheets = get_random_npcs(r'games\datingsim\resources\charactersheets.json')
        # number of how often each player can say sth
        n_turns = 15
        max_retries = 2

        # load prompts
        initial_prompt_a = self.load_template('resources/initial_prompts/initialprompt_playerA.template') 
        initial_prompt_b = self.load_template('resources/initial_prompts/initialprompt_playerB.template')

        further_prompts = self.load_template('resources/prompts/further_prompts.template')

        reprompt_prompt = self.load_template('resources/prompts/reprompt.template')

        for topic in EXPERIMENTS:

            if topic == "easy":

                experiment = self.add_experiment(topic)

                experiment["n_turns"] = n_turns
                experiment["max_retries"] = max_retries
                experiment["re_prompt_allowed"] = False

                for game_id in range(N_INSTANCES):

                    # save charactersheets for players
                    char_player_a = random.choice(char_sheets)
                    char_player_b = random.choice(char_sheets)

                    instance = self.add_game_instance(experiment, game_id)

                    # populate game with parameters
                    instance["char_a_a"] = char_player_a
                    instance["char_a_b"] = char_player_b
                    instance["char_b_a"] = char_player_a
                    instance["char_b_b"] = char_player_b

                    instance["initial_prompt_player_a"] = initial_prompt_a.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_a_a", str(instance["char_a_a"])).replace("$charsheet_a_b", str(instance["char_a_b"]))
                    instance["initial_prompt_player_b"] = initial_prompt_b.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_b_b", str(instance["char_b_b"])).replace("$charsheet_b_a", str(instance["char_b_a"]))
                    instance["further_prompts"] = further_prompts
                    instance["reprompt_prompt"] = reprompt_prompt

            elif topic == "medium":

                experiment = self.add_experiment(topic)

                experiment["n_turns"] = n_turns
                experiment["max_retries"] = max_retries
                experiment["re_prompt_allowed"] = False

                for game_id in range(N_INSTANCES):

                    # save charactersheets for players
                    char_player_a = random.choice(char_sheets)
                    char_player_b = random.choice(char_sheets)

                    instance = self.add_game_instance(experiment, game_id)

                    # populate game with parameters
                    # info player a has about themselves
                    instance["char_a_a"] = deepcopy(char_player_a)
                    
                    # info player a has about player b
                    instance["char_a_b"] = deepcopy(char_player_b)
                    instance["char_a_b"].pop("HOBBIES")
                    instance["char_a_b"].pop("LIKES")
                    instance["char_a_b"].pop("DISLIKES")
                    
                    # info player b has about player a
                    instance["char_b_a"] = deepcopy(char_player_a)
                    instance["char_b_a"].pop("HOBBIES")
                    instance["char_b_a"].pop("LIKES")
                    instance["char_b_a"].pop("DISLIKES")
                    
                    # info player b has about themselves 
                    instance["char_b_b"] = deepcopy(char_player_b)

                    instance["initial_prompt_player_a"] = initial_prompt_a.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_a_a", str(instance["char_a_a"])).replace("charsheet_a_b", str(instance["char_a_b"]))
                    instance["initial_prompt_player_b"] = initial_prompt_b.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_b_b", str(instance["char_b_b"])).replace("charsheet_b_a", str(instance["char_b_a"]))
                    instance["further_prompts"] = further_prompts
                    instance["reprompt_prompt"] = reprompt_prompt

            elif topic == "difficult":

                experiment = self.add_experiment(topic)

                experiment["n_turns"] = n_turns
                experiment["max_retries"] = max_retries
                experiment["re_prompt_allowed"] = False

                for game_id in range(N_INSTANCES):

                    # save charactersheets for players
                    char_player_a = random.choice(char_sheets)
                    char_player_b = random.choice(char_sheets)

                    instance = self.add_game_instance(experiment, game_id)

                    # populate game with parameters
                    # info player a has about themselves
                    instance["char_a_a"] = deepcopy(char_player_a)
                    
                    # info player a has about player b - only leave name and summary 
                    instance["char_a_b"] = deepcopy(char_player_b)
                    instance["char_a_b"].pop("HOBBIES")
                    instance["char_a_b"].pop("LIKES")
                    instance["char_a_b"].pop("DISLIKES")
                    instance["char_a_b"].pop("AGE")
                    instance["char_a_b"].pop("APPEARANCE")
                    instance["char_a_b"].pop("OCCUPATION")
                    instance["char_a_b"].pop("GENDER")
                    
                    # info player b has about player a
                    instance["char_b_a"] = deepcopy(char_player_a)
                    instance["char_b_a"].pop("HOBBIES")
                    instance["char_b_a"].pop("LIKES")
                    instance["char_b_a"].pop("DISLIKES")
                    instance["char_b_a"].pop("AGE")
                    instance["char_b_a"].pop("APPEARANCE")
                    instance["char_b_a"].pop("OCCUPATION")
                    instance["char_b_a"].pop("GENDER")
                    
                    # info player b has about themselves 
                    instance["char_b_b"] = deepcopy(char_player_b)

                    instance["initial_prompt_player_a"] = initial_prompt_a.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_a_a", str(instance["char_a_a"])).replace("charsheet_a_b", str(instance["char_a_b"]))
                    instance["initial_prompt_player_b"] = initial_prompt_b.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_b_b", str(instance["char_b_b"])).replace("charsheet_b_a", str(instance["char_b_a"]))
                    instance["further_prompts"] = further_prompts
                    instance["reprompt_prompt"] = reprompt_prompt

            elif topic == "easy-reprompt":
                experiment = self.add_experiment(topic)

                experiment["n_turns"] = n_turns
                experiment["max_retries"] = max_retries
                experiment["re_prompt_allowed"] = True

                for game_id in range(N_INSTANCES):

                    # save charactersheets for players
                    char_player_a = random.choice(char_sheets)
                    char_player_b = random.choice(char_sheets)

                    instance = self.add_game_instance(experiment, game_id)

                    # populate game with parameters
                    instance["char_a_a"] = char_player_a
                    instance["char_a_b"] = char_player_b
                    instance["char_b_a"] = char_player_a
                    instance["char_b_b"] = char_player_b

                    instance["initial_prompt_player_a"] = initial_prompt_a.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_a_a", str(instance["char_a_a"])).replace("charsheet_a_b", str(instance["char_a_b"]))
                    instance["initial_prompt_player_b"] = initial_prompt_b.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_b_b", str(instance["char_b_b"])).replace("charsheet_b_a", str(instance["char_b_a"]))
                    instance["further_prompts"] = further_prompts
                    instance["reprompt_prompt"] = reprompt_prompt

            elif topic == "medium-reprompt":
                experiment = self.add_experiment(topic)

                experiment["n_turns"] = n_turns
                experiment["max_retries"] = max_retries
                experiment["re_prompt_allowed"] = True

                for game_id in range(N_INSTANCES):

                    # save charactersheets for players
                    char_player_a = random.choice(char_sheets)
                    char_player_b = random.choice(char_sheets)

                    instance = self.add_game_instance(experiment, game_id)

                    # populate game with parameters
                    # info player a has about themselves
                    instance["char_a_a"] = deepcopy(char_player_a)
                    
                    # info player a has about player b
                    instance["char_a_b"] = deepcopy(char_player_b)
                    instance["char_a_b"].pop("HOBBIES")
                    instance["char_a_b"].pop("LIKES")
                    instance["char_a_b"].pop("DISLIKES")
                    
                    # info player b has about player a
                    instance["char_b_a"] = deepcopy(char_player_a)
                    instance["char_b_a"].pop("HOBBIES")
                    instance["char_b_a"].pop("LIKES")
                    instance["char_b_a"].pop("DISLIKES")
                    
                    # info player b has about themselves 
                    instance["char_b_b"] = deepcopy(char_player_b)

                    instance["initial_prompt_player_a"] = initial_prompt_a.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_a_a", str(instance["char_a_a"])).replace("charsheet_a_b", str(instance["char_a_b"]))
                    instance["initial_prompt_player_b"] = initial_prompt_b.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_b_b", str(instance["char_b_b"])).replace("charsheet_b_a", str(instance["char_b_a"]))
                    instance["further_prompts"] = further_prompts
                    instance["reprompt_prompt"] = reprompt_prompt

            elif topic == "difficult-reprompt":
                experiment = self.add_experiment(topic)

                experiment["n_turns"] = n_turns
                experiment["max_retries"] = max_retries
                experiment["re_prompt_allowed"] = False

                for game_id in range(N_INSTANCES):

                    # save charactersheets for players
                    char_player_a = random.choice(char_sheets)
                    char_player_b = random.choice(char_sheets)

                    instance = self.add_game_instance(experiment, game_id)

                    # populate game with parameters
                    # info player a has about themselves
                    instance["char_a_a"] = deepcopy(char_player_a)
                    
                    # info player a has about player b - only leave name and summary 
                    instance["char_a_b"] = deepcopy(char_player_b)
                    instance["char_a_b"].pop("HOBBIES")
                    instance["char_a_b"].pop("LIKES")
                    instance["char_a_b"].pop("DISLIKES")
                    instance["char_a_b"].pop("AGE")
                    instance["char_a_b"].pop("APPEARANCE")
                    instance["char_a_b"].pop("OCCUPATION")
                    instance["char_a_b"].pop("GENDER")
                    
                    # info player b has about player a
                    instance["char_b_a"] = deepcopy(char_player_a)
                    instance["char_b_a"].pop("HOBBIES")
                    instance["char_b_a"].pop("LIKES")
                    instance["char_b_a"].pop("DISLIKES")
                    instance["char_b_a"].pop("AGE")
                    instance["char_b_a"].pop("APPEARANCE")
                    instance["char_b_a"].pop("OCCUPATION")
                    instance["char_b_a"].pop("GENDER")
                    
                    # info player b has about themselves 
                    instance["char_b_b"] = deepcopy(char_player_b)

                    instance["initial_prompt_player_a"] = initial_prompt_a.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_a_a", str(instance["char_a_a"])).replace("charsheet_a_b", str(instance["char_a_b"]))
                    instance["initial_prompt_player_b"] = initial_prompt_b.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_b_b", str(instance["char_b_b"])).replace("charsheet_b_a", str(instance["char_b_a"]))
                    instance["further_prompts"] = further_prompts
                    instance["reprompt_prompt"] = reprompt_prompt

            elif topic == "easy-themselves":
                experiment = self.add_experiment(topic)

                experiment["n_turns"] = n_turns
                experiment["max_retries"] = max_retries
                experiment["re_prompt_allowed"] = False

                for game_id in range(N_INSTANCES):

                    # save charactersheets for players
                    char_player_a = random.choice(char_sheets)

                    instance = self.add_game_instance(experiment, game_id)

                    # populate game with parameters
                    instance["char_a_a"] = char_player_a
                    instance["char_a_b"] = char_player_a
                    instance["char_b_a"] = char_player_a
                    instance["char_b_b"] = char_player_a

                    instance["initial_prompt_player_a"] = initial_prompt_a.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_a_a", str(instance["char_a_a"])).replace("charsheet_a_b", str(instance["char_a_b"]))
                    instance["initial_prompt_player_b"] = initial_prompt_b.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_b_b", str(instance["char_b_b"])).replace("charsheet_b_a", str(instance["char_b_a"]))
                    instance["further_prompts"] = further_prompts
                    instance["reprompt_prompt"] = reprompt_prompt

            elif topic == "medium-themselves":
                experiment = self.add_experiment(topic)

                experiment["n_turns"] = n_turns
                experiment["max_retries"] = max_retries
                experiment["re_prompt_allowed"] = False

                for game_id in range(N_INSTANCES):

                    # save charactersheets for players
                    char_player_a = random.choice(char_sheets)

                    instance = self.add_game_instance(experiment, game_id)

                    # populate game with parameters
                    # info player a has about themselves
                    instance["char_a_a"] = deepcopy(char_player_a)
                    
                    # info player a has about player b
                    instance["char_a_b"] = deepcopy(char_player_a)
                    instance["char_a_b"].pop("HOBBIES")
                    instance["char_a_b"].pop("LIKES")
                    instance["char_a_b"].pop("DISLIKES")
                    
                    # info player b has about player a
                    instance["char_b_a"] = deepcopy(char_player_a)
                    instance["char_b_a"].pop("HOBBIES")
                    instance["char_b_a"].pop("LIKES")
                    instance["char_b_a"].pop("DISLIKES")
                    
                    # info player b has about themselves 
                    instance["char_b_b"] = deepcopy(char_player_a)

                    instance["initial_prompt_player_a"] = initial_prompt_a.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_a_a", str(instance["char_a_a"])).replace("charsheet_a_b", str(instance["char_a_b"]))
                    instance["initial_prompt_player_b"] = initial_prompt_b.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_b_b", str(instance["char_b_b"])).replace("charsheet_b_a", str(instance["char_b_a"]))
                    instance["further_prompts"] = further_prompts
                    instance["reprompt_prompt"] = reprompt_prompt

            elif topic == "difficult-themselves":
                experiment = self.add_experiment(topic)

                experiment["n_turns"] = n_turns
                experiment["max_retries"] = max_retries
                experiment["re_prompt_allowed"] = False

                for game_id in range(N_INSTANCES):

                    # save charactersheets for players
                    char_player_a = random.choice(char_sheets)
                    char_player_b = random.choice(char_sheets)

                    instance = self.add_game_instance(experiment, game_id)

                    # populate game with parameters
                    # info player a has about themselves
                    instance["char_a_a"] = deepcopy(char_player_a)
                    
                    # info player a has about player b - only leave name and summary 
                    instance["char_a_b"] = deepcopy(char_player_a)
                    instance["char_a_b"].pop("HOBBIES")
                    instance["char_a_b"].pop("LIKES")
                    instance["char_a_b"].pop("DISLIKES")
                    instance["char_a_b"].pop("AGE")
                    instance["char_a_b"].pop("APPEARANCE")
                    instance["char_a_b"].pop("OCCUPATION")
                    instance["char_a_b"].pop("GENDER")
                    
                    # info player b has about player a
                    instance["char_b_a"] = deepcopy(char_player_a)
                    instance["char_b_a"].pop("HOBBIES")
                    instance["char_b_a"].pop("LIKES")
                    instance["char_b_a"].pop("DISLIKES")
                    instance["char_b_a"].pop("AGE")
                    instance["char_b_a"].pop("APPEARANCE")
                    instance["char_b_a"].pop("OCCUPATION")
                    instance["char_b_a"].pop("GENDER")
                    
                    # info player b has about themselves 
                    instance["char_b_b"] = deepcopy(char_player_a)

                    instance["initial_prompt_player_a"] = initial_prompt_a.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_a_a", str(instance["char_a_a"])).replace("charsheet_a_b", str(instance["char_a_b"]))
                    instance["initial_prompt_player_b"] = initial_prompt_b.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_b_b", str(instance["char_b_b"])).replace("charsheet_b_a", str(instance["char_b_a"]))
                    instance["further_prompts"] = further_prompts
                    instance["reprompt_prompt"] = reprompt_prompt

            elif topic == "easy-same_gender":
                experiment = self.add_experiment(topic)

                experiment["n_turns"] = n_turns
                experiment["max_retries"] = max_retries
                experiment["re_prompt_allowed"] = False

                for game_id in range(N_INSTANCES):

                    # save charactersheets for players
                    char_player_a = random.choice(char_sheets)
                    char_a_gender = char_player_a["GENDER"]

                    char_b_gender = None

                    # check the gender of player b, if it is not, then
                    # pick as(s) often a new character until the gender
                    # matches 
                    while True:
                        if char_b_gender == char_a_gender:
                            break
                        else:
                            char_player_b = random.choice(char_sheets)
                            char_b_gender = char_player_b["GENDER"]

                    instance = self.add_game_instance(experiment, game_id)

                    # populate game with parameters
                    instance["char_a_a"] = char_player_a
                    instance["char_a_b"] = char_player_b
                    instance["char_b_a"] = char_player_a
                    instance["char_b_b"] = char_player_b

                    instance["initial_prompt_player_a"] = initial_prompt_a.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_a_a", str(instance["char_a_a"])).replace("charsheet_a_b", str(instance["char_a_b"]))
                    instance["initial_prompt_player_b"] = initial_prompt_b.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_b_b", str(instance["char_b_b"])).replace("charsheet_b_a", str(instance["char_b_a"]))
                    instance["further_prompts"] = further_prompts
                    instance["reprompt_prompt"] = reprompt_prompt

            elif topic == "medium-same_gender":
                
                experiment = self.add_experiment(topic)

                experiment["n_turns"] = n_turns
                experiment["max_retries"] = max_retries
                experiment["re_prompt_allowed"] = False

                for game_id in range(N_INSTANCES):

                    # save charactersheets for players
                    char_player_a = random.choice(char_sheets)
                    char_a_gender = char_player_a["GENDER"]

                    char_b_gender = None

                    # check the gender of player b, if it is not, then
                    # pick as(s) often a new character until the gender
                    # matches 
                    while True:
                        if char_b_gender == char_a_gender:
                            break
                        else:
                            char_player_b = random.choice(char_sheets)
                            char_b_gender = char_player_b["GENDER"]

                    instance = self.add_game_instance(experiment, game_id)

                    # populate game with parameters
                    instance["char_a_a"] = deepcopy(char_player_a)
                    
                    # info player a has about player b
                    instance["char_a_b"] = deepcopy(char_player_b)
                    instance["char_a_b"].pop("HOBBIES")
                    instance["char_a_b"].pop("LIKES")
                    instance["char_a_b"].pop("DISLIKES")
                    
                    # info player b has about player a
                    instance["char_b_a"] = deepcopy(char_player_a)
                    instance["char_b_a"].pop("HOBBIES")
                    instance["char_b_a"].pop("LIKES")
                    instance["char_b_a"].pop("DISLIKES")
                    
                    # info player b has about themselves 
                    instance["char_b_b"] = deepcopy(char_player_b)

                    instance["initial_prompt_player_a"] = initial_prompt_a.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_a_a", str(instance["char_a_a"])).replace("charsheet_a_b", str(instance["char_a_b"]))
                    instance["initial_prompt_player_b"] = initial_prompt_b.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_b_b", str(instance["char_b_b"])).replace("charsheet_b_a", str(instance["char_b_a"]))
                    instance["further_prompts"] = further_prompts
                    instance["reprompt_prompt"] = reprompt_prompt
                
            elif topic == "difficult-same_gender":
                
                experiment = self.add_experiment(topic)

                experiment["n_turns"] = n_turns
                experiment["max_retries"] = max_retries
                experiment["re_prompt_allowed"] = False

                for game_id in range(N_INSTANCES):

                    # save charactersheets for players
                    char_player_a = random.choice(char_sheets)
                    char_a_gender = char_player_a["GENDER"]

                    char_b_gender = None

                    # check the gender of player b, if it is not, then
                    # pick as(s) often a new character until the gender
                    # matches 
                    while True:
                        if char_b_gender == char_a_gender:
                            break
                        else:
                            char_player_b = random.choice(char_sheets)
                            char_b_gender = char_player_b["GENDER"]

                    instance = self.add_game_instance(experiment, game_id)

                    # populate game with parameters
                    instance["char_a_a"] = deepcopy(char_player_a)
                    
                    # info player a has about player b
                    instance["char_a_b"] = deepcopy(char_player_b)
                    instance["char_a_b"].pop("HOBBIES")
                    instance["char_a_b"].pop("LIKES")
                    instance["char_a_b"].pop("DISLIKES")
                    instance["char_a_b"].pop("AGE")
                    instance["char_a_b"].pop("APPEARANCE")
                    instance["char_a_b"].pop("OCCUPATION")
                    instance["char_a_b"].pop("GENDER")
                    
                    # info player b has about player a
                    instance["char_b_a"] = deepcopy(char_player_a)
                    instance["char_a_b"].pop("HOBBIES")
                    instance["char_a_b"].pop("LIKES")
                    instance["char_a_b"].pop("DISLIKES")
                    instance["char_a_b"].pop("AGE")
                    instance["char_a_b"].pop("APPEARANCE")
                    instance["char_a_b"].pop("OCCUPATION")
                    instance["char_a_b"].pop("GENDER")
                    
                    # info player b has about themselves 
                    instance["char_b_b"] = deepcopy(char_player_b)

                    instance["initial_prompt_player_a"] = initial_prompt_a.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_a_a", str(instance["char_a_a"])).replace("charsheet_a_b", str(instance["char_a_b"]))
                    instance["initial_prompt_player_b"] = initial_prompt_b.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_b_b", str(instance["char_b_b"])).replace("charsheet_b_a", str(instance["char_b_a"]))
                    instance["further_prompts"] = further_prompts
                    instance["reprompt_prompt"] = reprompt_prompt

            elif topic == "medium-less_turns":

                experiment = self.add_experiment(topic)

                experiment["n_turns"] = n_turns - 5
                experiment["max_retries"] = max_retries
                experiment["re_prompt_allowed"] = False

                for game_id in range(N_INSTANCES):

                    # save charactersheets for players
                    char_player_a = random.choice(char_sheets)
                    char_player_b = random.choice(char_sheets)

                    instance = self.add_game_instance(experiment, game_id)

                    # populate game with parameters
                    # info player a has about themselves
                    instance["char_a_a"] = deepcopy(char_player_a)
                    
                    # info player a has about player b
                    instance["char_a_b"] = deepcopy(char_player_b)
                    instance["char_a_b"].pop("HOBBIES")
                    instance["char_a_b"].pop("LIKES")
                    instance["char_a_b"].pop("DISLIKES")
                    
                    # info player b has about player a
                    instance["char_b_a"] = deepcopy(char_player_a)
                    instance["char_b_a"].pop("HOBBIES")
                    instance["char_b_a"].pop("LIKES")
                    instance["char_b_a"].pop("DISLIKES")
                    
                    # info player b has about themselves 
                    instance["char_b_b"] = deepcopy(char_player_b)

                    instance["initial_prompt_player_a"] = initial_prompt_a.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_a_a", str(instance["char_a_a"])).replace("charsheet_a_b", str(instance["char_a_b"]))
                    instance["initial_prompt_player_b"] = initial_prompt_b.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_b_b", str(instance["char_b_b"])).replace("charsheet_b_a", str(instance["char_b_a"]))
                    instance["further_prompts"] = further_prompts
                    instance["reprompt_prompt"] = reprompt_prompt

            elif topic == "medium-more_turns":

                experiment = self.add_experiment(topic)

                experiment["n_turns"] = n_turns + 5 
                experiment["max_retries"] = max_retries
                experiment["re_prompt_allowed"] = False

                for game_id in range(N_INSTANCES):

                    # save charactersheets for players
                    char_player_a = random.choice(char_sheets)
                    char_player_b = random.choice(char_sheets)

                    instance = self.add_game_instance(experiment, game_id)

                    # populate game with parameters
                    # info player a has about themselves
                    instance["char_a_a"] = deepcopy(char_player_a)
                    
                    # info player a has about player b
                    instance["char_a_b"] = deepcopy(char_player_b)
                    instance["char_a_b"].pop("HOBBIES")
                    instance["char_a_b"].pop("LIKES")
                    instance["char_a_b"].pop("DISLIKES")
                    
                    # info player b has about player a
                    instance["char_b_a"] = deepcopy(char_player_a)
                    instance["char_b_a"].pop("HOBBIES")
                    instance["char_b_a"].pop("LIKES")
                    instance["char_b_a"].pop("DISLIKES")
                    
                    # info player b has about themselves 
                    instance["char_b_b"] = deepcopy(char_player_b)

                    instance["initial_prompt_player_a"] = initial_prompt_a.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_a_a", str(instance["char_a_a"])).replace("charsheet_a_b", str(instance["char_a_b"]))
                    instance["initial_prompt_player_b"] = initial_prompt_b.replace("$number_of_turns", str(experiment["n_turns"])).replace("$charsheet_b_b", str(instance["char_b_b"])).replace("charsheet_b_a", str(instance["char_b_a"]))
                    instance["further_prompts"] = further_prompts
                    instance["reprompt_prompt"] = reprompt_prompt

if __name__ == '__main__':
    random.seed(SEED)
    # always call this, which will actually generate and save the JSON file
    DatingSimInstanceGenerator().generate(filename="instances.json")
