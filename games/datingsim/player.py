#here implement class player
from typing import List, Tuple, Dict, Any

from clemgame.clemgame import Player


class PC(Player):
    def __init__(self, model_name: str, player:str):
        super().__init__(model_name)
        self.player: str = player
        self.history: List = []
        #make it a dict maybe? and include turns

    def __call__(self, messages: List[Dict], turn_idx) -> Tuple[Any, Any, str]:
