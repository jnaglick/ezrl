from libtcodpy import console_wait_for_keypress, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_ENTER, KEY_ESCAPE

class KeymapInputManager():
    def __init__(self):
        self.keymaps = [MainKeymap()] # stack of keymaps
        self.actions = [] # stack of actions
        self.command = None # command to send this time
        self.buffer = '' # buffer for building a command between keymaps

    def fetchCommand(self): # TODO command not commands
        currentKeymap = self.keymaps[-1]
        # get new actions
        newActions = None
        while newActions == None:
            newActions = currentKeymap.getActionsFromKey(self.waitForKeypress())

        # push new actions in reverse order so they're in order while poppin
        # note: we dont use a queue coz we wanna run newActions before pending ones
        for i in range(len(newActions)-1, -1, -1): self.actions.append(newActions[i]) # sorry about the syntax...

        # process actions until we can send command. otherwise, send buffer
        while self.actions:
            action = self.actions.pop()
            action(self, currentKeymap)
            if self.command is not None: return self.flushCommand()
        return self.flushBuffer()

    def waitForKeypress(self):
        key = console_wait_for_keypress(True)
        if key.c not in [0, 8, 9, 13, 27, 32]: key = chr(key.c) # accounts for backspace, tab, enter, esc, space
        else: key = key.vk
        return key

    def flushCommand(self):
        c = self.command
        self.command = None
        return [c]

    def flushBuffer(self):
        b = self.buffer
        self.buffer = ''
        return [b]

    def _sendCommand(self, command):
        self.command = command

    def _appendToBuffer(self, val):
        self.buffer += val

    def _switchTo(self, newMap, args=None):
        if args is not None:
            self.keymaps.append(newMap(*args))
        else:
            self.keymaps.append(newMap())

    def _returnFrom(self, keymap, val=None):
        self.keymaps.pop()
        if val is not None:
            self._appendToBuffer(val)
        else:
            self._appendToBuffer(keymap.getOutput())

def sendCommand(command): return lambda mngr, map: mngr._sendCommand(command)
def appendToBuffer(val): return lambda mngr, map: mngr._appendToBuffer(val)
def switchTo(newMap, args=None): return lambda mngr, map: mngr._switchTo(newMap, args)
def returnFrom(val=None): return lambda mngr, map: mngr._returnFrom(map, val)

class Keymap:
    def __init__(self):
        self.keyToActions = {}
        self.build()

    def build(self): raise NotImplementedError
    def updateInternalState(self, key): None
    def getOutput(self): raise NotImplementedError('Likely caused by Keymap using 0-argument returnFrom() without defining getOutput')

    def getActionsFromKey(self, key):
        self.updateInternalState(key)
        try:
            return self.keyToActions[key]
        except KeyError:
            return None

    def addMapping(self, key_or_keys, actions):
        if isinstance(key_or_keys, list):
            for key in key_or_keys: self.addMapping(key, actions)
        else:
            if not isinstance(actions, list): actions = [actions]
            self.keyToActions[key_or_keys] = actions

class MainKeymap(Keymap):
    def __init__(self):
        Keymap.__init__(self)

    def build(self):
        self.addMapping(KEY_ESCAPE, [switchTo(ConfirmKeymap, ('sys quit', 'sys query Oh okay then.')),
                                     sendCommand('sys query Really Quit?')])

        self.addMapping([KEY_UP, 'k'], sendCommand('p move u'))
        self.addMapping([KEY_DOWN, 'j'], sendCommand('p move d'))
        self.addMapping([KEY_LEFT, 'h'], sendCommand('p move l'))
        self.addMapping([KEY_RIGHT, 'l'], sendCommand('p move r'))
        self.addMapping('u', sendCommand('p move ul'))
        self.addMapping('i', sendCommand('p move ur'))
        self.addMapping('n', sendCommand('p move dl'))
        self.addMapping('m', sendCommand('p move dr'))

        self.addMapping(['p', ','], sendCommand('p pickup'))
        self.addMapping('e', [appendToBuffer('p eat '), # TODO fix having to manually add a space?
                              switchTo(InvKeymap),
                              sendCommand('sys query Eat What?')])
        self.addMapping('d', [appendToBuffer('p drop '),
                              switchTo(InvKeymap),
                              sendCommand('sys query Drop What?')])
        self.addMapping('t', [appendToBuffer('p throw '),
                              switchTo(InvKeymap),
                              sendCommand('sys query Throw What?'),
                              appendToBuffer(' '),
                              switchTo(TargetingKeymap),
                              sendCommand('sys query Throw Where?')])

class InvKeymap(Keymap):
    def __init__(self):
        Keymap.__init__(self)

    def build(self):
        for i in range(0, 10): self.addMapping(str(i), returnFrom(str(i)))

class ConfirmKeymap(Keymap): # if y/Y returns affirmVal, if n/N returns denyVal
    def __init__(self, affirmVal, denyVal):
        self.affirmVal = affirmVal
        self.denyVal = denyVal
        Keymap.__init__(self)

    def build(self):
        self.addMapping(['y', 'Y'], returnFrom(self.affirmVal))
        self.addMapping(['n', 'N'], returnFrom(self.denyVal))

class TargetingKeymap(Keymap):
    def __init__(self):
        self.offsetX = 0
        self.offsetY = 0
        Keymap.__init__(self)

    def build(self):
        self.addMapping(KEY_UP, sendCommand('sys query u'))
        self.addMapping(KEY_DOWN, sendCommand('sys query d'))
        self.addMapping(KEY_LEFT, sendCommand('sys query l'))
        self.addMapping(KEY_RIGHT, sendCommand('sys query r'))
        self.addMapping(KEY_ENTER, returnFrom())

    def updateInternalState(self, key):
        if key == KEY_UP: self.offsetY += -1
        if key == KEY_DOWN: self.offsetY += 1
        if key == KEY_LEFT: self.offsetX += -1
        if key == KEY_RIGHT: self.offsetX += 1

    def getOutput(self):
        return str(self.offsetX) + ',' + str(self.offsetY)
