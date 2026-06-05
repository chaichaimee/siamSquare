# siamSquareCore.py

import os
import sys
import json
import codecs
import re
import time
import threading
import wx
import gui
import api
import ui
import textInfos
import logHandler
import watchdog
import keyboardHandler
from keyboardHandler import KeyboardInputGesture
import core
from . import settingManager
import speech

log = logHandler.log
addonHandler = sys.modules.get('addonHandler')

class SuggestionsDialog(wx.Dialog):
	def __init__(self, parent, original_word, suggestions, core_instance):
		super(SuggestionsDialog, self).__init__(parent, title="คำแนะนำสำหรับคำสะกดผิด", size=(450, 350))
		self.original_word = original_word
		self.suggestions = suggestions
		self.core_instance = core_instance
		self.selected_suggestion = None
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.create_controls()
		self.SetSizer(self.main_sizer)
		self.CentreOnScreen()

	def create_controls(self):
		lbl_info = wx.StaticText(self, label=f"คำที่พบ: {self.original_word}")
		self.main_sizer.Add(lbl_info, 0, wx.ALL, 10)
		lbl_list = wx.StaticText(self, label="เลือกคำที่ถูกต้องเพื่อแทนที่:")
		self.main_sizer.Add(lbl_list, 0, wx.LEFT | wx.RIGHT, 10)
		self.suggestion_list = wx.ListBox(self, choices=self.suggestions, style=wx.LB_SINGLE)
		if self.suggestions:
			self.suggestion_list.SetSelection(0)
		self.main_sizer.Add(self.suggestion_list, 1, wx.EXPAND | wx.ALL, 10)
		btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.replace_button = wx.Button(self, wx.ID_ANY, label="แทนที่คำ")
		self.replace_button.Bind(wx.EVT_BUTTON, self.on_replace_click)
		btn_sizer.Add(self.replace_button, 0, wx.ALL, 5)
		btn_cancel = wx.Button(self, wx.ID_CANCEL, label="ยกเลิก")
		btn_sizer.Add(btn_cancel, 0, wx.ALL, 5)
		self.main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
		self.suggestion_list.SetFocus()
		self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
		self.Bind(wx.EVT_BUTTON, self.on_button_click)

	def on_replace_click(self, event):
		selection = self.suggestion_list.GetSelection()
		if selection != wx.NOT_FOUND:
			self.selected_suggestion = self.suggestion_list.GetString(selection)
			core_instance_ref = self.core_instance
			self.EndModal(wx.ID_OK)
			wx.CallAfter(core_instance_ref.execute_replacement, self.selected_suggestion)
		else:
			self.EndModal(wx.ID_CANCEL)

	def on_button_click(self, event):
		button_id = event.GetId()
		if button_id == wx.ID_OK:
			selection = self.suggestion_list.GetSelection()
			if selection != wx.NOT_FOUND:
				self.selected_suggestion = self.suggestion_list.GetString(selection)
				core_instance_ref = self.core_instance
				wx.CallAfter(core_instance_ref.execute_replacement, self.selected_suggestion)
			event.Skip()

	def on_char_hook(self, event):
		key_code = event.GetKeyCode()
		if key_code == wx.WXK_RETURN:
			selection = self.suggestion_list.GetSelection()
			if selection != wx.NOT_FOUND:
				self.selected_suggestion = self.suggestion_list.GetString(selection)
				core_instance_ref = self.core_instance
				self.EndModal(wx.ID_OK)
				wx.CallAfter(core_instance_ref.execute_replacement, self.selected_suggestion)
			else:
				self.EndModal(wx.ID_CANCEL)
		elif key_code == wx.WXK_ESCAPE:
			self.EndModal(wx.ID_CANCEL)
		else:
			event.Skip()

class SiamSquareCore:
	def __init__(self, setting_manager):
		self.setting_manager = setting_manager
		self.dictionary = {}
		self.base_initialized = False
		thai_consonants = ['ก', 'ข', 'ค', 'ฆ', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ', 'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท', 'ธ', 'น', 'บ', 'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ศ', 'ษ', 'ส', 'ห', 'ฬ', 'อ', 'ฮ', 'ฤ', 'ฦ']
		self.valid_filenames = set(["{}.json".format(c) for c in thai_consonants] + ["others.json"])
		self.load_dictionary()

	def _get_base_dictionary_path(self):
		current_dir = os.path.dirname(os.path.abspath(__file__))
		return os.path.join(current_dir, "dictionary")

	def _get_user_dictionary_path(self):
		import globalVars
		user_config_dir = globalVars.appArgs.configPath
		return os.path.join(user_config_dir, "ChaiChaimee", "SiamSquare", "dictionary")

	def _is_valid_dictionary_file(self, filename):
		return filename in self.valid_filenames

	def _cleanup_invalid_files(self, directory):
		if not os.path.exists(directory):
			return
		for filename in os.listdir(directory):
			if filename.endswith('.json') and not self._is_valid_dictionary_file(filename):
				try:
					os.remove(os.path.join(directory, filename))
					log.info(f"Removed invalid dictionary file: {filename}")
				except Exception as e:
					log.error(f"Failed to remove invalid file {filename}: {e}")

	def load_dictionary(self):
		base_dir = self._get_base_dictionary_path()
		user_dir = self._get_user_dictionary_path()
		self._cleanup_invalid_files(base_dir)
		self._cleanup_invalid_files(user_dir)
		self.dictionary.clear()
		if os.path.exists(base_dir):
			for filename in os.listdir(base_dir):
				if filename.endswith('.json') and self._is_valid_dictionary_file(filename):
					self._load_file_into_dict(os.path.join(base_dir, filename))
		if os.path.exists(user_dir):
			for filename in os.listdir(user_dir):
				if filename.endswith('.json') and self._is_valid_dictionary_file(filename):
					self._load_file_into_dict(os.path.join(user_dir, filename))

	def _load_file_into_dict(self, filepath):
		try:
			with codecs.open(filepath, 'r', encoding='utf-8') as f:
				data = json.load(f)
				if isinstance(data, dict):
					for word, definitions in data.items():
						if word not in self.dictionary:
							self.dictionary[word] = []
						if isinstance(definitions, list):
							self.dictionary[word].append(definitions)
						else:
							self.dictionary[word].append([str(definitions)])
		except Exception as e:
			log.error(f"Error loading dictionary file {filepath}: {e}")

	def save_user_word(self, word, definitions, filename):
		if not self._is_valid_dictionary_file(filename):
			log.error(f"Attempted to save to invalid filename: {filename}")
			return False
		user_dir = self._get_user_dictionary_path()
		try:
			os.makedirs(user_dir, exist_ok=True)
			filepath = os.path.join(user_dir, filename)
			data = {}
			if os.path.exists(filepath):
				try:
					with codecs.open(filepath, 'r', encoding='utf-8') as f:
						data = json.load(f)
				except Exception:
					data = {}
			data[word] = definitions
			with codecs.open(filepath, 'w', encoding='utf-8') as f:
				json.dump(data, f, ensure_ascii=False, indent=4)
			return True
		except Exception as e:
			log.error(f"Error saving user word: {e}")
			return False

	def add_word(self, word, definition):
		if not word or not definition:
			return False
		match = re.search(r'^[เแโไใ]?([ก-ฮ])', word)
		if match:
			filename = "{}.json".format(match.group(1))
		else:
			filename = "others.json"
		if word not in self.dictionary:
			self.dictionary[word] = []
		self.dictionary[word].append([definition])
		return self.save_user_word(word, [definition], filename)

	def update_word(self, old_word, new_word, new_definition):
		if not old_word or not new_word or not new_definition:
			return False
		if old_word in self.dictionary:
			del self.dictionary[old_word]
		if new_word not in self.dictionary:
			self.dictionary[new_word] = []
		self.dictionary[new_word].append([new_definition])
		match = re.search(r'^[เแโไใ]?([ก-ฮ])', new_word)
		filename = "{}.json".format(match.group(1)) if match else "others.json"
		return self.save_user_word(new_word, [new_definition], filename)

	def get_definition(self, word):
		if not word:
			ui.message("ไม่พบคำสำหรับค้นหา")
			return
		definitions = self.dictionary.get(word)
		if not definitions:
			ui.message(f"ไม่พบความหมายของคำว่า {word}")
			return
			
		flat_definitions = []
		for item in definitions:
			if isinstance(item, list):
				for sub_item in item:
					if isinstance(sub_item, list):
						for sub_sub in sub_item:
							item_str = str(sub_sub).strip().replace("[", "").replace("]", "")
							if item_str and item_str not in flat_definitions:
								flat_definitions.append(item_str)
					else:
						item_str = str(sub_item).strip().replace("[", "").replace("]", "")
						if item_str and item_str not in flat_definitions:
							flat_definitions.append(item_str)
			else:
				item_str = str(item).strip().replace("[", "").replace("]", "")
				if item_str and item_str not in flat_definitions:
					flat_definitions.append(item_str)
					
		output_text = ", ".join(flat_definitions)
		if not output_text.strip():
			ui.message(f"ไม่พบความหมายของคำว่า {word}")
		else:
			ui.message(output_text)

	def generate_suggestions(self, word):
		if not word:
			return []
		suggestions = []
		for dict_word in self.dictionary.keys():
			if len(dict_word) >= 4 and len(word) >= 4:
				if dict_word[:4] == word[:4]:
					suggestions.append(dict_word)
			elif dict_word[:2] == word[:2]:
				suggestions.append(dict_word)
		return suggestions[:10]

	def spell_word(self, word):
		if not word:
			ui.message("ไม่พบคำสำหรับสะกด")
			return
		
		# สร้างลำดับการอ่านสะกดคำทีละอักษร โดยบังคับใส่คอมมาและช่องว่างเบิ้ล เพื่อบังคับทางอ้อมให้เอนจิ้นเสียงหน่วงเวลาสระ/วรรณยุกต์เท่าเทียมพยัญชนะ
		spelled_sequence = []
		for char in list(word):
			spelled_sequence.append(char)
			spelled_sequence.append(", ")
			
		output_text = "".join(spelled_sequence).strip(", ")
		ui.message(output_text)

	def execute_replacement(self, text_to_paste):
		if not text_to_paste:
			return
		if " " in text_to_paste:
			self._paste_sentence_classic(text_to_paste)
		else:
			self._paste_single_word(text_to_paste)

	def _paste_single_word(self, word):
		try:
			self._clear_clipboard()
			for character in word:
				gesture = KeyboardInputGesture.fromName(character)
				gesture.send()
			log.info(f"Single word paste executed for: {word}")
		except Exception as e:
			log.error(f"Error in single word paste logic: {e}")
			self._paste_sentence_classic(word)

	def _paste_sentence_classic(self, text_to_paste):
		try:
			focused_object = api.getFocusObject()
			window_handle = getattr(focused_object, "windowHandle", None)
			backup_text = ""
			try:
				backup_text = api.getClipData()
			except Exception:
				pass
			api.copyToClip(text_to_paste)
			try:
				paste_gesture = KeyboardInputGesture.fromName("shift+insert")
				paste_gesture.send()
				log.info("Paste sent via Shift+Insert")
				core.callLater(150, self._restore_clipboard, backup_text)
				return
			except Exception:
				pass
			if window_handle:
				WM_PASTE = 0x0302
				watchdog.cancellableSendMessage(window_handle, WM_PASTE, 0, 0)
				log.info("Paste sent via WM_PASTE")
			else:
				log.error("No paste method available")
				ui.message("ไม่สามารถวางข้อความได้")
			core.callLater(150, self._restore_clipboard, backup_text)
		except Exception as e:
			log.error(f"Error sending paste command: {e}")

	def _restore_clipboard(self, backup_text):
		try:
			api.copyToClip(backup_text if backup_text else "")
		except Exception as e:
			log.error(f"Error restoring clipboard: {e}")

	def _clear_clipboard(self):
		try:
			api.copyToClip("")
		except Exception as e:
			log.error(f"Error clearing clipboard: {e}")