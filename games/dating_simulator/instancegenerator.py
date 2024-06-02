import os
import json
import clemgame
from clemgame.clemgame import GameInstanceGenerator



class GameInstanceGenerator(GameResourceLocator):

    # include the self.load_template() and self.load_file() for initial prompt and stuff 
    
    def __init__(self, name: str):
        super().__init__(name)
        self.instances = dict(experiments=list())
    
    def on_generate(self, **kwargs):
        random.seed(42)
        
        """
        Game-specific instance generation.
        """
        
        player_char_prompt = self.load_template("path to the initial prompt aka start_prompt")

        # add experiment 
        # add instance 
        
        raise NotImplementedError()

if __name__ == '__main__':
    ReferenceGameInstanceGenerator().generate(filename="instances.json")


#######################################################################
# generate JSON file to save playthrough of game
save_dir = "./playthroughs/"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# get number of playthroughs # should we divide between LLM and Human playthroughs?
nr_of_plays = len(os.listdir(save_dir))
# probably yes for evaluation
playthrough_json = f"./playthroughs/{nr_of_plays+1}_playthrough.json"

with open(playthrough_json, "w", encoding="UTF-8") as file:
    current_play_json = json.load(file)
print(current_play_json)

