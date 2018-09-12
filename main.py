import input_controller
import max7219_controller

poller = input_controller.EventPoller()
display = max7219_controller.MAX7219()
while True:
    display.show_message(str(poller.next_event().value))
