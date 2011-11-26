from libtcodpy import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, console_wait_for_keypress

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
            ord('p')    : 'p pickup'
        }

    def fetchCommands(self):
        actions = []

        key = console_wait_for_keypress(True)

        if key.c != 0: keycode = key.c #printable char
        else: keycode = key.vk #physical key

        try: actions.append(self.inputToCommand[keycode])
        except KeyError: None

        return actions
