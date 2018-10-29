from time import sleep


class DisplayController:
    """ Class used for controlling output devices used in the game.
 This class shouldn't be used in tests since it is dependent on
 modules which directly work with physical displays. """

    def __init__(self):
        # We want to be able to run tests (HW dependless) everywhere
        from ..display import segment
        from ..display import lcd
        self.segment_d = segment.MAX7219()
        self.lcd_d = lcd.LcdDisplay()

    def segment_set_text(self, text):
        self.segment_d.show_message(text)

    def lcd_set_first_line(self, text, duration=-1.0):
        self.__lcd_set_line(self.lcd_d.first_line, text, duration)

    def lcd_set_second_line(self, text, duration=-1.0):
        self.__lcd_set_line(self.lcd_d.second_line, text, duration)

    def warning(self, text):
        """ Just a simple shortcut to displaying a message to the
second row of the LCD display which will disapear after a given
magic time constant."""
        self.lcd_set_second_line(text, 0.75)

    def clean_up(self):
        self.lcd_d.clean_up()
        self.segment_d.clean_up()

    def __lcd_set_line(set_fun, text, duration):
        set_fun(text)
        if duration > 0:
            sleep(duration)
            set_fun("")
