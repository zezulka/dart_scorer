import unittest
import game_logic
from queue import Queue
from input_controller import *

class TestingPoller:
    def __init__(self, event_array):
        self.event_queue = Queue()
        self.fill_queue(event_array)

    # To be used in the initializer only.
    def fill_queue(self, event_array):
        for event in event_array:
            self.event_queue.put(event) 

    def next_event(self):
        return self.event_queue.get()

# Just a noop implementation
class TestingRenderer:
    def action(_, __):
        pass

    def score(_, __):
        pass

    def warning(_, __):
        pass

class TestGameLogic(unittest.TestCase):
    def test_score_substitution(self):
        evs = [
                  Event(EventType.NUMBER, 1),
                  Event(EventType.NUMBER, 0),
                  Event(EventType.ACTION, Action.CONFIRM)
              ]
        game = game_logic.Game501(TestingPoller(evs), TestingRenderer())
        self.assertEqual(game.current_score, " " * 12)
        
        self.assertEqual(game.current_score, " 12D" + " " * 8)

if __name__ == "__main__":
    unittest.main()
