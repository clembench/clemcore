import json
import random

"""
To-Do:
> check if folder for playthrough exists, if not, create it, after that a dict so we can save the reesults as a json later on
> work on function "further_actions()"
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


def start_level(location, main_action_number):
    #####################
    # prompt location ##
    #####################

    actions = location["MAIN-ACTIONS"][main_action_number*4:main_action_number*4+4]
    location_prompt = f"""START: You are in {location["LOCATION"]}
{location["DESCRIPTION"]} 

ACTION: Choose one of the following actions and reason why you have chosen it:
1) {actions[0]}
2) {actions[1]}
3) {actions[2]}
4) {actions[3]}

Use the following template to answer:
NUMBER:
REASON:
"""
    return location_prompt, actions

def choose_further_mainaction(npc_transcript, location, main_action_number):
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

    npc_response = npc_transcript[-1]["cleaned response"]["ANSWER"]
    
    actions = location["MAIN-ACTIONS"][main_action_number*4:main_action_number*4+4]

    sub_actions_prompt = f"""
NPC'S RESPONSE: {npc_response}

Choose one of the following SUB ACTIONS and reason why you have chosen it:
1) {actions[0]}
2) {actions[1]}
3) {actions[2]}
4) {actions[3]}

Use the following template to answer:
NUMBER:
REASON:
""" 
    return sub_actions_prompt

def choose_further_subactions(sub_actions, npc_transcript):
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

    npc_response = npc_transcript[-1]["cleaned response"]["ANSWER"]
    sub_actions_prompt = f"""
NPC'S RESPONSE: {npc_response}

Choose one of the following SUB ACTIONS and reason why you have chosen it:
{sub_actions}

Use the following template to answer:
NUMBER:
REASON:
""" 
    return sub_actions_prompt

def choose_next_location(locations, level):
    location_options = locations[(level+1)**2:(level+1)**2+3]
    prompt = f"""Choose one of the following LOCATIONS for your next date.
1) {location_options[0]}
2) {location_options[1]}
3) {location_options[2]}

Use the following template to answer:
NUMBER:
REASON:
"""
    return prompt

def end_game(game_transcript, answer, ap):
    # message from DM to PC that the game has ended 

    npc_response = game_transcript[-1]["content"]["cleaned response"]["RESPONSE"]
    
    if answer == "YES":
        end = "Congratulations! You were able to impress your date and successfully start to date them!"
    else:
        end = "Daaam daaam daaam... You failed to impress your date. You were unable to become a pair."
    
    prompt = f"""After spending three dates with your date, you decide to ask them if they want to officially date you.
    Your date answers with
        {npc_response}
{end}

THE END 
And with this you have finished the game. Here are your statistics:
{ap}

Thank you for playing rizzSim!

Do not answer to this message.
"""
    return prompt

def aborted_game_bc_of_npc(location, game_transcript, ap):
    prompt = f"""
You asked your date for a next date at the {location}.
Unfortunatly, your date is not interested to meet you again and says {game_transcript[-1]["cleaned response"]["RESPONSE"]}

Better luck next time, hopless romantic birdy.

THE END 
And with this you have finished the game. Here are your statistics:
{ap}

Thank you for playing rizzSim!

Do not answer to this message.
"""
    return prompt