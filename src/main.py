from src.logic.game_logic import game_factory


def main():
    while True:
        with game_factory() as game:
            game.loop()


if __name__ == "__main__":
    main()
