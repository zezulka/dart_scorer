"""Module responsible for controlling and reading from input devices (for the time being,\
 the only input device will be the numerical keyboard)."""
from sys import stderr as serr
from select import select
from enum import Enum
from evdev import InputDevice, categorize, ecodes
from evdev.events import KeyEvent

# Path to the numerical keyboard
NUM_KEY_PATH = "/dev/input/by-id/usb-SIGMACHIP_USB_Keyboard-event-kbd"
KEY_DOWN = KeyEvent.key_down
CODE_TO_NUMBER_DICT = {
    ecodes.KEY_KP0 : 0, ecodes.KEY_KP1 : 1, ecodes.KEY_KP2 : 2,
    ecodes.KEY_KP3 : 3, ecodes.KEY_KP4 : 4, ecodes.KEY_KP5 : 5,
    ecodes.KEY_KP6 : 6, ecodes.KEY_KP7 : 7, ecodes.KEY_KP8 : 8,
    ecodes.KEY_KP9 : 9, ecodes.KEY_SPACE : 20, ecodes.KEY_KPDOT : 25
}


class Action(Enum):
    """ Enum representing abstract actions from the game logic point of view."""
    def __iter__(self):
        for attr in dir(Action):
            if not attr.startswith("__"):
                yield attr

    CONFIRM = 1
    DOUBLE = 2
    TRIPLE = 3
    CLEAR = 4
    RESTART = 5
    UNDO = 6

# KEY_NUMLOCK
CODE_TO_ACTION_DICT = {
    ecodes.KEY_KPENTER : Action.CONFIRM, ecodes.KEY_KPPLUS : Action.TRIPLE,
    ecodes.KEY_KPMINUS : Action.DOUBLE, ecodes.KEY_BACKSPACE : Action.CLEAR,
    ecodes.KEY_KPASTERISK : Action.RESTART, ecodes.KEY_KPSLASH : Action.UNDO
}

class EventType(Enum):
    """ Enum used for decoding the type of event.\
 NUMBER represents a multi-digit number."""
    ACTION = 0
    NUMBER = 1

class Event:
    """ Basic struct containing EventType and the value itself.\
 For EventType.NUMBER events, the value represents the raw numeric value (i.e. throw value)\
 and the EventType.ACTION events contain an instance of the Action enum."""
    def __init__(self, e_type, value):
        self.e_type = e_type
        self.value = value

def number_pressed(code):
    """Returns a bool telling whether the scancode retrieved from an
 input device represents a number."""
    return code in CODE_TO_NUMBER_DICT

def code_to_number(code):
    """Mapping from a scancode to the "nominal" value of the key."""
    return CODE_TO_NUMBER_DICT[code]

def action_pressed(code):
    """Returns a bool telling whether the scancode retrieved from an
 input device represents a game action."""
    return code in CODE_TO_ACTION_DICT

def code_to_action(code):
    """Mapping from a scancode to an Action enum."""
    return CODE_TO_ACTION_DICT[code]

class EventPoller:
    """Class reading scancodes from an input device with a hardcoded path NUM_KEY_PATH.\
 This implementation is Linux compatible only."""
    def __init__(self):
        try:
            self.keyboard = InputDevice(NUM_KEY_PATH)
        except FileNotFoundError:
            print("It seems that the numerical keyboard is not available at the moment.\
 Please check that the keyboard is connected and try again.", serr)
            exit(1)
        self.ev_stack = []

    def __get_next_event(self):
        _ = select([self.keyboard], [], [])
        for event in self.keyboard.read_loop():
            if event is not None and event.type == ecodes.EV_KEY and event.value == KEY_DOWN:
                return event
        raise ValueError("read_loop() shouldn't have ended!")

    def wait_for_next_number(self):
        """This is a shortcut to the EventPoller.next_event() function which only returns a\
 number and throws away any other events."""
        while True:
            ev = self.next_event()
            if ev.e_type == EventType.NUMBER:
                return ev.value

    def next_event(self):
        """Returns next relevant event available from an input device.\
 A relevant event is either an action or a number recognizable by this module."""
        if len(self.ev_stack) > 0:
            return self.ev_stack.pop()
        event = self.__get_next_event()
        code = event.code
        if number_pressed(code):
            num = code_to_number(code)
            if num > 10:
                self.ev_stack.append(Event(EventType.NUMBER, num % 10))
                num = (num // 10) % 10
            return Event(EventType.NUMBER, num)
        elif action_pressed(code):
            return Event(EventType.ACTION, code_to_action(code))
        else:
            print(categorize(event))
            return self.next_event()
