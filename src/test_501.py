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

class Test501GameLogic(unittest.TestCase):
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

    def test_triple_bulls_eye(self):
         evs =  [
                   Event(EventType.NUMBER, 2),
                   Event(EventType.NUMBER, 5),
                   Event(EventType.ACTION, Action.TRIPLE),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]
         evs +=  [
                   Event(EventType.ACTION, Action.CONFIRM),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]
         game = game_logic.Game501(1, TestingPoller(evs), testing_renderer())
         self.assertEqual(game.players[0], 501)
         game.loop()
         # Note: the first throw will be "25" since the intermediate result is not erased
         # so, the sequence goes like this: "2" -> "25" -> "25" (with the error message of "25T" of not being valid)
         self.assertEqual(game.players[0], 476)

    def test_triple_bulls_eye_second_corner_case(self):
         evs =  [
                   Event(EventType.ACTION, Action.TRIPLE),
                   Event(EventType.NUMBER, 2),
                   Event(EventType.NUMBER, 5),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]
         evs +=  [
                   Event(EventType.ACTION, Action.CONFIRM),
                   Event(EventType.ACTION, Action.CONFIRM)
                ]
         game = game_logic.Game501(1, TestingPoller(evs), testing_renderer())
         self.assertEqual(game.players[0], 501)
         game.loop()
         # Note: the first throw will be "2" since the intermediate result is not erased
         # so, the sequence goes like this: "T" -> "2T" -> "2T" (with the error message of "25T" of not being valid)
         self.assertEqual(game.players[0], 495)

    def test_points_to_segment_display_string_one_person_throw(self):
         evs = [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.ACTION, Action.CONFIRM)
               ]
         game = game_logic.Game501(1, TestingPoller(evs), testing_renderer())
         self.assertEqual(game.points_to_segment_display_string(), "501")
         game.loop()
         self.assertEqual(game.points_to_segment_display_string(), "500")

    def test_points_to_segment_display_string_one_person_round(self):
         evs = [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.ACTION, Action.CONFIRM)
               ] * 3
         game = game_logic.Game501(1, TestingPoller(evs), testing_renderer())
         self.assertEqual(game.points_to_segment_display_string(), "501")
         game.loop()
         self.assertEqual(game.points_to_segment_display_string(), "498")

    def test_points_to_segment_display_string_two_people(self):
         evs = [
                   Event(EventType.NUMBER, 1),
                   Event(EventType.ACTION, Action.CONFIRM)
               ] * 3
         evs += [
                   Event(EventType.NUMBER, 2),
                   Event(EventType.ACTION, Action.CONFIRM)
                ] * 3
         game = game_logic.Game501(2, TestingPoller(evs), testing_renderer())
         self.assertEqual(game.points_to_segment_display_string(), "501 501")
         game.loop()
         self.assertEqual(game.points_to_segment_display_string(), "498 495")

    def test_points_to_segment_display_string_three_people(self):
         evs = []
         for i in range(1,4):
            evs += [
                      Event(EventType.NUMBER, i),
                      Event(EventType.ACTION, Action.CONFIRM)
                   ] * 3
         game = game_logic.Game501(3, TestingPoller(evs), testing_renderer())
         self.assertEqual(game.points_to_segment_display_string(), "501 501")
         game.loop()
         self.assertEqual(game.points_to_segment_display_string(), "498 495")
         self.assertEqual(game.players, [498, 495, 492])

    def test_points_to_segment_display_string_three_people_two_rounds(self):
         evs = []
         for i in range(1,3):
            evs += [
                      Event(EventType.NUMBER, i),
                      Event(EventType.ACTION, Action.CONFIRM)
                   ] * 3
         game = game_logic.Game501(3, TestingPoller(evs), testing_renderer())
         self.assertEqual(game.points_to_segment_display_string(), "501 501")
         game.loop()
         self.assertEqual(game.points_to_segment_display_string(), "501")
         self.assertEqual(game.players, [498, 495, 501])

    def test_points_to_segment_display_string_four_people(self):
         evs = []
         for i in range(1,5):
            evs += [
                      Event(EventType.NUMBER, i),
                      Event(EventType.ACTION, Action.CONFIRM)
                   ] * 3
         game = game_logic.Game501(4, TestingPoller(evs), testing_renderer())
         self.assertEqual(game.points_to_segment_display_string(), "501 501")
         game.loop()
         self.assertEqual(game.points_to_segment_display_string(), "498 495")
         self.assertEqual(game.players, [498, 495, 492, 489])

    def test_restart(self):
        evs = [
                  Event(EventType.NUMBER, 1),
                  Event(EventType.ACTION, Action.CONFIRM),
                  Event(EventType.ACTION, Action.RESTART)
              ]
        game = game_logic.Game501(1, TestingPoller(evs), testing_renderer())
        self.assertFalse(game.over())
        game.loop()
        self.assertTrue(game.over())

    def test_undo_display_text(self):
        evs = [
                  Event(EventType.NUMBER, 2),
                  Event(EventType.NUMBER, 0),
                  Event(EventType.ACTION, Action.CONFIRM),
                  Event(EventType.ACTION, Action.UNDO)
              ]
        game = game_logic.Game501(1, TestingPoller(evs), testing_renderer())
        game.loop()
        self.assertEqual(game.renderer.current_display_score, "  0 " * 3)

    def test_undo_game_logic(self):
        evs = [
                  Event(EventType.NUMBER, 2),
                  Event(EventType.NUMBER, 0),
                  Event(EventType.ACTION, Action.CONFIRM),
                  Event(EventType.ACTION, Action.UNDO)
              ]
        game = game_logic.Game501(1, TestingPoller(evs), testing_renderer())
        game.loop()
        self.assertEqual(game.players[0], 501)

    def test_undo_segment_string(self):
        evs = [
                  Event(EventType.NUMBER, 2),
                  Event(EventType.NUMBER, 0),
                  Event(EventType.ACTION, Action.CONFIRM),
                  Event(EventType.ACTION, Action.UNDO)
              ]
        game = game_logic.Game501(1, TestingPoller(evs), testing_renderer())
        game.loop()
        self.assertEqual(game.points_to_segment_display_string(), "501")

    def test_segment_string_digits_on_the_same_place(self):
        evs = [
                  Event(EventType.NUMBER, 2),
                  Event(EventType.NUMBER, 0),
                  Event(EventType.ACTION, Action.CONFIRM),
              ] * 3 * 7 * 2 # 3 throws per round, seven rounds so that
                            # score is below 100 and there are two players
        game = game_logic.Game501(2, TestingPoller(evs), testing_renderer())
        game.loop()
        self.assertEqual(game.points_to_segment_display_string(), "81  " + "81")

    def test_segment_string_digits_on_the_same_place_player_with_even_index(self):
        evs = [
                  Event(EventType.NUMBER, 2),
                  Event(EventType.NUMBER, 0),
                  Event(EventType.ACTION, Action.CONFIRM),
              ] * ( 3 * 7 * 2 - 1)
        game = game_logic.Game501(2, TestingPoller(evs), testing_renderer())
        game.loop()
        self.assertEqual(game.points_to_segment_display_string(), "81  " + "101")

class TestPosition(unittest.TestCase):
    def test_add(self):
        second = game_logic.Position.FIRST
        second += 1
        self.assertEqual(game_logic.Position.SECOND, second)

if __name__ == "__main__":
    unittest.main()