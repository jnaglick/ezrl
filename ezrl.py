from DisplayManager import *
from Engine import *
from InputProcessor import *

displayManager = DisplayManager()
engine = Engine()
inputProcessor = InputProcessor()

while(True):
	displayManager.draw(engine.getGame())
	engine.processCommands(inputProcessor.fetchCommands())
