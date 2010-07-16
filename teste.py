from topd import *
import time

p = Patch()
osc = Object(p, 'osc~ 440')

for x in range(100):
    osc.move(x,x)
    time.sleep(1)
    
