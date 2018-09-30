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
        return reduce(lambda acc, next_: acc + next_.points(), 
                      filter(lambda throw : throw is not None, 
                             [self.first_throw, self.second_throw, self.third_throw]), 
                      0)

def game_factory():
    renderer = Renderer()
    user_config = renderer.get_user_config()
    input_ctrl = input_controller.EventPoller() 
    if user_config.game_type == GameType.X01:
        return Game501(user_config.num_players, input_ctrl, renderer)
    else:
        raise ValueError("Not supported yet.")

class GameType(Enum):
    X01 = 1,
    Cricket = 2,
    RoundTheClock = 3,

class UserConfig:
    def __init__(self, num_players, game_type, input_ctrl):
        if num_players < 1:
            raise ValueError("There must be at least one player in the game.")
        if not game_type:
            raise ValueError("No game selected.")
        self.num_players = num_players
        self.game_type = game_type

def game_type_factory(number):
    if number == 1:
        return GameType.X01
    else:
        raise ValueError("Unsupported game type.")

class DisplayController:
    def __init__(self):
        self.segment_d = max7219_controller.MAX7219()
        self.lcd_d = lcd_display.LcdDisplay()

    def segment_set_text(self, text):
        self.segment_d.show_message(text)

    def lcd_set_line(self, set_fun, text, duration):
        set_fun(text)
        if duration > 0:
            sleep(duration)
            set_fun("")

    def lcd_set_first_line(self, text, duration=-1.0):
        self.lcd_set_line(self.lcd_d.first_line, text, duration)

    def lcd_set_second_line(self, text, duration=-1.0):
        self.lcd_set_line(self.lcd_d.second_line, text, duration)

    def clean_up(self):
        self.lcd_d.clean_up()
        self.segment_d.clean_up()

class Renderer:
    def __init__(self, displ_ctrl = DisplayController()):
        self.__init_display_score = "  0 " * 3
        self.current_display_score = self.__init_display_score
        self.displ_ctrl = displ_ctrl

    def wait_for_next_number(self, input_ctrl):
        while True:
            e = input_ctrl.next_event()
            if e.e_type == input_controller.EventType.NUMBER:
                return e.value
                

    def get_user_config(self):
        input_ctrl = input_controller.EventPoller()
        num_players = -1
        game_type = None
        first_line = "no. players:"
        self.displ_ctrl.lcd_set_first_line(first_line)
        num_players = self.wait_for_next_number(input_ctrl)
        first_line += " " + str(num_players)
        self.displ_ctrl.lcd_set_first_line(first_line)
        
        second_line = "game type:"
        self.displ_ctrl.lcd_set_second_line(second_line)
        game_id = self.wait_for_next_number(input_ctrl)
        game_type = game_type_factory(game_id)
        second_line += " " + game_type.name
        self.displ_ctrl.lcd_set_second_line(second_line, 0.50)
        self.clear_lcd()
        return UserConfig(num_players, game_type, input_ctrl)    

    def clear_lcd(self):
        self.current_display_score = self.__init_display_score
        self.score()

    def clean_up(self):
        self.displ_ctrl.clean_up()

    def points(self, points):
        self.displ_ctrl.segment_set_text(str(points))

    def score(self):
        self.displ_ctrl.lcd_set_first_line(self.current_display_score)
   
    def subscore_for_throw(self, pos):
        return self.current_display_score[ ((pos - 1) * 4) : (pos * 4) ]
 
    def substitute_score_on_position(self, score, pos):
        if score == None or len(score) != 4:
            raise ValueError("the score string must be of length 4")
        self.current_display_score = self.current_display_score[:((pos - 1) * 4)] + score + \
                                     self.current_display_score[(pos * 4):]

    def highlight_current_throw(self, no):
        no -= 1
        no *= 4
        aux_str = "####" + " " * 8
        aux_str = aux_str[-no:] + aux_str[:-no]
        self.displ_ctrl.lcd_set_second_line(aux_str)        

    def warning(self, text):
        warning_duration = 0.75
        self.displ_ctrl.lcd_set_second_line(text, warning_duration)

class Game501:
    def __init__(self, num_players, input_ctrl, renderer):
        self.round = GameRound()
        self.input_ctrl = input_ctrl
        self.renderer = renderer
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
        self.renderer.clear_lcd()
        self.current_player = (self.current_player + 1) % self.num_players
        self.round.clear()
    
    # TODO: the parsing is really weird, we should get the information
    # from somewhere else
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
        return self.renderer.subscore_for_throw(curr_pos_int)

    def substitute_score_at_current_throw(self, score):
        if score == None or len(score) != 4:
            raise ValueError("the score string must be of length 4")
        curr_pos_int = self.round.current_position.to_int()
        self.renderer.substitute_score_on_position(score, curr_pos_int)

    def score_after_action(self, action):
        modif_score = self.score_for_current_throw()
        if action == input_controller.Action.DOUBLE:
            modif_score = modif_score[:3] + 'D'
        elif action == input_controller.Action.TRIPLE:
            modif_score = modif_score[:3] + 'T'
        elif action == input_controller.Action.CONFIRM:
            self.save_points_for_current_throw()
            curr_pts = curr_pts = self.players[self.current_player] - self.round.points()
            if curr_pts < 0:
                self.renderer.warning("Overthrow!")
            self.round.current_position += 1
            if self.round.current_position == Position.FIRST or curr_pts <= 0:
                self.next_round()
            modif_score = self.score_for_current_throw()
        elif action == input_controller.Action.UNDO:
            modif_score = "  0 "
        assert(len(modif_score) == 4)
        return modif_score

    def score_after_digit(self, digit):
        space = " "
        digit = str(digit)
        score = self.score_for_current_throw()
        if match(space * 2 + "0" + "[ DT]", score):
            appendix = score[3]
            score = space * 2 + digit + appendix
        elif match(space * 2 + "[0-9][ DT]", score):
            tens = score[2]
            appendix = score[3]
            if tens == "1" or (tens == "2" and digit in ["0", "5"]):
                score = space + tens + digit + appendix
            else:
                self.renderer.warning(tens + digit + " not valid!")
        else:
            self.renderer.warning("hit <-")
        return score

    def points_to_segment_display_string(self):
        points = str(self.players[self.current_player] - self.round.points())
        if self.num_players > 1:
           points += " " + str(self.players[(self.current_player + 1) % self.num_players])
        return points

    def loop(self):
        while not self.over():           
            self.renderer.highlight_current_throw(self.round.current_position.to_int())
            self.renderer.score() 
            self.renderer.points(self.points_to_segment_display_string())
            next_event = self.input_ctrl.next_event()
            if not next_event:
                return
            after_fun = None
            if next_event.e_type == input_controller.EventType.NUMBER: 
                after_fun = self.score_after_digit
            elif next_event.e_type == input_controller.EventType.ACTION:
                after_fun = self.score_after_action
            elif next_event.e_type == input_controller.EventType.NOTHING:
                continue
            else:
                raise ValueError("Unexpected event occurred.")
            self.substitute_score_at_current_throw(after_fun(next_event.value))
