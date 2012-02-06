from DisplayManager import DisplayManager
from Engine import Engine
from InputManager import KeymapInputManager

displayManager = DisplayManager()
engine = Engine()
inputManager = KeymapInputManager()

while True:
    displayManager.draw(engine.getGame())
    engine.updateGame(inputManager.fetchCommand())
