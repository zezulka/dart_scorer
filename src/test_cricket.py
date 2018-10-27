import unittest

from test_common import *
from input_controller import Event, EventType, Action
from game_logic import Cricket

class TestCricket(unittest.TestCase):
    def test_game_over(self):
         evs = [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.NUMBER, 0),
                   Event(EventType.ACTION, Action.CONFIRM),
               ]
         game = Cricket(1, TestingPoller(evs * 6), RENDERER)
         self.assertFalse(game.over())
