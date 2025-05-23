from DIYables_Pico_Keypad import Keypad
import time

NUM_ROWS = 4
NUM_COLS = 4

# Constants for GPIO pins
ROW_PINS = [40, 39, 38, 48]  # GPIO numbers for row pins
COLUMN_PINS = [1, 2, 42, 41]  # GPIO numbers for column pins

# Keymap corresponds to the layout of the keypad 4x4
KEYMAP = ['1', '2', '3', 'A',
          '4', '5', '6', 'B',
          '7', '8', '9', 'C',
          '*', '0', '#', 'D']

# Initialize the keypad
keypad = Keypad(KEYMAP, ROW_PINS, COLUMN_PINS, NUM_ROWS, NUM_COLS)
keypad.set_debounce_time(400) # 400ms, addjust it if it detects twice for single press

# Main loop to check for key presses
while True:
    key = keypad.get_key()
    if key:
        print("Key pressed:", key)
    