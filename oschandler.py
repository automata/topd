# dependencia: pyOSC
# $ git clone git://gitorious.org/pyosc/devel.git
# $ cd devel
# $ sudo ./setup.py install

# executando: inicie o seu programa que enviara mensagens OSC e PD (recebe.pd)
# - execute em Processing o sketch processing/testatoPD.pde
# - execute em PD o patch recebe.pd
# - execute em Python o oschandler:
# $ python oschandler.py
# - clique na janela de Processing...

from topd import *
import OSC
import time
import threading

def printing_handler(addr, tags, stuff, source):
    print "---"
    print "received new osc msg from %s" % OSC.getUrlStr(source)
    print "with addr : %s" % addr
    print "typetags %s" % tags
    print "data %s" % stuff
    print "---"

def obj_handler(addr, tags, stuff, source):
    label = stuff[0]
    x = stuff[1]
    y = stuff[2]
    Object(p, label, x, y)

p = Patch()

osc_socket = OSC.OSCServer(('127.0.0.1', 12000))

osc_socket.addDefaultHandlers()
osc_socket.addMsgHandler("/print", printing_handler)
osc_socket.addMsgHandler("/obj", obj_handler)

print "Registered Callback-functions are :"
for addr in osc_socket.getOSCAddressSpace():
    print addr

st = threading.Thread(target=osc_socket.serve_forever)
st.start()
print "Starting OSCServer. Use ctrl-C to quit."    
    
try:
    while True:
        time.sleep(5)
        
except KeyboardInterrupt:
    print "\nClosing OSCServer."
    osc_socket.close()
    print "Waiting for Server-thread to finish"
    st.join()
    print "Done! Bye!"
