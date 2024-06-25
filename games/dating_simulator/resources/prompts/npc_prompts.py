
import re


def npc_initial_prompt(given_npc, chosen_action):
    char_prompt = f"""You are now a NPC within a dating simulator. The player character (PC) has the goal to romance you throughout the game and get as many affinity points as possible. 
This is the character you play:
{given_npc}
Throughout the game, the PC chooses actions to do during the date. Rate the chosen actions based on yout character with the following SCALE:
1) really bad: I would never do this
2) bad: I would not like that
3) neutral: I have no strong opinion on that. But why not?
4) good: I'd like to do that
5) really good: I'd really love to do that

Chosen ACTION: {chosen_action}

Rate the given ACTION given the SCALE and REASON your rating. Formulate a RESPONSE. 
Use the following TEMPLATE and NOTHING ELSE:
NUMBER: 
REASON: 
RESPONSE:
"""
    return char_prompt

def get_npc_response(chosen_action):
    prompt = f"""PC tells you: {chosen_action}
Rate the chosen option based on the SCALE, reason your decision and formulate a response in the following format: 
NUMBER: 
REASON: 
RESPONSE:
"""
    return prompt

def next_date(location):

    prompt = f"""Your date asks you out for a next date. They suggest to meet at the {location} next time.
Rate the chosen option based on the SCALE, reason your decision and formulate a response in the following format: 
NUMBER: 
REASON: 
RESPONSE:
"""
    return prompt

def grant_next_date():
    prompt = f"""You are satisfied with today's date at would like to try out another one at the LOCATION, PC suggested.
Formulate a response for the PC where you express that you would like to go on the proposed second date.
Use the following TEMPLATE to answer:
RESPONSE: 
"""
    return prompt

def decline_next_date():
    prompt = f"""You are NOT satisfied with today's date and would not like to try out another one.
Formulate a response for the PC where you express that you do not like to go on the proposed second date.
Use the following TEMPLATE to answer:
RESPONSE: 
"""
    return prompt

def become_couple(answer):
    if answer == "NO":
        prompt = f"""The date is over now and you had three dates with the PC. They now ask you, you to become an official pair with them.
        But you are not happy with the way the date turned out, therefore, you decide against becoming a pair with the PC.
        Formulate an answer to the question: "Do you want to officially date me?"
        Use the following TEMPLATE to answer:
        RESPONSE: 
"""
    else:
        prompt = f"""The date is over now and you had three dates with the PC. They now ask you, you to become an official pair with them.
        You were happy with the way the dates turned out, therefore, you agree to becoming a pair with the PC.
        Formulate an answer to the question: "Do you want to officially date me?"
        Use the following TEMPLATE to answer:
        RESPONSE: 
"""
        
    return prompt
