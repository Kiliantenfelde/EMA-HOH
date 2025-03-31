class Pin:
   IN = 0
   OUT = 0
   PULL_UP = 0
   def __init__(self, number, mode=-1, pull=-1):
     self.number = number
   def on(self):
     print('Pin %d switches ON' % self.number)
   def off(self):
     print('Pin %d switches OFF' % self.number)
   def value(self):
     return 1