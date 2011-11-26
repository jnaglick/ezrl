class Engine:
    def __init__(self):
        from MapMakers import RandomMapMaker, TestMapMaker

        #create map
        #mapMaker = TestMapMaker()
        mapMaker = RandomMapMaker()

        #create player
        getPlayerStartCoords = mapMaker.getPlayerStartCoords()
        player = Player(getPlayerStartCoords[0], getPlayerStartCoords[1])

        #create game
        self.game = Game(player, mapMaker.getMap())

    def getGame(self): return self.game

    def _vTileWalkable(self, x, y):
        map = self.game.getMap()
        return x >= 0 and x < map.getW() and y >= 0 and y < map.getH() and map.getTile(x, y).getProp('walkable')

    def _vEntityMove(self, entity, adj):
        x, y = entity.getX(), entity.getY()
        try:
            return {
                'u' : self._vTileWalkable(x, y - 1),
                'd' : self._vTileWalkable(x, y + 1),
                'l' : self._vTileWalkable(x - 1, y),
                'r' : self._vTileWalkable(x + 1, y),
                'ul' : self._vTileWalkable(x - 1, y - 1),
                'ur' : self._vTileWalkable(x + 1, y - 1),
                'dl' : self._vTileWalkable(x - 1, y + 1),
                'dr' : self._vTileWalkable(x + 1, y + 1)
            }[adj]
        except KeyError: return False

    def _vEntityPickup(self, entity):
        return entity.getInventory().isNotFull()

    def _vEntityEat(self, entity, adj):
        item = entity.getInventory().getItem(int(adj))
        return item is not None and item.getProp('edible') == 1

    def _verifyEntityCommand(self, entity, verb, adj):
        if verb == 'move': return self._vEntityMove(entity, adj)
        elif verb == 'pickup': return self._vEntityPickup(entity)
        elif verb == 'eat': return self._vEntityEat(entity, adj)
        else: return False

    def _cEntityMove(self, entity, adj):
        if adj == 'u':
            entity.decY()
            d = 'up'
        elif adj == 'd':
            entity.incY()
            d = 'down'
        elif adj == 'l':
            entity.decX()
            d = 'left'
        elif adj == 'r':
            entity.incX()
            d = 'right'
        elif adj == 'ul':
            entity.decY()
            entity.decX()
            d = 'up and to the left'
        elif adj == 'ur':
            entity.decY()
            entity.incX()
            d = 'up and to the right'
        elif adj == 'dl':
            entity.incY()
            entity.decX()
            d = 'down and to the left'
        elif adj == 'dr':
            entity.incY()
            entity.incX()
            d = 'down and to the right'

        for i in range(len(adj)):
            entity.incSteps()

        entity.addStatusMessage('You walk ' + d + '.')

    def _cEntityPickup(self, entity):
        tile = self.game.getMap().getTile(entity.getX(), entity.getY())
        if tile.getInventory().getSize() > 0:
            item = tile.getInventory().takeFirstItem()
            entity.getInventory().addItem(item)
            entity.addStatusMessage('You pickup a ' + item.getName() + '.')
        else:
            entity.addStatusMessage('There\'s nothing to pickup.')

    def _cEntityEat(self, entity, adj):
        food = entity.getInventory().takeItem(int(adj))
        entity.addStatusMessage('You eat the ' + food.getName() + '. It tasted great, really, seriously.')

    def _processEntityCommand(self, entity, verb, adj):
        if not self._verifyEntityCommand(entity, verb, adj):
            entity.addStatusMessage('You can\'t do that.')
            return
        if verb == 'move': self._cEntityMove(entity, adj)
        elif verb == 'pickup': self._cEntityPickup(entity)
        elif verb == 'eat': self._cEntityEat(entity, adj)

    def _processSysCommand(self, verb, adj):
        if verb == 'exit': exit()
        if verb == 'query': self.game.setQuery(adj)

    def processCommands(self, commands):
        if commands is None: return

        for c in commands:
            noun, verb, adj = None, None, None

            a = c.split()
            if len(a) >= 1: noun = a[0]
            if len(a) >= 2: verb = a[1]
            if len(a) >= 3: adj = c[(len(noun) + len(verb) + 2):]

            if noun == 'sys': self._processSysCommand(verb, adj)
            if noun == 'p': self._processEntityCommand(self.game.getPlayer(), verb, adj)

    def generateEngineCommands(self):
        commands = []

        if self.game.getQuery() is not None: commands.append('sys query')

        return commands

    def updateGame(self, playerCommands):
        self.processCommands(self.generateEngineCommands())
        self.processCommands(playerCommands)

class MapTileTypeToMapTile:
    def get(self, type):
        tile = None
        if type   == MapTileType.none:  tile = MapTile(MapTileType.none,  {'walkable': 0, 'opacity': 1})
        elif type == MapTileType.floor: tile = MapTile(MapTileType.floor, {'walkable': 1, 'opacity': 0})
        elif type == MapTileType.hwall: tile = MapTile(MapTileType.hwall, {'walkable': 0, 'opacity': 1})
        elif type == MapTileType.vwall: tile = MapTile(MapTileType.vwall, {'walkable': 0, 'opacity': 1})
        elif type == MapTileType.xwall: tile = MapTile(MapTileType.xwall, {'walkable': 0, 'opacity': 1})
        elif type == MapTileType.hall:  tile = MapTile(MapTileType.hall,  {'walkable': 1, 'opacity': 0})
        elif type == MapTileType.door:  tile = MapTile(MapTileType.door,  {'walkable': 1, 'opacity': 0, 'open': 1})
        return tile

class MapTileType:
    none    = 'none'
    floor   = 'floor'
    hwall   = 'hwall'
    vwall   = 'vwall'
    xwall   = 'xwall'
    door    = 'door'
    hall    = 'hall'

class MapTile:
    def __init__(self, type, props):
        self.type = type
        self.props = props
        self.inventory = Inventory(5)
        self.item = None

    def getType(self): return self.type
    def getProp(self, k): return self.props[k]

    def getInventory(self): return self.inventory

class Map:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.tiles = []
        for i in range(w * h): self.tiles.append(None)

    def setTile(self, x, y, tile):
        if x >= 0 and y >= 0 and x < self.w and y < self.h:
            self.tiles[(y * self.w) + x] = tile

    def getTile(self, x, y):
        if x >= 0 and y >= 0 and x < self.w and y < self.h:
            return self.tiles[(y * self.w) + x]
        else:
            return None

    def getW(self): return self.w
    def getH(self): return self.h

class ItemTypeToItem:
    def get(self, type):
        item = None
        if type   == ItemType.apple:    item = Item(ItemType.apple, 'apple', 1, {'edible': 1})
        elif type == ItemType.banana:   item = Item(ItemType.banana, 'banana', 1, {'edible': 1})
        elif type == ItemType.pear:     item = Item(ItemType.pear, 'pear', 1, {'edible': 1})
        return item

class ItemType:
    apple   = 'apple'
    banana  = 'banana'
    pear    = 'pear'

class Item:
    def __init__(self, type, name, weight, props):
        self.type = type
        self.name = name
        self.weight = weight
        self.props = props

    def getType(self): return self.type
    def getName(self): return self.name
    def getWeight(self): return self.weight
    def getProp(self, k): return self.props[k]

class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = {}

    def getCapacity(self): return self.capacity

    def getSize(self): return len(self.items)

    def getItems(self): return self.items.values()

    def getItem(self, key):
        if self.items.has_key(key):
            return self.items[key]
        else:
            return None

    def getFirstItem(self):
        if self.isNotEmpty():
            #find lowest occupied spot (theres probably a better way..)
            for i in range(self.capacity):
                if self.items.has_key(i):
                    k = i
                    break
            return self.getItem(k)

    def takeItem(self, key):
        if self.items.has_key(key):
            item = self.items[key]
            del self.items[key]
            return item
        else:
            return None

    def takeFirstItem(self):
        if self.isNotEmpty():
            #find lowest occupied spot (theres probably a better way..)
            for i in range(self.capacity):
                if self.items.has_key(i):
                    k = i
                    break
            return self.takeItem(k)

    def addItem(self, itemToAdd):
        if self.isNotFull():
            #find lowest open spot (theres probably a better way..)
            for i in range(self.capacity):
                if not self.items.has_key(i):
                    k = i
                    break
            self.items[k] = itemToAdd

    def isFull(self): return self.getSize() == self.getCapacity()
    def isEmpty(self): return self.getSize() == 0
    def isNotFull(self): return not self.isFull()
    def isNotEmpty(self): return not self.isEmpty()

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.steps = 0
        self.statusMessages = []
        self.inventory = Inventory(10)

    def getY(self): return self.y
    def setY(self, y): self.y = y
    def incY(self): self.y += 1
    def decY(self): self.y -= 1

    def getX(self): return self.x
    def setX(self, x): self.x = x
    def incX(self): self.x += 1
    def decX(self): self.x -= 1

    def getSteps(self): return self.steps
    def incSteps(self): self.steps += 1

    def getInventory(self): return self.inventory

    def getStatusMessages(self): return self.statusMessages
    def addStatusMessage(self, statusMessage): self.statusMessages.append(statusMessage)

class Game:
    def __init__(self, player, map):
        self.player = player
        self.map = map

        self.query = None

    def getPlayer(self): return self.player
    def getMap(self): return self.map

    def getQuery(self): return self.query
    def setQuery(self, query): self.query = query