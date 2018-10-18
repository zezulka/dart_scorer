import unittest

from test_common import *
from game_logic import RendererCricket

def testing_renderer():
    return RendererCricket(TestingDisplayController())

class TestCricket(unittest.TestCase):
    def test_game_over(self):
         evs = [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.NUMBER, 0),
                   Event(EventType.ACTION, Action.CONFIRM),
               ]
         game = game_logic.Cricket(1, TestingPoller(evs * 6), testing_renderer())
         self.assertFalse(game.over())
