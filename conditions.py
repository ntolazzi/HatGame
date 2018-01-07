"""This modules provides a flexible condition classes"""
import time
import operator as op


class DigitalCondition:
    def __init__(self, switch, fullfilled_if_on=True, debug=False):
        self.switch = switch
        self.debug = debug
        self.fullfilled_if_on = fullfilled_if_on

    def __bool__(self):
        switch_state = self.switch.value
        return switch_state if self.fullfilled_if_on else not switch_state


class AnalogCondition:
    comparison_operators = {'bigger': [op.gt, '>'], 'smaller': [op.lt, '<'], 'equal': [op.eq, '==']}

    def __init__(self, adc, threshold=0.0, equal_epsilon=0.01, condition='bigger', debug=False, hold_true=None):
        self.adc = adc
        self.threshold = threshold
        self.debug = debug
        self.hold_true = hold_true
        self._start_true_time = 0.0
        self.timed_condition = False
        self.equal_epsilon = equal_epsilon
        try:
            self.operator = AnalogCondition.comparison_operators[condition]
        except IndexError:
            raise IndexError('Provide one of the following strings: bigger, smaller, equal')

    def __bool__(self):
        reading = self.adc.value
        if self.operator[0] is op.eq:
            condition_fulfilled = True if (abs(reading - self.threshold) < self.equal_epsilon) else False
        else:
            condition_fulfilled = self.operator[0](reading, self.threshold)
        if self.hold_true:
            if condition_fulfilled:
                if not self.timed_condition:
                    if self._start_true_time == 0.0:
                        self._start_true_time = time.time()
                    else:
                        if (time.time() - self._start_true_time) > self.hold_true:
                            self._start_true_time = 0.0
                            self.timed_condition = True
                        else:
                            self.timed_condition = False
            else:
                self.timed_condition = False
                self._start_true_time = 0.0
        else:
            self.timed_condition = condition_fulfilled

        if self.debug:
            print('{:.4f} {} {:.4f} -> {}'.format(reading, self.operator[1], self.threshold, condition_fulfilled))
        return self.timed_condition

    @property
    def fulfilled(self):
        return self.__bool__()


if __name__ == '__main__':
    from hardware import ADC

    adc = ADC()
    cond = AnalogCondition(adc, threshold=0.3, debug=False, equal_epsilon=0.1, condition='equal', hold_true=1.0)
    while True:
        print(cond.fulfilled)
