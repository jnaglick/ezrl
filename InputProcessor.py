from libtcodpy import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, console_wait_for_keypress

from types import StringType, TupleType

class ConsoleInputProcessor: # InputProcessor that simulates a CLI
    def __init__(self):
        self.command = None

    def fetchCommands(self):
        if self.command == None: self.command = ''

        print '$ %s' % self.command

        key = console_wait_for_keypress(True)

        if key.c != 0: #printable char (??)
            if key.c == 27: # Esc
                return ['sys exit']
            elif key.c == 13: # Enter
                return self.resolve()
            elif key.c == 8: # Backspace
                if len(self.command) > 0: self.command = self.command[:-1]
            else:
                self.command += chr(key.c)

        return self.fetchCommands()

    def resolve(self):
        r = self.command
        self.command = None
        return [r]

class KeyboardInputProcessor:
    def __init__(self):
        self.partialCommand = None
        self.nextPartialCommands = None
        
        self.inventoryPartialCommands = {}
        for i in range(0, 10): self.inventoryPartialCommands[ord(str(i))] = str(i) # ord('0'):'0', ord('1'):'1', etc
        
        self.inputToCommand = {
            ord('x')    : 'sys exit',

            KEY_UP      : 'p move u',
            ord('k')    : 'p move u',

            KEY_DOWN    : 'p move d',
            ord('j')    : 'p move d',

            KEY_LEFT    : 'p move l',
            ord('h')    : 'p move l',

            KEY_RIGHT   : 'p move r',
            ord('l')    : 'p move r',

            ord('u')    : 'p move ul',
            ord('i')    : 'p move ur',
            ord('n')    : 'p move dl',
            ord('m')    : 'p move dr',

            ord(',')    : 'p pickup',
            ord('p')    : 'p pickup',

            ord('e')    : ('sys query Eat What?', 'p eat',  self.inventoryPartialCommands)
        }

    def fetchCommands(self):
        actions = []

        key = console_wait_for_keypress(True)

        if key.c != 0: keycode = key.c #printable char
        else: keycode = key.vk #physical key

        if self.partialCommand != None:
            actions.append(self.resolvePartialCommand(keycode))
        else:
            try:
                command = self.inputToCommand[keycode]
                if type(command) == StringType: actions.append(command) # simple command
                elif type(command) == TupleType: actions.append(self.setupPartialCommand(*command)) # partial command
            except KeyError: None

        return actions

    def setupPartialCommand(self, immediateCommand, partialCommand, nextPartialCommands):
        self.partialCommand = partialCommand
        self.nextPartialCommands = nextPartialCommands
        return immediateCommand

    def resolvePartialCommand(self, keycode):
        command = None
        try: command = self.partialCommand + ' ' + self.nextPartialCommands[keycode]
        except KeyError: command = 'sys query Nevermind.'
        self.partialCommand = None
        self.nextPartialCommands = None
        return command
