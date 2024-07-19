import sys
import time
import threading
import itertools

def clear_screen():
    sys.stdout.write("\033[2J\033[H")

def move_cursor(x, y):
    sys.stdout.write(f"\033[{y};{x}H")

def set_color(color):
    sys.stdout.write(f"\033[{color}m")

def reset_color():
    sys.stdout.write("\033[0m")

def clear_line():
    sys.stdout.write("\033[2K\r")

def print_at(x, y, text, color_code=None):
    move_cursor(x, y)
    if color_code:
        set_color(color_code)
    sys.stdout.write(text)
    if color_code:
        reset_color()

def save_cursor():
    sys.stdout.write("\033[s")

def restore_cursor():
    sys.stdout.write("\033[u")
