from ..logic.cricket import Cricket
from ..display.controller import DisplayController
from ..logic.common import GameType
from ..input.input_controller import EventPoller
from .game_x01 import GameX01


class UserConfig:
    def __init__(self, num_players, game):
        if num_players < 1:
            raise ValueError("There must be at least one player in the game.")
        if not game:
            raise ValueError("No game selected.")
        self.num_players = num_players
        self.game = game


def get_user_config(output_ctrl, input_ctrl):
    first_line = "no. players:"
    output_ctrl.lcd_set_first_line(first_line)
    num_players = input_ctrl.wait_for_next_number()
    first_line += " " + str(num_players)
    output_ctrl.lcd_set_first_line(first_line)

    second_line = "game type:"
    output_ctrl.lcd_set_second_line(second_line)
    game_id = input_ctrl.wait_for_next_number()
    game_type = GameType(game_id)
    second_line += " " + game_type.name
    output_ctrl.lcd_set_second_line(second_line, 0.50)
    return UserConfig(num_players, game_type)


def game_factory():
    input_ctrl = EventPoller()
    output_ctrl = DisplayController()
    user_config = get_user_config(output_ctrl, input_ctrl)
    if user_config.game == GameType.X01:
        return GameX01(user_config.num_players, input_ctrl, output_ctrl)
    elif user_config.game == GameType.Cricket:
        return Cricket(user_config.num_players, input_ctrl, output_ctrl)
    else:
        raise ValueError("Not supported yet.")
