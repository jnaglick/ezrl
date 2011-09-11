from libtcodpy import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, console_wait_for_keypress

class InputProcessor:
	def __init__(self):
		self.inputToCommand = {
			ord('x')	: 'sys exit',
			KEY_UP		: 'p move up',
			KEY_DOWN	: 'p move down',
			KEY_LEFT	: 'p move left',
			KEY_RIGHT	: 'p move right'
		}
		
	def fetchCommands(self):
		actions = []

		key = console_wait_for_keypress(True)
		
		if key.c != 0: keycode = key.c #printable char
		else: keycode = key.vk #physical key
			
		try: actions.append(self.inputToCommand[keycode]) 
		except KeyError: None

		return actions
