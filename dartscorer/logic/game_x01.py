from functools import reduce

from ..input.input_controller import Action
from .common import Game, Multiplier, Throw, zero_throw


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
        if action == Action.DOUBLE:
            self.round.set_current_throw(Throw(points_nominal, Multiplier.DOUBLE))
        elif action == Action.TRIPLE:
            if points_nominal == 25:
                self.output_ctrl.warning("25T not valid!")
            else:
                self.round.set_current_throw(Throw(points_nominal, Multiplier.TRIPLE))
        elif action == Action.CONFIRM:
            self.round.hop_to_next_position()
            curr_pts = self.players[self.current_player] - self.round.points()
            if curr_pts < 0:
                self.output_ctrl.warning("Overthrow!")
            if curr_pts <= 0 or self.round.is_over():
                self.__next_round()
        elif action == Action.CLEAR:
            self.round.set_current_throw(zero_throw())
        elif action == Action.RESTART:
            self.force_quit = True
        elif action == Action.UNDO and \
                not self.round.is_first_throw():
            self.round.hop_to_next_position()  # 3 is congruent to -1 (mod 4)
            self.round.hop_to_next_position()
            self.round.hop_to_next_position()
            self.round.set_current_throw(zero_throw())

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
