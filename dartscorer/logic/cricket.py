from .common import Game, GameVisitor
from functools import reduce
from collections import OrderedDict


class Confirm(GameVisitor):
    def visit(self, game):
        thrw = game.round.current_throw()
        (pts, mult) = (thrw.points, thrw.multiplier)
        if pts >= 15:
            next_score = game.players[game.current_player][pts] + mult
            if next_score > 3:
                next_score = 3
            game.players[game.current_player][pts] = next_score
        game.round.hop_to_next_position()
        if game.round.is_over():
            game.next_round()


def cricket_score_init():
    """
    :return: Map ordered by keys. The map depicts the initial state of a cricket game.
    """
    result = {i: 0 for i in range(15, 21)}
    result[25] = 0
    return OrderedDict(sorted(result.items(), key=lambda t: t[0]))


class Cricket(Game):
    def __init__(self, num_players, input_ctrl, output_ctrl):
        super().__init__(num_players, input_ctrl, output_ctrl)
        aux = []
        for i in range(0, num_players):
            aux.append(cricket_score_init())
        self.players = aux

    def over(self):
        return self.force_quit or reduce(lambda so_far, player: so_far or
                                                                reduce(lambda in_so_far, tup: in_so_far and tup == 3,
                                                                       player.values(), True), self.players, False)

    def confirm_action(self):
        return Confirm

    def restart(self):
        self.force_quit = True

    def refresh(self):
        point_str = self.__points_to_string()
        self.output_ctrl.lcd_set_first_line(point_str[0])
        self.output_ctrl.lcd_set_second_line(point_str[1])
        self.output_ctrl.segment_set_text(self.__game_round_to_string())

    def next_round(self):
        self.current_player = (self.current_player + 1) % self.num_players
        self.round.clear()

    def __points_to_string(self):
        first = ""
        second = ""
        curr_player = self.players[self.current_player]
        for key in curr_player:
            displ_key = key
            thrown = curr_player[key]
            if thrown == 3:
                displ_key = ""
                thrown = ""
            first += "{:2}".format(displ_key)
            second += "{:2}".format(thrown)
            # Just to separate the displayed numbers.
            # We don't have that much space (16 cells)
            #     but at least make an effort.
            if key != 25 and (key == 17 or key == 19):
                first += " "
                second += " "
        return [first, second]

    def __game_round_to_string(self):
        curr_thrw = self.round.current_throw()
        if curr_thrw.points == 0:
            return ""
        return "{:4}".format(str(curr_thrw.points) + curr_thrw.multiplier.to_string().lower()) + "thr" + \
               str(self.round.current_position_int() + 1)
