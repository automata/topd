from topd import *

# !!! open recebe.pd on a pd process first !!!
# !!! abra recebe.pd em um processo pd primeiro !!!

# creates a 'virtual' patch, connecting to a pd instance (running recebe.pd)
# cria um patch 'virtual', conectando-o a uma instancia de pd (rodando recebe.pd)
p = Patch('recebe.pd', 'localhost', 4242)

# creates some boxes
# cria algumas caixas
msg = Message(p, '220', 100, 10)
osc = Object(p, 'osc~ 440', 100, 100)
dac = Object(p, 'dac~', 100, 200)

# connect the boxes
# conecta as caixas
msg.connect(0, osc, 0)
osc.connect(0, dac, 0)
osc.connect(0, dac, 1)

# turn on the audio
# liga o audio
p.dsp(True)
