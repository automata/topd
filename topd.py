import socket

# boxes ########################################################################

class Box(object):
    def __init__(self, patch, fudi_token, label, x, y):
        if x is None and y is None:
            freex, freey = patch.next_freeposition()
            self.x = freex
            self.y = freey
        else:
            self.x = x
            self.y = y
        self.patch = patch
        self.fudi_token = fudi_token
        self.label = label
        self.patch.boxes.append(self)
        self.patch.editmode(True)
        self.patch.send('%s %i %i %s' % (fudi_token, self.x, self.y, label))

    def delete(self):
        self.patch.send('mouse %i %i 1 0' % (self.x - 1, self.y - 1))
        self.patch.send('motion %i %i 0' % (self.x + 1, self.y + 1))
        self.patch.send('mouseup %i %i 1 0' % (self.x + 1, self.y + 1))
        self.patch.send('cut')
        self.patch.boxes.remove(self)

    def __str__(self):
        return 'Hi... I am a box :-P'

    def move(self, x, y):
        self.patch.send('mouse %i %i 1 0' % (self.x + 1, self.y + 1))
        self.patch.send('motion %i %i 0' % (x, y))
        self.patch.send('mouseup %i %i 1 0' % (x, y))
        self.patch.send('mouse %i %i 1 0' % (self.x - 2, self.y - 2))
        self.patch.send('mouseup %i %i 1 0' % (self.x -2, self.y - 2))
        self.x = x
        self.y = y
        self.patch.boxes[self.patch.boxes.index(self)] = self

    def click(self):
        self.patch.send('mouse %i %i 1 0' % (self.x + 1, self.y + 1))
        self.patch.send('mouseup %i %i 1 0' % (self.x + 1, self.y + 1))

    def edit(self, label):
        self.unselect()
        self.click()

        for c in label:
            self.patch.send('key 1 %i 0' % ord(c))
            self.patch.send('key 0 %i 0' % ord(c))

        self.unselect()
        self.label = label

    def select(self):
        self.patch.send('mouse %i %i 1 0' % (self.x - 2, self.y - 2))
        self.patch.send('motion %i %i 0' % (self.x + 1, self.y + 1))
        self.patch.send('mouseup %i %i 1 0' % (self.x + 1, self.y + 1))

    def unselect(self):
        self.patch.send('mouse %i %i 1 0' % (self.x - 1, self.y - 1))
        self.patch.send('mouseup %i %i 1 0' % (self.x - 1, self.y - 1))

    def connect(self, source_outlet, target_box, target_inlet):
        self.patch.send('connect %i %i %i %i' %
                        (self.patch.boxes.index(self) + 1, source_outlet,
                         self.patch.boxes.index(target_box) + 1, target_inlet))
        c = Connection(self, source_outlet, target_box, target_inlet)
        self.patch.connections.append(c)

    def disconnect(self, source_outlet, target_box, target_inlet):
        self.patch.send('disconnect %i %i %i %i' %
                        (self.patch.boxes.index(self) + 1, source_outlet,
                         self.patch.boxes.index(target_box) + 1, target_inlet))
        for c in self.patch.connections:
            if ((c.source_box == self) and
                (c.source_outlet == source_outlet) and
                (c.target_box == target_box) and
                (c.target_inlet == target_inlet)):
                break
        self.patch.connections.remove(c)

class Object(Box):
    def __init__(self, patch, label, x=None, y=None):
        super(Object, self).__init__(patch, 'obj', label, x, y)
        splitted_label = label.split(' ')
        self.name = splitted_label[0]
        self.arguments = splitted_label[1:]

    def __str__(self):
        return '[ %s ]' % self.label

class Message(Box):
    def __init__(self, patch, label, x=None, y=None):
        super(Message, self).__init__(patch, 'msg', label, x, y)

    def __str__(self):
        return '[ %s (' % self.label

class Number(Box):
    def __init__(self, patch, x=None, y=None):
        super(Number, self).__init__(patch, 'floatatom', '', x, y)

    def __str__(self):
        return 'Hi... I am a number ;-)'

class Symbol(Box):
    def __init__(self, patch, x=None, y=None):
        super(Symbol, self).__init__(patch, 'symbolatom', '', x, y)

    def __str__(self):
        return 'Hi... I am a symbol ;-)'

class Comment(Box):
    def __init__(self, patch, label, x=None, y=None):
        super(Comment, self).__init__(patch, 'text', label, x, y)

    def __str__(self):
        return '" %s "' % self.label

# GUIs #########################################################################

class GUI(Object):
    def __init__(self, patch, label, x=None, y=None):
        super(GUI, self).__init__(patch, label, x, y)

    # FIXME: to add common GUI properties here: color, label, ...

class Bang(GUI):
    def __init__(self, patch, x=None, y=None):
        super(Bang, self).__init__(patch, 'bng', x, y)

    def bang(self):
        self.patch.editmode(False)
        self.click()
        self.patch.editmode(True)

class HSlider(GUI):
    def __init__(self, patch, x=None, y=None):
        super(HSlider, self).__init__(patch, 'hsl', x, y)
        self.value = 0
        self.min = 0
        self.max = 127

    def increment(self, step=1):
        if self.value < self.max:
            self.value += step

            self.patch.editmode(False)
            self.patch.send('mouse %i %i 1 0' %
                            (self.x + self.value, self.y + 1))
            self.patch.send('motion %i %i 0' %
                            (self.x + self.value + 1, self.y + 1))
            self.patch.send('mouseup %i %i 0 1' %
                            (self.x + self.value + 1, self.y + 1))
            self.patch.editmode(True)
        
    def decrement(self, step=1):
        if self.value > self.min:
            self.value -= step

            self.patch.editmode(False)
            self.patch.send('mouse %i %i 1 0' %
                            (self.x + 1, self.y + 1))
            self.patch.send('motion %i %i 0' %
                            (self.x, self.y + 1))
            self.patch.send('mouseup %i %i 0 1' %
                            (self.x, self.y + 1))
            self.patch.editmode(True)

class VSlider(GUI):
    def __init__(self, patch, x=None, y=None):
        super(VSlider, self).__init__(patch, 'vsl', x, y)
        self.value = 0
        self.min = 0
        self.max = 127

    def increment(self, step=1):
        if self.value < self.max:
            self.value += step

            self.patch.editmode(False)
            self.patch.send('mouse %i %i 1 0' %
                            (self.x + 1, self.y + 1))
            self.patch.send('motion %i %i 0' %
                            (self.x + 1, self.y))
            self.patch.send('mouseup %i %i 0 1' %
                            (self.x + 1, self.y))
            self.patch.editmode(True)
        
    def decrement(self, step=1):
        if self.value > self.min:
            self.value -= step

            self.patch.editmode(False)
            self.patch.send('mouse %i %i 1 0' %
                            (self.x + 1, self.y + self.value))
            self.patch.send('motion %i %i 0' %
                            (self.x + 1, self.y + self.value + 1))
            self.patch.send('mouseup %i %i 0 1' %
                            (self.x + 1, self.y + self.value + 1))
            self.patch.editmode(True)

class Toggle(GUI):
    def __init__(self, patch, x=None, y=None):
        super(Toggle, self).__init__(patch, 'tgl', x, y)
        self.state = False

    def on(self):
        if not self.state:
            self.patch.editmode(False)
            self.click()            
            self.patch.editmode(True)
            self.state = True
        else:
            print 'Warning! Toggle already ON.'

    def off(self):
        if self.state:
            self.patch.editmode(False)
            self.click()            
            self.patch.editmode(True)
            self.state = False
        else:
            print 'Warning! Toggle already OFF.'

class Number2(GUI):
    def __init__(self, patch, x=None, y=None):
        super(Number2, self).__init__(patch, 'nbx', x, y)

class Radio(GUI):
    def __init__(self, patch, x=None, y=None):
        super(Radio, self).__init__(patch, label, x, y)

class VRadio(Radio):
    def __init__(self, patch, x=None, y=None):
        super(VRadio, self).__init__(patch, 'vradio', x, y)

class HRadio(Radio):
    def __init__(self, patch, x=None, y=None):
        super(HRadio, self).__init__(patch, 'hradio', x, y)

class VU(GUI):
    def __init__(self, patch, x=None, y=None):
        super(VU, self).__init__(patch, 'vu', x, y)

class Canvas(GUI):
    def __init__(self, patch, x=None, y=None):
        super(Canvas, self).__init__(patch, 'cnv', x, y)

# connections #################################################################

class Connection(object):
    def __init__(self, source_box, source_outlet, target_box, target_inlet):
        self.source_box = source_box
        self.source_outlet = source_outlet
        self.target_box = target_box
        self.target_inlet = target_inlet

    def __str__(self):
        return '%s %i->%i %s' % (self.source_box.__str__(), self.source_outlet, self.target_inlet, self.target_box.__str__())

# patch #######################################################################

class Patch(object):
    def __init__(self, filename='receive.pd', hostname='localhost', port=4242):
        self.filename = filename
        self.hostname = hostname
        self.port = port
        self.boxes = []
        self.connections = []
        self.freeposition = (0,0)
        try: 
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((hostname, port))
        except socket.error, (value, message):
            if self.s:
                self.s.close()
            print 'Could not connect to patch %s at %s:%s' % (filename, hostname, port)
            print 'Socket error:', message 

    def __str__(self):
        str = 'Remote patch %s connected at %s:%i.\n\n' % (self.filename, self.hostname, self.port)
        if self.boxes != []:
            str += '%i boxes:\n' % len(self.boxes)
            for b in self.boxes:
                str += '\t%s\n' % b.__str__()
        else:
            str += 'No boxes yet.\n'
        if self.connections != []:
            str += '%i connections:\n' % len(self.connections)
            for c in self.connections:
                str += '\t%s\n' % c.__str__()
        else:
            str += 'No connections yet.\n'
        return str

    def editmode(self, state):
        if state:
            self.send('editmode 1')
        else:
            self.send('editmode 0')
        
    def dsp(self, state):
        if state:
            self.s.send('pd dsp 1;')
        else:
            self.s.send('pd dsp 0;')

    def send(self, fudi_msg):
        self.s.send('pd-%s %s;' % (self.filename, fudi_msg))

    def clear(self):
        for b in self.boxes:
            b.delete()

        for c in self.connections:
            c.delete()

    def next_freeposition(self):
        x, y = self.freeposition
        self.freeposition = (x, y + 20)
        return (x, y)
    
    # DEPRECATED: manter os metodos abaixo para garantir compatibilidade?!

    def delete(self, box):
        box.delete()

    def move(self, box, x, y):
        box.move(x, y)

    def click(self, box):
        box.click()

    def edit(self, box, label):
        box.edit(label)

    def select(self, box):
        box.select()

    def unselect(self, box):
        box.unselect()

    def connect(self, source_box, source_outlet, target_box, target_inlet):
        source_box.connect(source_outlet, target_box, target_inlet)

    def disconnect(self, source_box, source_outlet, target_box, target_inlet):
        source_box.disconnect(source_outlet, target_box, target_inlet)
