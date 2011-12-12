from EngineActions import *

class Engine:
    def __init__(self):
        from MapMakers import RandomMapMaker, TestMapMaker

        mapMaker = RandomMapMaker()
        player = Player()
        self.game = Game(mapMaker.getMap(), player, mapMaker.getPlayerStartCoords()[0], mapMaker.getPlayerStartCoords()[1])

    def getGame(self): return self.game

    def _instance(self, className, initArgs):
        constructor = globals()[className]
        instance = constructor(*initArgs)
        return instance

    def _gameAction(self, action, adj):
        self._instance(action, (self.game, adj))

    def _characterGameAction(self, action, character, adj):
        self._instance(action, (character, self.game, adj))

    def processCommands(self, commands):
        if commands is None: return
        for c in commands:
            character, action, adj = None, None, None
            a = c.split()
            if len(a) >= 1: character = a[0]
            if len(a) >= 2: action = a[1]
            if len(a) >= 3: adj = c[(len(character) + len(action) + 2):]
            if character == 'sys': self._gameAction(action, adj)
            if character == 'p':   self._characterGameAction(action, self.game.getPlayer(), adj)

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
        elif type == MapTileType.door:  tile = MapTile(MapTileType.door,  {'walkable': 1, 'opacity': 0, 'open': 1})
        return tile

class MapTileType:
    none    = 'none'
    floor   = 'floor'
    hwall   = 'hwall'
    vwall   = 'vwall'
    xwall   = 'xwall'
    door    = 'door'

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

class CharacterMap:
    def __init__(self, w, h):
        self.w = w
        self.h = h

        self.charactersByCoords = {}
        self.coordsByCharacters = {}
        self.charactersById = {}
        self.currentId = 0

    def addCharacter(self, character, x, y):
        self.charactersByCoords[(x, y)] = character
        self.coordsByCharacters[character] = (x, y)
        self.charactersById[self.currentId] = character
        self.currentId += 1
        return self.currentId - 1 # return character id

    def getCharacterFromCoords(self, x, y):
        try: return self.charactersByCoords[(x, y)]
        except KeyError: return None

    def getCoords(self, character):
        return self.coordsByCharacters[character]

    def getCharacterFromId(self, id):
        return self.charactersById[id]

    def _doMove(self, character, newX, newY):
        oldX, oldY = self.getCoords(character)

        self.charactersByCoords[(oldX, oldY)] = None
        self.charactersByCoords[(newX, newY)] = character
        self.coordsByCharacters[character] = (newX, newY)

    def moveUp(self, character):
        x, y =  self.getCoords(character)
        self._doMove(character, x, y-1)

    def moveDown(self, character):
        x, y =  self.getCoords(character)
        self._doMove(character, x, y+1)

    def moveLeft(self, character):
        x, y =  self.getCoords(character)
        self._doMove(character, x-1, y)

    def moveRight(self, character):
        x, y =  self.getCoords(character)
        self._doMove(character, x+1, y)

class Player:
    def __init__(self):
        self.steps = 0
        self.statusMessages = []
        self.inventory = Inventory(10)

    def getSteps(self): return self.steps
    def incSteps(self): self.steps += 1

    def getInventory(self): return self.inventory

    def getStatusMessages(self): return self.statusMessages
    def addStatusMessage(self, statusMessage): self.statusMessages.append(statusMessage)

class Game:
    def __init__(self, map, player, playerStartX, playerStartY):
        self.map = map
        self.characterMap = CharacterMap(self.map.getW(), self.map.getH())
        self.playerId = self.characterMap.addCharacter(player, playerStartX, playerStartY)
        self.query = None

    def getMap(self): return self.map

    def getCharacterMap(self): return self.characterMap
    def getPlayer(self): return self.characterMap.getCharacterFromId(self.playerId)
    def getCharacterCoords(self, character): return self.characterMap.getCoords(character)

    def getQuery(self): return self.query
    def setQuery(self, query): self.query = query