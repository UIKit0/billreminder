import gtk

class Statusbar(gtk.HBox):
    """ This class implements the status bar """
    def __init__(self):
        gtk.HBox.__init__(self)
        self.latest_id = 0
        self.label = gtk.Label()
        self.label.set_justify(gtk.JUSTIFY_LEFT)
        self.pack_start(self.label, expand=False, fill=True, padding=2)
        self.set_border_width(2)
        # message stack is a dictionary as this is a very easy type
        # to add and remove from
        self.stack = {}

    def push(self, message):
        #increment message_id - this will be key for
        #message and highest message_id will be 'top of stack'
        self.latest_id += 1
        self.stack[self.latest_id] = message
        self.displayTopOfStack()
        #print "adding",self.latest_id, message
        return self.latest_id

    def remove(self, message_id):
        #remove message from stack (frst check if it's really there)
        if message_id in self.stack:
            del self.stack[message_id]
        #print "clearing", message_id
        self.displayTopOfStack()

    def displayTopOfStack(self):
        # if stack is now empty then clear status bar
        if len(self.stack) == 0:
            self.label.set_markup("")
            return
        # find the message at the top of the stack and display it
        self.label.set_markup(self.stack[max(self.stack.keys())])
