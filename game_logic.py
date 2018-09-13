class Throw:
    def __init__(self, points, multiplier):
        self.points = points
        self.multiplier = multiplier

    def points(self):
        return self.points * self.multiplier

class GameRound:
    def __init__(self):
        self.first_throw = Throw()
        self.second_throw = Throw()
        self.third_throw = Throw()

    def clear(self):
        self.__init__()

    def points(self):
        return self.first_throw.points() + self.second_throw.points() + self.third_throw.points()

class Game501:
    def __init__(self):
        self.points = 501
        self.darts_thrown = 0
        self.round = GameRound()

    def next_round(self):
        self.points -= self.round.points()
        self.game_round.clear()
