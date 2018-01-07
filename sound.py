"""This module provides sound paying functionality"""
import subprocess


def play_sound(soundfile):
    print('Playing %s' % soundfile)
    return_code = subprocess.call(['aplay', '--device=default:CARD=Device', soundfile], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(return_code)

