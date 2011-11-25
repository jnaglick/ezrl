from DisplayManager import DisplayManager
from Engine import Engine
from InputProcessor import InputProcessor

displayManager = DisplayManager()
engine = Engine()
inputProcessor = InputProcessor()

while(True):
    displayManager.draw(engine.getGame())
    engine.processCommands(inputProcessor.fetchCommands())
