class GameAction: # An action that affects the game
    def __init__(self, game, adj):
        self.game = game
        self.adj = adj
        if self.verify(): self.do()

    def verify(self): raise NotImplementedError
    def do(self): raise NotImplementedError

class query(GameAction):
    def __init__(self, game, adj):
        GameAction.__init__(self, game, adj)

    def verify(self): return True
    def do(self): self.game.setQuery(self.adj)

class quit(GameAction):
    def __init__(self, game, adj):
        GameAction.__init__(self, game, adj)

    def verify(self): return True
    def do(self): exit()

class CharacterGameAction(GameAction): # An action that affects a character and/or the game
    def __init__(self, character, game, adj):
        self.character = character
        GameAction.__init__(self, game, adj)

class move(CharacterGameAction):
    def __init__(self, character, game, adj):
        CharacterGameAction.__init__(self, character, game, adj)

    def verify(self):
        def walkable(x, y): return x >= 0 and x < self.game.getMap().getW() and y >= 0 and y < self.game.getMap().getH() and self.game.getMap().getTile(x, y).getProp('walkable')

        x, y = self.game.getCharacterCoords(self.character)
        try:
            verified = {
                'u' : walkable(x, y - 1),
                'd' : walkable(x, y + 1),
                'l' : walkable(x - 1, y),
                'r' : walkable(x + 1, y),
                'ul' : walkable(x - 1, y - 1),
                'ur' : walkable(x + 1, y - 1),
                'dl' : walkable(x - 1, y + 1),
                'dr' : walkable(x + 1, y + 1)
            }[self.adj]
        except KeyError: verified = False

        if not verified: self.character.addStatusMessage('That space is blocked.')

        return verified

    def do(self):
        if 'u' in self.adj: self.game.getCharacterMap().moveUp(self.character)
        if 'd' in self.adj: self.game.getCharacterMap().moveDown(self.character)
        if 'l' in self.adj: self.game.getCharacterMap().moveLeft(self.character)
        if 'r' in self.adj: self.game.getCharacterMap().moveRight(self.character)

        self.character.incSteps(len(self.adj))

        self.character.incHunger(10 * len(self.adj))

        way = {
            'u' : 'up',
            'd' : 'down',
            'l' : 'left',
            'r' : 'right',
            'ul' : 'up and to the left',
            'ur' : 'up and to the right',
            'dl' : 'down and to the left',
            'dr' : 'down and to the right'
        }[self.adj]

        self.character.addStatusMessage('You move ' + way + '.')

class pickup(CharacterGameAction):
    def __init__(self, character, game, adj):
        CharacterGameAction.__init__(self, character, game, None)

    def verify(self):
        if self.character.getInventory().isFull():
            self.character.addStatusMessage('Your inventory is full.')
            return False
        else:
            x, y = self.game.getCharacterCoords(self.character)
            tile = self.game.getMap().getTile(x, y)
            if tile.getInventory().getSize() > 0:
                return True
            else:
                self.character.addStatusMessage('There\'s nothing to pickup.')

    def do(self):
        x, y = self.game.getCharacterCoords(self.character)
        tile = self.game.getMap().getTile(x, y)
        item = tile.getInventory().takeFirstItem()
        self.character.getInventory().addItem(item)

        self.character.incHunger(1)

        self.character.addStatusMessage('You pickup a ' + item.getName() + '.')

class drop(CharacterGameAction):
    def __init__(self, character, game, adj):
        CharacterGameAction.__init__(self, character, game, adj)

    def verify(self):
        item = self.character.getInventory().getItem(int(self.adj))
        if item is None:
            self.character.addStatusMessage('There\'s nothing there.')
            return False
        else: return True

    def do(self):
        x, y = self.game.getCharacterCoords(self.character)
        tile = self.game.getMap().getTile(x, y)
        item = self.character.getInventory().takeItem(int(self.adj))
        tile.getInventory().addItem(item)

        self.character.incHunger(1)

        self.character.addStatusMessage('You dropped a ' + item.getName() + '.')

class eat(CharacterGameAction):
    def __init__(self, character, game, adj):
        CharacterGameAction.__init__(self, character, game, adj)

    def verify(self):
        item = self.character.getInventory().getItem(int(self.adj))
        if item is None:
            self.character.addStatusMessage('There\'s nothing there.')
            return False
        elif item.getProp('edible') != 1:
            self.character.addStatusMessage('That isn\'t edible.')
            return False
        else: return True

    def do(self):
        food = self.character.getInventory().takeItem(int(self.adj))
        tasteDescription = self._getTasteDescription(self.character.getHungerPercent())
        self.character.decHunger(food.getProp('calories'))
        self.character.addStatusMessage('You eat the ' + food.getName() + '. It tastes ' + tasteDescription + '.')

    def _getTasteDescription(self, hungerPercent):
        ranges = {
            100: 'incredible',
            80:  'amazing',
            70:  'delicious',
            60:  'really good',
            50:  'great',
            40:  'good',
            20:  'fine'
        }

        for r in sorted(ranges.keys()):
            if hungerPercent <= r: return ranges[r]
