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
    class Renderer:
        def __init__(self):
            self.segment_d = max7219_controller.MAX7219()
            self.lcd_d = lcd_display.LcdDisplay()

        def action(self, action, input_ctrl):
            if action in [input_controller.Action.DOUBLE, input_controller.Action.TRIPLE]:
                input_ctrl.toggle_numlock()

        def score(self, score):
            self.lcd_d.lcd_string_first_line(score)

        def warning(self, text):
            self.lcd_d.lcd_string_second_line(text)
            sleep(0.75)
            self.lcd_d.lcd_string_second_line("")

    def __init__(self, input_ctrl = input_controller.EventPoller(), renderer=Renderer()):
        self.points = 501
        self.darts_thrown = 0
        self.round = GameRound()
        self.input_ctrl = input_ctrl
        self.renderer = renderer
        #Container which holds the text displayed to the LCD
        self.current_score = 12 * " "

    def next_round(self):
        self.points -= self.round.points()
        self.game_round.clear()

    def handle_action(self, action):
        modif_score = self.score_for_current_throw()
        if action == input_controller.Action.DOUBLE:
            modif_score = modif_score[:3] + 'D'
        elif action == input_controller.Action.TRIPLE:
            modif_score = modif_score[:3] + 'T'
        elif action == input_controller.Action.CONFIRM:
            self.round.current_position += 1
            modif_score = self.score_for_current_throw()
        elif action == input_controller.Action.UNDO:
            modif_score = " " * 4
        return modif_score
    
    def score_for_current_throw(self):
        curr_pos_int = self.round.current_position.value[0]
        return self.current_score[ ((curr_pos_int - 1) * 4) : (curr_pos_int * 4) ]

    def substitute_score_for_current_throw(self, score):
        if score == None or len(score) != 4:
            raise ValueError("the score string must be of length 4")
        curr_pos_int = self.round.current_position.value[0]
        self.current_score = self.current_score[:((curr_pos_int - 1) * 4)] + score + self.current_score[(curr_pos_int * 4):]

    def game_loop(self):
        while True:
            space = " "
            next_event = self.input_ctrl.next_event()
            if next_event.e_type == input_controller.EventType.NUMBER: 
                next_digit = str(next_event.value)
                score = self.score_for_current_throw()
                if score == space * 4:
                    score = space * 2 + next_digit + space
                elif match(space * 2 + "[0-9][ DT]", score):
                    tens = score[2]
                    appendix = score[3]
                    if tens == "1" or (tens == "2" and next_digit in ["0", "5"]):
                        score = space + tens + next_digit + appendix
                    else:
                        self.renderer.warning(tens + next_digit + " not valid!")
                else:
                    self.renderer.warning("hit <-")
            elif next_event.e_type == input_controller.EventType.ACTION:
                score = self.handle_action(next_event.value)
                self.renderer.action(next_event.value, self.input_ctrl)
            self.substitute_score_for_current_throw(score)
            self.renderer.score(self.current_score)
