
import re

from games.dating_simulator.resources.pc import prompt_char_sheets

given_npc = prompt_char_sheets(character_sheet="")

char_prompt = f"""You are now a NPC within a dating simulator. The player character (PC) has the goal to romance you throughout the game and get as many affinity points as possible. This is the character you play:

{given_npc}

Throughout the game, the PC chooses actions to do during the date. How do you find the activity according to your character?"""

scale = """CHOOSE a number. 
1) really bad: I would never do this
2) bad: I would not like that
3) neutral: I have no strong opinion on that. But why not?
4) good: I'd like to do that
5) really good: I'd really love to do that"""

point_scaling = {1: -5, 2: -3, 3: 0, 4: 3, 5: 5}

force_format = """Give a reason why and formulate a response in the following format: 
NUMBER: 
REASON: 
RESPONSE:
"""

example_response = """
3: 
REASON: While I'm an athletic person and enjoy physical activities, yoga or stretches aren't really my thing. I'd rather be doing something more adrenaline-pumping. However, I appreciate the idea of spending time together and enjoying the fresh air.
RESPONSE: "Hmm, I've never really been into yoga, but I'm game if you are! Let's give it a shot. Just don't expect me to be too flexible, haha. I'm more of a 'get moving and get the blood pumping' kind of person."
"""

action = ""

def trigger_reaction(number, pc_chosen_action):
    if number == 0:
        return f"""{char_prompt}
            PC'S CHOSEN ACTION: {pc_chosen_action}
            {scale}
            {force_format}"""
    else:
        return f"""PC'S CHOSEN ACTION: {pc_chosen_action}
        {scale}
        {force_format}"""

# Only npc_response is going to be given to the PC
def parse_model_response(response):
    """
    Parses the response from the model and extracts the number and text components.

    Args:
    response (str): The response string from the model.

    Returns:
    tuple: A tuple containing the number and the text components.
    """
    # Regular expression to match the number at the beginning of the response
    number_match = re.search(r"(\d+):", response)
    if number_match:
        number = int(number_match.group(1))
    else:
        number = None

    reason_match = re.search(r"REASON: (.*?)(?=RESPONSE:)", response, re.DOTALL)
    response_match = re.search(r"RESPONSE: (.*)", response, re.DOTALL)

    if reason_match:
        reason = reason_match.group(1).strip()
    else:
        reason = ""

    if response_match:
        npc_response = response_match.group(1).strip()
    else:
        npc_response = ""

    return number, reason, npc_response


def update_game_state(npc_response, game_state, player_action):
    number,_, npc_response = parse_model_response(npc_response)

    game_state["affinity_points"] += point_scaling.get(number, 0)
    game_state["actions"].append({
        "action": player_action,
        "reaction": npc_response,
    })

    # Check if the player gets dumped
    if game_state["affinity_points"] <= -10 or check_consecutive_bad_choices(game_state["actions"]):
        game_state["status"] = "dumped"
    elif game_state["affinity_points"] >= 50:
        game_state["status"] = "success"
    else:
        game_state["status"] = "ongoing"

    return game_state


def check_consecutive_bad_choices(actions):
    if len(actions) < 3:
        return False
    return all(action["reaction"] == "dislikes" for action in actions[-3:])

