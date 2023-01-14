import pygame
from time import sleep
import threading
from pygame.locals import * 
import numpy as np

class JoyManager():
    
    def __init__(self, user_callback = None):
        self.dt = 0.01 #Sampling frequence of the joystick
        self.runnign = False
        self.joy_thread_handle = threading.Thread(target=self.joy_thread)
        #an optional callback that can be used to send the reading values to a user provided function
        self.user_callback = user_callback
        pygame.init()
        self.offset = None

    def joy_thread(self):
        while self.running:   
            for event in [pygame.event.wait(200), ] + pygame.event.get():
                    # QUIT             none
                    # ACTIVEEVENT      gain, state
                    # KEYDOWN          unicode, key, mod
                    # KEYUP            key, mod
                    # MOUSEMOTION      pos, rel, buttons
                    # MOUSEBUTTONUP    pos, button
                    # MOUSEBUTTONDOWN  pos, button
                    # JOYAXISMOTION    joy, axis, value
                    # JOYBALLMOTION    joy, ball, rel
                    # JOYHATMOTION     joy, hat, value
                    # JOYBUTTONUP      joy, button
                    # JOYBUTTONDOWN    joy, button
                    # VIDEORESIZE      size, w, h
                    # VIDEOEXPOSE      none
                    # USEREVENT        code
                    if event.type == QUIT:
                        self.stop_daq()
                    elif event.type == KEYDOWN and event.key in [K_ESCAPE, K_q]:
                        self.stop_daq()
                    elif event.type == JOYAXISMOTION:
                        self.analog_cmd[event.axis] = event.value
                    elif event.type == JOYBUTTONUP:
                        self.digital_cmd[event.button] = 0
                    elif event.type == JOYBUTTONDOWN:
                        self.digital_cmd[event.button] = 1
                    if self.user_callback is not None and event.type!=NOEVENT:
                        if self.offset is None:
                            self.user_callback(self.analog_cmd, self.digital_cmd)
                        else:
                            self.user_callback(np.array(self.analog_cmd)-self.offset, self.digital_cmd)

                
    def start_daq(self, joy_idx):
        #Get the joy object
        assert pygame.joystick.get_count() != 0, 'No joysticks detected, you can not start the class'
        assert pygame.joystick.get_count() >= joy_idx, 'The requested joystick ID exceeds the number of availble devices'
        self.joy = pygame.joystick.Joystick(joy_idx)
        
        self.analog_cmd = [self.joy.get_axis(i) for i in range(self.joy.get_numaxes())]
        self.digital_cmd = [self.joy.get_button(i) for i in range(self.joy.get_numbuttons())]
        self.running = True
        self.joy_thread_handle.start()
        
    def stop_daq(self):
        self.running = False
        self.joy_thread_handle.join()
        
    def read_raw(self):
        return self.analog_cmd, self.digital_cmd

    def offset_calibration(self):
        analog , _ = self.read_raw()
        offset = np.array(analog)
        print('Put your stick at zero location and do not touch it')
        sleep(1)
        for i in range(2000):
            sleep(0.001)
            analog , _ = self.read_raw()
            offset += np.array(analog)
        self.offset = offset / 2000

    def read_values(self):
        analog, digital = self.read_raw()
        if self.offset is None:
            return analog, digital
        else:
            return analog-self.offset, digital