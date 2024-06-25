def give_rules():
    rules_prompt = """
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
SEX: 
AGE:
"""
    return rules_prompt