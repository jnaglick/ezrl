from Engine import Map, MapTile, MapTileGenerator
from random import randint

class MapMaker:
	VERT, HORZ = 'v', 'h'

	def __init__(self, w, h):
		self.map = Map(w, h)
		self.mapTileGenerator = MapTileGenerator()
		
	def getMap(self): return self.map
	
	def _create2dTiles(self, d_start, d_end, o, dir, tileType, tileTypeInteractions=None):
		if dir == MapMaker.HORZ: y = o
		else: x = o
		for d in range(d_start, d_end):
			if dir == MapMaker.HORZ: x = d
			else: y = d
			tileTypeToSet = tileType
			if tileTypeInteractions != None:
				try: tileTypeToSet = tileTypeInteractions[self.map.getTile(x, y).getType()]
				except KeyError: None
			self.map.setTile(x, y, self.mapTileGenerator.createTile(tileTypeToSet))	
			
	def _createHorzTiles(self, x_start, x_end, y, tileType, tileTypeInteractions=None):
		self._create2dTiles(x_start, x_end, y, MapMaker.HORZ, tileType, tileTypeInteractions)
		
	def _createVertTiles(self, y_start, y_end, x, tileType, tileTypeInteractions=None):
		self._create2dTiles(y_start, y_end, x, MapMaker.VERT, tileType, tileTypeInteractions)

	def createHorzWall(self, x_start, x_end, y):
		self._createHorzTiles(x_start, x_end, y, MapTile.T_HWALL, {MapTile.T_VWALL: MapTile.T_XWALL})

	def createVertWall(self, y_start, y_end, x):
		self._createVertTiles(y_start, y_end, x, MapTile.T_VWALL, {MapTile.T_HWALL: MapTile.T_XWALL})
		
	def createRoom(self, x, y, w, h):
		for i in range(w):
			for j in range(h):
				self.map.setTile(x + i, y + j, self.mapTileGenerator.createTile(MapTile.T_FLOOR))
		self.createHorzWall(x, x + w, y)
		self.createHorzWall(x, x + w, y + h - 1)
		self.createVertWall(y, y + h, x)
		self.createVertWall(y, y + h, x + w - 1)

class RandomMapMaker(MapMaker):
	def __init__(self, w, h):
		MapMaker.__init__(self, w, h)
		self.playerStartCoords = None
		
	def getPlayerStartCoords(self): return self.playerStartCoords
	
	def createRandomRoom(self):
		x, y, w, h = randint(1, 4), randint(1, 6), randint(4, 8), randint(4, 8)
		self.createRoom(x, y, w, h)
		return x, y, w, h
		
	def generateRandomMap(self):
		#create first room, set playerStartCoords to a random tile inside of it
		x, y, w, h = self.createRandomRoom()
		self.playerStartCoords = (randint(x+1, x+w-2), randint(y+1, y+h-2))
