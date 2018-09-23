#!/usr/bin/env python
import game_logic
def main():
    with game_logic.Game501() as game:
        game.loop()
    return 0

if __name__ == "__main__":
    main()
