# Module responsible for controlling and reading from input devices (in this case,
# the only input device will be the numerical keyboard).
from evdev import InputDevice, categorize, ecodes
from select import select
dev = InputDevice("/dev/input/by-id/usb-SIGMACHIP_USB_Keyboard-event-kbd")

while True:
    r,w,x = select([dev], [], [])
    for event in dev.read():
        if event.type == ecodes.EV_KEY:
            print(categorize(event))


