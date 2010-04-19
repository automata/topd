import socket

class Box(object):
    def __init__(self, patch, fudi_token, label, x, y):
        self.x = x
        self.y = y
        self.patch = patch
        self.fudi_token = fudi_token
        self.label = label
        self.patch.boxes.append(self)
        self.patch.editmode(1)
        self.patch.send('%s %i %i %s' % (fudi_token, x, y, label))

    def delete(self):
        #self.patch.editmode(1)
        self.patch.send('mouse %i %i 1 0' % (self.x - 1, self.y - 1))
        self.patch.send('motion %i %i 0' % (self.x + 1, self.y + 1))
        self.patch.send('mouseup %i %i 1 0' % (self.x + 1, self.y + 1))
        self.patch.send('cut')
        self.patch.boxes.remove(self)

    def __str__(self):
        return 'Hi... I am a box :-P'

    def move(self, x, y):
        #self.patch.editmode(1)
        self.patch.send('mouse %i %i 1 0' % (self.x + 1, self.y + 1))
        self.patch.send('motion %i %i 0' % (x, y))
        self.patch.send('mouseup %i %i 1 0' % (x, y))
        self.patch.send('mouse %i %i 1 0' % (self.x - 2, self.y - 2))
        self.patch.send('mouseup %i %i 1 0' % (self.x -2, self.y - 2))
        self.x = x
        self.y = y
        self.patch.boxes[self.patch.boxes.index(self)] = self

    def click(self):
        #self.patch.editmode(0)
        self.patch.send('mouse %i %i 1 0' % (self.x + 1, self.y + 1))
        self.patch.send('mouseup %i %i 1 0' % (self.x + 1, self.y + 1))

    def edit(self, label):
        self.unselect()
        self.click()

        for c in label:
            self.patch.send('key 1 %i 0' % ord(c))
            self.patch.send('key 0 %i 0' % ord(c))

        # precisa atualizar a lista de boxes?! e as connections?!
        self.unselect()
        self.label = label

    def select(self):
        #self.patch.editmode(1)
        self.patch.send('mouse %i %i 1 0' % (self.x - 2, self.y - 2))
        self.patch.send('motion %i %i 0' % (self.x + 1, self.y + 1))
        self.patch.send('mouseup %i %i 1 0' % (self.x + 1, self.y + 1))

    def unselect(self):
        #self.patch.editmode(1)
        self.patch.send('mouse %i %i 1 0' % (self.x - 1, self.y - 1))
        self.patch.send('mouseup %i %i 1 0' % (self.x - 1, self.y - 1))

    def connect(self, source_outlet, target_box, target_inlet):
        #self.patch.editmode(1)
        self.patch.send('connect %i %i %i %i' %
                        (self.patch.boxes.index(self) + 1, source_outlet,
                         self.patch.boxes.index(target_box) + 1, target_inlet))
        c = Connection(self, source_outlet, target_box, target_inlet)
        self.patch.connections.append(c)

    def disconnect(self, source_outlet, target_box, target_inlet):
        #self.patch.editmode(1)
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
    def __init__(self, patch, label, x, y):
        super(Object, self).__init__(patch, 'obj', label, x, y)
        splitted_label = label.split(' ')
        self.name = splitted_label[0]
        self.arguments = splitted_label[1:]

    def __str__(self):
        return '[ %s ]' % self.label

class Message(Box):
    def __init__(self, patch, label, x, y):
        super(Message, self).__init__(patch, 'msg', label, x, y)

    def __str__(self):
        return '[ %s (' % self.label

class Number(Box):
    def __init__(self, patch, x, y):
        super(Number, self).__init__(patch, 'floatatom', x, y)

    def __str__(self):
        return 'Hi... I am a number ;-)'

class Symbol(Box):
    def __init__(self, patch, x, y):
        super(Symbol, self).__init__(patch, 'symbolatom', x, y)

    def __str__(self):
        return 'Hi... I am a symbol ;-)'

class Comment(Box):
    def __init__(self, patch, label, x, y):
        super(Comment, self).__init__(patch, 'text', label, x, y)

    def __str__(self):
        return '" %s "' % self.label

class GUI(Box):
    pass

class Connection(object):
    def __init__(self, source_box, source_outlet, target_box, target_inlet):
        self.source_box = source_box
        self.source_outlet = source_outlet
        self.target_box = target_box
        self.target_inlet = target_inlet

    def __str__(self):
        return '%s %i->%i %s' % (self.source_box.__str__(), self.source_outlet, self.target_inlet, self.target_box.__str__())

class Patch(object):
    def __init__(self, filename='recebe.pd', hostname='localhost', port=3006):
        self.filename = filename
        self.hostname = hostname
        self.port = port
        self.boxes = []
        self.connections = []
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
        self.send('editmode %i' % state)
        
    def dsp(self, state):
        self.s.send('pd dsp %i;' % state)

    def send(self, fudi_msg):
        self.s.send('pd-%s %s;' % (self.filename, fudi_msg))

    def clear(self):
        for b in self.boxes:
            b.delete()

        for c in self.connections:
            c.delete()
            
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
