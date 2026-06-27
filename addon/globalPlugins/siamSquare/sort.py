# sort.py

import addonHandler

addonHandler.initTranslation()

class ThaiSorter:
	def __init__(self):
		self.consonants_order = {
			'ก': 1, 'ข': 2, 'ค': 3, 'ฆ': 4, 'ง': 5,
			'จ': 6, 'ฉ': 7, 'ช': 8, 'ซ': 9, 'ฌ': 10, 'ญ': 11,
			'ฎ': 12, 'ฏ': 13, 'ฐ': 14, 'ฑ': 15, 'ฒ': 16, 'ณ': 17,
			'ด': 18, 'ต': 19, 'ถ': 20, 'ท': 21, 'ธ': 22, 'น': 23,
			'บ': 24, 'ป': 25, 'ผ': 26, 'ฝ': 27, 'พ': 28, 'ฟ': 29, 'ภ': 30, 'ม': 31,
			'ย': 32, 'ร': 33, 'ล': 34, 'ว': 35,
			'ศ': 36, 'ษ': 37, 'ส': 38, 'ห': 39, 'ฬ': 40, 'อ': 41, 'ฮ': 42
		}
		
		self.vowels_order = {
			'ะ': 1, 'า': 2, 'ิ': 3, 'ี': 4, 'ึ': 5, 'ื': 6, 'ุ': 7, 'ู': 8,
			'เ': 9, 'แ': 10, 'โ': 11, 'ใ': 12, 'ไ': 13,
			'ๅ': 14, 'ํ': 15, 'ั': 16, 'ำ': 17, 'ๆ': 18
		}
		
		self.tone_marks_order = {
			'่': 1, '้': 2, '๊': 3, '๋': 4, '็': 5
		}
		
		self.other_marks_order = {
			'ฯ': 1, '๎': 2, '์': 3, '๚': 4, '๛': 5
		}
		
		self.kedmanee_map = {
			'`': '_', '1': 'ๅ', '2': '/', '3': '-', '4': 'ภ', '5': 'ถ', '6': 'ุ', '7': 'ึ', '8': 'ค', '9': 'ต', '0': 'จ', '-': 'ข', '=': 'ช',
			'~': '%', '!': '+', '@': '๑', '#': '๒', '$': '๓', '%': '๔', '^': 'ู', '&': '฿', '*': '๕', '(': '๖', ')': '๗', '_': '๘', '+': '๙',
			'q': 'ๆ', 'w': 'ไ', 'e': 'ำ', 'r': 'พ', 't': 'ะ', 'y': 'ั', 'u': 'ี', 'i': 'ร', 'o': 'น', 'p': 'ย', '[': 'บ', ']': 'ล', '\\': 'ฃ',
			'Q': '๐', 'W': '"', 'E': 'ฎ', 'R': 'ฑ', 'T': 'ธ', 'Y': 'ํ', 'U': '๊', 'I': 'ณ', 'O': 'ฯ', 'P': 'ญ', '{': 'ฐ', '}': ',', '|': 'ฅ',
			'a': 'ฟ', 's': 'ห', 'd': 'ก', 'f': 'ด', 'g': 'เ', 'h': '้', 'j': '่', 'k': 'า', 'l': 'ส', ';': 'ว', "'": 'ง',
			'A': 'ฤ', 'S': 'ฆ', 'D': 'ฏ', 'F': 'โ', 'G': 'ฌ', 'H': '็', 'J': '๋', 'K': 'ษ', 'L': 'ศ', ':': 'ซ', '"': '.',
			'z': 'ผ', 'x': 'ป', 'c': 'แ', 'v': 'อ', 'b': 'ิ', 'n': 'ื', 'm': 'ท', ',': 'ม', '.': 'ใ', '/': 'ฝ',
			'Z': '(', 'X': ')', 'C': 'ฉ', 'V': 'ฮ', 'B': 'ฺ', 'N': '์', 'M': '?', '<': 'ฒ', '>': 'ฬ', '?': 'ฦ',
		}
		
		self.vk_to_key = {
			0x41: 'a', 0x42: 'b', 0x43: 'c', 0x44: 'd', 0x45: 'e', 0x46: 'f', 0x47: 'g',
			0x48: 'h', 0x49: 'i', 0x4A: 'j', 0x4B: 'k', 0x4C: 'l', 0x4D: 'm', 0x4E: 'n',
			0x4F: 'o', 0x50: 'p', 0x51: 'q', 0x52: 'r', 0x53: 's', 0x54: 't', 0x55: 'u',
			0x56: 'v', 0x57: 'w', 0x58: 'x', 0x59: 'y', 0x5A: 'z',
			0x30: '0', 0x31: '1', 0x32: '2', 0x33: '3', 0x34: '4', 0x35: '5', 0x36: '6',
			0x37: '7', 0x38: '8', 0x39: '9',
			0xBA: ';', 0xBB: '=', 0xBC: ',', 0xBD: '-', 0xBE: '.', 0xBF: '/',
			0xC0: '`', 0xDB: '[', 0xDC: '\\', 0xDD: ']', 0xDE: "'",
			0x70: 'f1', 0x71: 'f2', 0x72: 'f3', 0x73: 'f4',
		}

	def get_character_order(self, char):
		if char in self.consonants_order:
			return _("{char} {number}").format(char=char, number=self.consonants_order[char])
		elif char in self.vowels_order:
			return _("{char} {number}").format(char=char, number=self.vowels_order[char])
		elif char in self.tone_marks_order:
			return _("{char} {number}").format(char=char, number=self.tone_marks_order[char])
		elif char in self.other_marks_order:
			return _("{char} {number}").format(char=char, number=self.other_marks_order[char])
		return None

	def get_thai_characters(self):
		thai_chars = []
		thai_chars.extend(self.consonants_order.keys())
		thai_chars.extend(self.vowels_order.keys())
		thai_chars.extend(self.tone_marks_order.keys())
		thai_chars.extend(self.other_marks_order.keys())
		return thai_chars

	def is_thai_character(self, char):
		if char in ['ฃ', 'ฅ', ',', '.', '?', '"', "'", '(', ')', '/', '-', '_', '%', '+', '๑', '๒', '๓', '๔', '๕', '๖', '๗', '๘', '๙', '๐', '฿']:
			return False
			
		return (char in self.consonants_order or 
				char in self.vowels_order or 
				char in self.tone_marks_order or 
				char in self.other_marks_order)

	def get_character_from_vk(self, vk_code, caps_lock, shift_pressed):
		key_base = self.vk_to_key.get(vk_code)
		if not key_base:
			return None
		
		if key_base in ['f1', 'f2', 'f3', 'f4']:
			return None
		
		is_alpha = key_base.isalpha() and len(key_base) == 1
		
		effective_shift = shift_pressed or caps_lock
		
		if effective_shift:
			shift_map = {
				'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F', 'g': 'G',
				'h': 'H', 'i': 'I', 'j': 'J', 'k': 'K', 'l': 'L', 'm': 'M', 'n': 'N',
				'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R', 's': 'S', 't': 'T', 'u': 'U',
				'v': 'V', 'w': 'W', 'x': 'X', 'y': 'Y', 'z': 'Z',
				'0': ')', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^',
				'7': '&', '8': '*', '9': '(', '-': '_', '=': '+',
				'`': '~', '[': '{', ']': '}', '\\': '|', ';': ':', "'": '"', ',': '<', '.': '>', '/': '?'
			}
			key_name = shift_map.get(key_base, key_base.upper() if is_alpha else key_base)
		else:
			key_name = key_base
		
		if key_name in self.kedmanee_map:
			char = self.kedmanee_map[key_name]
			if self.is_thai_character(char):
				return char
		
		return None