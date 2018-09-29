# Module responsible for controlling and reading from input devices (in this case,
# the only input device will be the numerical keyboard).
from evdev import InputDevice, categorize, ecodes 
from evdev.events import KeyEvent
from select import select
from enum import Enum

# Constants
# Path to the numerical keyboard
NUM_KEY_PATH = "/dev/input/by-id/usb-SIGMACHIP_USB_Keyboard-event-kbd"
KEY_DOWN     = KeyEvent.key_down
CODE_TO_NUMBER_DICT = {ecodes.KEY_KP0 : 0, ecodes.KEY_KP1 : 1, ecodes.KEY_KP2 : 2, ecodes.KEY_KP3 : 3, ecodes.KEY_KP4 : 4, 
                       ecodes.KEY_KP5 : 5, ecodes.KEY_KP6 : 6, ecodes.KEY_KP7 : 7, ecodes.KEY_KP8 : 8, ecodes.KEY_KP9 : 9}
class Action(Enum):
    def __iter__(self):
        for attr in dir(Action):
            if not attr.startswith("__"):
                yield attr

    NOTHING = 0
    CONFIRM = 1
    DOUBLE = 2
    TRIPLE = 3
    UNDO = 4
# KEY_NUMLOCK
CODE_TO_ACTION_DICT = { ecodes.KEY_KPENTER : Action.CONFIRM, ecodes.KEY_KPPLUS : Action.TRIPLE, 
                        ecodes.KEY_KPMINUS : Action.DOUBLE, ecodes.KEY_BACKSPACE : Action.UNDO }
# end of constants

class EventType(Enum):
    ACTION = 0
    NUMBER = 1
    NOTHING = 2

class Event:
    def __init__(self, e_type, value):
        self.e_type = e_type
        self.value = value

def number_pressed(code):
    return code in CODE_TO_NUMBER_DICT

def code_to_number(code):
    return CODE_TO_NUMBER_DICT[code]

def action_pressed(code):
    return code in CODE_TO_ACTION_DICT

def code_to_action(code):
    return CODE_TO_ACTION_DICT[code]

class EventPoller:
    def __init__(self):
        self.keyboard = InputDevice(NUM_KEY_PATH)

    # Should return None when there is no event available at the moment.
    def next_event(self):
        r,w,x = select([self.keyboard], [], [])
        # An arbitrary number for now
        num_tries = 1000
        event = None
        while event == None and num_tries > 0:
            num_tries -= 1
            candidate = self.keyboard.read_one()
            if candidate is not None and candidate.type == ecodes.EV_KEY and candidate.value == KEY_DOWN:
                event = candidate
        if event is not None:
            code = event.code
            if number_pressed(code):
                return Event(EventType.NUMBER, code_to_number(code))
            elif action_pressed(code):
                return Event(EventType.ACTION, code_to_action(code))
            else:
                print(categorize(event))
        return Event(EventType.NOTHING, -1)
