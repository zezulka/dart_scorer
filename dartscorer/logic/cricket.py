from .common import Game
from functools import reduce

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