# siamCenter.py

import wx
import gui
import api
import ui
import os
import json
import addonHandler
from . import settingManager
import core
import shutil
import globalVars
import re
import time
import logHandler

addonHandler.initTranslation()

class AddWordDialog(wx.Dialog):
	def __init__(self, parent, word="", definition="", edit_mode=False):
		title = _("แก้ไขคำ") if edit_mode else _("เพิ่มคำ")
		super(AddWordDialog, self).__init__(parent, title=title, size=(500, 400))
		self.word = word
		self.definition = definition
		self.edit_mode = edit_mode
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.create_controls()
		self.SetSizer(self.main_sizer)
		self.CentreOnScreen()

	def create_controls(self):
		word_label = wx.StaticText(self, label=_("คำ:"))
		self.main_sizer.Add(word_label, 0, wx.ALL, 5)
		
		self.word_ctrl = wx.TextCtrl(self)
		self.word_ctrl.SetValue(self.word)
		self.main_sizer.Add(self.word_ctrl, 0, wx.EXPAND | wx.ALL, 5)

		definition_label = wx.StaticText(self, label=_("ความหมาย:"))
		self.main_sizer.Add(definition_label, 0, wx.ALL, 5)
		
		self.definition_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 200))
		self.definition_ctrl.SetValue(self.definition)
		self.main_sizer.Add(self.definition_ctrl, 1, wx.EXPAND | wx.ALL, 5)

		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		
		if self.edit_mode:
			save_button = wx.Button(self, wx.ID_ANY, label=_("แก้ไขคำ"))
		else:
			save_button = wx.Button(self, wx.ID_ANY, label=_("เพิ่มคำ"))
		save_button.Bind(wx.EVT_BUTTON, self.on_save)
		button_sizer.Add(save_button, 0, wx.ALL, 5)

		cancel_button = wx.Button(self, wx.ID_CANCEL, label=_("ยกเลิก"))
		button_sizer.Add(cancel_button, 0, wx.ALL, 5)
		
		self.main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)

		self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
		self.word_ctrl.SetFocus()

	def on_save(self, event):
		word = self.word_ctrl.GetValue().strip()
		definition = self.definition_ctrl.GetValue().strip()
		
		if not word:
			wx.MessageBox(_("กรุณากรอกคำ"), _("ข้อผิดพลาด"), wx.OK | wx.ICON_ERROR)
			return
			
		if not definition:
			wx.MessageBox(_("กรุณากรอกความหมาย"), _("ข้อผิดพลาด"), wx.OK | wx.ICON_ERROR)
			return
		
		self.word = word
		self.definition = definition
		self.EndModal(wx.ID_OK)

	def on_char_hook(self, event):
		if event.GetKeyCode() == wx.WXK_ESCAPE:
			self.EndModal(wx.ID_CANCEL)
		else:
			event.Skip()


class SiamCenterDialog(wx.Dialog):
	def __init__(self, parent, selected_word=None, core_instance=None):
		super(SiamCenterDialog, self).__init__(parent, title=_("Siam Center"), size=(800, 600))
		self.settingManager = settingManager.SettingManager()
		self.core = core_instance  # Store core instance reference
		self.dictionary = {}
		self.selected_word = selected_word
		self.jump_word_prefix = ""
		self.last_key_time = 0.0
		self.load_dictionary()
		self.current_category = ""
		self.current_word = ""
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.create_controls()
		self.SetSizer(self.main_sizer)
		self.CentreOnScreen()
		
		if self.selected_word:
			self.auto_select_word(self.selected_word)

	def load_dictionary(self):
		"""Load dictionary from addon dictionary folder (primary source)"""
		self.dictionary = {}
		
		# Use addon directory path (this is where thaiDic.jsonl actually resides)
		addonPath = os.path.abspath(os.path.dirname(__file__))
		dictPath = os.path.join(addonPath, "dictionary", "thaiDic.jsonl")
		
		# Also check user config for backup/edits
		user_config_dir = globalVars.appArgs.configPath
		backup_dir = os.path.join(user_config_dir, "siamSquare")
		backup_path = os.path.join(backup_dir, "thaiDic.jsonl")
		
		load_path = None
		
		# 1. Try to load from User Config (edits/backup)
		if os.path.exists(backup_path):
			load_path = backup_path
		# 2. Fallback to Addon Default
		elif os.path.exists(dictPath):
			load_path = dictPath
		
		if not load_path:
			ui.message(_("ไม่พบไฟล์พจนานุกรม"))
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

	def save_dictionary(self):
		"""Save dictionary to user config location"""
		try:
			user_config_dir = globalVars.appArgs.configPath
			backup_dir = os.path.join(user_config_dir, "siamSquare")
			os.makedirs(backup_dir, exist_ok=True)
			backup_path = os.path.join(backup_dir, "thaiDic.jsonl")
			
			with open(backup_path, 'w', encoding='utf-8') as f:
				for word in sorted(self.dictionary.keys()):
					entry = {word: self.dictionary[word]}
					f.write(json.dumps(entry, ensure_ascii=False) + '\n')
			
			# Also save to addon directory for distribution
			if self.backup_checkbox.IsChecked():
				addonPath = os.path.abspath(os.path.dirname(__file__))
				dictPath = os.path.join(addonPath, "dictionary", "thaiDic.jsonl")
				os.makedirs(os.path.dirname(dictPath), exist_ok=True)
				shutil.copy2(backup_path, dictPath)
			
			self.reload_core_dictionary()
			return True
		except Exception as e:
			ui.message(_("เกิดข้อผิดพลาดในการบันทึกพจนานุกรม: {}").format(str(e)))
			return False

	def reload_core_dictionary(self):
		"""Reload dictionary in the core module"""
		try:
			if self.core is not None:
				self.core.dictionary = self.dictionary.copy()
				ui.message(_("พจนานุกรมถูกโหลดใหม่เรียบร้อยแล้ว"))
		except Exception as e:
			pass

	def get_thai_first_consonant(self, word):
		if not word:
			return None
		match = re.search(r'[ก-ฮ]', word)
		if match:
			return match.group(0)
		return None

	def auto_select_word(self, word):
		if not word:
			return
			
		first_consonant = self.get_thai_first_consonant(word)
		
		if first_consonant:
			categories = self.get_thai_initial_consonants()
			
			if first_consonant in categories:
				index = categories.index(first_consonant)
				self.category_list.SetSelection(index)
				self.current_category = first_consonant
				wx.CallLater(100, self.update_word_list_after_selection, word)

	def update_word_list_after_selection(self, target_word):
		self.update_word_list()
		
		words = self.word_list.GetStrings()
		for i, word in enumerate(words):
			if word == target_word:
				self.word_list.SetSelection(i)
				self.current_word = word
				self.word_list.SetFocus()
				wx.CallLater(100, self.update_definition_list)
				break
		else:
			ui.message(_("ไม่พบคำว่า: {} ในพจนานุกรม").format(target_word))

	def create_controls(self):
		category_label = wx.StaticText(self, label=_("หมวด:"))
		self.main_sizer.Add(category_label, 0, wx.ALL, 5)
		
		self.category_list = wx.ListBox(self, choices=self.get_thai_initial_consonants(), style=wx.LB_SINGLE)
		self.category_list.Bind(wx.EVT_LISTBOX, self.on_category_select)
		self.main_sizer.Add(self.category_list, 0, wx.EXPAND | wx.ALL, 5)

		word_label = wx.StaticText(self, label=_("คำ:"))
		self.main_sizer.Add(word_label, 0, wx.ALL, 5)
		
		self.word_list = wx.ListBox(self, style=wx.LB_SINGLE)
		self.word_list.Bind(wx.EVT_LISTBOX, self.on_word_select)
		self.word_list.Bind(wx.EVT_CONTEXT_MENU, self.on_word_context_menu)
		self.word_list.Bind(wx.EVT_CHAR, self.on_word_list_char)
		self.main_sizer.Add(self.word_list, 1, wx.EXPAND | wx.ALL, 5)

		definition_label = wx.StaticText(self, label=_("ความหมาย:"))
		self.main_sizer.Add(definition_label, 0, wx.ALL, 5)
		
		self.definition_list = wx.ListBox(self, style=wx.LB_SINGLE)
		self.definition_list.Bind(wx.EVT_CONTEXT_MENU, self.on_definition_context_menu)
		self.main_sizer.Add(self.definition_list, 1, wx.EXPAND | wx.ALL, 5)

		action_sizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.add_button = wx.Button(self, wx.ID_ANY, label=_("เพิ่มคำ"))
		self.add_button.Bind(wx.EVT_BUTTON, self.on_add_word)
		action_sizer.Add(self.add_button, 0, wx.ALL, 5)

		self.edit_button = wx.Button(self, wx.ID_ANY, label=_("แก้ไขคำ"))
		self.edit_button.Bind(wx.EVT_BUTTON, self.on_edit_word)
		action_sizer.Add(self.edit_button, 0, wx.ALL, 5)
		
		self.backup_checkbox = wx.CheckBox(self, label=_("สำรองไฟล์พจนานุกรมในโฟลเดอร์ Add-on"))
		self.backup_checkbox.SetValue(True)
		action_sizer.Add(self.backup_checkbox, 0, wx.ALL, 5)
		
		self.main_sizer.Add(action_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)

		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		close_button = wx.Button(self, wx.ID_CLOSE, label=_("ปิด"))
		close_button.Bind(wx.EVT_BUTTON, lambda evt: self.Close())
		button_sizer.Add(close_button, 0, wx.ALL, 5)
		self.main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)

		self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)

	def get_thai_initial_consonants(self):
		return ["ก", "ข", "ค", "ฆ", "ง", "จ", "ฉ", "ช", "ซ", "ฌ", "ญ", "ฎ", "ฏ", "ฐ", "ฑ", "ฒ", "ณ", "ด", "ต", "ถ", "ท", "ธ", "น", "บ", "ป", "ผ", "ฝ", "พ", "ฟ", "ภ", "ม", "ย", "ร", "ล", "ว", "ศ", "ษ", "ส", "ห", "ฬ", "อ", "ฮ"]

	def on_category_select(self, event):
		self.current_category = self.category_list.GetStringSelection()
		wx.CallLater(1, self.update_word_list)
		self.jump_word_prefix = ""

	def update_word_list(self):
		self.word_list.Clear()
		self.definition_list.Clear()
		if not self.current_category:
			return
			
		words_in_category = []
		for word in self.dictionary.keys():
			if word and self.get_thai_first_consonant(word) == self.current_category:
				words_in_category.append(word)
		
		words_in_category.sort()
		self.word_list.Set(words_in_category)

	def on_word_select(self, event):
		self.current_word = self.word_list.GetStringSelection()
		wx.CallLater(1, self.update_definition_list)

	def update_definition_list(self):
		self.definition_list.Clear()
		if not self.current_word:
			return
			
		definitions = self.dictionary.get(self.current_word, [])
		definition_texts = []
		
		for definition_group in definitions:
			if isinstance(definition_group, list):
				for definition in definition_group:
					if isinstance(definition, list):
						for sub_def in definition:
							item_str = str(sub_def).strip()
							if item_str and item_str not in definition_texts:
								definition_texts.append(item_str)
					else:
						item_str = str(definition).strip()
						if item_str and item_str not in definition_texts:
							definition_texts.append(item_str)
			else:
				item_str = str(definition_group).strip()
				if item_str and item_str not in definition_texts:
					definition_texts.append(item_str)
		
		self.definition_list.Set(definition_texts)

	def on_add_word(self, event):
		dialog = AddWordDialog(self)
		if dialog.ShowModal() == wx.ID_OK:
			word = dialog.word
			definition = dialog.definition
			
			self.dictionary[word] = [[definition]]
			
			if self.save_dictionary():
				ui.message(_("เพิ่มคำลงพจนานุกรมสมบูรณ์"))
				first_consonant = self.get_thai_first_consonant(word)
				if first_consonant == self.current_category:
					self.update_word_list_after_selection(word)
				else:
					categories = self.get_thai_initial_consonants()
					if first_consonant in categories:
						index = categories.index(first_consonant)
						self.category_list.SetSelection(index)
						self.current_category = first_consonant
						self.update_word_list_after_selection(word)
			else:
				ui.message(_("เกิดข้อผิดพลาดในการเพิ่มคำ"))
		
		dialog.Destroy()

	def on_edit_word(self, event):
		if not self.current_word:
			wx.MessageBox(_("กรุณาเลือกคำที่ต้องการแก้ไข"), _("ข้อผิดพลาด"), wx.OK | wx.ICON_ERROR)
			return
			
		definitions = self.dictionary.get(self.current_word, [])
		definition_text = ""
		if definitions:
			flat_list = []
			for item in definitions:
				if isinstance(item, list):
					for sub in item:
						if isinstance(sub, list):
							flat_list.extend([str(x).strip() for x in sub])
						else:
							flat_list.append(str(sub).strip())
				else:
					flat_list.append(str(item).strip())
			definition_text = "\n".join(flat_list)
			
		dialog = AddWordDialog(self, self.current_word, definition_text, edit_mode=True)
		if dialog.ShowModal() == wx.ID_OK:
			new_word = dialog.word
			new_definition = dialog.definition
			
			old_consonant = self.get_thai_first_consonant(self.current_word)
			new_consonant = self.get_thai_first_consonant(new_word)
			
			if new_word != self.current_word:
				del self.dictionary[self.current_word]
			
			self.dictionary[new_word] = [[new_definition]]
			
			if self.save_dictionary():
				ui.message(_("แก้ไขคำสมบูรณ์"))
				if new_consonant == old_consonant:
					self.current_category = new_consonant
					self.update_word_list_after_selection(new_word)
				else:
					categories = self.get_thai_initial_consonants()
					if new_consonant in categories:
						index = categories.index(new_consonant)
						self.category_list.SetSelection(index)
						self.current_category = new_consonant
						self.update_word_list_after_selection(new_word)
			else:
				ui.message(_("เกิดข้อผิดพลาดในการแก้ไขคำ"))
		
		dialog.Destroy()

	def on_word_context_menu(self, event):
		menu = wx.Menu()
		copy_item = menu.Append(wx.ID_ANY, _("คัดลอกคำ"))
		self.Bind(wx.EVT_MENU, self.on_copy_word, copy_item)
		self.PopupMenu(menu)
		menu.Destroy()

	def on_definition_context_menu(self, event):
		menu = wx.Menu()
		copy_item = menu.Append(wx.ID_ANY, _("คัดลอกความหมาย"))
		self.Bind(wx.EVT_MENU, self.on_copy_definition, copy_item)
		menu.AppendSeparator()
		copy_all_item = menu.Append(wx.ID_ANY, _("คัดลอกคำและความหมายทั้งหมด"))
		self.Bind(wx.EVT_MENU, self.on_copy_word_and_definition, copy_all_item)
		self.PopupMenu(menu)
		menu.Destroy()

	def on_copy_word(self, event):
		selected_word = self.word_list.GetStringSelection()
		if selected_word:
			if wx.TheClipboard.Open():
				wx.TheClipboard.SetData(wx.TextDataObject(selected_word))
				wx.TheClipboard.Close()
				ui.message(_("คัดลอกคำ: {}").format(selected_word))
			else:
				ui.message(_("ไม่สามารถเปิดคลิปบอร์ดได้"))

	def on_copy_definition(self, event):
		selected_definition = self.definition_list.GetStringSelection()
		if selected_definition:
			if wx.TheClipboard.Open():
				wx.TheClipboard.SetData(wx.TextDataObject(selected_definition))
				wx.TheClipboard.Close()
				ui.message(_("คัดลอกความหมายเรียบร้อย"))
			else:
				ui.message(_("ไม่สามารถเปิดคลิปบอร์ดได้"))

	def on_copy_word_and_definition(self, event):
		selected_word = self.word_list.GetStringSelection()
		selected_definition = self.definition_list.GetStringSelection()
		if selected_word and selected_definition:
			text = f"{selected_word}: {selected_definition}"
			if wx.TheClipboard.Open():
				wx.TheClipboard.SetData(wx.TextDataObject(text))
				wx.TheClipboard.Close()
				ui.message(_("คัดลอกคำและความหมายเรียบร้อย"))
			else:
				ui.message(_("ไม่สามารถเปิดคลิปบอร์ดได้"))

	def on_char_hook(self, event):
		key = event.GetKeyCode()
		if key == wx.WXK_ESCAPE:
			self.Close()
		else:
			event.Skip()

	def on_word_list_char(self, event):
		key = event.GetUnicodeKey()
		if key == wx.WXK_NONE:
			event.Skip()
			return
		
		if self.word_list.HasFocus():
			current_time = time.time()
			
			if 0x0E01 <= key <= 0x0E5B:
				char = chr(key)
				if current_time - self.last_key_time > 1.0:
					self.jump_word_prefix = ""
				self.jump_word_prefix += char
				self.last_key_time = current_time
				
				words = self.word_list.GetStrings()
				for i, word in enumerate(words):
					if word.startswith(self.jump_word_prefix):
						self.word_list.SetSelection(i)
						self.current_word = word
						self.update_definition_list()
						ui.message(_("{}").format(word))
						break
				else:
					self.jump_word_prefix = self.jump_word_prefix[:-1]
					ui.message(_("ไม่พบคำที่เริ่มด้วย: {}").format(self.jump_word_prefix))
			else:
				event.Skip()
		else:
			event.Skip()