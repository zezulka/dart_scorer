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
    OVER = 3

    # https://docs.python.org/3/reference/datamodel.html#special-method-names
    # += operator
    def __add__(self, other):
        other = other % 4
        return self.__from_int((other + self.value) % 4)

    def __from_int(self, i):
        if i == 0:
            return Position.FIRST
        elif i == 1:
            return Position.SECOND
        elif i == 2:
            return Position.THIRD
        elif i == 3:
            return Position.OVER
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

    def is_first_throw(self):
        return self.__current_position == Position.FIRST

    def is_over(self):
        return self.__current_position == Position.OVER

    def hop_to_next_position(self):
        self.__current_position += 1

    def set_current_position(self, pos):
        self.__current_position = pos

    def set_current_throw(self, throw):
        self.__throws[self.__current_position] = throw

    def to_string(self):
        result = ""
        for throw in self.__throws:
            result += "{:3}".format(throw.points) + throw.multiplier.to_string()
        return result

    def points(self):
        """ Returns number of points which were scored for the given game round and were confirmed by the player. """
        return reduce(lambda acc, next_: acc + next_.points, self.__throws[:self.__current_position.to_int()], 0)

def get_user_config(output_ctrl, input_ctrl):
    num_players = -1
    game_type = None
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
    input_ctrl = input_controller.EventPoller()
    output_ctrl = DisplayController()
    user_config = get_user_config(output_ctrl, input_ctrl)
    if user_config.game_type == GameType.X01:
        return Game501(user_config.num_players, input_ctrl, output_ctrl)
    elif user_config.game_type == GameType.Cricket:
        return Cricket(user_config.num_players, input_ctrl, output_ctrl)
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
    """ Class used for controlling output devices used in the game.
 This class shouldn't be used in tests since it is dependent on
 modules which directly work with physical displays. """
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

    def warning(self, text):
        """ Just a simple shortcut to displaying a message to the
second row of the LCD display which will disapear after a given
magic time constant."""
        self.lcd_set_second_line(text, 0.75)

    def clean_up(self):
        self.lcd_d.clean_up()
        self.segment_d.clean_up()

class Game(metaclass=ABCMeta):
    def __init__(self, num_players, input_ctrl, output_ctrl):
        self.round = GameRound()
        self.output_ctrl = output_ctrl
        self.input_ctrl = input_ctrl
        self.num_players = num_players
        self.current_player = 0
        self.force_quit = False

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _tb):
        self.output_ctrl.clean_up()

    def loop(self):
        """ Runs a game loop until the game is over. First, output devices
are refreshed with new game data and then the game waits for new events.
Game ends whether the self.over() returns True or there are no more other
events. """
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
        """ Returns a boolean value. True if the game is over, false otherwise."""
        pass

    @abstractmethod
    def digit_submitted(self, _):
        """ This method takes a digit as its input and modifies internal state of the
game object according to the game rules and the digit itself."""
        pass

    @abstractmethod
    def action_submitted(self, _):
        """ This method takes an action as its input and modifies internal state of the
game object according to the game rules and the action itself."""
        pass

def cricket_init():
    result = [(0, i) for i in range(15, 21)]
    result.append((0, 25))
    return [result]

class Cricket(Game):
    def __init__(self, num_players, input_ctrl, output_ctrl):
        super().__init__(num_players, input_ctrl, output_ctrl)
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

    def __init__(self, num_players, input_ctrl, output_ctrl):
        super().__init__(num_players, input_ctrl, output_ctrl)
        self.players = [501] * num_players

    def over(self):
        return self.force_quit or reduce(lambda x, y: x or y == 0, self.players, False)

    def refresh(self):
        self.__highlight_current_throw()
        self.output_ctrl.lcd_set_first_line(self.__game_round_to_string())
        self.output_ctrl.segment_set_text(self.__points_to_string())

    def action_submitted(self, action):
        points_nominal = self.round.current_throw().points
        if action == input_controller.Action.DOUBLE:
            self.round.set_current_throw(Throw(points_nominal, Multiplier.DOUBLE))
        elif action == input_controller.Action.TRIPLE:
            if points_nominal == 25:
                self.output_ctrl.warning("25T not valid!")
            else:
                self.round.set_current_throw(Throw(points_nominal, Multiplier.TRIPLE))
        elif action == input_controller.Action.CONFIRM:
            self.round.hop_to_next_position()
            curr_pts = curr_pts = self.players[self.current_player] - self.round.points()
            if curr_pts < 0:
                self.output_ctrl.warning("Overthrow!")
            if curr_pts < 0 or self.round.is_over():
                self.__next_round()
        elif action == input_controller.Action.CLEAR:
            self.round.set_current_throw(zero_throw())
        elif action == input_controller.Action.RESTART:
            self.force_quit = True
        elif action == input_controller.Action.UNDO and\
             not self.round.is_first_throw():
            self.round.hop_to_next_position() # 3 is congruent to -1 (mod 4)
            self.round.hop_to_next_position()
            self.round.hop_to_next_position()
            self.round.set_current_throw(zero_throw())

    def digit_submitted(self, digit):
        throw = self.round.current_throw()
        points_nominal = throw.points
        multiplier = throw.multiplier
        if points_nominal == 0:
            self.round.set_current_throw(Throw(digit, multiplier))
        elif points_nominal == 1:
            self.round.set_current_throw(Throw(10 + digit, multiplier))
        elif points_nominal == 2:
            points_cand = 20 + digit
            if digit == 0 or (digit == 5 and multiplier != Multiplier.TRIPLE):
                self.round.set_current_throw(Throw(points_cand, multiplier))
            else:
                self.output_ctrl.warning(str(points_cand) + multiplier.to_string() + " not valid!")
        else:
            self.output_ctrl.warning("hit <-")

    def __game_round_to_string(self):
        """ Returns a string representation of the current game round. In the case of X01,
 we show the player nominal value of each throw."""
        return self.round.to_string()

    def __next_round(self):
        curr_pts = self.players[self.current_player] - self.round.points()
        if curr_pts >= 0:
            self.players[self.current_player] = curr_pts
        self.current_player = (self.current_player + 1) % self.num_players
        self.round.clear()

    def __highlight_current_throw(self):
        no = self.round.current_position_int() * 4
        aux_str = "####" + " " * 8
        aux_str = aux_str[-no:] + aux_str[:-no]
        self.output_ctrl.lcd_set_second_line(aux_str)

    def __points_to_string(self):
        """ Returns a string representation of the score. Since the segment display has got
 limited display capacity, score of only two most recent players (starting with a player
 whose index in the player array is even) is diplayed. """
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
