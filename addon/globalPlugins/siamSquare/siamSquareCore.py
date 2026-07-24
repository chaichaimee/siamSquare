# siamSquareCore.py

import json
import os
import re
import globalVars
import ui
import wx
import gui
import textInfos
import api
import time
import core
import watchdog
from keyboardHandler import KeyboardInputGesture
import braille
from logHandler import log
import speech
import addonHandler

addonHandler.initTranslation()


class SuggestionsDialog(wx.Dialog):
	def __init__(self, parent, original_word, suggestions, core_instance):
		super(SuggestionsDialog, self).__init__(
			parent,
			title=_("คำแนะนำสำหรับคำสะกดผิด"),
			size=(450, 350),
			style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP
		)
		self.original_word = original_word
		self.suggestions = suggestions
		self.core_instance = core_instance
		self.selected_suggestion = None
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.create_controls()
		self.SetSizer(self.main_sizer)
		self.CentreOnScreen()
		self.Raise()
		self.SetFocus()

	def create_controls(self):
		lbl_info = wx.StaticText(self, label=_("คำที่พบ: {}").format(self.original_word))
		self.main_sizer.Add(lbl_info, 0, wx.ALL, 10)

		lbl_list = wx.StaticText(self, label=_("เลือกคำที่ถูกต้องเพื่อแทนที่:"))
		self.main_sizer.Add(lbl_list, 0, wx.LEFT | wx.RIGHT, 10)

		self.suggestion_list = wx.ListBox(self, choices=self.suggestions, style=wx.LB_SINGLE)
		if self.suggestions:
			self.suggestion_list.SetSelection(0)
		self.suggestion_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_double_click)
		self.suggestion_list.Bind(wx.EVT_KEY_DOWN, self.on_list_key_down)
		self.main_sizer.Add(self.suggestion_list, 1, wx.EXPAND | wx.ALL, 10)

		btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.replace_button = wx.Button(self, wx.ID_ANY, label=_("แทนที่คำ"))
		self.replace_button.Bind(wx.EVT_BUTTON, self.on_replace_click)
		btn_sizer.Add(self.replace_button, 0, wx.ALL, 5)

		btn_cancel = wx.Button(self, wx.ID_CANCEL, label=_("ยกเลิก"))
		btn_cancel.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))
		btn_sizer.Add(btn_cancel, 0, wx.ALL, 5)
		self.main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

		self.suggestion_list.SetFocus()
		self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)

	def on_list_key_down(self, event):
		key_code = event.GetKeyCode()
		if key_code == wx.WXK_RETURN:
			self.on_replace_click(event)
		else:
			event.Skip()

	def on_double_click(self, event):
		self.on_replace_click(event)

	def on_replace_click(self, event):
		selection = self.suggestion_list.GetSelection()
		if selection != wx.NOT_FOUND:
			self.selected_suggestion = self.suggestion_list.GetString(selection)
			# Keep a reference to core_instance before closing dialog
			core_ref = self.core_instance
			word_to_replace = self.selected_suggestion
			self.EndModal(wx.ID_OK)
			# Execute replacement after dialog is closed and focus is back to the document
			wx.CallAfter(core_ref.execute_replacement, word_to_replace)
		else:
			self.EndModal(wx.ID_CANCEL)

	def on_char_hook(self, event):
		key_code = event.GetKeyCode()
		if key_code == wx.WXK_RETURN:
			self.on_replace_click(event)
		elif key_code == wx.WXK_ESCAPE:
			self.EndModal(wx.ID_CANCEL)
		else:
			event.Skip()


class SiamSquareCore:
	def __init__(self, setting_manager):
		self.setting_manager = setting_manager
		self.dictionary = {}
		self.load_dictionary()

	def load_dictionary(self):
		self.dictionary = {}

		addon_path = os.path.abspath(os.path.dirname(__file__))
		dict_path = os.path.join(addon_path, "dictionary", "thaiDic.jsonl")

		user_config_dir = globalVars.appArgs.configPath
		backup_dir = os.path.join(user_config_dir, "siamSquare")
		backup_path = os.path.join(backup_dir, "thaiDic.jsonl")

		load_path = None

		if os.path.exists(backup_path):
			load_path = backup_path
		elif os.path.exists(dict_path):
			load_path = dict_path

		if not load_path:
			return

		try:
			with open(load_path, 'r', encoding='utf-8') as f:
				for line in f:
					line = line.strip()
					if not line:
						continue
					try:
						entry = json.loads(line)
						if isinstance(entry, dict):
							for word, definitions in entry.items():
								if isinstance(definitions, list):
									self.dictionary[word] = definitions
								else:
									self.dictionary[word] = [[str(definitions)]]
					except json.JSONDecodeError:
						continue
		except Exception as e:
			ui.message(_("เกิดข้อผิดพลาดในการโหลดพจนานุกรม: {}").format(str(e)))

	def get_definition(self, word):
		word = word.strip()
		if not word:
			ui.message(_("ไม่พบคำสำหรับค้นหา"))
			return

		definitions = self.dictionary.get(word, [])
		if definitions:
			definition_text = ""
			for group in definitions:
				if isinstance(group, list):
					for definition in group:
						if isinstance(definition, list):
							for sub_def in definition:
								item_str = str(sub_def).strip()
								if item_str:
									definition_text += item_str + ", "
						else:
							item_str = str(definition).strip()
							if item_str:
								definition_text += item_str + ", "
				else:
					item_str = str(group).strip()
					if item_str:
						definition_text += item_str + ", "

			output_text = definition_text.rstrip(", ")
			if output_text:
				ui.message(output_text)
			else:
				ui.message(_("ไม่พบความหมายของคำว่า {}").format(word))
		else:
			ui.message(_("ไม่พบความหมายของคำว่า {}").format(word))

	def generate_suggestions(self, word):
		suggestions = []
		word = word.strip()

		if not word:
			return suggestions

		for dict_word in self.dictionary.keys():
			if dict_word.startswith(word):
				suggestions.append(dict_word)

		if len(word) > 2:
			base_word = word[:-1]
			for dict_word in self.dictionary.keys():
				if dict_word.startswith(base_word) and dict_word not in suggestions:
					suggestions.append(dict_word)

		pattern_suggestions = self.get_pattern_suggestions(word)
		suggestions.extend(pattern_suggestions)

		unique_suggestions = list(set(suggestions))
		return sorted(unique_suggestions)[:15]

	def get_pattern_suggestions(self, word):
		suggestions = []

		if len(word) < 4:
			return suggestions

		first_char = word[0]
		last_char = word[-1]
		second_char = word[1] if len(word) > 1 else ''
		second_last_char = word[-2] if len(word) > 1 else ''

		pattern = f"^{re.escape(first_char)}{re.escape(second_char)}.*{re.escape(second_last_char)}{re.escape(last_char)}$"

		try:
			regex = re.compile(pattern)
			for dict_word in self.dictionary.keys():
				if regex.match(dict_word) and dict_word not in suggestions:
					suggestions.append(dict_word)
		except re.error:
			pass

		month_patterns = {
			r'^พฤศพาคม$': 'พฤษภาคม',
			r'^พฤศภาคม$': 'พฤษภาคม',
			r'^กุมภา.*$': 'กุมภาพันธ์',
			r'^มีนา.*$': 'มีนาคม',
			r'^เมษา.*$': 'เมษายน',
			r'^พฤษภา.*$': 'พฤษภาคม',
			r'^มิถุนา.*$': 'มิถุนายน',
			r'^กรกฎา.*$': 'กรกฎาคม',
			r'^สิงหา.*$': 'สิงหาคม',
			r'^กันยา.*$': 'กันยายน',
			r'^ตุลา.*$': 'ตุลาคม',
			r'^พฤศจิก.*$': 'พฤศจิกายน',
			r'^ธันวา.*$': 'ธันวาคม'
		}

		for pattern, correction in month_patterns.items():
			if re.match(pattern, word) and correction in self.dictionary:
				suggestions.append(correction)

		return suggestions

	def spell_word(self, word):
		if not word:
			ui.message(_("ไม่พบคำสำหรับสะกด"))
			return

		consonants = r'[ก-ฮ]'
		vowels = r'[ะาๅิีึืุูเแโใไ]'
		tone_marks = r'[่้๊๋]'

		def get_char_name(char):
			if re.match(consonants, char):
				return char
			elif re.match(vowels, char):
				return {
					'ะ': 'สระอะ', 'า': 'สระอา', 'ๅ': 'สระอา (ยาว)',
					'ิ': 'สระอิ', 'ี': 'สระอี', 'ึ': 'สระอึ', 'ื': 'สระอื',
					'ุ': 'สระอุ', 'ู': 'สระอู', 'เ': 'สระเอ', 'แ': 'สระแอ',
					'โ': 'สระโอ', 'ใ': 'สระใอ', 'ไ': 'สระไอ'
				}.get(char, f"สระ {char}")
			elif re.match(tone_marks, char):
				return {
					'่': 'ไม้เอก', '้': 'ไม้โท', '๊': 'ไม้ตรี', '๋': 'ไม้จัตวา'
				}.get(char, f"วรรณยุกต์ {char}")
			else:
				return char

		spelled_chars = []
		for char in word:
			char_name = get_char_name(char)
			spelled_chars.append(char_name)

		spelled_text = ", ".join(spelled_chars)
		ui.message(spelled_text)

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
				ui.message(_("ไม่สามารถวางข้อความได้"))

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

	def announceWordDefinition(self, word):
		self.get_definition(word)

	def getWordSuggestions(self, word):
		return self.generate_suggestions(word)

	def spellWord(self, word):
		self.spell_word(word)