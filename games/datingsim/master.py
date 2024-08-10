import collections
import copy
import re
from typing import Dict, List
from string import Template
import numpy as np
import re

from backends import Model
from clemgame import get_logger
from clemgame.metrics import METRIC_ABORTED, METRIC_SUCCESS, METRIC_LOSE, METRIC_REQUEST_COUNT, \
    METRIC_REQUEST_COUNT_VIOLATED, METRIC_REQUEST_COUNT_PARSED, METRIC_REQUEST_SUCCESS, BENCH_SCORE
from clemgame.clemgame import GameMaster, GameBenchmark, GameScorer, DialogueGameMaster
from games.datingsim.player import *

GAME_NAME = "datingsim"
logger = get_logger(__name__)


class DatingSimGameMaster(GameMaster):
    def __init__(self, experiment: Dict, player_models: List[Model]):
        super().__init__(GAME_NAME, experiment, player_models)

        # regex patterns here

        self.experiment = experiment
        self.model_a = player_models[0]
        self.model_b = player_models[1]

        self.re_prompt = experiment["re_promt_allowed"]  # fetches True or False from the experiment
        self.max_prompt_retries = experiment["max_retries"]

        # initialise attributes that will be used for the evaluation scores
        self.aborted: bool = False
        self.lose: bool = False
        self.complete_turns: int = 0
        self.won: bool = False

        # define game status
        self.proceed = True

        self.players_by_names: Dict[str, Player] = collections.OrderedDict()
        self.writer_history = []
        self.responder_history = []

    def add_player(self, player: Player) -> None:

        # player writer and responder
        idx = len(self.players_by_names)
        self.players_by_names[player.descriptor] = player
        player.descriptor = f"Player {idx + 1}"
        logger.warning("Invalid player index: %d", idx)
        logger.info(f"Added player {player.descriptor} with index {idx}")

    def add_message(self, player: Player, utterance: str, role="user") -> None:
        if player == self.player_a:
            self.writer_history.append({'role': role, 'content': utterance})
            action = {'type': 'send message', 'content': utterance}
            self.log_event(from_='GM', to="Player 1", action=action)
        else:
            self.responder_history.append({'role': role, 'content': utterance})
            action = {'type': 'send message', 'content': utterance}
            self.log_event(from_='GM', to="Player 2", action=action)


    def add_reprompt(self, player: Player, utterance: str, role="user") -> None:

        if player == self.player_a:
            self.writer_history.append({'role': role, 'content': utterance})
            action = {'type': 'reprompt', 'content': utterance}
            self.log_event(from_='GM', to="Player 1", action=action)
        else:
            self.responder_history.append({'role': role, 'content': utterance})
            action = {'type': 'reprompt', 'content': utterance}
            self.log_event(from_='GM', to="Player 2", action=action)


    def get_answer(self, player: Player) -> str:
        if player == self.player_a:
            prompt, raw_answer, answer = player(self.writer_history, self.current_turn)
            action = {"type": "get message", 'content': answer}
            self.log_event(from_="Player 1", to="GM", action=action,
                           call=(copy.deepcopy(prompt), raw_answer))

            self.writer_history.append({'role': "assistant", 'content': answer})
        else:
            prompt, raw_answer, answer = player(self.responder_history, self.current_turn)
            action = {'type': 'get message', 'content': answer}
            self.log_event(from_="Player 2", to="GM", action=action,
                           call=(copy.deepcopy(prompt), raw_answer))
            self.responder_history.append({'role': "assistant", 'content': answer})

        return answer


    def setup(self, **game_instance) -> None:
        """
        This function sets up the game with the given game instance configuration.
        """

        logger.info("Setup")

        # import game instances
        self.game_instance = game_instance
        self.game_id = self.game_instance["game_id"]

        self.current_turn = 0
        self.n_turns = self.experiment['n_turns']
        self.num_reprompts = 0
        self.num_completed_turns = 0

        self.last_response = None
        self.last_sentiment = None

        self.conditions_met = False
        self.time_agreement = False
        self.location_agreement = False
        self.action_agreement = False

        # initialise metrics
        self.request_counts = [0] * (self.n_turns + 1)
        self.parsed_request_counts = [0] * (self.n_turns + 1)
        self.violated_request_counts = [0] * (self.n_turns + 1)

        # metric to save the number of turns players needed to find an agreement
        self.turns_to_win_game = 0

        # create player/s here
        self.player_a = Dater(self.model_a, "Writer")
        self.player_b = Dater(self.model_b, "Responder")

        self.initial_prompt_player_a = self.game_instance["initial_prompt_player_a"]
        self.initial_prompt_player_b = self.game_instance["initial_prompt_player_b"]
        
        self.location = self.game_instance['location']
        
        self.log_players({
            "GM": "Game master for datingsim",
            "Player 1": self.player_models[0].get_name(),
            "Player 2": self.player_models[1].get_name()}
        )

        self.log_key("n_turns", self.n_turns)

        self.further_prompt = self.game_instance["further_prompts"]
        self.further_prompt_a = self.further_prompt.replace("$character_name", self.game_instance["char_b"]["NAME"])
        self.further_prompt_b = self.further_prompt.replace("$character_name", self.game_instance["char_a"]["NAME"])

        self.reprompt_prompt = self.game_instance["reprompt_prompt"]


    def play(self):

        while self.proceed:

            self.log_next_turn()

            print(f"current turn:{self.current_turn}")

            # this would be the initial prompt
            # and the FIRST TURN
            if self.current_turn == 0:

                # Step 1a
                # GM to P1
                # Provides character sheet
                # initial prompt is (same for both): game description, goal, game rules, char-sheet
                # write first ("you are this person (char sheet A) and you write to another person (char sheet B)")
                self.add_message(self.player_a, utterance=self.initial_prompt_player_a)

                # P1 to GM
                # Writes a beginning message to P2
                answer_a = self.get_answer(self.player_a)

                # check if player a gives correct response
                is_valid_turn = self.check_validity_reprompt(answer_a, self.player_a)
                self.proceed = is_valid_turn
                if is_valid_turn == False:
                    self.log_key("completed_turns", self.turns_to_win_game)
                    break

                self.last_response = self.update_response(answer_a)


            # SECOND TURN - initial prompt for player2 
            elif self.current_turn == 1:

                # Step 1b - second TURN
                # GM to P2
                # Provides character sheet
                # initial prompt is (same for both): game description, goal, game rules, char-sheet
                # get written to ("you are this person (char sheet B) and another person (char sheet A) writes to you this *mess*")
                # + reply to P1

                b_initial_prompt = self.initial_prompt_player_b.replace("$message_player_A", self.last_response)
                self.add_message(self.player_b, utterance=b_initial_prompt)

                # P2 to GM
                # Answers begin message to P1
                answer_b = self.get_answer(self.player_b)

                # check if player a gives correct response
                is_valid_turn = self.check_validity_reprompt(answer_b, self.player_b)
                self.proceed = is_valid_turn
                if is_valid_turn == False:
                    self.log_key("completed_turns", self.turns_to_win_game)
                    break

                self.last_response = self.update_response(answer_b)

                # check if they found agreement|mismatched agreement
                self.proceed = self.check_for_agreement(self.last_sentiment, answer_b)
                if self.proceed == False:
                    self.log_key("completed_turns", self.turns_to_win_game)
                    break

                # if game continues: update recent sentiment and continue
                self.last_sentiment = self.update_sentiment(answer_b)

            # further turns after turn 0 and 1
            else:

                # based on turn number we can determine which player is supposed to be 
                # adressed
                # even numbers: player1 (writer) -> number%2 == False
                # odd numbers: player2 (responder) -> number%2 == True

                if self.current_turn % 2 == False:
                    self.player = self.player_a
                    utterance = self.further_prompt_a
                else:
                    self.player = self.player_b
                    utterance = self.further_prompt_b

                # GM -> Player
                # prepare further prompt 
                self.add_message(self.player, utterance=utterance.replace("$response", self.last_response))

                # Player -> GM
                # get answer from player
                answer = self.get_answer(self.player)

                # check if player a gives correct response
                is_valid_turn = self.check_validity_reprompt(answer, self.player)

                self.proceed = is_valid_turn

                if is_valid_turn == False:
                    self.log_key("completed_turns", self.turns_to_win_game)
                    break

                # update last response and sentiment
                self.last_response = self.update_response(answer)

                # check if they found agreement|mismatched agreement
                self.proceed = self.check_for_agreement(self.last_sentiment, answer)
                if self.proceed == False:
                    self.log_key("completed_turns", self.turns_to_win_game)
                    break

                # if game continues: update recent sentiment and continue
                self.last_sentiment = self.update_sentiment(answer)

            self.current_turn += 1
            self.complete_turns += 1

            if self.current_turn > self.n_turns:
                action = {'type': 'out of turns', 'content': 'game unsuccessful out of turns'}
                self.log_event(from_='GM', to='GM', action=action)
                self.log_key("completed_turns", self.turns_to_win_game)
                self.proceed = False


    def check_validity_reprompt(self, answer, player):
        """
        Disclaimer: Bad function name, feel free to change. Is the working name 
        I remember good now but misleading for people reading the code !!!


        Function which checks validity of given answer.
        If reprompt is not allowed, just uses the 'normal' validity
        check.
        If reprompting is allowed, then it goes through the beautiful
        while loop of repromting.

        Input:
        answer (str)    : Answer of the player to a given prompt.
        player (str)    : Player who gave the answer (player A or B)
        
        Output:
        valid (bool)    : returns True if the answer follows the template.
                            Returns False if the answer does not follow
                            the template or too many reprompts were used.
        """

        print("Checking validity")

        # if reprompting is not allowed, just use the normal one
        if self.re_prompt == False:
        
            valid = self.check_validity(answer)


        # if reprompting IS allowed, we get here
        else:

            # check if answer is valid - manually without the method
            # mostly take over what we have in the other function. But we log
            # and save information differently and include another loop
            # this prevents an infinite loop...

            # 1.: define answer pattern
            pattern_for_answer = r"\[reason\]\s.+\s\[end\]\s+\[sentiment\] (Overall Agreement|Agreement on Location|Agreement on Time|Agreement on Action|Continue Conversation) \[end\]\s+\[response\]\s.+\s\[end\]"
            
            # 2.: Define validity status of answer 
            valid = False 

            # 3.: Define while loop.
            """
            While loop runs until 
            1) answer is valid or
            2) max number of retries has been reached.
            """
            while True:

                # 3.1.: check status of valid
                # if it is True, answer of player fits pattern and game can continue
                if valid == True:

                    # 3.1.1.: increase counter of requests that conform rules
                    self.parsed_request_counts[self.current_turn] += 1

                    # 3.1.2.: log the fact that the answer was correct
                    action = {'type': 'parse',
                            'content': f'{answer} conforms to rules'}
                    self.log_event(from_='GM', to='GM', action=action)
                    break

                # 3.2 check if rempromt still allowed
                elif self.num_reprompts >= self.max_prompt_retries:
                    
                    # if not, abort game 
                    self.aborted = True

                    # log the abortion event
                    action = {'type': 'out of retries', 'content': 'Aborted'}
                    self.log_event(from_='GM', to='GM', action=action)
                    logger.info(f"out of retries")

                    # increase the counter of requests that violate form rules
                    self.violated_request_counts[self.current_turn] += 1

                    break

                # 3.3.: Check if follows answer pattern
                elif not re.fullmatch(pattern_for_answer, answer, re.DOTALL):
                    print("answer does not match the pattern !!")
                    # 3.3.1.: Log wrong answer pattern
                    action = {'type': 'invalid format', 'content': 'reprompt'}
                    print(f"action: {action}")
                    self.log_event(from_='GM', to='GM', action=action)
                    logger.info(f"invalid format")

                    # 3.3.2.: increase counter of requests that violate template
                    self.violated_request_counts[self.current_turn] += 1
                    print(f"number of violated requests: {self.violated_request_counts}")
                    self.num_reprompts += 1

                    # 3.3.3.: Reprompt to the player
                    self.add_reprompt(player, utterance=self.reprompt_prompt)

                    # 3.3.4.: Get answer from the player
                    answer = self.get_answer(player)
                
                    # 3.3.5.: Repeat while loop :)


                # 3.4.: check token length
                elif re.fullmatch(pattern_for_answer, answer, re.DOTALL) is not None:
                    
                    follows_num_tokens = self.check_token_length(answer)

                    if follows_num_tokens == False:
                        # 3.4.1.: log wrong format
                        action = {'type': 'invalid format', 'content': 'reprompt'}
                        self.log_event(from_='GM', to='GM', action=action)
                        logger.info(f"invalid format")

                        # 3.4.2.: increase counter of requests that violate template
                        self.violated_request_counts[self.current_turn] += 1
                        self.num_reprompts += 1

                        # 3.4.3.: Reprompt to the player
                        self.add_reprompt(player, utterance=self.reprompt_prompt)

                        # 3.4.4.: Get answer from the player
                        answer = self.get_answer(self.player)

                        # 3.4.5.: Repeat while loop :)

                    # 3.4.5.: If number is correct, the answer follows the template.
                    else:
                        valid = True

                # 3.5.: If none of the above happen, the answer follows the template.
                else:
                    valid = True 

        # valid is either True or False 
        return valid


    def check_validity(self, answer):
        
        """
        This function is being used to check if the given answer of a player
        follows the given template.
        But only if repromting is deactivated.
        Otherwise the other validity check will be conducted.
        """

        # define answer pattern
        pattern_for_answer = r"\[reason\]\s.+\s\[end\]\s+\[sentiment\] (Overall Agreement|Agreement on Location|Agreement on Time|Agreement on Action|Continue Conversation) \[end\]\s+\[response\]\s.+\s\[end\]"

        # check if the template is used correctly
        if not re.fullmatch(pattern_for_answer, answer, re.DOTALL):  # abort game

            # if re-prompt not allowed, ends the game
            self.aborted = True

            # log the abortion event
            action = {'type': 'invalid format', 'content': 'Aborted'}
            self.log_event(from_='GM', to='GM', action=action)
            logger.info(f"invalid format")

            # increase the counter of requests that violate form rules
            self.violated_request_counts[self.current_turn] += 1

            return False


        elif  re.fullmatch(pattern_for_answer, answer, re.DOTALL) is not None:
            follows_num_tokens = self.check_token_length(answer)
            
            if follows_num_tokens == False:
                self.aborted = True

                # log the abortion event
                action = {'type': 'invalid format', 'content': 'Aborted'}
                self.log_event(from_='GM', to='GM', action=action)
                logger.info(f"invalid format")

                # increase the counter of requests that violate form rules
                self.violated_request_counts[self.current_turn] += 1

                return False
            
            else:
                # increase the counter of requests that conform to form rules
                self.parsed_request_counts[self.current_turn] += 1
                # log the event that the string was valid (no strange characters)
                action = {'type': 'valid', 'content': 'valid string'}
                self.log_event(from_='GM', to='GM', action=action)

                # log the fact that the answer was correct
                action = {'type': 'parse',
                        'content': f'{answer} conforms to rules'}

                self.log_event(from_='GM', to='GM', action=action)
                return True


        # check, if we even need this else statement???
        # Bc so far, if pattern does not match - is catched by if statement
        # if num tokens does not match - catched by first elif statement
        # if pattern matches AND number of tokens is correct - also catched by first elif statement 

        # answer matches, continue game
        else:
        
            # increase the counter of requests that conform to form rules
            self.parsed_request_counts[self.current_turn] += 1
            # log the event that the string was valid (no strange characters)
            action = {'type': 'valid', 'content': 'valid string'}
            self.log_event(from_='GM', to='GM', action=action)

            # log the fact that the answer was correct
            action = {'type': 'parse',
                    'content': f'{answer} conforms to rules'}

            self.log_event(from_='GM', to='GM', action=action)
            return True

    def update_response(self, answer):
        """
        Update the last response said
        """
        # filter out the response 
        response_pattern = r"\[response\](.+)"
        response_match = re.search(response_pattern, answer, re.DOTALL)
        last_message = response_match.group(1)
        return last_message
    

    def update_sentiment(self, answer):
        """
        Function which fetches the sentiment of the answer
        """
        sentiment_pattern = r"\[sentiment\] (Overall Agreement|Agreement on Location|Agreement on Time|Agreement on Action|Continue Conversation) \[end\]"
        sentiment_match = re.search(sentiment_pattern, answer, re.DOTALL)
        last_sentiment = sentiment_match.group(1)
        return last_sentiment


    def check_for_agreement(self, last_sentiment, answer):
        """
        Function which checks if the players found an agreement. 
        Takes last message and new message.
        If last message == Found Agreement, new message must also be "Found Agreement"
        Otherwise the players lost the came by not proper communicating :)
        """    
        # get new sentiment from answer
        new_sentiment = self.update_sentiment(answer)

        if last_sentiment == "Agreement on Time":
            if self.time_agreement == True: # if they have already agreed for it, to penalize later or for smh like that

                # log the event that the sentimeents don't match
                action = {'type': 'already agreed', 'content': 'Agreement on Time was already achieved.'}
                self.log_event(from_='GM', to='GM', action=action)
                logger.info(f"Agreement on Time was already achieved")

                # return True as they have not finished the game yet
                return True 

            else:
                if new_sentiment != "Agreement on Time":
                    self.time_agreement = False

                    # log the event that the sentimeents don't match
                    action = {'type': 'no time agreement', 'content': 'no time agreement, mismatched sentiment'}
                    self.log_event(from_='GM', to='GM', action=action)
                    logger.info(f"no agreement on time at the same time")

                    # return True as they have not finished the game yet
                    return True 
                
                elif new_sentiment =="Agreement on Time":
                    self.time_agreement = True

                    action = {'type': 'time agreement', 'content': 'agreement on time successful'}
                    self.log_event(from_='GM', to='GM', action=action)
                    logger.info(f"successful agreement, agreement on time was settled")

                    # return True as they have not finished the game yet
                    return True
            
        elif last_sentiment == "Agreement on Location":
            if self.location_agreement == True: # if they have already agreed for it, to penalize later or for smh like that
                # log the event that the sentimeents don't match
                action = {'type': 'already agreed', 'content': 'Agreement on Location was already achieved.'}
                self.log_event(from_='GM', to='GM', action=action)
                logger.info(f"Agreement on Location was already achieved")

                # return True as they have not finished the game yet
                return True 

            else:
                if new_sentiment != "Agreement on Location":
                    self.location_agreement = False

                    # log the event that the sentimeents don't match
                    action = {'type': 'no location agreement', 'content': 'no location agreement, mismatched sentiment'}
                    self.log_event(from_='GM', to='GM', action=action)
                    logger.info(f"no agreement on location at the same time")

                    # return True as they have not finished the game yet
                    return True 
                
                elif new_sentiment == "Agreement on Location":
                    self.location_agreement = True
                    action = {'type': 'location agreement', 'content': 'agreement on location successful'}
                    self.log_event(from_='GM', to='GM', action=action)
                    logger.info(f"successful agreement, agreement on location was settled")

                    # return True as they have not finished the game yet
                    return True
    
        elif last_sentiment == "Agreement on Action":
            if self.action_agreement == True: # if they have already agreed for it, to penalize later or for smh like that
                # log the event that the sentimeents don't match
                action = {'type': 'already agreed', 'content': 'Agreement on Action was already achieved.'}
                self.log_event(from_='GM', to='GM', action=action)
                logger.info(f"Agreement on Action was already achieved")

                # return True as they have not finished the game yet
                return True 
            
            else:
                if new_sentiment != "Agreement on Action":
                    self.action_agreement = False

                    # log the event that the sentimeents don't match
                    action = {'type': 'no location agreement', 'content': 'no action agreement, mismatched sentiment'}
                    self.log_event(from_='GM', to='GM', action=action)
                    logger.info(f"no agreement on action at the same time")

                    # return True as they have not finished the game yet
                    return True 
                
                elif new_sentiment == "Agreement on Action":
                    self.action_agreement = True
                    action = {'type': 'action agreement', 'content': 'agreement on action successful'}
                    self.log_event(from_='GM', to='GM', action=action)
                    logger.info(f"successful agreement, agreement on action was settled")

                    # return True as they have not finished the game yet
                    return True
        
        elif last_sentiment == "Overall Agreement":
            if self.time_agreement == True and self.location_agreement == True and self.action_agreement == True: # if they have not agreed on Time/Location/Action
                if new_sentiment != "Overall Agreement":
                    self.aborted = True

                    # log the event that the sentimeents don't match
                    action = {'type': 'friendzone', 'content': 'game unsuccessful, mismatched sentiment'}
                    self.log_event(from_='GM', to='GM', action=action)
                    logger.info(f"lost game, no agreement at the same time")

                    return False
                
                elif new_sentiment == "Overall Agreement":
                    self.won = True
                    action = {'type': 'overall agreement', 'content': 'game successful'}
                    self.log_event(from_='GM', to='GM', action=action)
                    logger.info(f"won game, agreement was settled")

                    # update metric of how many turns they needed to win the game 
                    self.turns_to_win_game = self.current_turn + 1

                    logger.info(f"Players needed {self.turns_to_win_game} turns to win the game.")

                    # return false bc when they won we want to end the game
                    return False
            
            else: # if they have not agreed on Time/Location/Action
                self.aborted = True

                # log the event that the sentimeents don't match
                action = {'type': 'conditions not met', 'content': 'game unsuccessful, conditions have not met to finalize the game'}
                self.log_event(from_='GM', to='GM', action=action)
                logger.info(f"lost game, The player tried to finish the game before meeting the conditions")

                return False
        
        # otherwise continue
        else: # if players continued to conversation
            return True


    def check_token_length(self, answer):
        """
        Function to check if player follows 
        token length restriction.
        """
        # get response 
        response_pattern = r"\[response\](.+)"
        response_match = re.search(response_pattern, answer, re.DOTALL)

        response = response_match.group(1)
        # clean response from [response] and [end]
        cleaned_response = response.lstrip("[response] ").rstrip(" [end]")

        
        # split into tokens at whitespace 
        splitted_response = cleaned_response.split()
        
        num_tokens = len(splitted_response)

        # if below or even 100 return true
        if num_tokens <= 100:
            return True
        else:
            return False


##########################################################


class DatingSimGameScorer(GameScorer):
    def __init__(self, experiment: Dict, game_instance: Dict):
        super().__init__(GAME_NAME, experiment, game_instance)
        # TODO: add response patterns of players if you want to work on avg dialogue length and vocab size

    def compute_scores(self, episode_interactions: Dict) -> None:
        """
        TODO: 3 main metrics: 
            ++ we need to evaluate both players
            efficiency: number of turns taken to agree / max pre-defined number of turns
            agreement rate
            error handling: error counter?
            clemscore = efficiency * agreement rate - error handling
            (bonus) average dialogue length:
            (bonus) vocabulary size:
        
        """
        """Episode level scores"""
        max_n_turns = episode_interactions["n_turns"]
        turns = episode_interactions["turns"]
        #completed_turns = episode_interactions["completed_turns"]

        total_agreements = 0 # TODO: can there be more than one agreement per episode?
        turn_scores = []

        aborted = False

        # TODO look at the implementation of generated expression length from referencegame
        # TODO differentiate between Player 1 and Player 2 when the game is aborted

        for turn_idx, turn in enumerate(turns): 
            turn_score = {
                "last_message": None,
                "request_count": 0,
                "violated_request_count": 0,
                "parsed_request_count": 0,
                "reprompts_count": 0,
                "agreement": 0,
                "friendzone": 0,
                "out_of_reprompts": 0,
            }

            for event in turn:
                action = event["action"]

                if action["type"] == "invalid format":
                    turn_score["violated_request_count"] = 1
                    turn_score["parsed_request_count"] = 0
                    turn_score["aborted"] = 0
                    aborted = True
                
                if action["type"] == "parse":
                    turn_score["violated_request_count"] = 0
                    turn_score["parsed_request_count"] = 1
                
                if action["type"] == "reprompt": # error handling
                    # TODO: since we do not go to next turn, check if reprompt overrides the prev failed one's stats
                    turn_score["reprompts_count"] += 1
                    turn_score["violated_request_count"] += 1
                    turn_score["parsed_request_count"] = 0
                
                if action["type"] == "out_of_reprompts":
                    turn_score["out_of_reprompts"] = 1
                    aborted = True

                if action["type"] == "agreement": # agreement rate
                    turn_score["last_message"] = action["content"]
                    turn_score["agreement"] = 1

                if action["type"] == "friendzone": # mismatch_agreement
                    turn_score["last_message"] = action["content"]
                    turn_score["agreement"] = 0

                if action["type"] == "out of turns": # no agreement settled in max amount of turns
                    turn_score["agreement"] = 0

                turn_score["request_count"] = turn_score["violated_request_count"] + turn_score["parsed_request_count"]

            self.log_turn_score(turn_idx, METRIC_REQUEST_COUNT_VIOLATED, turn_score["violated_request_count"]) 
            self.log_turn_score(turn_idx, METRIC_REQUEST_COUNT_PARSED, turn_score["parsed_request_count"])
            self.log_turn_score(turn_idx, METRIC_REQUEST_COUNT, turn_score["request_count"])
            self.log_turn_score(turn_idx, 'Turn Reprompts', turn_score['reprompts_count']) 
            self.log_turn_score(turn_idx, 'Out of reprompts', turn_score["out_of_reprompts"])
            
            self.log_turn_score(turn_idx, 'Turn Agreement', turn_score["agreement"]) 
            self.log_turn_score(turn_idx, 'Turn Friendzone', turn_score["friendzone"])

            turn_scores.append(turn_score)
        
        violated_request_count = sum([turn["violated_request_count"] for turn in turn_scores])
        self.log_episode_score(METRIC_REQUEST_COUNT_VIOLATED, violated_request_count)

        parsed_request_count = sum([turn["parsed_request_count"] for turn in turn_scores])
        self.log_episode_score(METRIC_REQUEST_COUNT_PARSED, parsed_request_count)

        request_count = sum([turn["request_count"] for turn in turn_scores])
        self.log_episode_score(METRIC_REQUEST_COUNT, request_count)

        self.log_episode_score(METRIC_REQUEST_SUCCESS, parsed_request_count / request_count)
        
        efficiency = len(turns) / max_n_turns
        #efficiency_penalty = len(turns) / max_n_turns
        # efficiency = 1 - efficiency_penalty

        total_agreements = sum([turn["agreement"] for turn in turn_scores]) 
        total_friendzones = sum([turn["friendzone"] for turn in turn_scores]) 
        total_out_of_reprompts = sum([turn["out_of_reprompts"] for turn in turn_scores]) 

        
        error_handling = sum([turn["reprompts_count"] for turn in turn_scores]) 
        error_mapping = {0: 0, 1: 0.05, 2: 0.1}
        #error_handling = min(max(error_handling, 0), 0.1)  
        # 0.1 --> # of reprompting exceeded.
        # 0 --> # of reprompting is 0. all numbers needs to be normalised between 0-0.1

        self.log_episode_score("Efficiency", efficiency)
        self.log_episode_score("Total Agreement", total_agreements)
        self.log_episode_score("Error Handling", error_handling)

        self.log_episode_score("Total Friendzones", total_friendzones)
        self.log_episode_score("Total Out of reprompts", total_out_of_reprompts)
        
        # Common metrics
        if aborted:  # invalid format / ouf of reprompts
            self.log_episode_score(METRIC_ABORTED, 1)
            self.log_episode_score(METRIC_SUCCESS, 0)
            self.log_episode_score(METRIC_LOSE, 0)
            # Game-specific metrics 
            self.log_episode_score(BENCH_SCORE, np.nan)  # metric not applicable
        else:
            self.log_episode_score(METRIC_ABORTED, 0)
            if total_agreements > 0:
                self.log_episode_score(METRIC_SUCCESS, 1)
                self.log_episode_score(METRIC_LOSE, 0)
                self.log_episode_score(BENCH_SCORE, total_agreements - efficiency - error_handling)
            else:
                self.log_episode_score(METRIC_SUCCESS, 0)
                self.log_episode_score(METRIC_LOSE, 1)
                self.log_episode_score(BENCH_SCORE, 0)


##########################################################
##########################################################


class DatingSimGameBenchmark(GameBenchmark):

    def __init__(self):
        super().__init__(GAME_NAME)

    # defines whether the game is single player or not
    def is_single_player(self):
        return False

    # add a description of your game
    def get_description(self):
        return "A game where LLMs date"

    def create_game_master(
            self, experiment: Dict, player_models: List[Model]
    ) -> GameMaster:
        return DatingSimGameMaster(experiment=experiment, player_models=player_models)

    def create_game_scorer(self, experiment: Dict, game_instance: Dict) -> GameScorer:
        return DatingSimGameScorer(experiment, game_instance)