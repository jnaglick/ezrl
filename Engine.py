from random import randint

class Engine:
	def __init__(self):
		from MapMakers import RandomMapMaker, TestMapMaker

		#create map
		#mapMaker = TestMapMaker()
		mapMaker = RandomMapMaker()
		
		map = mapMaker.getMap()

		#create new player
		getPlayerStartCoords = mapMaker.getPlayerStartCoords()
		player = Player(getPlayerStartCoords[0], getPlayerStartCoords[1])
		
		#create game
		self.game = Game(player, map)
		
	def _vTileWalkable(self, x, y):
		map = self.game.getMap()
		return x >= 0 and x < map.getW() and y >= 0 and y < map.getH() and map.getTile(x, y).getProp('walkable')
		
	def _vEntityMove(self, entity, adj):
		x, y = entity.getX(), entity.getY()
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

	def _verifyEntityCommand(self, entity, verb, adj):
		if verb == 'move': return self._vEntityMove(entity, adj)
		return False
		
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
			
		entity.setStatus('You walk ' + d + '.')

	def _processEntityCommand(self, entity, verb, adj):
		if (not self._verifyEntityCommand(entity, verb, adj)): 
			entity.setStatus('You can\' do that.')
			return
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

class MapTileType:
	T_NONE 	= 'none'
	T_FLOOR = 'floor'
	T_HWALL = 'hwall'
	T_VWALL = 'vwall'
	T_XWALL = 'xwall'
	T_DOOR 	= 'door'
	T_HALL  = 'hall'
	
class MapTile:
	def __init__(self, type, props):
		self.type = type
		self.props = props

	def getType(self): return self.type
	def getProp(self, k): return self.props[k]

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

class Player:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.steps = 0
		self.status = ''
		
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
	
	def getStatus(self): return self.status
	def setStatus(self, status): self.status = status

class Game:
	def __init__(self, player, map):
		self.player = player
		self.map = map
		
	def getPlayer(self): return self.player
	def getMap(self): return self.map
