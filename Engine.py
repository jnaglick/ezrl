from random import randint

class MapTile:
	T_NONE 	= 'none'
	T_FLOOR = 'floor'
	T_HWALL = 'hwall'
	T_VWALL = 'vwall'
	T_XWALL = 'xwall'
	T_DOOR 	= 'door'

	def __init__(self, type, props):
		self.type = type
		self.props = props
		
	def getType(self): return self.type
	def getProp(self, k): return self.props[k]

class MapTileGenerator:
	def createTile(self, type):
		if type == MapTile.T_NONE:
			return MapTile(type, {'walkable': 0, 'opacity': 1})
		if type == MapTile.T_FLOOR:
			return MapTile(type, {'walkable': 1, 'opacity': 0})
		if (MapTile.T_HWALL, MapTile.T_VWALL, MapTile.T_XWALL).count(type) > 0:
			return MapTile(type, {'walkable': 0, 'opacity': 1})
		if type == MapTile.T_DOOR:
			return MapTile(type, {'walkable': 1, 'opacity': 0, 'open': 1})

class Map:
	def __init__(self, w, h):
		self.w = w
		self.h = h
		self.tiles = []
		for i in range(w * h): self.tiles.append(MapTileGenerator().createTile(MapTile.T_NONE))
		
	def setTile(self, x, y, tile): self.tiles[(y * self.w) + x] = tile
	def getTile(self, x, y): return self.tiles[(y * self.w) + x]
	
	def getW(self): return self.w
	def getH(self): return self.h
	
class MapGenerator:
	VERT = 'v'
	HORZ = 'h'
	
	def __init__(self, w, h):
		self.map = Map(w, h)
		for x in range(w):
			for y in range(h):
				self.map.setTile(x, y, MapTileGenerator().createTile('none'))
				
	def getMap(self): return self.map
				
	def _createLineOfTiles(self, x_start, y_start, len, dir, tileType, tileTypeInteractions=None):
		for i in range(len):
			if dir == MapGenerator.HORZ:
				x_delta = x_start + i
				y_delta = y_start
			elif dir == MapGenerator.VERT:
				x_delta = x_start
				y_delta = y_start + i
				
			tileTypeToSet = tileType

			if tileTypeInteractions != None:
				try: tileTypeToSet = tileTypeInteractions[self.map.getTile(x_delta, y_delta).getType()]
				except KeyError: None
					
			self.map.setTile(x_delta, y_delta, MapTileGenerator().createTile(tileTypeToSet))

	def createHWall(self, x, y, len):
		self._createLineOfTiles(x, y, len, MapGenerator.HORZ, MapTile.T_HWALL, {MapTile.T_VWALL: MapTile.T_XWALL})

	def createVWall(self, x, y, len):
		self._createLineOfTiles(x, y, len, MapGenerator.VERT, MapTile.T_VWALL, {MapTile.T_HWALL: MapTile.T_XWALL})	

	def createHallway(self, x, y, len, dir):
		self._createLineOfTiles(x, y, len, dir, MapTile.T_FLOOR, {MapTile.T_HWALL: MapTile.T_DOOR, \
																  MapTile.T_VWALL: MapTile.T_DOOR})		

	def createHHallway(self, x, y, len):
		self.createHallway(x, y, len, MapGenerator.HORZ)

	def createVHallway(self, x, y, len):
		self.createHallway(x, y, len, MapGenerator.VERT)
				
	def createRoom(self, x, y, w, h):
		self.createHWall(x, y, w + 2)
		self.createHWall(x, y + h + 1, w + 2)
		self.createVWall(x, y, h + 2)
		self.createVWall(x + w + 1, y, h + 2)
		for i in range(w):
			for j in range(h):
				self.map.setTile(x + i + 1, y + j + 1, MapTileGenerator().createTile(MapTile.T_FLOOR))

class RandomMapGenerator(MapGenerator):
	def __init__(self, w, h):
		MapGenerator.__init__(self, w, h)
		self.playerStartCoords = None
		
	def getPlayerStartCoords(self): return self.playerStartCoords
	
	def createRandomRoom(self):
		x, y, w, h = randint(1, 4), randint(1, 6), randint(4, 8), randint(4, 8)
		self.createRoom(x, y, w, h)
		return x, y, w, h
		
	def generateRandomMap(self):
		#create first room, set playerStartCoords to a random tile inside of it
		x, y, w, h = self.createRandomRoom()
		self.playerStartCoords = (randint(x+1, x+w), randint(y+1, y+h))

class Player:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.steps = 0
		
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

class Game:
	def __init__(self, player, map):
		self.player = player
		self.map = map
		
	def getPlayer(self): return self.player
	def getMap(self): return self.map

class Engine:
	def __init__(self):
		#create random map
		randomMapGenerator = RandomMapGenerator(20, 20)
		randomMapGenerator.generateRandomMap()
		map = randomMapGenerator.getMap()

		#create new player
		getPlayerStartCoords = randomMapGenerator.getPlayerStartCoords()
		player = Player(getPlayerStartCoords[0], getPlayerStartCoords[1])		
		
		#create game
		self.game = Game(player, map)
		
	def _vTileWalkable(self, x, y):
		return self.game.getMap().getTile(x, y).getProp('walkable') == 1
		
	def _vEntityMove(self, entity, adj):	
		if adj == 'up': 
			return entity.getY() > 0 \
				   and self._vTileWalkable(entity.getX(), entity.getY() - 1)
		if adj == 'down': 
			return entity.getY() < self.game.getMap().getH() - 1 \
				   and self._vTileWalkable(entity.getX(), entity.getY() + 1)
		if adj == 'left': 
			return entity.getX() > 0 \
				   and self._vTileWalkable(entity.getX() - 1, entity.getY())
		if adj == 'right': 
			return entity.getX() < self.game.getMap().getW() - 1 \
				   and self._vTileWalkable(entity.getX() + 1, entity.getY())

	def _verifyEntityCommand(self, entity, verb, adj):
		if verb == 'move': return self._vEntityMove(entity, adj)
		return 0
		
	def _cEntityMove(self, entity, adj):
		if adj == 'up': entity.decY()
		if adj == 'down': entity.incY()
		if adj == 'left': entity.decX()
		if adj == 'right': entity.incX()
		entity.incSteps()

	def _processEntityCommand(self, entity, verb, adj):
		if (not self._verifyEntityCommand(entity, verb, adj)): return
		if verb == 'move': self._cEntityMove(entity, adj)
		
	def _processSysCommand(self, verb):
		if verb == 'exit': exit()

	def processCommands(self, commands):
		for c in commands:
			a = c.split()
			noun, verb = a[0], a[1]
			if (len(a) == 3):
				adj = a[2]
			else:
				adj = None
			
			if noun == 'sys': self._processSysCommand(verb)
			if noun == 'p': self._processEntityCommand(self.game.getPlayer(), verb, adj)

	def getGame(self): return self.game