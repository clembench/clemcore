import copy
from typing import List, Dict
import random

import clemgame.metrics as ms
from clemgame.clemgame import GameMaster, GameBenchmark
from clemgame import get_logger
from games.dating_simulator.game import PC, NPC, Assistant

from games.dating_simulator.instancegenerator import GAME_NAME, GameInstanceGenerator


class DatingSimulatorGameMaster(GameMaster):
    """Implement mechanisms for playing Dating Simulator."""
    def __init__(self, experiment: Dict, player_backends: List[str]):
        super().__init__(GAME_NAME, experiment, player_backends)

        # save experiment and player attributes that will be necessary later
        self.location = experiment['location']  # Predefined for first level
        self.model_player = player_backends[0]
        self.model_npc = player_backends[1]
        self.model_assistant = player_backends[2]

        # initialise attributes that will be used for the evaluation scores
        self.aborted: bool = False
        self.lose: bool = False
        self.complete_turns: int = 0

    def setup(self, initial_location: str, game_id: int) -> None:
        """Setup the episode (mandatory)."""

        #Im not sure where all this stuff should be honestly
        # instantiate player, NPC, and assistant
        self.player = PC(self.model_player, 'player')
        self.npc = NPC(self.model_npc, 'npc')
        self.assistant = Assistant(self.model_assistant, 'assistant')

        # initialise game variables
        self.current_turn: int = 0
        self.location: str = initial_location

        # initialise common metrics
        self.request_counts = [0] * 3  # Assuming 3 interactions per level
        self.parsed_request_counts = [0] * 3
        self.violated_request_counts = [0] * 3

        # initial prompts
        prompt_player = self.load_template('resources/initial_prompts/pc.template')
        prompt_npc = self.load_template('resources/initial_prompts/npc.template')
        prompt_assistant = self.load_template('resources/initial_prompts/assistant.template')

        self.initiate(prompt_player, prompt_npc, prompt_assistant)

        # always log the details of the players in this format (see logdoc)
        self.log_players({
            'GM': 'Game master for Dating Simulator',
            'PC': f'Player: {self.model_player}',
            'NPC': f'NPC: {self.model_npc}',
            'Assistant': f'Assistant: {self.model_assistant}'
        })

        # log any additional keys that will be relevant for evaluation
        self.log_key('initial_location', initial_location)

    def initiate(self, prompt_player: str, prompt_npc: str, prompt_assistant: str) -> None:
        """Initialise the dialogue history (dating simulator specific)."""
        # always call log_next_turn what a turn starts
        self.log_next_turn()

        # append the initial message of each player to their history
        self.player.history.append({'role': 'system', 'content': prompt_player})
        self.npc.history.append({'role': 'system', 'content': prompt_npc})
        self.assistant.history.append({'role': 'system', 'content': prompt_assistant})

        # also log the messages as events for the transcriptions
        action = {'type': 'send message', 'content': prompt_player}
        self.log_event(from_='GM', to='PC', action=action)
        action = {'type': 'send message', 'content': prompt_npc}
        self.log_event(from_='GM', to='NPC', action=action)
        action = {'type': 'send message', 'content': prompt_assistant}
        self.log_event(from_='GM', to='Assistant', action=action)

    def play(self) -> None:
        """Run the game episode (mandatory)."""

        # Initial interaction sequence (steps 1 to 6)
        self.log_next_turn()

        # Step 1: GM asks PC
        # What is your age, gender?
        gm_to_pc_message = self.load_template('resources/questions/gm_to_pc.template')
        self.log_event(from_='GM', to='PC', action={'type': 'send message', 'content': gm_to_pc_message})
        self.player.history.append({'role': 'system', 'content': gm_to_pc_message})

        # Step 2: PC replies to GM
        # Im 666 year old potato
        player_message = self.player._custom_response(self.player.history, 1)
        self.log_event(from_='PC', to='GM', action={'type': 'send message', 'content': player_message})
        self.player.history.append({'role': 'assistant', 'content': player_message})

        # Step 3: GM asks PC again
        # Who do you wanna date?
        gm_to_pc_message = self.load_template('resources/questions/gm_to_pc2.template')
        self.log_event(from_='GM', to='PC', action={'type': 'send message', 'content': gm_to_pc_message})
        self.player.history.append({'role': 'system', 'content': gm_to_pc_message})

        # Step 4: PC replies to GM
        # I wanna date number 3
        player_message = self.player._custom_response(self.player.history, 2)
        self.log_event(from_='PC', to='GM', action={'type': 'send message', 'content': player_message})
        self.player.history.append({'role': 'assistant', 'content': player_message})

        # Step 5: GM writes to NPC
        # You are now this person, reply ready if u got it
        self.log_event(from_='GM', to='NPC', action={'type': 'send message', 'content': player_message})
        self.npc.history.append({'role': 'user', 'content': player_message})

        # Step 6: NPC responds to GM
        # ready
        npc_message = self.npc._custom_response(self.npc.history, 1)
        self.log_event(from_='NPC', to='GM', action={'type': 'send message', 'content': npc_message})
        self.npc.history.append({'role': 'user', 'content': npc_message})

        # Repeat steps 7 to 16 for four iterations
        for big_iteration in range(1, 5):
            dupa = "continue"

            while dupa == "continue":
                self.log_next_turn()

                # Step 7: GM asks PC
                # What main action u wanna?
                gm_to_pc_message = self.load_template('resources/questions/gm_to_pc3.template')
                self.log_event(from_='GM', to='PC', action={'type': 'send message', 'content': gm_to_pc_message})
                self.player.history.append({'role': 'system', 'content': gm_to_pc_message})

                # Step 8: PC replies to GM
                # I wanna do yoga
                player_message = self.player._custom_response(self.player.history, big_iteration)
                self.log_event(from_='PC', to='GM', action={'type': 'send message', 'content': player_message})
                self.player.history.append({'role': 'assistant', 'content': player_message})

                # Step 9: GM writes to NPC
                # your partner wanna do yoga, judge them
                self.log_event(from_='GM', to='NPC', action={'type': 'send message', 'content': player_message})
                self.npc.history.append({'role': 'user', 'content': player_message})

                # Step 10: NPC replies to GM
                # i judge them like this
                npc_message = self.npc._custom_response(self.npc.history, big_iteration)
                self.log_event(from_='NPC', to='GM', action={'type': 'send message', 'content': npc_message})
                self.npc.history.append({'role': 'user', 'content': npc_message})

                # GM makes a decision
                # Ok do i continue main action, change main action or end game?
                dupa = self.make_decision()  # Decide "continue", "try again", or "dumped"
                if dupa == "dumped":
                    break

                # Inner loop: Repeat steps 11 to 16 four times
                for small_iteration in range(1, 5):
                    if dupa != "continue":
                        break

                    kupa = "continue sub iter"
                    while kupa == "continue sub iter":
                        self.log_next_turn()

                        # Step 11: GM writes to ASSISTANT
                        # Gimme subactions for this main action yoga
                        gm_to_assistant_message = self.load_template('resources/questions/gm_to_assistant.template')
                        self.log_event(from_='GM', to='Assistant',
                                       action={'type': 'send message', 'content': gm_to_assistant_message})
                        self.assistant.history.append({'role': 'system', 'content': gm_to_assistant_message})

                        # Step 12: ASSISTANT replies to GM
                        # Ok here u have 4 subactions
                        assistant_message = self.assistant._custom_response(self.assistant.history, small_iteration)
                        self.log_event(from_='Assistant', to='GM',
                                       action={'type': 'send message', 'content': assistant_message})
                        self.assistant.history.append({'role': 'system', 'content': assistant_message})

                        # Step 13: GM asks PC
                        # What subaction u wanna do?
                        self.log_event(from_='GM', to='PC',
                                       action={'type': 'send message', 'content': assistant_message})
                        self.player.history.append({'role': 'system', 'content': assistant_message})

                        # Step 14: PC replies to GM
                        # I wanna make a backflip
                        player_message = self.player._custom_response(self.player.history, small_iteration)
                        self.log_event(from_='PC', to='GM', action={'type': 'send message', 'content': player_message})
                        self.player.history.append({'role': 'assistant', 'content': player_message})

                        # Step 15: GM writes to NPC
                        # Your date made a backflip, judge them
                        self.log_event(from_='GM', to='NPC', action={'type': 'send message', 'content': player_message})
                        self.npc.history.append({'role': 'user', 'content': player_message})

                        # Step 16: NPC responds to GM
                        # This is my judgment
                        npc_message = self.npc._custom_response(self.npc.history, small_iteration)
                        self.log_event(from_='NPC', to='GM', action={'type': 'send message', 'content': npc_message})
                        self.npc.history.append({'role': 'user', 'content': npc_message})

                        # GM makes a decision
                        # Should I continue main action but change sub action (still yoga but not backflip),
                        # Or go back to choose main action
                        # Or end game
                        kupa = self.make_sub_decision()  # Decide "continue sub iter", "continue main iter", or "success or dumped"
                        if kupa == "continue main iter":
                            dupa = kupa
                            break
                        elif kupa == "success or dumped":
                            dupa = kupa
                            break

            if dupa == "dumped" or dupa == "success or dumped":
                break

            self.current_turn += 1

        self.log_next_turn()
        # Log end of the game or any other wrap-up actions.

    def compute_scores(self, interactions: Dict) -> None:
        """Compute and log scores (mandatory)."""
        # Example of computing and logging scores
        self.log_episode_score('METRIC_COMPLETE_TURNS', self.current_turn)
        self.log_episode_score('METRIC_ABORTED', self.aborted)
        self.log_episode_score('METRIC_LOSE', self.lose)

    def make_sub_decision(self):

        # Option 1) Continue main action but change sub action (still yoga but not backflip),
        # Option 2) go back to choose main action
        # Option 3) end game
        pass


if __name__ == '__main__':
    random.seed(123)
    experiment = GameInstanceGenerator.generate()
    player_backends = ['player_model', 'npc_model', 'assistant_model']
    gm = DatingSimulatorGameMaster(experiment, player_backends)
    gm.setup(initial_location='cafe', game_id=1)
    gm.play()
    interactions = gm.get_interactions()
    gm.compute_scores(interactions)