#!/usr/bin/env python3
import unittest
import game_logic
from queue import Queue
from input_controller import *
from game_logic import Renderer

# In testing, this should be no-op since
# the real implementation only directly controls
# displays.
# TODO: might add debug messages instead of only calling 'pass'es.

class TestingDisplayController:
    def __init__(self):
        pass     

    def segment_set_text(self, _):
        pass

    def lcd_set_first_line(self, _, _d = None):
        pass

    def lcd_set_second_line(self, _, _d = None):
        pass

    def clean_up(self):
        pass

class TestingPoller:
    def __init__(self, event_array):
        self.event_queue = Queue()
        self.fill_queue(event_array)

    # To be used in the initializer only.
    def fill_queue(self, event_array):
        for event in event_array:
            self.event_queue.put(event) 

    def next_event(self):
        if self.event_queue.empty():
            return None
        return self.event_queue.get()

def testing_renderer():
    return Renderer(TestingDisplayController())

class TestGameLogic(unittest.TestCase):
    def test_single_score(self):
        evs = [
                  Event(EventType.NUMBER, 1),
                  Event(EventType.NUMBER, 0),
                  Event(EventType.ACTION, Action.CONFIRM)
              ]
        game = game_logic.Game501(1, TestingPoller(evs), testing_renderer())
        self.assertEqual(game.players[0], 501)
        game.loop()
        # Points are ONLY subtracted iff the round is over.
        self.assertEqual(game.players[0], 501)

    def test_display_empty_after_one_round(self):
        evs = [
                  Event(EventType.NUMBER, 1),
                  Event(EventType.NUMBER, 0),
                  Event(EventType.ACTION, Action.CONFIRM)
              ]
        game = game_logic.Game501(1, TestingPoller(evs * 3), testing_renderer())
        game.loop()
        self.assertEqual(game.renderer.current_display_score, "  0 " * 3)

    def test_whole_round(self):
         evs = [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.NUMBER, 0),
                   Event(EventType.ACTION, Action.CONFIRM),
               ]
         game = game_logic.Game501(1, TestingPoller(evs * 3), testing_renderer())
         self.assertEqual(game.players[0], 501)
         game.loop()
         self.assertEqual(game.players[0], 471)
         self.assertEqual(game.renderer.current_display_score, "  0 " * 3)

    def test_two_rounds(self):
         evs = [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.NUMBER, 0),
                   Event(EventType.ACTION, Action.CONFIRM),
               ]
         game = game_logic.Game501(1, TestingPoller(evs * 6), testing_renderer())
         self.assertEqual(game.players[0], 501)
         game.loop()
         self.assertEqual(game.players[0], 441)
     
    def test_game_nine_finisher(self):
         evs = [
                   Event(EventType.NUMBER, 2),
                   Event(EventType.NUMBER, 0),
                   Event(EventType.ACTION, Action.TRIPLE),
                   Event(EventType.ACTION, Action.CONFIRM)
               ]
         evs = evs * 6
         evs += [
                   Event(EventType.NUMBER, 2),
                   Event(EventType.NUMBER, 0),
                   Event(EventType.ACTION, Action.TRIPLE),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]

         evs += [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.NUMBER, 9),
                   Event(EventType.ACTION, Action.TRIPLE),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]
         evs += [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.NUMBER, 2),
                   Event(EventType.ACTION, Action.DOUBLE),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]
         game = game_logic.Game501(1, TestingPoller(evs), testing_renderer())
         self.assertEqual(game.players[0], 501)
         game.loop()
         self.assertEqual(game.players[0], 0)
         self.assertTrue(game.over())

    def test_game_ten_finisher(self):
         evs = [
                   Event(EventType.NUMBER, 2),
                   Event(EventType.NUMBER, 0),
                   Event(EventType.ACTION, Action.TRIPLE),
                   Event(EventType.ACTION, Action.CONFIRM)
               ]
         evs = evs * 6
         evs += [
                   Event(EventType.NUMBER, 2),
                   Event(EventType.NUMBER, 0),
                   Event(EventType.ACTION, Action.TRIPLE),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]

         evs += [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.NUMBER, 9),
                   Event(EventType.ACTION, Action.TRIPLE),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]
         # Player misses the board
         evs += [  Event(EventType.ACTION, Action.CONFIRM) ]
         evs += [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.NUMBER, 2),
                   Event(EventType.ACTION, Action.DOUBLE),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]
         game = game_logic.Game501(1, TestingPoller(evs), testing_renderer())
         self.assertEqual(game.players[0], 501)
         game.loop()
         self.assertEqual(game.players[0], 0)
         self.assertTrue(game.over())

    def test_game_eleven_finisher(self):
         evs = [
                   Event(EventType.NUMBER, 2),
                   Event(EventType.NUMBER, 0),
                   Event(EventType.ACTION, Action.TRIPLE),
                   Event(EventType.ACTION, Action.CONFIRM)
               ]
         evs = evs * 6
         evs += [
                   Event(EventType.NUMBER, 2),
                   Event(EventType.NUMBER, 0),
                   Event(EventType.ACTION, Action.TRIPLE),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]

         evs += [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.NUMBER, 9),
                   Event(EventType.ACTION, Action.TRIPLE),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]
         # Player misses the board twice
         evs += [  
                   Event(EventType.ACTION, Action.CONFIRM),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]
         evs += [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.NUMBER, 2),
                   Event(EventType.ACTION, Action.DOUBLE),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]
         game = game_logic.Game501(1, TestingPoller(evs), testing_renderer())
         self.assertEqual(game.players[0], 501)
         game.loop()
         self.assertEqual(game.players[0], 0)
         self.assertTrue(game.over())

    def test_overthrow_after_ninth(self):
         evs = [
                   Event(EventType.NUMBER, 2),
                   Event(EventType.NUMBER, 0),
                   Event(EventType.ACTION, Action.TRIPLE),
                   Event(EventType.ACTION, Action.CONFIRM)
               ] * 9
         game = game_logic.Game501(1, TestingPoller(evs), testing_renderer())
         self.assertEqual(game.players[0], 501)
         game.loop()
         self.assertEqual(game.players[0], 501 - 3 * 20 * 6)
         self.assertFalse(game.over())

    def test_overthrow_after_tenth(self):
         evs = [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.NUMBER, 8),
                   Event(EventType.ACTION, Action.TRIPLE),
                   Event(EventType.ACTION, Action.CONFIRM)
               ]
         evs = evs * 9
         evs += [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.NUMBER, 6),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]
         game = game_logic.Game501(1, TestingPoller(evs), testing_renderer())
         self.assertEqual(game.players[0], 501)
         game.loop()
         self.assertEqual(game.players[0], 501 - 3 * 18 * 9)

    def test_overthrow_after_eleventh(self):
         evs = [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.NUMBER, 8),
                   Event(EventType.ACTION, Action.TRIPLE),
                   Event(EventType.ACTION, Action.CONFIRM)
               ]
         evs = evs * 9
         evs += [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.NUMBER, 4),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]
         evs += [
                   Event(EventType.NUMBER, 2),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]
         game = game_logic.Game501(1, TestingPoller(evs), testing_renderer())
         self.assertEqual(game.players[0], 501)
         game.loop()
         self.assertEqual(game.players[0], 501 - 3 * 18 * 9)

class TestPosition(unittest.TestCase):
    def test_add(self):
        second = game_logic.Position.FIRST
        second += 1
        self.assertEqual(game_logic.Position.SECOND, second)

if __name__ == "__main__":
    unittest.main()
