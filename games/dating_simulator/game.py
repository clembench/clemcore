import random
from string import ascii_lowercase as letters
from typing import List

from clemgame.clemgame import Player

class PC(Player):

    def __init__(self, model_name: str, player: str): # model_name = nam of the LLM to use; player=pc/npc or assistent
        super().__init__(model_name)
      self.player = player

      # a list to keep the dialogue history
      self.history: List = []

    def __call__(self, instruction: Instruction, turn_idx):
        return super().__call__(instruction.convert_to_query_messages(), turn_idx)

class NPC(Player):

    def __init__(self, model_name: str, player: str): # model_name = nam of the LLM to use; player=pc/npc or assistent
        super().__init__(model_name)
      self.player = player

      # a list to keep the dialogue history
      self.history: List = []

    def __call__(self, instruction: Instruction, turn_idx):
        return super().__call__(instruction.convert_to_query_messages(), turn_idx)

class Assistant(Player):

    def __init__(self, model_name: str, player: str): # model_name = nam of the LLM to use; player=pc/npc or assistent
        super().__init__(model_name)
      self.player = player

      # a list to keep the dialogue history
      self.history: List = []

    def __call__(self, instruction: Instruction, turn_idx):
        return super().__call__(instruction.convert_to_query_messages(), turn_idx)

  '''
  Method only needed for testing - programmatic (in case we do not have a LLM)
  
    def _custom_response(self, messages, turn_idx):
      if self.player == "PC":
        
        answer = random.choice(["first", "second", "third"])
        return f"Answer: {answer}"
  '''
