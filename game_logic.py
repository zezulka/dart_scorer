import input_controller
import max7219_controller
import lcd_display
from re import match
from evdev import categorize, uinput, ecodes as e
from time import sleep
from enum import Enum

class Throw:
    def __init__(self, points, multiplier):
        self.points = points
        self.multiplier = multiplier

    def points(self):
        return self.points * self.multiplier

class Position(Enum):
    FIRST = 1,
    SECOND = 2,
    THIRD = 3

    # https://docs.python.org/3/reference/datamodel.html#special-method-names
    # += operator
    def __iadd__(self, other):
        other = other % 3
        if other == 0:
            return self
        elif other == 1:
            if self == Position.FIRST:
                return Position.SECOND
            elif self == Position.SECOND:
                return Position.THIRD
            elif self == Position.THIRD:
                return Position.FIRST
        elif other == 2:
            if self == Position.FIRST:
                return Position.THIRD
            elif self == Position.SECOND:
                return Position.FIRST
            elif self == Position.THIRD:
                return Position.SECOND
        raise ValueError("could not add, args: {} += {}".format(self, other))

class GameRound:
    def __init__(self):
        self.first_throw = None
        self.second_throw = None
        self.third_throw = None
        self.current_position = Position.FIRST

    def clear(self):
        self.__init__()

    def points(self):
        return self.first_throw.points() + self.second_throw.points() + self.third_throw.points()

class Game501:
    def __init__(self):
        self.points = 501
        self.darts_thrown = 0
        self.round = GameRound()
        self.input_ctrl = input_controller.EventPoller()
        self.segment_d = max7219_controller.MAX7219()
        self.lcd_d = lcd_display.LcdDisplay()
        #Container which holds the text displayed to the LCD
        self.current_score = 12 * " "

    def next_round(self):
        self.points -= self.round.points()
        self.game_round.clear()

    def handle_action(self, action):
        if action == input_controller.Action.DOUBLE:
            self.input_ctrl.toggle_numlock()
            self.current_score += "D"
        elif action == input_controller.Action.TRIPLE:
            self.input_ctrl.toggle_numlock()
            self.current_score += "T"
        elif action == input_controller.Action.CONFIRM:
            self.input_ctrl.toggle_numlock()
            self.round.current_position += 1
        elif action == input_controller.Action.UNDO:
            self.current_score = ""
    
    def game_loop(self):
        while True:
            next_event = self.input_ctrl.next_event()
            curr_pos = self.round.current_position.value[0]
            if next_event.e_type == input_controller.EventType.NUMBER: 
                #segment_d.show_message(str(next_event.value))
                next_digit = str(next_event.value)
                score = self.current_score[((curr_pos - 1) * 4) : (curr_pos * 4) ]
                if score == " " * 4:
                    score = "  " + next_digit
                elif match("  [0-9][ DT]", score):
                    tens = score[2]
                    appendix = score[3]
                    if tens == "1" or (tens == "2" and next_digit in ["0", "5"]):
                        score = tens + next_digit + appendix
                    else:
                        self.lcd_d.lcd_string_second_line(tens + next_digit + " not valid!")
                        sleep(0.75)
                        self.lcd_d.lcd_string_second_line("")
                else:
                    self.lcd_d.lcd_string_second_line("hit <-")    
            elif next_event.e_type == input_controller.EventType.ACTION:
                self.handle_action(next_event.value)
            self.current_score = self.current_score[:((curr_pos - 1)* 4)] + score + self.current_score[(curr_pos * 4):]
            self.lcd_d.lcd_string_first_line(self.current_score)
