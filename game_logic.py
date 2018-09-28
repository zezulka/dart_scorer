import input_controller
import max7219_controller
import lcd_display
from re import match
from evdev import categorize, uinput, ecodes as e
from time import sleep
from enum import Enum
from functools import reduce

class Throw:
    def __init__(self, pts, multiplier):
        self.pts = pts
        self.multiplier = multiplier

    def points(self):
        return self.pts * self.multiplier

class Position(Enum):
    FIRST = 1,
    SECOND = 2,
    THIRD = 3,

    # https://docs.python.org/3/reference/datamodel.html#special-method-names
    # += operator
    def __add__(self, other):
        other = other % 3
        if other == 0:
            return self
        elif other == 1:
            if self == Position.FIRST:
                return Position.SECOND
            elif self == Position.SECOND:
                return  Position.THIRD
            elif self == Position.THIRD:
                return Position.FIRST
        elif other == 2:
            if self == Position.FIRST:
                return  Position.THIRD
            elif self == Position.SECOND:
                return Position.FIRST
            elif self == Position.THIRD:
                return Position.SECOND

    def to_int(self):
        return self.value[0]

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

        def clean_up(self):
            self.lcd_d.clean_up()

        def action(self, action, input_ctrl):
            if action in [input_controller.Action.DOUBLE, input_controller.Action.TRIPLE]:
                input_ctrl.toggle_numlock()

        def points(self, points):
            self.segment_d.show_message(str(points))

        def score(self, score):
            self.lcd_d.lcd_string_first_line(score)

        def warning(self, text):
            self.lcd_d.lcd_string_second_line(text)
            sleep(0.75)
            self.lcd_d.lcd_string_second_line("")

    def __init__(self, num_players, input_ctrl, renderer=Renderer()):
        self.round = GameRound()
        self.input_ctrl = input_ctrl
        self.renderer = renderer
        #Container which holds the text displayed to the LCD
        self.current_score = 12 * " "
        self.current_player = 0
        self.num_players = num_players
        self.players = [501] * num_players

    def __enter__(self):
        return self
 
    def over(self):
        return reduce(lambda x,y: x or y == 0, self.players, False)

    def __exit__(self, _type, _value, _tb):
        self.renderer.clean_up()

    def next_round(self):
        curr_pts = self.players[self.current_player] - self.round.points()
        if curr_pts >= 0:
            self.players[self.current_player] = curr_pts
        else:
            self.renderer.warning("Overthrow!")
        self.current_score = " " * 12
        self.current_player = (self.current_player + 1) % self.num_players
        self.round.clear()

    def handle_action(self, action):
        modif_score = self.score_for_current_throw()
        if action == input_controller.Action.DOUBLE:
            modif_score = modif_score[:3] + 'D'
        elif action == input_controller.Action.TRIPLE:
            modif_score = modif_score[:3] + 'T'
        elif action == input_controller.Action.CONFIRM:
            self.save_points_for_current_throw()
            modif_score = " " * 4
            self.round.current_position += 1
            # We have overflown the positions which means that the new round has started
            if self.round.current_position == Position.FIRST:
                self.next_round()
        elif action == input_controller.Action.UNDO:
            modif_score = " " * 4
        assert(len(modif_score) == 4)
        return modif_score
    
    def save_points_for_current_throw(self):
        curr_score = self.score_for_current_throw()
        int_score = int(curr_score[1] + curr_score[2])
        int_multiplier = 1
        multiplier = curr_score[3]
        if multiplier == 'D':
            int_multiplier = 2
        elif multiplier == 'T':
            int_multiplier = 3
        curr_pos = self.round.current_position
        if curr_pos == Position.FIRST:
            self.round.first_throw = Throw(int_score, int_multiplier)
        elif curr_pos == Position.SECOND:
            self.round.second_throw = Throw(int_score, int_multiplier)
        elif curr_pos == Position.THIRD:
            self.round.third_throw = Throw(int_score, int_multiplier)

    def score_for_current_throw(self):
        curr_pos_int = self.round.current_position.to_int()
        return self.current_score[ ((curr_pos_int - 1) * 4) : (curr_pos_int * 4) ]

    def substitute_score_for_current_throw(self, score):
        if score == None or len(score) != 4:
            raise ValueError("the score string must be of length 4")
        curr_pos_int = self.round.current_position.to_int()
        self.current_score = self.current_score[:((curr_pos_int - 1) * 4)] + score + self.current_score[(curr_pos_int * 4):]

    def loop(self):
        while not self.over():
            space = " "
            next_event = self.input_ctrl.next_event()
            score = self.score_for_current_throw()
            if not next_event:
                return
            if next_event.e_type == input_controller.EventType.NUMBER: 
                next_digit = str(next_event.value)
                if match(space * 3 + "[ DT]", score):
                    appendix = score[3]
                    score = space * 2 + next_digit + appendix
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
            points = str(self.players[self.current_player])
            if self.num_players > 1:
                points += " " + str(self.players[(self.current_player + 1) % self.num_players])
            self.renderer.points(points)
