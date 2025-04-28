from machine import Pin
from time import sleep

tasterpin = Pin(4, Pin.IN)
testpin = Pin(47, Pin.OUT)


while True:
    if tasterpin.value() == 1:
        print("True")
        testpin.on()
        
    else:
        print("False")
        testpin.off()
    sleep(0.2)