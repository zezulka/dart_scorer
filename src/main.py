import game_logic
import input_controller
from enum import Enum
from game_logic import GameType, UserConfig, game_factory

def main():
    while True:
        with game_factory() as game:
            game.loop()
    return 0

if __name__ == "__main__":
    main()
