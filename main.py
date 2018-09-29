#!/usr/bin/env python
import game_logic
import input_controller
from enum import Enum
from game_logic import GameType, UserConfig, game_factory

def main():
    input_ctrl = input_controller.EventPoller()
    with game_factory() as game:
        game.loop()
    return 0

if __name__ == "__main__":
    main()
