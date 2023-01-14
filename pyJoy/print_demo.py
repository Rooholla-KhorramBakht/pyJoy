from pyJoy.joy_daq import JoyManager
import signal
import sys

def print_callback(analog, digital):
    analog_print = [f'{a:0.2f}' for a in analog]
    print(f'Analog values: {analog_print}')
    print(f'Digital values: {digital}')

joy1  = JoyManager(user_callback=print_callback)

def signal_handler(sig, frame):
    joy1.stop_daq()
    print('You pressed Ctrl+C!')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    joy1.start_daq(joy_idx=0)
    joy1.offset_calibration()


if __name__ == '__main__':
    main()