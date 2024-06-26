import json
import random

"""
To-Do:
> check if folder for playthrough exists, if not, create it, after that a dict so we can save the reesults as a json later on
> work on function "further_actions()"
"""

def choose_date(path_to_npc_sheets):
    # TODO: this needs to be implemented in game_flow. I added the thing in choose_date.template
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

    #choose_npc_prompt = 
    
    return choose_npc_prompt


def start_level(location, main_action_number):
    #####################
    # prompt location ## TODO: needs to be implemented in game-flow. also check: start_level.template
    #####################

    actions = location["MAIN-ACTIONS"][main_action_number*4:main_action_number*4+4]
    location_prompt = start_level.template
    
    return location_prompt, actions

def choose_further_mainaction(npc_transcript, location, main_action_number):
    # TODO needs to be in game-flow. further check choose_further_mainaction.template
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

    sub_actions_prompt = choose_further_mainaction.template
    return sub_actions_prompt

def choose_further_subactions(sub_actions, npc_transcript):
    # TODO needs to be in game-flow. further check choose_further_subaction.template
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
    sub_actions_prompt = ""
    return sub_actions_prompt

def choose_next_location(locations, level):
    # TODO implement in gameflow. further check choose_next_location.template
    location_options = locations[(level+1)**2:(level+1)**2+3]
    prompt = f""
    return prompt

def end_game(game_transcript, answer, ap):
    # TODO gotta dissect this into a if else statement in master.py and .template
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
