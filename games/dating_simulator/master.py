import copy
from typing import List, Dict, Tuple

import numpy as np

import clemgame.metrics as ms
from clemgame.clemgame import GameMaster, GameBenchmark
from clemgame import get_logger

from games.firstlast.players import Speaker
from games.firstlast.instancegenerator import GAME_NAME

class FirstLast(GameMaster):
    """Implement mechanisms for playing FirstLast."""
    def __init__(self, experiment: Dict, player_backends: List[str]):
        super().__init__(GAME_NAME, experiment, player_backends)

        # save experiment and player attributes that will be necessary later
        self.topic = experiment['name']
        self.model_a = player_backends[0] # npc -- but maybe save npc and assistant in seperate lists 
        self.model_b = player_backends[1] # assistant

        '''
        Need this only later on
        
        # initialise attributes that will be used for the evaluation scores
        self.aborted: bool = False
        self.lose: bool = False
        self.complete_turns: int = 0
        '''
