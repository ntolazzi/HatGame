"""This modules provides the hardware access"""
import Adafruit_BBIO.ADC as adc
import Adafruit_BBIO.GPIO as gpio
import Adafruit_BBIO.PWM as PWM


class ADC:
    adc_subsystem_started = False

    def __init__(self, pin, average_samples=None, mock_hardware=False):
        self.pin = pin
        self._value = 0.0
        self.average_samples = average_samples
        self.mock_hardware = mock_hardware
        if self.mock_hardware:
            self.path = "hardware_files/%s" % self.pin
        if not ADC.adc_subsystem_started and not self.mock_hardware:
            adc.setup()
            ADC.adc_subsystem_started = True

    @property
    def value(self):
        try:
            if self.average_samples:
                self._value = sum([self.adc_read() for _ in range(self.average_samples)]) / float(
                    self.average_samples)
            else:
                self._value = self.adc_read()
        except IOError:
            self._value = 0.0
            raise IOError('Cannot read ADC {}'.format(self.pin))
        return self._value

    def adc_read(self):
        if self.mock_hardware:
            with open(self.path, 'r') as fh:
                value = fh.read()
        else:
            value = adc.read(self.pin)
        try:
            ret_val = float(value)
        except ValueError:
            # print('Could not convert %s to float' % value)
            ret_val = 0.0
        return ret_val


class Switch:
    def __init__(self, pin, mock_hardware=False):
        self.pin = pin
        self.mock_hardware = mock_hardware
        self._value = False
        if self.mock_hardware:
            self.path = "hardware_files/%s" % self.pin

        if not self.mock_hardware:
            gpio.setup(self.pin, gpio.IN)

    @property
    def value(self):
        try:
            if not self.mock_hardware:
                self._value = gpio.input(self.pin)
            else:
                with open(self.path, 'r') as fh:
                    value = fh.read()
                try:
                    self._value = True if value == '1' else False
                except ValueError:
                    print("Error reading %s" % self.path)
                    self._value = False
        except IOError:
            self._value = False
            raise IOError('Cannot read GPIO {}'.format(self.pin))
        return bool(self._value)


class LED:
    def __init__(self, pin, mock_hardware=False):
        self.pin = pin
        self.mock_hardware = mock_hardware
        if not self.mock_hardware:
            gpio.setup(self.pin, gpio.OUT)
        self._state = False

    def turn_on(self):
        self.state = True

    def turn_off(self):
        self.state = False

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        if new_state != self.state:
            print("Turning led  %s to %s" % (self.pin, new_state))
            self._state = new_state
            if not self.mock_hardware:
                if new_state:
                    gpio.output(self.pin, gpio.HIGH)
                else:
                    gpio.output(self.pin, gpio.LOW)


class Servo:
    def __init__(self, pin, min_duty=4.0, max_duty=15.0, mock_hardware=False):
        self.pin = pin
        self.mock_hardware = mock_hardware
        if not self.mock_hardware:
            print("Initializing hardware")
            PWM.start(self.pin, min_duty)
        self.set_frequency(68.0)
        self.max_duty = max_duty
        self.min_duty = min_duty
        self.movement_threshold = 0.04
        self._angle = 0.0
        self.angle = 0.0

    def set_frequency(self, frequency):
        if not self.mock_hardware:
            PWM.set_frequency(self.pin, frequency)
        else:
            print("%s Setting Frequency to %f" % (self.pin, frequency))

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        if abs(self.angle - value) > self.movement_threshold:
            self._angle = value
            if self.mock_hardware:
                print("%s Setting angle to %.2f" % (self.pin, value))
            value = value * 100.0
            duty_range = self.max_duty - self.min_duty
            step = duty_range / 100.0
            duty_cycle = self.min_duty + value * step
            self.set_duty_cycle(duty_cycle)

    def set_duty_cycle(self, duty_cycle):
        if not self.mock_hardware:
            print(duty_cycle)
            PWM.set_duty_cycle(self.pin, duty_cycle)


if __name__ == "__main__":
    adc0 = ADC(pin="AIN1") # working
    adc1 = ADC(pin="AIN3") # working
    adc2 = ADC(pin="AIN5") # working
    adc3 = ADC(pin="AIN4", average_samples=100) # working
    #led4 = LED("P9_41") # working
    #led4.state = True
    #servo0 = Servo("P9_14", min_duty=6.0, max_duty=13.0) # move atom
    #servo1 = Servo("P9_42", min_duty=6.0, max_duty=13.0) # atom eject
    #servo2 = Servo("P8_13", min_duty=7.0, max_duty=15.0) # cavity eject
    #sw = Switch("P9_30")
    try:
        while True:
            print("%.2f %.2f %.2f %.2f" % (adc0.value, adc1.value, adc2.value, adc3.value))
            ##servo2.angle = adc1.value
            ##led4.state = sw.value
    except KeyboardInterrupt:
        gpio.cleanup()

    #adc0 = ADC(pin="AIN1") # working
    #servo0 = Servo("P9_14")
    #while True:
        #servo0.angle = adc0.value

    #import time
    #led0 = LED("P9_15") # working
    #led1 = LED("P9_23") # working
    #led2 = LED("P8_15") # working
    #led3 = LED("P9_27") # working
    #led4 = LED("P9_41") # working
    #led0.state = False
    #led1.state = False
    #led2.state = False
    #led3.state = False
    #led4.state = True
    #while True:
        #led0.state = not led0.state
        #led1.state = not led1.state
        #led2.state = not led2.state
        #led3.state = not led3.state
        #led4.state = not led4.state
        #time.sleep(1.0)
