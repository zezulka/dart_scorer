import unittest
import game_logic
from queue import Queue
from input_controller import *
from game_logic import Renderer

def testing_renderer():
    return Renderer(TestingDisplayController())

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
        self.__fill_queue(event_array)

    def __fill_queue(self, event_array):
        for event in event_array:
            self.event_queue.put(event)

    def next_event(self):
        if self.event_queue.empty():
            return None
        return self.event_queue.get()
