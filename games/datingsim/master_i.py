from typing import List

from backends import Model
from clemgame.clemgame import Player

import re 

logger = get_logger(__name__)

# Do we need this?
class Player(Player):
    def __init__(self,  model_name: str, player: str):
        # always initialise the Player class with the model_name argument
        # if the player is a program and you don't want to make API calls to
        # LLMS, use model_name="programmatic"

        super().__init__(model_name)
        self.player: str = player

        # list to keep dialogue history
        self.history: List = list()


import copy
from typing import List, Dict, Tuple
from string import ascii_lowercase as letters

import numpy as np

import clemgame.metrics as ms
from clemgame.clemgame import GameMaster, GameBenchmark
from clemgame import get_logger

# from games.datingsim.players import Speaker
from games.datingsim.instancegenerator import DatingSimInstanceGenerator

class datingsim(GameMaster):
    def __init__(self, experiment: Dict, player_backends: List[str]):
        super().__init__(DatingSimInstanceGenerator, experiment, player_backends)

        # save experiment and player attributes that will be necessary later
        self.experiment = experiment
        self.topic = experiment['name']     # yes
        self.model_a = player_backends[0]   # yes
        self.model_b = player_backends[1]   # yes

        # initialise attributes that will be used for the evaluation scores
        self.aborted: bool = False
        self.lose: bool = False
        self.complete_turns: int = 0

        # define game status
        self.proceed = True


    def setup(self, n_turns: int, prompt_player_a: str, prompt_player_b: str, game_id: int):

        self.n_turns = n_turns  #yes
        self.playerA = Player(self.model_a, "PlayerA")
        self.playerB = Player(self.model_b, "PlayerB")

        # initialise game variables
        self.current_turn = 0   # yes
        self.num_prompt_retries = 0
        self.max_prompt_retries = 3

        self.last_message = None

        # initialise metrics
        self.request_counts = [0] * (n_turns + 1)
        self.parsed_request_counts = [0] * (n_turns + 1)
        self.violated_request_counts = [0] * (n_turns + 1)

        # add initial prompts to each player's messages
        self.initiate(prompt_player_a, prompt_player_b)

        # always log the details of the players in this format (see logdoc)
        self.log_players({
            'GM': 'Game master for datingSim',
            'Player 1': f'Player A: {self.model_a}',
            'Player 2': f'Player B: {self.model_b}'
            })

        # log any additional keys that will be relevant for evaluation
        self.log_key('n_turns', n_turns)
        # perhaps Grice Maxims


    def play(self):
        # play the game
        while self.proceed():
            self.current_turn += 1
            # always call log_next_turn when a new turn starts
            self.log_next_turn()
            self.turn()

        if self.complete_turns >= self.n_turns:
            # log a message informing that the players weren't able to finish the game in time
            action = {'type': 'info', 'content': 'Game unsuccessful. You are out of turns'}
            self.log_event(from_='GM', to='GM', action=action)

        # log a final message saying that the game did came to an end
        action = {'type': 'info', 'content': 'End of game'}
        self.log_event(from_='GM', to='GM', action=action)
        # log all temporary game variables that are needed for evaluation
        self.log_eval_assets()


    def append_utterance(self, utterance:str, player:str, role:str):
        """
        Add utterance of a player to history to the player
        """
        assert player in ("A", "B")
        if player == "A":
            self.playerA.history.append({'role': role, 'content': utterance})
        else:
            self.playerB.history.append({'role': role, 'content': utterance})


    def initiate(self, prompt_player_a: str, prompt_player_b: str):
        """
        Initialise turn 0 with the initial prompts for the players 
        """
        # always call log_next_turn what a turn starts
        self.log_next_turn()

        self.playerA.history.append({'role': 'user', 'content': prompt_player_a})
        self.playerB.history.append({'role': 'user', 'content': prompt_player_b})

        # also log the messages as events for the transcriptions
        action = {'type': 'send message', 'content': prompt_player_a}
        self.log_event(from_='GM', to='Player 1', action=action)
        action = {'type': 'send message', 'content': prompt_player_b}
        self.log_event(from_='GM', to='Player 2', action=action)


    def proceed(self) -> None:
        """
        Check if the game loop should continue.
        If turn number is over turn-limit, players
        have lost.
        If number of prompt retries is over the allowed
        max, game is aborted.
        """
        if self.current_turn > self.n_turns:
            return self.lose
        elif self.num_prompt_retries > self.max_prompt_retries:
            return self.aborted
        

    def log_eval_assets(self):
        """
        Log counts and variables for scoring
        """
        self.log_key("Played turns", self.current_turn)
        self.log_key('Complete turns', self.complete_turns)
        self.log_key(ms.METRIC_ABORTED, self.aborted)
        self.log_key(ms.METRIC_LOSE, self.lose)
        self.log_key(ms.METRIC_REQUEST_COUNT, self.request_counts)
        self.log_key(ms.METRIC_REQUEST_COUNT_PARSED, self.parsed_request_counts)
        self.log_key(ms.METRIC_REQUEST_COUNT_VIOLATED, self.violated_request_counts)


    def update_message(answer):
        """
        Update the last response said
        """
        # filter out the response 
        response_pattern = r"\[response\](.+)\[end\]"
        response_match = re.search(response_pattern, answer, re.DOTALL)
        last_message = response_match.group(1)

        return last_message
    

    def turn(self):
        """
        Define a turn.
        A turn is over as soon as player A and player B exchanged sentences.
        Player A marks the beginning of a turn 
        """
        # get player A's reply and add it to its history
        answer_a = self.get_utterance("A")

        # check if game should continue 
        is_valid_turn = self.check_validity(answer_a)
        if not is_valid_turn:
            # stop the game
            return None
        
        # add playerA's reply to B's history
        self.append_utterance(answer_a, "B", "user")
        # add reply to transcript
        action = {'type': 'send message', 'content': answer_a}
        self.log_event(from_='GM', to='Player 2', action=action)

        # next player gets message from previous player
        self.last_message = self.update_message(answer_a)

        # now implement turn for player B
        answer_b = self.get_utterance("B")

        is_valid_turn = self.check_validity(answer_b)
        if not is_valid_turn:
            return None
        
        # add B's response to A's history and transcript
        self.append_utterance(answer_b, "A", "user")
        action = {'type': 'send message', 'content': answer_b}
        self.log_event(from_='GM', to='Player 1', action=action)

        self.last_message = self.update_message(answer_b)
        self.complete_turns += 1

    def get_utterance(self, player:str):
        """
        Get utterance/response from player and lot it
        """
        assert player in ("A", "B")
        if player == "A":
            prompt, raw_answer, answer = self.playerA(
                self.playerA.history, self.current_turn)
            # add api call to records
            action = {'type': 'get message', 'content': answer}
            self.log_event(from_='Player 1', to='GM', action=action,
                        call=(copy.deepcopy(prompt), raw_answer))
            # add reply to its own memory
            self.append_utterance(answer, 'A', 'assistant')
        else:
            prompt, raw_answer, answer = self.playerB(
                self.playerB.history, self.current_turn)
            # add api call to records
            action = {'type': 'get message', 'content': answer}
            self.log_event(from_='Player 2', to='GM', action=action,
                        call=(copy.deepcopy(prompt), raw_answer))
            # add reply to its own memory
            self.append_utterance(answer, 'B', 'assistant')
            
        # increase the number of API requests 
        self.request_counts[self.current_turn] += 1
        return answer
    
    def check_validity(self, answer:str):
        """
        Check if given answer by yplayer is valid or
        if it must be re-entered.
        """
        # check, if answer begins and ends with 
        pattern_for_answer = r"\[reason\].+\[end\]\n\[sentiment\].+\[end\]\n\[response\].+\[end\]"
        import re
        if re.fullmatch(pattern_for_answer, answer, re.DOTALL):
            pass
            # return True
        else: # abort game 
            self.aborted = True
            
            # log the abortion event
            action = {'type': 'invalid format', 'content': 'Aborted'}
            self.log_event(from_='GM', to='GM', action=action)

            # increase the counter of requests that violate form rules
            self.violated_request_counts[self.current_turn] += 1
            return False
        
        # increase the counter of requests that conform to form rules
        self.parsed_request_counts[self.current_turn] += 1
        # log the event that the string was valid (no strange characters)
        action = {'type': 'metadata', 'content': 'valid string'}
        self.log_event(from_='GM', to='GM', action=action)

        # log the fact that the answer was correct
        action = {'type': 'parse',
                  'content': f'{answer} conforms to rules'}

        self.log_event(from_='GM', to='GM', action=action)
        return True
    

    def compute_scores(self, episode_interactions: Dict) -> None:
        """Compute episode-level and turn-level scores (mandatory)."""
        played_turns = episode_interactions['Played turns']
        complete_turns = episode_interactions['Complete turns']
        # turn 0 was only the initial prompts, so we disregard it here
        reqs = episode_interactions[ms.METRIC_REQUEST_COUNT][1:]
        p_reqs = episode_interactions[ms.METRIC_REQUEST_COUNT_PARSED][1:]
        v_reqs = episode_interactions[ms.METRIC_REQUEST_COUNT_VIOLATED][1:]
        n_turns = len(reqs)

        for turn in range(0, played_turns):
            self.log_turn_score(turn, ms.METRIC_REQUEST_COUNT, reqs[turn])
            self.log_turn_score(turn, ms.METRIC_REQUEST_COUNT_PARSED, p_reqs[turn])
            self.log_turn_score(turn, ms.METRIC_REQUEST_COUNT_VIOLATED, v_reqs[turn])

        aborted = int(episode_interactions[ms.METRIC_ABORTED])
        lose = int(episode_interactions[ms.METRIC_LOSE]) if not aborted else 0
        success =  1 - lose if not aborted else 0
        bench_score = complete_turns / n_turns if not aborted else np.nan
        
        self.log_episode_score(ms.METRIC_ABORTED, aborted)
        self.log_episode_score(ms.METRIC_LOSE, lose)
        self.log_episode_score(ms.METRIC_SUCCESS, success)
        self.log_episode_score(ms.METRIC_REQUEST_COUNT, sum(reqs))
        self.log_episode_score(ms.METRIC_REQUEST_COUNT_PARSED, sum(p_reqs))
        self.log_episode_score(ms.METRIC_REQUEST_COUNT_VIOLATED, sum(v_reqs))
        self.log_episode_score(ms.METRIC_REQUEST_SUCCESS, sum(p_reqs) / sum(reqs))
        self.log_episode_score(ms.BENCH_SCORE, bench_score)

    def log_eval_assets(self) -> None:
            """Aux to log variables needed for scoring (firstlast specific)"""
            self.log_key('Played turns', self.current_turn)
            self.log_key('Complete turns', self.complete_turns)
            self.log_key(ms.METRIC_ABORTED, self.aborted)
            self.log_key(ms.METRIC_LOSE, self.lose)
            self.log_key(ms.METRIC_REQUEST_COUNT, self.request_counts)
            self.log_key(ms.METRIC_REQUEST_COUNT_PARSED, self.parsed_request_counts)
            self.log_key(ms.METRIC_REQUEST_COUNT_VIOLATED, self.violated_request_counts)
