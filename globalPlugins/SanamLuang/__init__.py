# __init__.py
# Copyright (C) 2025 ['CHAI CHAIMEE]
# Licensed under GNU General Public License. See COPYING.txt for details.

import addonHandler
import globalPluginHandler
import globalVars
import gui
import os
import json
import wx
import speech
import ui
import re
import api
import textInfos
import time
from scriptHandler import script
from logHandler import log

addonHandler.initTranslation()

# Path to configuration file
_configPath = globalVars.appArgs.configPath
_configFile = os.path.join(_configPath, "SanamLuang.json")

# Path to addon directory for default dictionary
_addonDir = os.path.dirname(os.path.abspath(__file__))
_defaultDictPath = os.path.join(_addonDir, "dictionary", "SanamLuang.json")

# Constants for word data structure
WORD_VALUE = "value"
WORD_IS_REGEX = "is_regex"
WORD_REPLACEMENT = "replacement"

class SanamLuangConfig:
    """Configuration manager for SanamLuang addon with JSON file storage"""
   
    def __init__(self):
        self.entries = []  # List of correction entries
        self.enabled = True  # Addon enabled state
        self._load_config()
   
    def _load_default_dictionary(self):
        """Load default dictionary from addon directory or use built-in defaults"""
        default_entries = []
       
        try:
            if os.path.exists(_defaultDictPath):
                with open(_defaultDictPath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                   
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                if "value" in item and "is_regex" in item:
                                    default_entries.append({
                                        WORD_VALUE: item["value"],
                                        WORD_IS_REGEX: item["is_regex"],
                                        WORD_REPLACEMENT: item.get("replacement", "")
                                    })
                                else:
                                    for key, value in item.items():
                                        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], list):
                                            replacement = value[0][0] if value[0] else ""
                                        else:
                                            replacement = value if isinstance(value, str) else ""
                                       
                                        default_entries.append({
                                            WORD_VALUE: key,
                                            WORD_IS_REGEX: False,
                                            WORD_REPLACEMENT: replacement
                                        })
                            elif isinstance(item, str):
                                default_entries.append({
                                    WORD_VALUE: item,
                                    WORD_IS_REGEX: False,
                                    WORD_REPLACEMENT: ""
                                })
            else:
                log.warning(f"Default dictionary not found at: {_defaultDictPath}")
                # Use built-in default entries
                default_entries = [
                    {WORD_VALUE: "ำ่", WORD_IS_REGEX: False, WORD_REPLACEMENT: "่ำ"},
                    {WORD_VALUE: "ำ้", WORD_IS_REGEX: False, WORD_REPLACEMENT: "้ำ"},
                    {WORD_VALUE: "เเ", WORD_IS_REGEX: False, WORD_REPLACEMENT: "แ"},
                    {WORD_VALUE: "ํา", WORD_IS_REGEX: False, WORD_REPLACEMENT: "ำ"},
                    {WORD_VALUE: "ํ่า", WORD_IS_REGEX: False, WORD_REPLACEMENT: "่ำ"},
                    {WORD_VALUE: "ํ้า", WORD_IS_REGEX: False, WORD_REPLACEMENT: "้ำ"}
                ]
       
        except Exception as e:
            log.error(f"Error loading default dictionary: {e}")
            # Fallback to built-in default entries
            default_entries = [
                {WORD_VALUE: "ำ่", WORD_IS_REGEX: False, WORD_REPLACEMENT: "่ำ"},
                {WORD_VALUE: "ำ้", WORD_IS_REGEX: False, WORD_REPLACEMENT: "้ำ"},
                {WORD_VALUE: "เเ", WORD_IS_REGEX: False, WORD_REPLACEMENT: "แ"},
                {WORD_VALUE: "ํา", WORD_IS_REGEX: False, WORD_REPLACEMENT: "ำ"},
                {WORD_VALUE: "ํ่า", WORD_IS_REGEX: False, WORD_REPLACEMENT: "่ำ"},
                {WORD_VALUE: "ํ้า", WORD_IS_REGEX: False, WORD_REPLACEMENT: "้ำ"}
            ]
       
        return default_entries
   
    def _load_config(self):
        """Load configuration from user config file"""
        try:
            if os.path.exists(_configFile):
                with open(_configFile, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Load entries
                    if isinstance(data, dict):
                        if "entries" in data:
                            self.entries = data["entries"]
                        else:
                            self.entries = []
                        
                        # Load enabled state
                        if "enabled" in data:
                            self.enabled = data["enabled"]
                        else:
                            self.enabled = True
                    else:
                        self.entries = data if isinstance(data, list) else []
                        self.enabled = True
            else:
                # Load default dictionary if config doesn't exist
                self.entries = self._load_default_dictionary()
                self.enabled = True
                self._save_config()
        except Exception as e:
            log.error(f"Error loading config: {e}")
            self.entries = self._load_default_dictionary()
            self.enabled = True
   
    def _save_config(self):
        """Save configuration to user config file"""
        try:
            data = {
                "entries": self.entries,
                "enabled": self.enabled,
                "version": "1.1"
            }
            
            with open(_configFile, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            log.error(f"Error saving config: {e}")
            return False
   
    def get_display_word(self, word_data):
        """Helper to create display string for word in listbox"""
        value = word_data.get(WORD_VALUE, "")
        is_regex = word_data.get(WORD_IS_REGEX, False)
        replacement = word_data.get(WORD_REPLACEMENT, "")
       
        if is_regex:
            if replacement:
                return f"[{_('Regex')}] {value}  {replacement}"
            else:
                return f"[{_('Regex')}] {value}"
        else:
            if replacement:
                return f"{value}  {replacement}"
            else:
                return value
   
    def get_entries(self):
        return self.entries
   
    def add_entry(self, pattern, is_regex, replacement=""):
        new_entry = {WORD_VALUE: pattern, WORD_IS_REGEX: is_regex, WORD_REPLACEMENT: replacement}
       
        if not any(d[WORD_VALUE] == pattern and d[WORD_IS_REGEX] == is_regex for d in self.entries):
            self.entries.append(new_entry)
            self.entries.sort(key=lambda x: x[WORD_VALUE].lower())
            return self._save_config()
        return False
   
    def update_entry(self, old_entry, new_pattern, new_is_regex, new_replacement=""):
        try:
            index = -1
            for i, d in enumerate(self.entries):
                if d[WORD_VALUE] == old_entry[WORD_VALUE] and d[WORD_IS_REGEX] == old_entry[WORD_IS_REGEX]:
                    index = i
                    break
           
            if index != -1:
                new_entry = {WORD_VALUE: new_pattern, WORD_IS_REGEX: new_is_regex, WORD_REPLACEMENT: new_replacement}
               
                if any(d[WORD_VALUE] == new_pattern and d[WORD_IS_REGEX] == new_is_regex and i != index
                       for i, d in enumerate(self.entries)):
                    self.entries.pop(index)
                else:
                    self.entries[index] = new_entry
               
                self.entries.sort(key=lambda x: x[WORD_VALUE].lower())
                return self._save_config()
        except Exception as e:
            log.error(f"Error updating entry: {e}")
        return False
   
    def remove_entry(self, entry):
        try:
            self.entries.remove(entry)
            return self._save_config()
        except ValueError:
            log.error("SanamLuang Config: Entry not found for removal.")
        return False
   
    def reset_to_defaults(self):
        self.entries = self._load_default_dictionary()
        return self._save_config()
    
    def set_enabled(self, enabled):
        """Set addon enabled state"""
        self.enabled = enabled
        return self._save_config()
    
    def get_enabled(self):
        """Get addon enabled state"""
        return self.enabled

class SanamLuangDialog(wx.Dialog):
    def __init__(self, parent, config):
        super(SanamLuangDialog, self).__init__(
            parent,
            title="การตั้งค่าสนามหลวง - แก้ไขคำไทย",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        self.config = config
        self.editing_entry = None
        self.entries = self.config.get_entries()
        self.initUI()
        self.Centre()
        
        # Bind ESC key to close dialog
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        wx.CallAfter(self.entriesList.SetFocus)

    def on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.Close()
        event.Skip()

    def initUI(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # Status label
        statusSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.statusLabel = wx.StaticText(self, label="")
        statusSizer.Add(self.statusLabel, 0, wx.ALL, 5)
        mainSizer.Add(statusSizer, 0, wx.ALL, 5)
        self._update_status()
       
        # Listbox for entries
        listBoxLabel = wx.StaticText(self, label="รายการแก้ไขคำ:")
        mainSizer.Add(listBoxLabel, 0, wx.ALL, 5)
       
        self.entriesList = wx.ListBox(self, style=wx.LB_SINGLE | wx.LB_HSCROLL)
        self.entriesList.SetMinSize((500, 250))
        self._refresh_entries_list()
        mainSizer.Add(self.entriesList, 1, wx.EXPAND | wx.ALL, 5)
       
        # Buttons for entry management
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
       
        self.addButton = wx.Button(self, label="&เพิ่ม")
        self.addButton.Bind(wx.EVT_BUTTON, self.on_add)
        buttonSizer.Add(self.addButton, 0, wx.RIGHT, 5)
       
        self.editButton = wx.Button(self, label="&แก้ไข")
        self.editButton.Bind(wx.EVT_BUTTON, self.on_edit)
        buttonSizer.Add(self.editButton, 0, wx.RIGHT, 5)
       
        self.removeButton = wx.Button(self, label="&ลบ")
        self.removeButton.Bind(wx.EVT_BUTTON, self.on_remove)
        buttonSizer.Add(self.removeButton, 0, wx.RIGHT, 5)
       
        self.resetButton = wx.Button(self, label="&คืนค่าเริ่มต้น")
        self.resetButton.Bind(wx.EVT_BUTTON, self.on_reset)
        buttonSizer.Add(self.resetButton, 0, wx.RIGHT, 5)
       
        # Close button
        closeButton = wx.Button(self, wx.ID_CLOSE, label="&ปิด")
        closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Close())
        buttonSizer.Add(closeButton, 0, wx.ALIGN_CENTER | wx.ALL, 10)
       
        mainSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
       
        self.SetSizerAndFit(mainSizer)
        self.SetSize((650, 450))

    def _update_status(self):
        """Update status label"""
        if self.config.get_enabled():
            self.statusLabel.SetLabel("สถานะ: สนามหลวงเปิด")
            self.statusLabel.SetForegroundColour(wx.Colour(0, 128, 0))  # Green
        else:
            self.statusLabel.SetLabel("สถานะ: สนามหลวงปิด")
            self.statusLabel.SetForegroundColour(wx.Colour(255, 0, 0))  # Red

    def _refresh_entries_list(self):
        self.entries = self.config.get_entries()
        self.entriesList.Clear()
        for entry in self.entries:
            self.entriesList.Append(self.config.get_display_word(entry))

    def on_add(self, event):
        dlg = EntryDialog(self, self.config)
        if dlg.ShowModal() == wx.ID_OK:
            pattern = dlg.patternValue.GetValue()
            is_regex = dlg.regexCheckbox.GetValue()
            replacement = dlg.replacementValue.GetValue()
           
            if pattern:
                if self.config.add_entry(pattern, is_regex, replacement):
                    self._refresh_entries_list()
                    ui.message("เพิ่มรายการเรียบร้อย")
                else:
                    wx.MessageBox("มีรายการนี้อยู่แล้ว", "ผิดพลาด", wx.OK | wx.ICON_ERROR)
        dlg.Destroy()

    def on_edit(self, event):
        selection = self.entriesList.GetSelection()
        if selection == wx.NOT_FOUND:
            wx.MessageBox("กรุณาเลือกรายการที่จะแก้ไข", "ผิดพลาด", wx.OK | wx.ICON_ERROR)
            return
       
        old_entry = self.entries[selection]
        dlg = EntryDialog(self, self.config, old_entry)
        if dlg.ShowModal() == wx.ID_OK:
            new_pattern = dlg.patternValue.GetValue()
            new_is_regex = dlg.regexCheckbox.GetValue()
            new_replacement = dlg.replacementValue.GetValue()
           
            if new_pattern:
                if self.config.update_entry(old_entry, new_pattern, new_is_regex, new_replacement):
                    self._refresh_entries_list()
                    ui.message("แก้ไขรายการเรียบร้อย")
                else:
                    wx.MessageBox("แก้ไขรายการไม่สำเร็จ", "ผิดพลาด", wx.OK | wx.ICON_ERROR)
        dlg.Destroy()

    def on_remove(self, event):
        selection = self.entriesList.GetSelection()
        if selection == wx.NOT_FOUND:
            wx.MessageBox("กรุณาเลือกรายการที่จะลบ", "ผิดพลาด", wx.OK | wx.ICON_ERROR)
            return
       
        if wx.MessageBox("แน่ใจว่าต้องการลบรายการนี้?", "ยืนยัน", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            entry = self.entries[selection]
            if self.config.remove_entry(entry):
                self._refresh_entries_list()
                ui.message("ลบรายการเรียบร้อย")

    def on_reset(self, event):
        if wx.MessageBox("แน่ใจว่าต้องการคืนค่ารายการเริ่มต้น? รายการที่แก้ไขทั้งหมดจะหายไป",
                        "ยืนยัน", wx.YES_NO | wx.ICON_WARNING) == wx.YES:
            if self.config.reset_to_defaults():
                self._refresh_entries_list()
                ui.message("คืนค่ารายการเริ่มต้นเรียบร้อย")

class EntryDialog(wx.Dialog):
    def __init__(self, parent, config, entry=None):
        super(EntryDialog, self).__init__(parent, title="เพิ่ม/แก้ไข รายการ")
        self.config = config
        self.entry = entry
        self.initUI()
        
        # Bind ESC key to close dialog
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)

    def on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.Close()
        event.Skip()

    def initUI(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
       
        # Pattern field
        patternLabel = wx.StaticText(self, label="รูปแบบคำ (คำหรือนิพจน์ปรกติ):")
        mainSizer.Add(patternLabel, 0, wx.ALL, 5)
       
        self.patternValue = wx.TextCtrl(self)
        mainSizer.Add(self.patternValue, 0, wx.EXPAND | wx.ALL, 5)
       
        # Regex checkbox
        self.regexCheckbox = wx.CheckBox(self, label="รูปแบบนี้เป็นนิพจน์ปรกติ")
        mainSizer.Add(self.regexCheckbox, 0, wx.ALL, 5)
       
        # Replacement field
        replacementLabel = wx.StaticText(self, label="คำที่แทนที่ (ปล่อยว่างเพื่อลบ):")
        mainSizer.Add(replacementLabel, 0, wx.ALL, 5)
       
        self.replacementValue = wx.TextCtrl(self)
        mainSizer.Add(self.replacementValue, 0, wx.EXPAND | wx.ALL, 5)
       
        # Buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
       
        okButton = wx.Button(self, wx.ID_OK, label="&ตกลง")
        okButton.SetDefault()
        buttonSizer.Add(okButton, 0, wx.RIGHT, 5)
       
        cancelButton = wx.Button(self, wx.ID_CANCEL, label="&ยกเลิก")
        buttonSizer.Add(cancelButton, 0)
       
        mainSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
       
        self.SetSizerAndFit(mainSizer)
       
        # Populate fields if editing
        if self.entry:
            self.patternValue.SetValue(self.entry.get(WORD_VALUE, ""))
            self.regexCheckbox.SetValue(self.entry.get(WORD_IS_REGEX, False))
            self.replacementValue.SetValue(self.entry.get(WORD_REPLACEMENT, ""))

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = "SanamLuang"
   
    def __init__(self):
        super(GlobalPlugin, self).__init__()
        self.config = SanamLuangConfig()
        self._original_process_text = None
        self._last_gesture_time = 0
        self._double_tap_threshold = 0.5  # 0.5 seconds for double-tap
        self._single_tap_timer = None
        self._single_tap_pending = False
       
        # Hook into speech processing
        self._hook_speech()
        log.info("SanamLuang loaded with entries: %s", self.config.get_entries())
   
    def _hook_speech(self):
        """Hook into the speech processing chain"""
        if hasattr(speech, "speech"):
            self._original_process_text = speech.speech.processText
            speech.speech.processText = self._process_text_hook
        else:
            self._original_process_text = speech.processText
            speech.processText = self._process_text_hook
   
    def _unhook_speech(self):
        """Unhook from speech processing"""
        if self._original_process_text:
            if hasattr(speech, "speech"):
                speech.speech.processText = self._original_process_text
            else:
                speech.processText = self._original_process_text
            self._original_process_text = None

    def _process_text_hook(self, locale, text, symbolLevel=None, **kwargs):
        """Process text through correction entries before speaking"""
        if not self.config.get_enabled():
            return self._original_process_text(locale, text, symbolLevel, **kwargs)
       
        entries = self.config.get_entries()
        if not entries:
            return self._original_process_text(locale, text, symbolLevel, **kwargs)
       
        literal_entries = []
        regex_patterns = []
       
        for entry in entries:
            pattern = entry.get(WORD_VALUE)
            is_regex = entry.get(WORD_IS_REGEX, False)
            replacement = entry.get(WORD_REPLACEMENT, "")
            if pattern:
                if is_regex:
                    regex_patterns.append((pattern, replacement))
                else:
                    literal_entries.append((pattern, replacement))
       
        # Process literal entries (longest first to avoid conflicts)
        literal_entries_sorted = sorted(literal_entries, key=lambda x: len(x[0]), reverse=True)
        for pattern, replacement in literal_entries_sorted:
            text = text.replace(pattern, replacement)
       
        # Process regex entries
        for pattern, replacement in regex_patterns:
            try:
                text = re.sub(pattern, replacement, text)
            except re.error as e:
                log.error(f"SanamLuang: Invalid regex skipped: '{pattern}'. Error: {e}")
       
        return self._original_process_text(locale, text, symbolLevel, **kwargs)

    def _apply_corrections(self, text):
        """Apply all corrections to text without checking for changes first"""
        # Always apply corrections regardless of enabled state for text replacement
        entries = self.config.get_entries()
        corrected_text = text
       
        if entries:
            literal_entries = []
            regex_patterns = []
           
            for entry in entries:
                pattern = entry.get(WORD_VALUE)
                is_regex = entry.get(WORD_IS_REGEX, False)
                replacement = entry.get(WORD_REPLACEMENT, "")
                if pattern:
                    if is_regex:
                        regex_patterns.append((pattern, replacement))
                    else:
                        literal_entries.append((pattern, replacement))
           
            # Process literal entries (longest first to avoid conflicts)
            literal_entries_sorted = sorted(literal_entries, key=lambda x: len(x[0]), reverse=True)
            for pattern, replacement in literal_entries_sorted:
                corrected_text = corrected_text.replace(pattern, replacement)
           
            # Process regex entries
            for pattern, replacement in regex_patterns:
                try:
                    corrected_text = re.sub(pattern, replacement, corrected_text)
                except re.error as e:
                    log.error(f"SanamLuang: Invalid regex skipped: '{pattern}': {e}")
       
        return corrected_text

    def _replace_text_in_document(self, obj, textInfo, corrected_text):
        """Replace text in document using clipboard method without external dependencies"""
        try:
            # Backup current clipboard content using NVDA API
            import api
            clipboard_backup = api.getClipData()
        except:
            clipboard_backup = None
        
        try:
            # Copy corrected text to clipboard using NVDA API
            api.copyToClip(corrected_text)
            time.sleep(0.1)  # Small delay for clipboard
            
            # Update selection and paste
            textInfo.updateSelection()
            
            # Use NVDA's keyboard input gesture for Ctrl+V
            from keyboardHandler import KeyboardInputGesture
            KeyboardInputGesture.fromName("control+v").send()
            
            # Restore clipboard if we backed it up
            if clipboard_backup:
                # Use core.callLater to restore clipboard after paste
                import core
                core.callLater(300, lambda: api.copyToClip(clipboard_backup))
                
            return True
                
        except Exception as e:
            log.error(f"Error replacing text: {e}")
            # Fallback: try to set the text directly
            try:
                # Try to set the text directly if possible
                textInfo.updateSelection()
                # For editable text controls, try to set the text
                if hasattr(obj, 'value'):
                    obj.value = corrected_text
                    return True
            except Exception as e2:
                log.error(f"Fallback replace also failed: {e2}")
                return False

    def _toggle_addon(self):
        """Toggle addon enabled state"""
        new_state = not self.config.get_enabled()
        self.config.set_enabled(new_state)
        
        if new_state:
            ui.message("สนามหลวงเปิด")
        else:
            ui.message("สนามหลวงปิด")
        
        log.info(f"SanamLuang toggled to {'enabled' if new_state else 'disabled'}")

    def _execute_single_tap_action(self):
        """Execute the single tap action (check text selection and act)"""
        # Reset the pending flag
        self._single_tap_pending = False
        
        # Check for text selection
        try:
            # Get focused object
            obj = api.getFocusObject()
            
            # Try to get selected text
            try:
                textInfo = obj.makeTextInfo(textInfos.POSITION_SELECTION)
                if textInfo.isCollapsed:
                    # No text selected - open settings
                    log.info("No text selected, opening settings")
                    wx.CallAfter(self.open_settings)
                    return
                
                # We have selected text - get it
                original_text = textInfo.text
                if not original_text:
                    ui.message("ไม่พบข้อความที่เลือก")
                    log.info("No text found in selection")
                    return
                
                log.info(f"Original text: {repr(original_text)}")
                log.info(f"Original text length: {len(original_text)}")
                
                # Apply corrections directly without checking first
                corrected_text = self._apply_corrections(original_text)
                
                log.info(f"Corrected text: {repr(corrected_text)}")
                
                # Check if text has changed
                if corrected_text == original_text:
                    ui.message("ไม่พบคำที่ต้องแก้ไขในข้อความที่เลือก")
                    return
                
                # Replace text in document
                if self._replace_text_in_document(obj, textInfo, corrected_text):
                    ui.message("แก้ไขข้อความเรียบร้อย")
                else:
                    ui.message("ไม่สามารถแก้ไขข้อความได้")
                    
            except Exception as e:
                log.error(f"Error accessing text: {e}")
                # If we can't access text, open settings
                wx.CallAfter(self.open_settings)
                
        except Exception as e:
            log.error(f"Error in single tap action: {e}")
            ui.message("เกิดข้อผิดพลาด")

    @script(
        description="เปิดการตั้งค่าสนามหลวง (ไม่มีข้อความที่เลือก) หรือแทนที่ข้อความที่เลือก หรือดับเบิลแทปเพื่อเปิด/ปิดสนามหลวง",
        gesture="kb:NVDA+shift+F4"
    )
    def script_main(self, gesture):
        """Main script: check for double-tap, text selection and act accordingly"""
        current_time = time.time()
        
        # Check for double-tap
        if current_time - self._last_gesture_time < self._double_tap_threshold:
            # Double-tap detected - cancel any pending single tap timer
            if self._single_tap_timer and self._single_tap_timer.IsRunning():
                self._single_tap_timer.Stop()
                self._single_tap_timer = None
                log.info("Double-tap: cancelled pending single-tap timer")
            
            # Toggle addon
            self._toggle_addon()
            
            # Reset last gesture time
            self._last_gesture_time = 0
            return
        
        # Update last gesture time
        self._last_gesture_time = current_time
        
        # Cancel any existing timer
        if self._single_tap_timer and self._single_tap_timer.IsRunning():
            self._single_tap_timer.Stop()
            self._single_tap_timer = None
        
        # Schedule single tap action after double-tap threshold
        self._single_tap_timer = wx.CallLater(int(self._double_tap_threshold * 1000), self._execute_single_tap_action)

    def open_settings(self):
        """Open settings dialog"""
        try:
            gui.mainFrame.prePopup()
            dlg = SanamLuangDialog(gui.mainFrame, self.config)
            dlg.ShowModal()
            dlg.Destroy()
        finally:
            gui.mainFrame.postPopup()

    def terminate(self):
        """Clean up when addon is disabled"""
        # Cancel any pending timer
        if self._single_tap_timer and self._single_tap_timer.IsRunning():
            self._single_tap_timer.Stop()
            self._single_tap_timer = None
        
        self._unhook_speech()
        super(GlobalPlugin, self).terminate()
