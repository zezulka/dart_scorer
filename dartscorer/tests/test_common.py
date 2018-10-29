from queue import Queue
from pathlib import Path
import time
import os


class TestingDisplayController:
    """ Implement a DisplayController which basically does nothing
except from printing out the current state of its virtual 'displays' to a file."""

    def __init__(self, out_file):
        self.lcd_first_line = ""
        self.lcd_second_line = ""
        self.segment_text = ""
        self.output_file = out_file

    def clear(self):
        self.lcd_first_line = ""
        self.lcd_second_line = ""
        self.segment_text = ""

    def warning(self, text):
        print("Warn: {}".format(text), file=self.output_file)

    def clean_up(self):
        print("Cleaning up.", file=self.output_file)

    def segment_set_text(self, text):
        self.segment_text = text
        print(self.__to_string(), file=self.output_file)

    def lcd_set_first_line(self, text, _duration=None):
        self.lcd_first_line = text
        print(self.__to_string(), file=self.output_file)

    def lcd_set_second_line(self, text, _duration=None):
        self.lcd_second_line = text
        print(self.__to_string(), file=self.output_file)

    def __to_string(self):
        return "=-" * 15 + "\nLCD[1]: {} \t\t\t SEGMENT: {}\nLCD[2]: {}\n".format(
            self.lcd_first_line, self.segment_text, self.lcd_second_line) + "=-" * 15


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


def make_sure_output_dir_exists():
    dirname = Path("./test_output")
    dirname.mkdir(parents=True, exist_ok=True)


def testing_renderer():
    make_sure_output_dir_exists()
    return TestingDisplayController(open(os.path.join("./test_output",
                                                      time.strftime("%Y%m%d-%H%M%S")) + ".txt", "a"))


RENDERER = testing_renderer()
