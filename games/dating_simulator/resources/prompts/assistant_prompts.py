import json

def assistant_initial_prompt(i,  
                            all_chosen_actions, 
                            instance_index,
                            npc_transcript, 
                            chosen_npc,
                            location):

    prompt = f"""You are now the assistant to the Game Master of a dating simulator game. 
    Based on the chosen main actions of the player character (PC) and the response of the NPC to PC, 
    you are supposed to create 4 possible sub actions the PC can do. Include a dialogue phrase consisting of one sentence.

    Example: 
    MAIN ACTION: Feed the ducks. 
    NPC RESPONSE: Very cool! 

    TEMPLATE: NUMBER) SUB ACTION: 'DIALOGUE'
    1) Buy duck food: "Let’s buy some food for the ducks!".
    2) Start a conversation: "Let’s talk a little and get to know each other more!"
    3) Run after ducks: "Wanna chase these ducks??"
    4) Get intimate with your date: "I know a great spot to spend some alone time"

    NOTE: This is their {i+1} date. Here are the actions chosen by PC so far:
    MAIN ACTION 1: {all_chosen_actions}

    CURRENT MAIN ACTION: {instance_index}
    NPC’S RESPONSE: {npc_transcript[-1]["cleaned response"]["ANSWER"]}

    NOTE: You should also take into account the NPC’s character sheet. Here are the NPC’s character details:
    {chosen_npc}

    Give your response with SUB ACTIONS:
    Enumerate the possible SUB ACTIONS and give your answer in the following TEMPLATE:
    
    <OPT>1) SUB ACTION: "DIALOGUE"
    2) SUB ACTION: "DIALOGUE"
    3) SUB ACTION: "DIALOGUE"
    4) SUB ACTION: "DIALOGUE"<OPT>

    Don't forget to include the special symbols <OPT> and <OPT>

    ONLY PRODUCE OUTPUT ACCORDING TO THE TEMPLATE NOTHING MORE
"""

    return prompt

def assistant_further_subactions(i,  
                            all_chosen_actions, 
                            instance_index,
                            npc_transcript, 
                            chosen_npc,
                            location):

    prompt = f"""Create 4 more possible sub actions the PC can do. Include a dialogue phrase consisting of one sentence.

    NOTE: This is their {i+1} date. Here are the actions chosen by PC so far:
    {all_chosen_actions}

    CURRENT MAIN ACTION: {instance_index}
    NPC’S RESPONSE: {npc_transcript[-1]["cleaned response"]["ANSWER"]}

    Give your response with SUB ACTIONS:
    Enumerate the possible SUB ACTIONS and give your answer in the following TEMPLATE:
    
    <OPT>1) SUB ACTION: "DIALOGUE"
    2) SUB ACTION: "DIALOGUE"
    3) SUB ACTION: "DIALOGUE"
    4) SUB ACTION: "DIALOGUE"
    <OPT>

    Don't forget to include the special symbols <OPT> and <OPT>

    ONLY PRODUCE OUTPUT ACCORDING TO THE TEMPLATE NOTHING MORE
"""

    return prompt


    sub_action_template = """
    Provide 4 new suitable SUB ACTIONS with one possible dialogue sentence to the chosen MAIN ACTION and the NPC’s reaction to it. 
    NOTE: This is their ["Level"] date. The game is at MAIN ACTION ["Level"]["Main Action"]["Number"][i] and now we are at SUB ACTION ["Level"]["Main Action"]["Number"][i].["Main Action"]["Number"][i]["Sub Action"]["Number"][j]. Here are the actions chosen by PC so far:

    NPC’S REACTION SCALE: 1) really bad: I would never do this 2) bad: I would not like that 3) neutral: I have no strong opinion on that. But why not? 4) good: I'd like to do that 5) really good: I'd really love to do that

    MAIN ACTION 1:["Level"]["Main Action"]["Action"] NPC’S REACTION: ["Level"]["Main Action"]["NPC"]["Reaction"]
    SUB ACTION 1.1: ["Level"]["Main Action"]["Sub Action"]["Action"] - NPC’S REACTION: ["Level"]["Main Action"]["Sub Action"]["NPC"]["Reaction"]

    NOTE: Take into account the NPC’s character sheet and the NPC's reaction scale.

    Give your answer in the following template:
    SUBACTION 1: NUMBER) SUB ACTION: “DIALOGUE”

    ONLY PRODUCE OUTPUT ACCORDING TO THE TEMPLATE NOTHING MORE
    """

    sub_actions = "output of the LLM"
    return sub_actions