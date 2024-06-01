import json
import random

To-Do:
"""
> check if folder for playthrough exists, if not, create it, after that a dict so we can save the reesults as a json later on
> work on function "further_actions()"
"""

def start_game():
    start_prompt = """
You are now playing a game.
GOAL: Throughout the game, romance a character (NPC) and get as many affinity points as possible. 
RULES: 
1) Affinity points are gained by interactions with the NPC based on the choice of action and dialogue you choose. 
2) If the NPC likes your choice, affinity points will be increased. If they don't, they get reduced. 
3) If you are able to reach a certain amount of affinity points throughout the game, you finish it with success. 
4) One game consists of three levels, which are specific locations which provide you with action options. 
5) You get dumped if your affinity points reach a certain low level or if you make 3 choices in a row which the NPC is "very dissatisfied" with. 
START: If you are ready to play the game, choose which gender and age you want to take on as the player character (PC). 
Use the following template to answer and nothing more or less. 
GENDER: 
AGE:
"""

def prompt_char_sheets(character_sheet):
    prompt = f"""
    GENDER: {character_sheet["GENDER"]}
    AGE: {character_sheet["AGE"]}
    APPEARANCE: {character_sheet["APPEARANCE"]}
    LIKES: {character_sheet["LIKES"]}
    DISLIKES: {character_sheet["DISLIKES"]}
    HOBBIES: {character_sheet["HOBBIES"]}
    SUMMARY: {character_sheet["SUMMARY"]}
    """
    return prompt

 # character sheets file path

def choose_date(path_to_npc_sheets):
    #####################
    # prompt npc sheets #
    #####################

    # fetch character sheets
    with open(path_to_npc_sheets, "r", encoding="UTF8") as file:
        npc_sheets = json.load(file)

    # shuffle the list and pick random character sheets
    random.shuffle(npc_sheets)
    # pick 2 random character sheets
    indices = random.sample(range(len(npc_sheets)), 3)

    npc1 = prompt_char_sheets(npc_sheets[indices[0]])
    npc2 = prompt_char_sheets(npc_sheets[indices[1]])
    npc3 = prompt_char_sheets(npc_sheets[indices[2]])

    choose_npc_prompt = f"""
CHOOSE YOUR DATE: From the following list choose the NPC you want to date. Respond with the number of the chosen character with: NUMBER: 
1) {npc1}
2) {npc2}
3) {npc3}

Use the following template to answer and nothing more or less.
NUMBER:
"""
    
    return choose_npc_prompt

def get_random_actions(list_of_main_actions, nr_of_main_action):
    """
    Function which extracts the next for unique MAIN-ACTIONS available
    for the current LOCATION and avoinds to pick one more than once by
    taking the nr of main actions into considerations
    
    Input:
    list_of_main_actions (list) :   List of MAIN-ACTIONS available for the 
                                    current location.
    nr_of_main_action (int)     :   Number of MAIN-ACTION. Can be any number
                                    between 1-4.

    Output:
    random_actions (list)       : List of random MAIN-ACTIONS for the PC to
                                    choose from.
    """
    if nr_of_main_action == 1:
        start_index = 0
        end_index = start_index + 4
        random_actions = list_of_main_actions[start_index:end_index]
 
    else:
        start_index = 0 + (nr_of_main_action-1)*4
        end_index = start_index + 4
        random_actions = list_of_main_actions[start_index:end_index]
    return random_actions

def start_level():
    #####################
    # prompt location ##
    #####################

    # load locations
    path_to_location_sheets = "./location_sheets.json"
    with open(path_to_location_sheets, "r", encoding="UTF8") as file:
        location_sheets = json.load(file)

    # get random location
    random_location = random.choice(location_sheets)
    random.shuffle(random_location["MAIN-ACTIONS"])

    print(type(random_location["MAIN-ACTIONS"]))
    random_actions = get_random_actions(random_location["MAIN-ACTIONS"],1)

    location_prompt = f"""
START: You are in {random_location["LOCATION"]}
{random_location["LOCATION"]} 

ACTION: Choose one of the following actions and reason why you have chosen it:
1) {random_actions[0]}
2) {random_actions[1]}
3) {random_actions[2]}
4) {random_actions[3]}

Use the following template to answer:
NUMBER:
REASON:
"""
    return location_prompt

def further_actions(npc_response, list_of_4_actions):
    """
    Function which prompts all following SUB- and MAIN-ACTIONS.

    Input:
    npc_response (str)              : Response of the NPC (the date) towards the last 
                                        chosen action. Can be a MAIN- or a SUB-ACTION.
    list_of_4_actions (list)    	: List which includes 4 ACTION options.

    Output:
    sub_actions_prompt (str)        : Prompt for the PC to choose a next (MAIN-/SUB-)
                                        ACTION.
    """

    sub_actions_prompt = f"""
NPC'S RESPONSE: {npc_response}

Choose one of the following SUB ACTIONS and reason why you have chosen it:
1) {list_of_4_actions[0]}
2) {list_of_4_actions[1]}
3) {list_of_4_actions[2]}
4) {list_of_4_actions[3]}

Use the following template to answer:
NUMBER:
REASON:
""" 
    return sub_actions_prompt



# path_to_npc_sheets = "./npc_sheets.json"
