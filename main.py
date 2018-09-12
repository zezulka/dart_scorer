import input_controller

poller = input_controller.EventPoller()
while True:
    poller.next_event()
