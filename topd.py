import socket

class Box(object):
    def __init__(self, patch, fudi_msg, x, y):
        self.x = x
        self.y = y
        self.patch = patch
        self.fudi_msg = fudi_msg
        self.patch.boxes.append(self)
        self.patch.editmode(1)
        self.patch.s.send('pd-%s %s;' % (patch.filename, fudi_msg))

    def delete(self):
        self.patch.editmode(1)
        self.patch.s.send('pd-%s mouse %i %i 1 0;' %
                          (self.patch.filename, self.x - 1, self.y - 1))
        self.patch.s.send('pd-%s motion %i %i 0;' %
                          (self.patch.filename, self.x + 1, self.y + 1))
        self.patch.s.send('pd-%s mouseup %i %i 1 0;' %
                          (self.patch.filename, self.x + 1, self.y + 1))
        self.patch.s.send('pd-%s cut;' % self.patch.filename)
        self.patch.boxes.remove(self)

    def move(self, x, y):
        self.patch.editmode(1)
        self.patch.s.send('pd-%s mouse %i %i 1 0;' %
                          (self.patch.filename, self.x + 1, self.y + 1))
        self.patch.s.send('pd-%s motion %i %i 0;' %
                          (self.patch.filename, x, y))
        self.patch.s.send('pd-%s mouseup 10 10 0 1;' % self.patch.filename)
        self.x = x
        self.y = y
        self.patch.boxes[self.patch.boxes.index(self)] = self

    def click(self):
        self.patch.editmode(0)
        self.patch.s.send('pd-%s mouse %i %i 1 0;' %
                          (self.patch.filename, self.x + 1, self.y + 1))
        self.patch.s.send('pd-%s mouseup %i %i 0 1;' %
                          (self.patch.filename, self.x + 1, self.y + 1))

    def edit(self, newbox):
        print 'Sorry... not implemented yet :-P'

    def connect(self, source_outlet, target_box, target_inlet):
        self.patch.editmode(1)
        self.patch.s.send('pd-%s connect %i %i %i %i;' %
                          (self.patch.filename,
                           self.patch.boxes.index(self) + 1, source_outlet,
                           self.patch.boxes.index(target_box) + 1, target_inlet))

    def disconnect(self, source_outlet, target_box, target_inlet):
        self.patch.editmode(1)
        self.patch.s.send('pd-%s disconnect %i %i %i %i;' %
                          (self.patch.filename,
                           self.patch.boxes.index(self) + 1, source_outlet,
                           self.patch.boxes.index(target_box) + 1, target_inlet))


class Object(Box):
    def __init__(self, patch, name, arguments, x, y):
        super(Object, self).__init__(patch,
                                     'obj %i %i %s %s' %
                                     (x, y, name, arguments),
                                     x, y)
        self.name = name
        self.arguments = arguments

class Message(Box):
    def __init__(self, patch, value, x, y):
        super(Message, self).__init__(patch,
                                      'msg %i %i %s' % (x, y, value),
                                      x, y)
        self.value = value

class Number(Box):
    def __init__(self, patch, x, y):
        super(Number, self).__init__(patch,
                                     'floatatom %i %i' % (x, y),
                                     x, y)

class Symbol(Box):
    def __init__(self, patch, x, y):
        super(Symbol, self).__init__(patch,
                                     'symbolatom %i %i' % (x, y),
                                     x, y)

class Comment(Box):
    def __init__(self, patch, value, x, y):
        super(Comment, self).__init__(patch,
                                      'text %i %i %s' % (x, y, value),
                                      x, y)
        self.value = value

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
