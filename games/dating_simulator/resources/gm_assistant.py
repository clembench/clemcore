import json
from games.dating_simulator.resources.pc import prompt_char_sheets

TODO: # maybe it is better to write a class since some values needs to be updated and reflects on other values.

with open("games/dating_simulator/in/ex_NPC_sheet.json", "r", encoding="UTF8") as file:
    npc_sheets = json.load(file)

with open("PC_decisions.json", "r", encoding="UTF8") as file:
    pc_decisions = json.load(file)

npc_id = pc_decisions["NPC"]["ID"]
character_sheet = prompt_char_sheets(npc_id)
level = pc_decisions["Level"]
current_main_action = pc_decisions["Level"]["Main Action"]["Number"]["Action"]

def get_pc_decisions():
    """
    In order to get the following PC decisions
    """
    with open("PC_decisions.json", "r", encoding="UTF8") as file:
    pc_decisions = json.load(file)
    return pc_decisions

def get_npc_assessment():
    """
    In order to get the following NPC response and dialogue for each action
    """
    with open("NPC_decisions.json", "r", encoding="UTF8") as file:
    npc_decision = json.load(file)

    npc_response = npc_decision["Level"]["Main Action"]["Sub Action"]["NPC"]["Reaction"]
    npc_dialogue = npc_decision["Level"]["Main Action"]["Sub Action"]["NPC"]["Dialogue"]

    return npc_response, npc_dialogue

def initiate_assistant(character_sheet, current_main_action):
    """
    Input: character_sheet, current_main_action
    """
    assistant_initial_prompt = """
    You are now the assistant to the Game Master of a dating simulator game. 
    Based on the chosen main actions of the player character (PC) and the response of the NPC to PC, 
    you are supposed to create 4 possible sub actions the PC can do. Include a dialogue phrase consisting of one sentence.

    Example: 
    MAIN ACTION: Feed the ducks. 
    NPC RESPONSE: Very cool! 

    NUMBER) SUB ACTION:”DIALOGUE”
    1) Buy duck food: “Let’s buy some food for the ducks!”.
    2) Start a conversation: “Let’s talk a little and get to know each other more!”
    3) Run after ducks: “Wanna chase these ducks??”
    4) Get intimate with your date: “I know a great spot to spend some alone time” 

    Provide 4 suitable SUB ACTIONS with one possible dialogue sentence to the chosen MAIN ACTION.
    NOTE: This is their {npc_decision["Level"]} date. Here are the actions chosen by PC so far:
    MAIN ACTION 1: {main_action_1}

    CURRENT MAIN ACTION: {current_main_action}
    NPC’S RESPONSE: {npc_response}
    NPC’S DIALOGUE: {npc_dialogue}

    NOTE: You should also take into account the NPC’s character sheet. Here is the NPC’s character details:
    {character_sheet}

    Give your response with SUB ACTIONS:
    Enumerate the possible SUB ACTIONS and give your answer in the following template:
    NUMBER) SUB ACTION: “DIALOGUE”

    ONLY PRODUCE OUTPUT ACCORDING TO THE TEMPLATE NOTHING MORE
    """

    first_sub_actions = "output of the LLM"
    return first_sub_actions

def prompt_subactions():
    sub_action_template = """
    Provide 4 new suitable SUB ACTIONS with one possible dialogue sentence to the chosen MAIN ACTION and the NPC’s reaction to it. 
    NOTE: This is their ["Level"] date. The game is at MAIN ACTION ["Level"]["Main Action"]["Number"][i] and now we are at SUB ACTION ["Level"]["Main Action"]["Number"][i].["Main Action"]["Number"][i]["Sub Action"]["Number"][j]. Here are the actions chosen by PC so far:

    NPC’S REACTION SCALE: 1) really bad: I would never do this 2) bad: I would not like that 3) neutral: I have no strong opinion on that. But why not? 4) good: I'd like to do that 5) really good: I'd really love to do that

    MAIN ACTION 1:["Level"]["Main Action"]["Action"] NPC’S REACTION: ["Level"]["Main Action"]["NPC"]["Reaction"]
    SUB ACTION 1.1: ["Level"]["Main Action"]["Sub Action"]["Action"] - NPC’S REACTION: ["Level"]["Main Action"]["Sub Action"]["NPC"]["Reaction"]

    NOTE: Take into account the NPC’s character sheet and the NPC's reaction scale.

    Give your answer in the following template:
    NUMBER) SUB ACTION: “DIALOGUE”

    ONLY PRODUCE OUTPUT ACCORDING TO THE TEMPLATE NOTHING MORE
    """

    sub_actions = "output of the LLM"
    return sub_actions
