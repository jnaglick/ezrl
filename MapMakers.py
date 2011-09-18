from Engine import Map, MapTile, MapTileGenerator
from random import randint

class MapMaker:
	VERT = 'v'
	HORZ = 'h'
	
	def __init__(self, w, h):
		self.map = Map(w, h)
		self.mapTileGenerator = MapTileGenerator()
		
	def getMap(self): return self.map
				
	def _createLineOfTiles(self, x_start, y_start, len, dir, tileType, tileTypeInteractions=None):
		for i in range(len):
			if dir == MapMaker.HORZ:
				x_delta = x_start + i
				y_delta = y_start
			elif dir == MapMaker.VERT:
				x_delta = x_start
				y_delta = y_start + i
				
			tileTypeToSet = tileType

			if tileTypeInteractions != None:
				try: tileTypeToSet = tileTypeInteractions[self.map.getTile(x_delta, y_delta).getType()]
				except KeyError: None
					
			self.map.setTile(x_delta, y_delta, self.mapTileGenerator.createTile(tileTypeToSet))

	def createHWall(self, x, y, len):
		self._createLineOfTiles(x, y, len, MapMaker.HORZ, MapTile.T_HWALL, {MapTile.T_VWALL: MapTile.T_XWALL})

	def createVWall(self, x, y, len):
		self._createLineOfTiles(x, y, len, MapMaker.VERT, MapTile.T_VWALL, {MapTile.T_HWALL: MapTile.T_XWALL})	

	def createHallway(self, x, y, len, dir):
		self._createLineOfTiles(x, y, len, dir, MapTile.T_FLOOR, {MapTile.T_HWALL: MapTile.T_DOOR, \
																  MapTile.T_VWALL: MapTile.T_DOOR})		

	def createHHallway(self, x, y, len):
		self.createHallway(x, y, len, MapMaker.HORZ)

	def createVHallway(self, x, y, len):
		self.createHallway(x, y, len, MapMaker.VERT)
				
	def createRoom(self, x, y, w, h):
		self.createHWall(x, y, w + 2)
		self.createHWall(x, y + h + 1, w + 2)
		self.createVWall(x, y, h + 2)
		self.createVWall(x + w + 1, y, h + 2)
		for i in range(w):
			for j in range(h):
				self.map.setTile(x + i + 1, y + j + 1, self.mapTileGenerator.createTile(MapTile.T_FLOOR))

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
		self.playerStartCoords = (randint(x+1, x+w), randint(y+1, y+h))
