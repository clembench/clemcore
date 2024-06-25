# here implement class player
from typing import List, Tuple, Dict, Any

from clemgame.clemgame import Player


class PC(Player):
    def __init__(self, model_name: str, player: str):
        super().__init__(model_name)
        self.player: str = player
        self.history: List = []
        # make it a dict maybe? and include turns

    def __call__(self, messages: List[Dict], turn_idx) -> Tuple[Any, Any, str]:
        # all the important stuff goes here
        return None


class NPC(Player):
    def __init__(self, model_name: str, player: str):
        super().__init__(model_name)
        self.player: str = player
        self.history: List = []
        # make it a dict maybe? and include turns

    def __call__(self, messages: List[Dict], turn_idx) -> Tuple[Any, Any, str]:
        # all the important stuff goes here
        return None


class Assistant(Player):
    def __init__(self, model_name: str, player: str):
        super().__init__(model_name)
        self.player: str = player
        self.history: List = []
        # make it a dict maybe? and include turns

    def __call__(self, messages: List[Dict], turn_idx) -> Tuple[Any, Any, str]:
        # all the important stuff goes here
        return None
