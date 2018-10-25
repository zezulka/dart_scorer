from functools import reduce
from time import sleep
from enum import IntEnum, Enum, unique
from abc import ABCMeta, abstractmethod

import input_controller

MULT_TO_STR = {1 : " ", 2 : "D", 3 : "T"}

class Multiplier(IntEnum):
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3

    def to_string(self):
        return MULT_TO_STR[self.value]

class Throw:
    def __init__(self, points, multiplier):
        isinstance(multiplier, Multiplier)
        self.points = points
        self.multiplier = multiplier

    def points_with_multiplier(self):
        return self.points * self.multiplier.value

def zero_throw():
    return Throw(0, Multiplier.SINGLE)

@unique
class Position(IntEnum):
    FIRST = 0
    SECOND = 1
    THIRD = 2

    # https://docs.python.org/3/reference/datamodel.html#special-method-names
    # += operator
    def __add__(self, other):
        other = other % 3
        return self.__from_int((other + self.value) % 3)

    def __from_int(self, i):
        if i == 0:
            return Position.FIRST
        elif i == 1:
            return Position.SECOND
        elif i == 2:
            return Position.THIRD
        raise ValueError("The integer passed must be in {0,1,2}.")

    def to_int(self):
        return self.value

class GameRound:
    def __init__(self):
        self.__throws = [zero_throw()] * 3
        self.__current_position = Position.FIRST

    def clear(self):
        self.__init__()

    def current_throw(self):
        return self.__throws[self.__current_position]

    def current_position_int(self):
        return self.__current_position.value

    def hop_to_next_position(self):
        self.__current_position += 1

    def set_current_position(self, pos):
        self.__current_position = pos

    def set_current_throw(self, throw):
        self.__throws[self.__current_position] = throw

    def points(self):
        return reduce(lambda acc, next_: acc + next_.points,
                      filter(lambda throw: throw is not None, self.__throws), 0)

def get_user_config(renderer, input_ctrl):
    num_players = -1
    game_type = None
    first_line = "no. players:"
    renderer.prompt_text_first_line(first_line)
    num_players = input_ctrl.wait_for_next_number()
    first_line += " " + str(num_players)
    renderer.prompt_text_first_line(first_line)

    second_line = "game type:"
    renderer.prompt_text_second_line(second_line)
    game_id = input_ctrl.wait_for_next_number()
    game_type = GameType(game_id)
    second_line += " " + game_type.name
    renderer.prompt_text_second_line(second_line, 0.50)
    renderer.empty_lcd()
    return UserConfig(num_players, game_type)

def game_factory():
    input_ctrl = input_controller.EventPoller()
    renderer = Renderer(DisplayController())
    user_config = get_user_config(renderer, input_ctrl)
    if user_config.game_type == GameType.X01:
        return Game501(user_config.num_players, input_ctrl, renderer)
    elif user_config.game_type == GameType.Cricket:
        return Cricket(user_config.num_players, input_ctrl, renderer)
    else:
        raise ValueError("Not supported yet.")

class GameType(Enum):
    X01 = 1
    Cricket = 2
    RoundTheClock = 3

class UserConfig:
    def __init__(self, num_players, game_type):
        if num_players < 1:
            raise ValueError("There must be at least one player in the game.")
        if not game_type:
            raise ValueError("No game selected.")
        self.num_players = num_players
        self.game_type = game_type

def lcd_set_line(set_fun, text, duration):
    set_fun(text)
    if duration > 0:
        sleep(duration)
        set_fun("")

class DisplayController:
    def __init__(self):
        # We want to be able to run tests (HW dependless) everywhere
        import lcd_display
        import max7219_controller
        self.segment_d = max7219_controller.MAX7219()
        self.lcd_d = lcd_display.LcdDisplay()

    def segment_set_text(self, text):
        self.segment_d.show_message(text)

    def lcd_set_first_line(self, text, duration=-1.0):
        lcd_set_line(self.lcd_d.first_line, text, duration)

    def lcd_set_second_line(self, text, duration=-1.0):
        lcd_set_line(self.lcd_d.second_line, text, duration)

    def clean_up(self):
        self.lcd_d.clean_up()
        self.segment_d.clean_up()

class Renderer:
    def __init__(self, displ_ctrl):
        self.__init_display_score = "  0 " * 3
        self.current_display_score = self.__init_display_score
        self.displ_ctrl = displ_ctrl

    def prompt_text_first_line(self, text):
        self.displ_ctrl.lcd_set_first_line(text)

    def prompt_text_second_line(self, text, duration=-1.0):
        self.displ_ctrl.lcd_set_second_line(text, duration)

    def clear_lcd(self):
        self.current_display_score = self.__init_display_score
        self.score()

    def empty_lcd(self):
        self.displ_ctrl.lcd_set_first_line("")
        self.displ_ctrl.lcd_set_second_line("")
        self.current_display_score = self.__init_display_score

    def clean_up(self):
        self.displ_ctrl.clean_up()

    def points(self, points):
        self.displ_ctrl.segment_set_text(str(points))

    def score(self):
        self.displ_ctrl.lcd_set_first_line(self.current_display_score)

    def warning(self, text):
        warning_duration = 0.75
        self.displ_ctrl.lcd_set_second_line(text, warning_duration)

class Game(metaclass=ABCMeta):
    def __init__(self, num_players, input_ctrl, renderer):
        self.round = GameRound()
        self.renderer = renderer
        self.input_ctrl = input_ctrl
        self.num_players = num_players
        self.current_player = 0
        self.force_quit = False

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _tb):
        self.renderer.clean_up()

    def loop(self):
        while not self.over():
            self.refresh()
            next_event = self.input_ctrl.next_event()
            if not next_event:
                return
            if next_event.e_type == input_controller.EventType.NUMBER:
                self.digit_submitted(next_event.value)
            elif next_event.e_type == input_controller.EventType.ACTION:
                self.action_submitted(next_event.value)

    @abstractmethod
    def refresh(self):
        """ At the beginning of each game cycle, this method is called so that
new information is displayed on the output devices (usually a set of displays)."""
        pass

    @abstractmethod
    def over(self):
        pass

    @abstractmethod
    def digit_submitted(self, _):
        pass

    @abstractmethod
    def action_submitted(self, _):
        pass

def cricket_init():
    result = [(0, i) for i in range(15, 21)]
    result.append((0, 25))
    return [result]

class Cricket(Game):
    def __init__(self, num_players, input_ctrl, renderer):
        super().__init__(num_players, input_ctrl, renderer)
        self.players = cricket_init() * num_players

    def over(self):
        return self.force_quit or reduce(lambda so_far, player: so_far or
                                         reduce(lambda in_so_far, tup: in_so_far and tup[0] == 3,
                                                player, True), self.players, False)

    def refresh(self):
        pass

    def digit_submitted(self, value):
        pass

    def action_submitted(self, value):
        pass

class Game501(Game):

    def __init__(self, num_players, input_ctrl, renderer):
        super().__init__(num_players, input_ctrl, renderer)
        self.players = [501] * num_players

    def over(self):
        return self.force_quit or reduce(lambda x, y: x or y == 0, self.players, False)

    def refresh(self):
        self.__highlight_current_throw()
        self.renderer.score()
        self.renderer.points(self.__points_to_string())

    def action_submitted(self, action):
        points_nominal = self.round.current_throw().points
        if action == input_controller.Action.DOUBLE:
            self.round.set_current_throw(Throw(points_nominal, Multiplier.DOUBLE))
        elif action == input_controller.Action.TRIPLE:
            if points_nominal == 25:
                self.renderer.warning("25T not valid!")
            else:
                self.round.set_current_throw(Throw(points_nominal, Multiplier.TRIPLE))
        elif action == input_controller.Action.CONFIRM:
            curr_pts = curr_pts = self.players[self.current_player] - self.round.points()
            if curr_pts < 0:
                self.renderer.warning("Overthrow!")
            self.round.hop_to_next_position()
            if self.round.current_position_int() == 1 or curr_pts <= 0:
                self.__next_round()
        elif action == input_controller.Action.CLEAR:
            self.round.set_current_throw(zero_throw())
        elif action == input_controller.Action.RESTART:
            self.force_quit = True
        elif action == input_controller.Action.UNDO and\
             self.round.current_position_int() != Position.FIRST:
            self.round.hop_to_next_position() # 2 is congruent to -1 (mod 3)
            self.round.hop_to_next_position()
            self.round.set_current_throw(zero_throw())

    def digit_submitted(self, digit):
        digit = digit
        throw = self.round.current_throw()
        points_nominal = throw.points
        multiplier = throw.multiplier
        if points_nominal == 0:
            self.round.set_current_throw(Throw(digit, multiplier))
        elif points_nominal == 1:
            self.round.set_current_throw(Throw(points_nominal * 10 + digit, multiplier))
        elif points_nominal == 2:
            points_cand = points_nominal * 10 + digit
            if digit == 0 or (digit == 5 and multiplier != Multiplier.TRIPLE):
                self.round.set_current_throw(Throw(points_cand, multiplier))
            else:
                self.renderer.warning(str(points_cand) + multiplier.to_string() + " not valid!")
        else:
            self.renderer.warning("hit <-")

    def __next_round(self):
        curr_pts = self.players[self.current_player] - self.round.points()
        if curr_pts >= 0:
            self.players[self.current_player] = curr_pts
        self.renderer.clear_lcd()
        self.current_player = (self.current_player + 1) % self.num_players
        self.round.clear()

    def __score_for_current_throw(self):
        """Returns a string of length 4 representing the current throw. This string
will then be represented to the user. Structrute of the string is defined as follows:
    at the last position, there will be a multiplier (empty space indicates single,
    D stands for double and T stands for triple) which will be preceded by a valid
    number (also in the context of the multiplier, i.e. no " 25T") padded by a
    sequence of spaces from the left.

Examples of valid strings:
"  0T"
" 20 "
" 19D"
"  1 "

Examples of illegal strings:
"    "
" 200"
" 1  "
"   D"
"12D "
"""
        throw = self.round.current_throw()
        return "{:3}".format(throw.points) + throw.multiplier.to_string()

    def __highlight_current_throw(self):
        no = self.round.current_position_int() * 4
        aux_str = "####" + " " * 8
        aux_str = aux_str[-no:] + aux_str[:-no]
        self.renderer.prompt_text_second_line(aux_str)

    def __points_to_string(self):
        """ Returns a string representation of the score for the current player."""
        curr_points = str(self.players[self.current_player] - self.round.points())
        if self.num_players == 1:
            return curr_points
        points = ""
        if self.current_player % 2 == 0:
            points += curr_points
            next_player_pos = self.current_player + 1
            if next_player_pos != self.num_players:
                points = "{:4}".format(points)
                points += str(self.players[next_player_pos])
        else:
            points += "{:4}".format(str(self.players[self.current_player - 1]))
            points += curr_points
        return points
