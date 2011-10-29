from libtcodpy import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, console_wait_for_keypress

class InputProcessor:
	def __init__(self):
		self.inputToCommand = {
			ord('x')	: 'sys exit',
			
			KEY_UP		: 'p move u',
			ord('k')	: 'p move u',
			
			KEY_DOWN	: 'p move d',
			ord('j')	: 'p move d',
			
			KEY_LEFT	: 'p move l',
			ord('h')	: 'p move l',
			
			KEY_RIGHT	: 'p move r',
			ord('l')	: 'p move r',
			
			ord('u')	: 'p move ul',
			ord('i')	: 'p move ur',
			ord('n')	: 'p move dl',
			ord('m')	: 'p move dr'
		}
		
	def fetchCommands(self):
		actions = []

		key = console_wait_for_keypress(True)
		
		if key.c != 0: keycode = key.c #printable char
		else: keycode = key.vk #physical key
			
		try: actions.append(self.inputToCommand[keycode]) 
		except KeyError: None

		return actions
