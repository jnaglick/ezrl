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

class EntityGameAction(GameAction): # An action that affects an entity and/or the game
    def __init__(self, entity, game, adj):
        self.entity = entity
        GameAction.__init__(self, game, adj)

class move(EntityGameAction):
    def __init__(self, entity, game, adj):
        EntityGameAction.__init__(self, entity, game, adj)

    def verify(self):
        def walkable(x, y): return x >= 0 and x < self.game.getMap().getW() and y >= 0 and y < self.game.getMap().getH() and self.game.getMap().getTile(x, y).getProp('walkable')

        x, y = self.entity.getX(), self.entity.getY()
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

        if not verified: self.entity.addStatusMessage('That space is blocked.')

        return verified

    def do(self):
        if 'u' in self.adj: self.entity.decY()
        if 'd' in self.adj: self.entity.incY()
        if 'l' in self.adj: self.entity.decX()
        if 'r' in self.adj: self.entity.incX()

        self.entity.incSteps()
        if len(self.adj) == 2: self.entity.incSteps()

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

        self.entity.addStatusMessage('You move ' + way + '.')

class pickup(EntityGameAction):
    def __init__(self, entity, game, adj):
        EntityGameAction.__init__(self, entity, game, None)

    def verify(self):
        if self.entity.getInventory().isFull():
            self.entity.addStatusMessage('Your inventory is full.')
            return False
        else:
            tile = self.game.getMap().getTile(self.entity.getX(), self.entity.getY())
            if tile.getInventory().getSize() > 0:
                return True
            else:
                self.entity.addStatusMessage('There\'s nothing to pickup.')

    def do(self):
        tile = self.game.getMap().getTile(self.entity.getX(), self.entity.getY())
        item = tile.getInventory().takeFirstItem()
        self.entity.getInventory().addItem(item)
        self.entity.addStatusMessage('You pickup a ' + item.getName() + '.')

class eat(EntityGameAction):
    def __init__(self, entity, game, adj):
        EntityGameAction.__init__(self, entity, game, adj)

    def verify(self):
        item = self.entity.getInventory().getItem(int(self.adj))
        if item is None:
            self.entity.addStatusMessage('There\'s nothing there.')
            return False
        elif item.getProp('edible') != 1:
            self.entity.addStatusMessage('That isn\'t edible.')
            return False
        else: return True

    def do(self):
        food = self.entity.getInventory().takeItem(int(self.adj))
        self.entity.addStatusMessage('You eat the ' + food.getName() + '. It tasted great, really, seriously.')
