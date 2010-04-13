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

class Comment(Box):
    pass

class GUI(Box):
    pass

class Patch:
    def __init__(self, filename='recebe.pd', hostname='localhost', port=3006):
        self.filename = filename
        self.hostname = hostname
        self.port = port
        self.boxes = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((hostname, port))

    def create(self, box):
        self.editmode(1)
        self.boxes.append(box)
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
