import socket

class Box(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Object(Box):
    def __init__(self, name, arguments, x, y):
        super(Object, self).__init__(x, y)
        self.name = name
        self.arguments = arguments
        self.fudi_msg = 'obj %i %i %s %s' % (x, y, name, arguments)

class Message(Box):
    def __init__(self, value, x, y):
        super(Message, self).__init__(x, y)
        self.value = value
        self.fudi_msg = 'msg %i %i %s' % (x, y, value)

class Number(Box):
    def __init__(self, x, y):
        super(Number, self).__init__(x, y)
        self.fudi_msg = 'floatatom %i %i' % (x, y)

class Symbol(Box):
    def __init__(self, x, y):
        super(Symbol, self).__init__(x, y)
        self.fudi_msg = 'symbolatom %i %i' % (x, y)

class Comment(Box):
    def __init__(self, value, x, y):
        super(Comment, self).__init__(x, y)
        self.value = value
        self.fudi_msg = 'text %i %i %s' % (x, y, value)

class GUI(Box):
    pass

class Patch(object):
    def __init__(self, filename='recebe.pd', hostname='localhost', port=3006):
        self.filename = filename
        self.hostname = hostname
        self.port = port
        self.boxes = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((hostname, port))

    def create(self, box):
        self.boxes.append(box)
        self.editmode(1)
        self.s.send('pd-%s %s;' % (self.filename, box.fudi_msg))

    def delete(self, box):
        self.editmode(1)
        self.s.send('pd-%s mouse %i %i 1 0;' %
                    (self.filename, box.x - 1, box.y - 1))
        self.s.send('pd-%s motion %i %i 0;' %
                    (self.filename, box.x + 1, box.y + 1))
        self.s.send('pd-%s mouseup %i %i 1 0;' %
                    (self.filename, box.x + 1, box.y + 1))
        self.s.send('pd-%s cut;' % self.filename)
        self.boxes.remove(box)

    def move(self, box, x, y):
        self.editmode(1)
        self.s.send('pd-%s mouse %i %i 1 0;' %
                    (self.filename, box.x + 1, box.y + 1))
        self.s.send('pd-%s motion %i %i 0;' %
                    (self.filename, x, y))
        self.s.send('pd-%s mouseup 0 0 1 0;' % self.filename)
        box.x = x
        box.y = y
        self.boxes[self.boxes.index(box)] = box

    def click(self, box):
        self.editmode(0)
        self.s.send('pd-%s mouse %i %i 1 0;' %
                    (self.filename, box.x + 1, box.y + 1))
        self.s.send('pd-%s mouseup %i %i 0 1;' %
                    (self.filename, box.x + 1, box.y + 1))

    def edit(self, box, newbox):
        print 'Sorry... not implemented yet :-P'

    def connect(self, source_box, source_outlet, target_box, target_inlet):
        self.editmode(1)
        self.s.send('pd-%s connect %i %i %i %i;' %
                    (self.filename,
                     self.boxes.index(source_box) + 1, source_outlet,
                     self.boxes.index(target_box) + 1, target_inlet))

    def disconnect(self, source_box, source_outlet, target_box, target_inlet):
        self.editmode(1)
        self.s.send('pd-%s disconnect %i %i %i %i;' %
                    (self.filename,
                     self.boxes.index(source_box) + 1, source_outlet,
                     self.boxes.index(target_box) + 1, target_inlet))

    def editmode(self, state):
        self.s.send('pd-%s editmode %i;' % (self.filename, state))
        
    def dsp(self, state):
        self.s.send('pd dsp %i;' % state)
