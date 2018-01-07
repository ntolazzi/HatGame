"""This is the central game file, where the game logic is contained"""

import time
from threading import Thread
from hardware import *
from conditions import AnalogCondition
from helpers import cavity_resonant_blinking, kick_out_atom, blink_alternating, blink_together,\
    blink_randomly, Sound
import random


class State:
    sound = Sound('sounds')

    def __init__(self, name, conditions, enter_actions=None, leave_actions=None, random_actions=None,
                 parallel_actions=None, next_states=[], fail_probability=0.0):
        self.name = name
        if enter_actions is None:
            enter_actions = [(print, 'Entering {} state'.format(self.name))]
        if leave_actions is None:
            leave_actions = [(print, 'Leaving {} state'.format(self.name))]
        if random_actions is None:
            random_actions = [(print, 'Random Action happened, going back to state %d' % next_states[1])]
        if parallel_actions is None:
            parallel_actions = [(print, '{} state running in parallel ...'.format(self.name)),
                                (time.sleep, 1.0)]
        self.enter_actions = enter_actions
        self.leave_actions = leave_actions
        self.random_actions = random_actions
        self.parallel_actions = parallel_actions
        self.conditions = [conditions]
        self.next_states = next_states
        self.fail_probability = fail_probability
        self.stop_parallel_thread = False

    def enter(self):
        State.sound.play_stage_sound(self.next_states[0] - 1)
        if self.next_states[1] != 99:
            State.sound.start_random_sound_loop()
        for action, params in self.enter_actions:
            action(params)

    def leave(self):
        State.sound.stop_sound_loop()
        for action, params in self.leave_actions:
            action(params)
        self.stop_parallel_thread = True

    def run_random_action(self):
        for action, params in self.random_actions:
            action(params)
        self.leave()
        return self.next_states[1]

    def run(self):
        self.enter()
        self.parallel_thread = Thread(target=self.run_parallel, args=())
        self.parallel_thread.daemon = True
        self.stop_parallel_thread = False
        self.parallel_thread.start()
        while True:
            if all(self.conditions):
                self.leave()
                return self.next_states[0]
            if random.random() < self.fail_probability:
                return self.run_random_action()
            time.sleep(0.1)

    def run_parallel(self):
        while True:
            for action, params in self.parallel_actions:
                if isinstance(params, tuple):
                    action(*params)
                else:
                    action(params)
            if self.stop_parallel_thread:
                break


class Game:
    debug = True
    mock_hardware = False
    hold_time = 3
    laser_poti = ADC(pin="AIN3", mock_hardware=mock_hardware)
    cavity_poti = ADC(pin="AIN1", mock_hardware=mock_hardware)
    atom_poti = ADC(pin="AIN5", mock_hardware=mock_hardware)
    photo_diode = ADC(pin="AIN4", mock_hardware=mock_hardware, average_samples=100)
    laser_switch = Switch(pin="P9_30", mock_hardware=mock_hardware)

    cavity_green_led = LED("P9_15")
    cavity_blue_led = LED("P9_23")
    spcm_0_led = LED("P8_15")
    spcm_1_led = LED("P9_27")
    laser_led = LED("P9_41")

    atom_servo = Servo("P9_14", min_duty=6.0, max_duty=13.0)
    atom_eject_servo = Servo("P9_42", min_duty=6.0, max_duty=13.0)
    cavity_servo = Servo("P8_13", min_duty=7.0, max_duty=15.0)

    states = {0: State('Align Mirror',
                       AnalogCondition(photo_diode, threshold=0.4, condition='bigger',
                                       hold_true=hold_time, debug=debug), next_states=[1, 1]),

              1: State('Change Cavity Length',
                       AnalogCondition(cavity_poti, condition='equal', equal_epsilon=0.03,
                                       threshold=0.7, hold_true=hold_time, debug=debug),
                       next_states=[2, 2], parallel_actions=[(cavity_resonant_blinking,
                                                              (cavity_blue_led, cavity_green_led,
                                                               cavity_poti))]),

              2: State('Trap Atom',
                       AnalogCondition(photo_diode, threshold=0.15, hold_true=hold_time,
                                       condition='smaller', debug=debug), next_states=[3, 3]),

              3: State('Tune Frequency Blocking',
                       AnalogCondition(laser_poti, condition='equal', equal_epsilon=0.1,
                                       threshold=0.2, hold_true=hold_time, debug=debug), next_states=[4, 2],
                       fail_probability=0.02, random_actions=[(kick_out_atom, atom_eject_servo)],
                       parallel_actions=[(blink_randomly, (spcm_0_led, spcm_1_led))]),

              4: State('Tune Frequency Conjunct Tunneling',
                       AnalogCondition(laser_poti, condition='equal', equal_epsilon=0.1,
                                       threshold=0.7, hold_true=hold_time, debug=debug),
                       parallel_actions=[(blink_alternating, (spcm_0_led, spcm_1_led))], next_states=[5, 5]),
              5: State('Success', False, next_states=[5, 99],
                       parallel_actions=[(blink_together, (spcm_0_led, spcm_1_led))]),
              }

    def __init__(self):
        self.servo_thread = Thread(target=self.thread_target, args=())
        self.servo_thread.daemon = True
        self.servo_thread.start()
        self.event_loop()

    def thread_target(self):
        while True:
            # Do all 'wiring' here
            Game.cavity_servo.angle = Game.cavity_poti.value
            Game.atom_servo.angle = Game.atom_poti.value
            Game.laser_led.state = Game.laser_switch.value

    def event_loop(self):
        next_state = 0
        while True:
            next_state = Game.states[next_state].run()


if __name__ == '__main__':
    Game()
