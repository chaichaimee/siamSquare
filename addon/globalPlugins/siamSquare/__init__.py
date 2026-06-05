# __init__.py
# Copyright (C) 2026 Chai Chaimee
# Licensed under GNU General Public License. See COPYING.txt for details.

import globalPluginHandler
import scriptHandler
import ui
import tones
import api
import wx
import gui
import core
import addonHandler
import globalVars
import textInfos
import winUser
from . import siamSquareCore
from . import settingManager
from . import siamCenter
from . import sort
from functools import wraps

addonHandler.initTranslation()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("Siam Square")
	
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		if globalVars.appArgs.secure:
			return
			
		self.settingManager = settingManager.SettingManager()
		self.siamSquareCore = siamSquareCore.SiamSquareCore(self.settingManager)
		self.thaiSorter = sort.ThaiSorter()
		self.inLayeredMode = False
		self.inThaiSorterMode = False

	def terminate(self):
		if hasattr(self, 'siamSquareCore'):
			self.siamSquareCore = None
		if hasattr(self, 'settingManager'):
			self.settingManager = None
		if hasattr(self, 'thaiSorter'):
			self.thaiSorter = None
		super().terminate()

	def getScript(self, gesture):
		if not self.inLayeredMode:
			return super().getScript(gesture)
		
		keyName = gesture.displayName
		
		if self.inThaiSorterMode:
			if keyName == "escape":
				@wraps(self.script_exitAllModes)
				def script(gesture):
					self.script_exitAllModes(gesture, silent=False)
				return script
			
			char = None
			if hasattr(gesture, 'vkCode'):
				caps_lock = winUser.getKeyState(winUser.VK_CAPITAL) & 1
				shift_pressed = (winUser.getKeyState(winUser.VK_LSHIFT) & 0x8000) or (winUser.getKeyState(winUser.VK_RSHIFT) & 0x8000)
				char = self.thaiSorter.get_character_from_vk(gesture.vkCode, caps_lock, shift_pressed)
			
			if char and self.thaiSorter.is_thai_character(char):
				@wraps(self.script_announceThaiOrder)
				def script(gesture):
					self.script_announceThaiOrder(gesture, char)
				return script
			
			@wraps(self.script_noCommandInThaiSorter)
			def script(gesture):
				self.script_noCommandInThaiSorter(gesture)
			return script
		
		if keyName == "f1":
			return self.script_layeredCommandF1
		elif keyName == "f2":
			return self.script_layeredCommandF2
		elif keyName == "f3":
			return self.script_layeredCommandF3
		elif keyName == "f4":
			return self.script_layeredCommandF4
		elif keyName == "escape":
			@wraps(self.script_exitAllModes)
			def script(gesture):
				self.script_exitAllModes(gesture, silent=False)
			return script
		
		char = None
		if hasattr(gesture, 'vkCode'):
			caps_lock = winUser.getKeyState(winUser.VK_CAPITAL) & 1
			shift_pressed = (winUser.getKeyState(winUser.VK_LSHIFT) & 0x8000) or (winUser.getKeyState(winUser.VK_RSHIFT) & 0x8000)
			char = self.thaiSorter.get_character_from_vk(gesture.vkCode, caps_lock, shift_pressed)
		
		if char and self.thaiSorter.is_thai_character(char):
			@wraps(self.script_enterThaiSorterMode)
			def script(gesture):
				self.script_enterThaiSorterMode(gesture, char)
			return script
		
		@wraps(self.script_noCommandInLayeredMode)
		def script(gesture):
			self.script_noCommandInLayeredMode(gesture)
		return script

	@scriptHandler.script(
		description=_("Siam Square Mode"),
		category=scriptCategory,
		gesture="kb:control+f1"
	)
	def script_activateLayeredCommands(self, gesture):
		if self.inLayeredMode:
			self.script_exitAllModes(gesture, silent=False)
			return
			
		self.inLayeredMode = True
		self.inThaiSorterMode = False
		tones.beep(880, 100)

	@scriptHandler.script(
		description=_("Exit All Modes"),
		category=scriptCategory
	)
	def script_exitAllModes(self, gesture, silent=False):
		self.inLayeredMode = False
		self.inThaiSorterMode = False
		if not silent:
			tones.beep(100, 100)
		
	@scriptHandler.script(
		description=_("Enter Thai Sorter Mode"),
		category=scriptCategory
	)
	def script_enterThaiSorterMode(self, gesture, char):
		self.inThaiSorterMode = True
		result = self.thaiSorter.get_character_order(char)
		if result:
			ui.message(result)
		else:
			tones.beep(300, 50)
		
	@scriptHandler.script(
		description=_("Announce Thai Character Order"),
		category=scriptCategory
	)
	def script_announceThaiOrder(self, gesture, char):
		result = self.thaiSorter.get_character_order(char)
		if result:
			ui.message(result)
		else:
			tones.beep(300, 50)

	@scriptHandler.script(
		description=_("No Command in Thai Sorter Mode"),
		category=scriptCategory
	)
	def script_noCommandInThaiSorter(self, gesture):
		tones.beep(300, 50)

	@scriptHandler.script(
		description=_("No Command in Layered Mode"),
		category=scriptCategory
	)
	def script_noCommandInLayeredMode(self, gesture):
		tones.beep(120, 100)

	@scriptHandler.script(
		description=_("ความหมายคำ"),
		category=scriptCategory
	)
	def script_layeredCommandF1(self, gesture):
		selectedText = self.getWordAtCaret()
		if selectedText:
			self.siamSquareCore.get_definition(selectedText)
		else:
			ui.message(_("ไม่พบคำที่ตำแหน่งเคอร์เซอร์"))
		self.script_exitAllModes(gesture, silent=True)

	@scriptHandler.script(
		description=_("คำสะกดผิด คำใกล้เคียง"),
		category=scriptCategory
	)
	def script_layeredCommandF2(self, gesture):
		selectedText = self.getWordAtCaret()
		if not selectedText:
			ui.message(_("ไม่พบคำที่ตำแหน่งเคอร์เซอร์"))
			self.script_exitAllModes(gesture, silent=True)
			return

		suggestions = self.siamSquareCore.generate_suggestions(selectedText)
		if not suggestions:
			ui.message(_("ไม่พบคำแนะนำที่ใกล้เคียง"))
			self.script_exitAllModes(gesture, silent=True)
			return

		# Safe invocation using the correct class reference from siamSquareCore module
		def launch_dialog():
			try:
				if hasattr(gui.mainFrame, 'popupSettingsDialog'):
					gui.mainFrame.popupSettingsDialog(siamSquareCore.SuggestionsDialog, selectedText, suggestions, self.siamSquareCore)
				else:
					gui.mainFrame._popupSettingsDialog(siamSquareCore.SuggestionsDialog, selectedText, suggestions, self.siamSquareCore)
			except Exception as e:
				log.error(f"Error popup suggestions dialog: {e}")
				ui.message(_("ไม่สามารถเปิดหน้าต่างคำแนะนำได้"))

		wx.CallAfter(launch_dialog)
		self.script_exitAllModes(gesture, silent=True)

	@scriptHandler.script(
		description=_("สะกดคำ"),
		category=scriptCategory
	)
	def script_layeredCommandF3(self, gesture):
		selectedText = self.getWordAtCaret()
		if selectedText:
			self.siamSquareCore.spell_word(selectedText)
		else:
			ui.message(_("ไม่พบคำที่ตำแหน่งเคอร์เซอร์"))
		self.script_exitAllModes(gesture, silent=True)

	@scriptHandler.script(
		description=_("Siam Center"),
		category=scriptCategory
	)
	def script_layeredCommandF4(self, gesture):
		selectedText = self.getWordAtCaret()
		try:
			wx.CallAfter(self._showSiamCenterDialog, selectedText)
		except Exception as e:
			ui.message(_("ไม่สามารถเปิด Siam Center ได้: {}").format(str(e)))
		self.script_exitAllModes(gesture, silent=True)

	def _showSiamCenterDialog(self, selectedText):
		try:
			if hasattr(gui.mainFrame, 'popupSettingsDialog'):
				gui.mainFrame.popupSettingsDialog(siamCenter.SiamCenterDialog, selectedText, self.siamSquareCore)
			else:
				gui.mainFrame._popupSettingsDialog(siamCenter.SiamCenterDialog, selectedText, self.siamSquareCore)
			wx.CallLater(100, self._focusDialog)
		except Exception as e:
			ui.message(_("ไม่สามารถเปิด Siam Center ได้: {}").format(str(e)))

	def _focusDialog(self):
		try:
			dialog = wx.GetActiveWindow()
			if dialog and isinstance(dialog, siamCenter.SiamCenterDialog):
				dialog.Raise()
				dialog.SetFocus()
		except Exception:
			pass

	def getWordAtCaret(self):
		try:
			obj = api.getFocusObject()
			info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
			if info and not info.isCollapsed:
				text = info.text
				if text and text.strip():
					return text.strip()
		except Exception:
			pass
		
		try:
			obj = api.getFocusObject()
			info = obj.makeTextInfo(textInfos.POSITION_CARET)
			info.expand(textInfos.UNIT_WORD)
			text = info.text.strip()
			if text:
				return text
		except Exception:
			pass
		
		try:
			obj = api.getCaretObject()
			info = obj.makeTextInfo(textInfos.POSITION_CARET)
			info.expand(textInfos.UNIT_WORD)
			text = info.text.strip()
			if text:
				return text
		except Exception:
			pass
		
		try:
			obj = api.getFocusObject()
			if hasattr(obj, 'IAccessibleObject') and obj.IAccessibleObject:
				value = obj.IAccessibleObject.accValue(0)
				if value:
					lines = str(value).split('\r')
					for line in lines:
						if line.strip():
							return line.strip()
		except Exception:
			pass
		
		try:
			obj = api.getFocusObject()
			if hasattr(obj, 'value') and obj.value:
				value = str(obj.value)
				if value:
					lines = value.split('\r')
					for line in lines:
						if line.strip():
							return line.strip()
		except Exception:
			pass
		
		return None