"""This module provides helper functions for several different tasks"""
import os
import random
import subprocess
import time
from queue import Queue
from threading import Thread


def cavity_resonant_blinking(led_0, led_1, adc):
    epsilon = 0.02
    steps_lightfield_1 = [x * 0.18 for x in range(10)]
    steps_lightfield_2 = [x * 0.16 + 0.08 for x in range(10)]
    adc_read = adc.value
    led_0.state = True if any(map(lambda x: abs(adc_read - x) < epsilon, steps_lightfield_1)) else False
    led_1.state = True if any(map(lambda x: abs(adc_read - x) < epsilon, steps_lightfield_2)) else False


def kick_out_atom(servo):
    servo.angle = 1.0
    time.sleep(0.5)
    servo.angle = 0.0
    time.sleep(0.5)


def blink_randomly(led_0, led_1):
    led_0.state = bool(random.randint(0, 1))
    led_1.state = bool(random.randint(0, 1))
    time.sleep(0.3)


def blink_alternating(led_0, led_1):
    led_0.state = True
    led_1.state = False
    time.sleep(0.3)
    led_0.state = False
    led_1.state = True
    time.sleep(0.3)


def blink_together(led_0, led_1):
    led_0.state = True
    led_1.state = True
    time.sleep(0.3)
    led_0.state = False
    led_1.state = False
    time.sleep(0.3)


class Sound:
    def __init__(self, soundfolder, effects=None, insults=None, stagesounds=None):
        self.soundfolder = soundfolder
        sounds = [sound for sound in os.listdir(self.soundfolder) if sound.endswith('.wav')]
        if effects is None:
            self.effects = [sound for sound in sounds if sound.startswith('E')]
        else:
            self.effects = effects
        if insults is None:
            self.insults = [sound for sound in sounds if sound.startswith('I')]
        else:
            self.insults = insults
        if stagesounds is None:
            self.stagesounds = [sound for sound in sounds if sound.startswith('S')]
        else:
            self.stagesounds = stagesounds
        self.stagesounds.sort(key=lambda x: x[1])
        self.break_sound_loop = False
        self.sound_queue = Queue()
        self.play_thread = Thread(target=self.sound_server, args=())
        self.play_thread.daemon = True
        self.play_thread.start()

    def play_sound(self, soundfile):
        soundfile = "%s/%s" % (self.soundfolder, soundfile)
        return_code = subprocess.call(['aplay', '--device=default:CARD=Device', soundfile], stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)

    def sound_server(self):
        while True:
            self.play_sound(self.sound_queue.get())

    def start_random_sound_loop(self):
        self.break_sound_loop = False
        sound_loop_thread = Thread(target=self.random_sound_loop, args=())
        sound_loop_thread.daemon = True
        sound_loop_thread.start()

    def random_sound_loop(self):
        time.sleep(10)
        break_loop = False
        while not break_loop:
            random_sound = random.choice(self.insults + self.effects)
            self.sound_queue.put(random_sound)
            for i in range(100):
                time.sleep(0.3)
                if self.break_sound_loop:
                    break_loop = True
                    break

    def clear_sound_loop(self):
        while not self.sound_queue.empty():
            _ = self.sound_queue.get(block=False)

    def stop_sound_loop(self):
        self.break_sound_loop = True
        self.clear_sound_loop()

    def play_stage_sound(self, stagenumber):
        try:
            self.sound_queue.put(self.stagesounds[stagenumber])
        except IndexError:
            print("Tried to put %d stagesound into queue but doesn't exist" % stagenumber)


if __name__ == '__main__':
    sound = Sound('sounds')
    sound.start_random_sound_loop()
    while True:
        pass
