from topd import *

# !!! open recebe.pd on a pd process first !!!
# !!! abra recebe.pd em um processo pd primeiro !!!

# creates a 'virtual' patch, connecting to a pd instance (running recebe.pd)
# cria um patch 'virtual', conectando-o a uma instancia de pd (rodando recebe.pd)
p = Patch('recebe.pd', 'localhost', 3006)

# creates some boxes
# cria algumas caixas
msg = Message('220', 100, 10)
osc = Object('osc~', '440', 100, 100)
dac = Object('dac~', '', 100, 200)

# adds the boxes to the patch
# adiciona as caixas ao patch
p.create(msg)
p.create(osc)
p.create(dac)

# connect the boxes
# conecta as caixas
p.connect(msg, 0, osc, 0)
p.connect(osc, 0, dac, 0)
p.connect(osc, 0, dac, 1)

# turn on the audio
# liga o audio
p.dsp(1)
