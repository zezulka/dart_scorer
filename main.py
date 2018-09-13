import input_controller
import max7219_controller
import lcd_display
from evdev import categorize, uinput, ecodes as e

poller = input_controller.EventPoller()
segment_d = max7219_controller.MAX7219()
lcd_d = lcd_display.LcdDisplay()

def handle_action(action, poller):
    if action == input_controller.Action.DOUBLE:
        poller.toggle_numlock()
    elif action == input_controller.Action.TRIPLE:
        poller.toggle_numlock()
    elif action == input_controller.Action.CONFIRM:
        poller.toggle_numlock()
    elif action == input_controller.Action.UNDO:
        pass

while True:
    next_event = poller.next_event()
    if next_event.e_type == input_controller.EventType.NUMBER: 
        #segment_d.show_message(str(next_event.value))
        lcd_d.lcd_string_first_line(str(next_event.value))
    elif next_event.e_type == input_controller.EventType.ACTION:
        handle_action(next_event.value, poller)
