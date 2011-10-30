from Engine import Map, MapTile, MapTileType, MapTileTypeToMapTile
from random import randint, choice

class MapMaker:
	def __init__(self, w, h):
		self.map = Map(w, h)
		self.mapTileTypeToMapTile = MapTileTypeToMapTile()
		self.makeMap()
		
	def getMap(self): return self.map
	
	def getPlayerStartCoords(self): raise NotImplementedError
	def makeMap(self): raise NotImplementedError
	
	def drawMapTileRectangle(self, rect):
		for w in range(0, rect.w):
			for h in range(0, rect.h):
				tileTypeToSet = rect.tileType
				if rect.tileTypeInteractions != None:
					targetTile = self.map.getTile(rect.x + w, rect.y + h)
					if targetTile != None:
						try: tileTypeToSet = rect.tileTypeInteractions[targetTile.getType()]
						except KeyError: None
				self.map.setTile(rect.x + w, rect.y + h, self.mapTileTypeToMapTile.get(tileTypeToSet))

class TestMapMaker(MapMaker):
	def __init__(self):
		MapMaker.__init__(self, 9, 9)

	def getPlayerStartCoords(self): return self.playerStartCoords

	def makeMap(self):
		#Create "None" tiles
		self.drawMapTileRectangle(MapTileRectangle(0, 0, self.map.getW(), self.map.getH(), MapTileType.none))
		
		self._drawCardinalSizeRoomAtCenter(4, 4, 1)
		
		self.playerStartCoords = (4, 4)
		
	def _drawCardinalSizeRoomAtCenter(self, center_x, center_y, size):
		room = MapMakerRoom(center_x - size, center_y - size, (2 * size) + 1, (2 * size) + 1)
		room.draw(self)
		return room		

class RandomMapMaker(MapMaker):
	def __init__(self):
		self.SKEWS_TO_DRAW = 10
		self.R_SUBROOM_ABS_MAX_SIZE_MIN = 3
		self.R_SUBROOM_ABS_MAX_SIZE_MAX = 5
		self.R_SUBROOM_TOTAL_MIN = 7
		self.R_SUBROOM_TOTAL_MAX = 15
		self.R_SKEW_STRENGTH_MIN = 15
		self.R_SKEW_STRENGTH_MAX = 20
		MapMaker.__init__(self, 199, 199) #These don't have to be odd, but it helps

	def getPlayerStartCoords(self): return self.playerStartCoords

	def makeMap(self):
		def flip(bit): return (bit + 1) % 2

		#Create "None" tiles
		self.drawMapTileRectangle(MapTileRectangle(0, 0, self.map.getW(), self.map.getH(), MapTileType.none))

		#Get center of map, set player start coord there
		map_center_x, map_center_y = (self.map.getW()-1)/2, (self.map.getH()-1)/2
		self.playerStartCoords = (map_center_x, map_center_y)
		
		#Lets make some map...
		center_x, center_y = map_center_x, map_center_y
		x_skew_dir, y_skew_dir = randint(0, 1), randint(0, 1) # pick random starting skew
		for i in range(self.SKEWS_TO_DRAW):
			room = self._drawRandomRoomSkew(center_x, center_y, x_skew_dir, y_skew_dir)
			
			# sew new center to a random floor tile in the last roomSkew
			center_x = randint(room.x + 1, room.x + room.w - 2) # random floor x
			center_y = randint(room.y + 1, room.y + room.h - 2) # random floor y
			
			# flip either the x or y skew
			if randint(0, 1): x_skew_dir = flip(x_skew_dir) 
			else: y_skew_dir = flip(y_skew_dir)

	def _drawRandomRoomSkew(self, start_center_x, start_center_y, x_skew_dir, y_skew_dir):
		subroom_absolute_max_size = randint(self.R_SUBROOM_ABS_MAX_SIZE_MIN, self.R_SUBROOM_ABS_MAX_SIZE_MAX)
		subroom_total = randint(self.R_SUBROOM_TOTAL_MIN, self.R_SUBROOM_TOTAL_MAX)
		skew_strength = randint(self.R_SKEW_STRENGTH_MIN, self.R_SKEW_STRENGTH_MAX)
		return self._drawRoomSkew(start_center_x, start_center_y,
											  subroom_absolute_max_size, 
											  subroom_total, 
											  skew_strength, 
											  x_skew_dir, 
											  y_skew_dir)
	
	# _drawRoomSkew : draws random-size cardinal rooms in a random linear skew pattern
	# --------------------------------------------------------------------------------------------
	# 1. Starting at (start_center_x, start_center_y), draws subroom_total square rooms of 
	# random Cardinal Size (for more control, subroom_absolute_max_size defines the max this can be).
	# 2. Because of the MapTileRectangles used by MapMakerRoom, these rooms are drawn additively
	# on top of each other. Look at how tileTypeInteractions work for more information
	# 3. Additional rooms after the first are drawn with their center point (ie, tile) 
	# at a randomly chosen floor tile of the room previously drawn.
	# 4. The real magic is that the randomly chosen floor tile from #3 is not chosen _completely_ randomly.
	# Instead, the concept of Random Linear Skew is used. See _randomLinearSkew for more info
	# 5. x_skew_dir: {True = Right, False = Left} y_skew_dir: {True = Down, False = Up}
	def _drawRoomSkew(self, 
					  start_center_x, start_center_y, 
					  subroom_absolute_max_size, 
					  subroom_total, 
					  skew_strength, 
					  x_skew_dir, 
					  y_skew_dir):
		room = self._drawRandomSizeCardinalRoom(start_center_x, start_center_y, subroom_absolute_max_size)
		for i in range(subroom_total):
			rand_floor_x = self._randomLinearSkew(room.x + 1, room.x + room.w - 2, skew_strength, x_skew_dir) 
			rand_floor_y = self._randomLinearSkew(room.y + 1, room.y + room.h - 2, skew_strength, y_skew_dir)
			newRoom = self._drawRandomSizeCardinalRoom(rand_floor_x, rand_floor_y, subroom_absolute_max_size)
			if newRoom == False: # No more rooms could fit, end prematurely
				return room
			else:
				room = newRoom
		return room	

	# dir: {True = max, False = min}
	def _randomLinearSkew(self, r_min, r_max, strength, dir):
		r = randint(r_min, r_max)
		for i in range(strength):
			if dir:
				r = max(r, randint(r_min, r_max))
			else:
				r = min(r, randint(r_min, r_max))
		return r

	# Draws a cardinal room of randomly-picked size. The important part of this function
	# is that it does not allow the room size to exceed the map boundries.
	def _drawRandomSizeCardinalRoom(self, center_x, center_y, absolute_max_size):
		max_size = min(absolute_max_size, 
					   center_x,
					   self.map.getW() - center_x - 1,
					   center_y,
					   self.map.getH() - center_y - 1)
		if max_size == 0: # Room cant fit at this location
			return False
		else:
			room = MapMakerCardinalRoom(center_x, center_y, randint(1, max_size))
			room.draw(self)
			return room

#
#	MapMaker Useful Abstraction Classes
#
class MapMakerRoom():
	def __init__(self, x, y, w, h):
		self.x, self.y, self.w, self.h = x, y, w, h

	def draw(self, mapMaker):
		x, y, w, h = self.x, self.y, self.w, self.h
		mapMaker.drawMapTileRectangle(Floor(x+1, y+1, w-2, h-2))
		mapMaker.drawMapTileRectangle(HWall(x, y, w))     #N
		mapMaker.drawMapTileRectangle(HWall(x, y+h-1, w)) #S
		mapMaker.drawMapTileRectangle(VWall(x, y, h))	  #W
		mapMaker.drawMapTileRectangle(VWall(x+w-1, y, h)) #E

class MapMakerCardinalRoom(MapMakerRoom):
	# Cardinal Size is defined as size 1=3x3, 2=5x5, 3=7x7, etc.
	# Ex: if you draw a size 1 room at location (3,3), you'll get a floor tile at (3,3) surrounded by walls.
	# Note that Cardinal Size Rooms always have a true center. This is useful for our random map generation alg.
	def __init__(self, center_x, center_y, size):
		MapMakerRoom.__init__(self, center_x - size, center_y - size, (2 * size) + 1, (2 * size) + 1)
		self.center_x = center_x
		self.center_y = center_y
		
#
#	MapTileRectangles
#
class MapTileRectangle():
	def __init__(self, x, y, w, h, tileType, tileTypeInteractions=None):
		self.x, self.y, self.w, self.h = x, y, w, h
		self.tileType, self.tileTypeInteractions = tileType, tileTypeInteractions

class Floor(MapTileRectangle):
	def __init__(self, x, y, w, h): 
		MapTileRectangle.__init__(self, x, y, w, h, MapTileType.floor)

class VWall(MapTileRectangle):
	def __init__(self, x, y, h): 
		MapTileRectangle.__init__(self, x, y, 1, h, 
								  MapTileType.vwall, {MapTileType.hwall: MapTileType.xwall,
													MapTileType.hall:  MapTileType.door,
													MapTileType.xwall: MapTileType.xwall,
													MapTileType.floor: MapTileType.floor})

class HWall(MapTileRectangle):
	def __init__(self, x, y, w): 
		MapTileRectangle.__init__(self, x, y, w, 1, 
								  MapTileType.hwall, {MapTileType.vwall: MapTileType.xwall,
													MapTileType.hall:  MapTileType.door,
													MapTileType.xwall: MapTileType.xwall,
													MapTileType.floor: MapTileType.floor})

class VHall(MapTileRectangle):
	def __init__(self, x, y, h): 
		MapTileRectangle.__init__(self, x, y, 1, h, 
								  MapTileType.hall, {MapTileType.hwall: MapTileType.door})

class HHall(MapTileRectangle):
	def __init__(self, x, y, w): 
		MapTileRectangle.__init__(self, x, y, w, 1, 
								  MapTileType.hall, {MapTileType.vwall: MapTileType.door})