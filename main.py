#!/usr/bin/env python
import game_logic
import input_controller
from enum import Enum
def main():
    input_ctrl = input_controller.EventPoller()
    with game_factory(get_user_config()) as game:
        game.loop()
    return 0

def game_factory(user_config):
    if user_config.game_type == GameType.X01:
        return game_logic.Game501(user_config.num_players, user_config.input_ctrl)
    else:
        raise ValueError("Not supported yet.")

class GameType(Enum):
    X01 = 1,
    Cricket = 2,
    RoundTheClock = 3,

class UserConfig:
    def __init__(self, num_players, game_type, input_ctrl):
        if num_players < 1:
            raise ValueError("There must be at least one player in the game.")
        if not game_type:
            raise ValueError("No game selected.")
        self.num_players = num_players
        self.game_type = game_type
        self.input_ctrl = input_ctrl

def game_type_factory(number):
    if number == 1:
        return GameType.X01
    else:
        raise ValueError("Unsupported game type.")

def get_user_config():
    input_ctrl = input_controller.EventPoller()
    num_players = -1
    game_type = None
    print("num players:")
    while True:
        e = input_ctrl.next_event()
        if e.e_type == input_controller.EventType.NUMBER:
            num_players = e.value
            break
    print("game type:")
    while True:
        e = input_ctrl.next_event()
        if e.e_type == input_controller.EventType.NUMBER:
            game_type = game_type_factory(e.value)
            break
    return UserConfig(num_players, game_type, input_ctrl)    

if __name__ == "__main__":
    main()
