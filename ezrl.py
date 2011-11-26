from DisplayManager import DisplayManager
from Engine import Engine
from InputProcessor import KeyboardInputProcessor, ConsoleInputProcessor

displayManager = DisplayManager()
engine = Engine()
inputProcessor = KeyboardInputProcessor()

while(True):
    displayManager.draw(engine.getGame())
    engine.updateGame(inputProcessor.fetchCommands())
