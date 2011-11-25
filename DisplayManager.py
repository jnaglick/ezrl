from libtcodpy import *
from Engine import MapTileType, ItemType
from datetime import date
from types import StringType, ListType

class DisplayManager:
    def __init__(self):
        #console window width, height, title
        self.C_WIDTH = 97
        self.C_HEIGHT = 64
        self.C_TITLE = 'New Game ' + date.today().strftime('%A %d-%B-%Y')

        #map draw distances: how much of the map to draw around the player
        self.M_HORZ_DRAW_DISTANCE = 38
        self.M_VERT_DRAW_DISTANCE = 27

        #misc constants
        self.PLAYER_STATUS_MESSAGES_TO_DRAW = 4

        #offsets: where to draw stuff
        self.playerInfoOffset = (3, 1)
        self.playerStatusMessagesOffset = (3, 59)
        self.playerItemListOffset = (81, 3)
        self.mapOffset = (3, 3)

        self.console = Console(self.C_WIDTH, self.C_HEIGHT, self.C_TITLE)
        self.mapTileToConsoleItem = MapTileToConsoleItem()

    def _drawPlayerInfo(self, player):
        playerItemWeight = 0
        for item in player.getInventory().getItems():
            if item != None:
                playerItemWeight += item.getWeight()
        s = 'X:[' + str(player.getX()) + '] ' + \
            'Y:[' + str(player.getY()) + '] ' + \
            'Steps:[' + str(player.getSteps()) + '] ' + \
            'Weight:[' + str(playerItemWeight) + ']'
        c = ConsoleItem(s, Color(128, 128, 128))
        self.console.drawConsoleItem(self.playerInfoOffset[0], self.playerInfoOffset[1], c)

    def _drawPlayerStatusMessages(self, player):
        c = ConsoleItem(player.getStatusMessages()[-self.PLAYER_STATUS_MESSAGES_TO_DRAW:], Color(128, 128, 128))
        self.console.drawConsoleItem(self.playerStatusMessagesOffset[0], self.playerStatusMessagesOffset[1], c)

    def _drawPlayerInventory(self, inventory):
        labels = []
        for i in range(inventory.getCapacity()):
            item = inventory.getItem(i)
            if item == None:
                labels.append(str(i) + ' - ')
            else:
                labels.append(str(i) + ' - ' + item.getName())
        c = ConsoleItem(labels, Color(255, 255, 255))
        self.console.drawConsoleItem(self.playerItemListOffset[0], self.playerItemListOffset[1], c)

    def _drawMap(self, map, x_start, x_stop, y_start, y_stop):
        i = 0
        for y in range(y_start, y_stop):
            j = 0
            for x in range(x_start, x_stop):
                tile = map.getTile(x, y)
                if tile != None:
                    c = self.mapTileToConsoleItem.get(tile)
                    self.console.drawConsoleItem(self.mapOffset[0] + j, self.mapOffset[1] + i, c)
                j += 1
            i += 1

    def _drawPlayer(self, player):
        c = ConsoleItem('@', white)
        self.console.drawConsoleItem(self.mapOffset[0] + self.M_HORZ_DRAW_DISTANCE, \
                                     self.mapOffset[1] + self.M_VERT_DRAW_DISTANCE, \
                                     c)

    def draw(self, game):
        self.console.clear()

        player = game.getPlayer()

        # info panes
        self._drawPlayerInfo(player)
        self._drawPlayerStatusMessages(player)
        self._drawPlayerInventory(player.getInventory())

        # map
        self._drawMap(game.getMap(),
                      player.getX() - self.M_HORZ_DRAW_DISTANCE,
                      player.getX() + self.M_HORZ_DRAW_DISTANCE+1,
                      player.getY() - self.M_VERT_DRAW_DISTANCE,
                      player.getY() + self.M_VERT_DRAW_DISTANCE+1)

        # and finally, the @ sign
        self._drawPlayer(player)

        self.console.flush()

class MapTileToConsoleItem:
    def get(self, mapTile):
        consoleItem = None

        if mapTile.getInventory().getSize() > 0:
            type = mapTile.getInventory().getFirstItem().getType()
            if type == ItemType.apple:        consoleItem = ConsoleItem('%', green)
            elif type == ItemType.banana:    consoleItem = ConsoleItem('(', yellow)
            elif type == ItemType.pear:        consoleItem = ConsoleItem('%', orange)
        else:
            type = mapTile.getType()
            if type == MapTileType.floor:    consoleItem = ConsoleItem('.', white)
            elif type == MapTileType.hwall: consoleItem = ConsoleItem('#', Color(188, 188, 188)) # -
            elif type == MapTileType.vwall: consoleItem = ConsoleItem('#', Color(188, 188, 188)) # |
            elif type == MapTileType.xwall: consoleItem = ConsoleItem('#', Color(148, 148, 148)) # +
            elif type == MapTileType.hall:  consoleItem = ConsoleItem('*', Color(188, 188, 188))
            elif type == MapTileType.none:  consoleItem = ConsoleItem('~', Color(0, 0, 127))
            elif type == MapTileType.door:
                if mapTile.getProp('open') == 1:   consoleItem = ConsoleItem('o', Color(188, 188, 188))
                elif mapTile.getProp('open') == 0: consoleItem = ConsoleItem('x', Color(188, 188, 188))

        return consoleItem

class ConsoleItem:
    def __init__(self, i, color, bcolor=None):
        self.i = i
        self.color = color
        self.bcolor = bcolor

    def getI(self): return self.i
    def getColor(self): return self.color
    def getBColor(self): return self.bcolor

class Console:
    def __init__(self, consoleWidth, consoleHeight, consoleTitle):
        self.c = console_init_root(consoleWidth, consoleHeight, consoleTitle, False)

    def drawConsoleItem(self, x, y, consoleItem):
        if type(consoleItem.getI()) == StringType:
            if len(consoleItem.getI()) == 1:
                self._drawChar(x, y, consoleItem)
            elif len(consoleItem.getI()) > 1:
                self._drawString(x, y, consoleItem)
        elif type(consoleItem.getI()) == ListType:
            self._drawList(x, y, consoleItem)

    def _drawChar(self, x, y, consoleItem):
        console_set_char(self.c, x, y, consoleItem.getI())
        console_set_fore(self.c, x, y, consoleItem.getColor())
        if (consoleItem.getBColor() != None): console_set_back(self.c, x, y, consoleItem.getBColor())

    def _drawString(self, x, y, consoleItem):
        console_print_left(self.c, x, y, BKGND_NONE, consoleItem.getI())
        for i in range(0, len(consoleItem.getI())):
            console_set_fore(self.c, x+i, y, consoleItem.getColor())
        if (consoleItem.getBColor() != None):
            for i in range(0, len(consoleItem.getI())):
                console_set_back(self.c, x+i, y, consoleItem.getBColor())

    def _drawList(self, x, y, consoleList): # TODO not the most elegant or functional. care later.
        i = 0
        for item in consoleList.getI():
            if len(item) == 1:
                self._drawChar(x, y+i, ConsoleItem(item, consoleList.getColor(), consoleList.getBColor()))
            elif len(item) > 1:
                self._drawString(x, y+i, ConsoleItem(item, consoleList.getColor(), consoleList.getBColor()))
            i += 1

    def flush(self):
        console_flush()

    def clear(self):
        console_clear(self.c)
