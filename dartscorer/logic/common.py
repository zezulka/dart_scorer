from functools import reduce
from enum import IntEnum, Enum, unique
from abc import ABCMeta, abstractmethod

from ..input import input_controller
from ..input.input_controller import Action

MULTIPLIER_TO_STR = {1: " ", 2: "D", 3: "T"}


class GameVisitor:
    """ Class representing abstract actions from the game logic point of view."""

    """ Each extending class defines a behaviour for the given action. Most of 
the actions will be very similar (or even the same)."""

    @abstractmethod
    def visit(self, _game):
        pass


class Double(GameVisitor):
    def visit(self, game):
        game.round.set_current_throw(Throw(game.round.current_throw().points, Multiplier.DOUBLE))


class Triple(GameVisitor):
    def visit(self, game):
        points_nominal = game.round.current_throw().points
        if points_nominal == 25:
            game.output_ctrl.warning("25T not valid!")
        else:
            game.round.set_current_throw(Throw(points_nominal, Multiplier.TRIPLE))


class Clear(GameVisitor):
    def visit(self, game):
        game.round.set_current_throw(zero_throw())


class Restart(GameVisitor):
    def visit(self, game):
        game.force_quit = True


class Undo(GameVisitor):
    def visit(self, game):
        game.round.hop_to_next_position()  # 3 is congruent to -1 (mod 4)
        game.round.hop_to_next_position()
        game.round.hop_to_next_position()
        game.round.set_current_throw(zero_throw())


# KEY_NUMLOCK

ACTION_TO_VISITOR_DICT = {
    Action.TRIPLE: Triple,
    Action.DOUBLE: Double, Action.CLEAR: Clear,
    Action.RESTART: Restart, Action.UNDO: Undo
}


class Multiplier(IntEnum):
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3

    def to_string(self):
        return MULTIPLIER_TO_STR[self.value]


class Throw:
    def __init__(self, points, multiplier):
        isinstance(multiplier, Multiplier)
        self.points = points
        self.multiplier = multiplier

    def total_points(self):
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
        return reduce(lambda acc, next_: acc + next_.total_points(), self.__throws[:self.__current_position.to_int()],
                      0)


class GameType(Enum):
    X01 = 1
    Cricket = 2
    RoundTheClock = 3


class Game(metaclass=ABCMeta):
    def __init__(self, num_players, input_ctrl, output_ctrl):
        self.round = GameRound()
        self.output_ctrl = output_ctrl
        self.input_ctrl = input_ctrl
        self.num_players = num_players
        self.current_player = 0
        self.force_quit = False
        self.config = self.default_config()
        self.action_to_visitor_dict = ACTION_TO_VISITOR_DICT
        self.action_to_visitor_dict[Action.CONFIRM] = self.confirm_action()

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _tb):
        self.output_ctrl.clean_up()

    @abstractmethod
    def refresh(self):
        """ At the beginning of each game cycle, this method is called so that
new information is displayed to the output devices (usually a set of displays)."""
        pass

    @abstractmethod
    def over(self):
        """:return: True if the game is over, False otherwise."""
        pass

    @abstractmethod
    def confirm_action(self):
        """ The action Action.CONFIRM is usually the one which differs the most among games.
Each is game is required to implement handler to this action as no abstract implementation
would make no sense here.
        """
        pass

    @abstractmethod
    def default_config(self):
        """
        :return: vector of constraints which are interesting to the game
        """
        pass

    def action_submitted(self, action):
        """ This method takes an action as its input and modifies internal state of the
game object according to the game rules and the action itself."""
        self.action_to_visitor_dict[action]().visit(self)

    def digit_submitted(self, digit):
        """ This method takes a digit as its input and modifies internal state of the
game object according to the game rules and the digit itself."""

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
