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

CODE_TO_ACTION_DICT = { ecodes.KEY_KPENTER : Action.CONFIRM, ecodes.KEY_KPPLUS : Action.TRIPLE, 
                        ecodes.KEY_KPMINUS : Action.DOUBLE, ecodes.KEY_BACKSPACE : Action.UNDO }
# end of constants

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

    def next_event(self):
        r,w,x = select([self.keyboard], [], [])
        for event in filter((lambda e : e.type == ecodes.EV_KEY and e.value == KEY_DOWN), self.keyboard.read()):
            code = event.code
            if number_pressed(code):
                print(code_to_number(code))
            elif action_pressed(code):
                print(code_to_action(code))
            else:
                print(categorize(event))
