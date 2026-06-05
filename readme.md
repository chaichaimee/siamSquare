<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>SiamSquare Thai Dictionary Add-on for NVDA</title>
<style>
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    padding: 20px;
    background-color: #f4f4f4;
}
.container {
    max-width: 800px;
    margin: auto;
    background: #fff;
    padding: 20px 40px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}
h1, h2, h3 {
    text-align: center;
}
b {
    font-weight: bold;
}
.section {
    margin-bottom: 30px;
}
.nvda-logo {
    display: block;
    margin: 0 auto 20px;
    width: 120px;
    height: auto;
}
.hotkey {
    background: #f8f9fa;
    border-left: 4px solid #3498db;
    padding: 15px;
    margin: 15px 0;
    border-radius: 0 4px 4px 0;
}
.tap-explanation {
    background: #e8f4fc;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}
.feature-item {
    margin: 15px 0;
    padding-left: 10px;
}
.note {
    background: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 12px;
    margin: 15px 0;
    border-radius: 0 4px 4px 0;
}
.footer-note {
    text-align: center;
    margin-top: 20px;
    font-size: 0.9em;
    color: #555;
}
</style>
</head>
<body>

<div class="container">

<div class="section">
    <img src="https://www.nvaccess.org/files/nvda/documentation/userGuide/images/nvda.ico" alt="NVDA Logo" class="nvda-logo">
    <h1>SiamSquare Thai Dictionary Add-on</h1>

<br>

<p style="text-align: center; font-size: 1.1em;">Navigate, understand, and master the Thai language with a fully accessible dictionary of over 30,000 words.</p>
</div>

<br>

<div class="section">
    <p style="text-align: center;"><b>Author:</b> Chai Chaimee</p>
    <p style="text-align: center;"><b>Repository:</b> <a href="https://github.com/chaichaimee/siamSquare">https://github.com/chaichaimee/siamSquare</a></p>
</div>

<hr>

<div class="section">
    <h2>What is SiamSquare?</h2>
    <p>SiamSquare is a professional-grade Thai dictionary add-on for NVDA. It provides instant access to more than 30,000 Thai words with their Thai definitions. The add-on is designed for students, writers, translators, educators, and anyone who works with the Thai language while relying on screen reader technology.</p>
    <p>Unlike generic online dictionaries, SiamSquare integrates directly into your workflow. You can look up word meanings, check spelling, listen to character-by-character spelling, add your own vocabulary entries, edit existing definitions, copy definitions to the clipboard, and manage a personal dictionary through the built-in Siam Center interface. All content is organized according to the standard Thai consonant order (ko kai to ho nokhuk).</p>
    <div class="note">
        <strong>Acknowledgement:</strong> SiamSquare is built upon linguistic data provided by <a href="https://kaikki.org">kaikki.org</a>. Their open linguistic resources make educational tools like this possible. We are grateful for their contribution to accessible Thai language learning.
    </div>
</div>

<br>

<div class="section">
    <h2>How the Layered Mode Works (Step by Step)</h2>
    <p>SiamSquare uses a two-step activation system to avoid conflicts with NVDA's native commands. This design keeps all dictionary functions separate from your everyday keystrokes.</p>
    
    <div class="tap-explanation">
        <strong>Step 1: Enter Siam Square Mode</strong><br>
        Press <strong>Control + F1</strong> simultaneously. A high-pitched beep confirms you are now in the layered command mode. While this mode is active, NVDA's standard keystrokes are temporarily suspended and replaced with SiamSquare's dictionary tools. This allows you to use simple keys like F1, F2, F3, F4 as dictionary shortcuts.
    </div>
    
    <div class="tap-explanation">
        <strong>Step 2: Execute Dictionary Commands</strong><br>
        While the layered mode is active (indicated by the beep), press any of the function keys or Thai characters to perform dictionary operations. You do not need to hold any modifier keys during this step.
    </div>
    
    <div class="tap-explanation">
        <strong>Step 3: Exit Layered Mode</strong><br>
        Press <strong>Escape</strong>. A short low beep confirms you have exited. NVDA returns to its normal keyboard behavior. You can also exit automatically after any dictionary command completes.
    </div>
</div>

<div class="section">
    <h2>Complete Hotkey Reference</h2>
    
    <div class="hotkey">
        <strong>Control + F1</strong><br>
        Toggle Siam Square layered mode on or off. This is the master switch for all dictionary features. A high beep indicates mode activated; a low beep indicates deactivation.
    </div>
    
    <div class="hotkey">
        <strong>F1 (while in layered mode)</strong><br>
        Look up definition. The add-on extracts the word at the caret position or any selected text, then searches the dictionary. If found, the definition is spoken immediately. If no word is found at the cursor, a message prompts you to position the cursor on a word.
    </div>
    
    <div class="hotkey">
        <strong>F2 (while in layered mode)</strong><br>
        Spelling suggestions. When the cursor is on a potentially misspelled word, SiamSquare generates a list of similar words from its 30,000-entry database. A dialog appears showing the most likely correct spellings. Select any suggestion, and the add-on will automatically replace the original misspelled word with your chosen correction.
    </div>
    
    <div class="hotkey">
        <strong>F3 (while in layered mode)</strong><br>
        Spell word character by character. Each character is spoken individually with a pause between letters. This is particularly useful for proper nouns, technical terms, or any word where precise spelling matters. The output includes consonants, vowels, and tone marks in sequence.
    </div>
    
    <div class="hotkey">
        <strong>F4 (while in layered mode)</strong><br>
        Open Siam Center dictionary manager. This is the full interface where you can browse words by initial consonant category (ko kai through ho nokhuk), view definitions, add new entries, edit existing ones, delete entries, and copy words or definitions to the clipboard.
    </div>
    
    <div class="hotkey">
        <strong>Escape (while in layered mode or Thai sorter mode)</strong><br>
        Exit all active modes immediately. Returns NVDA to standard operation without any confirmation dialog.
    </div>
    
    <div class="hotkey">
        <strong>Any Thai character (ko kai, kho khwai, etc.) while in layered mode</strong><br>
        Enter Thai sorter mode. The add-on announces the position of that character in the standard Thai alphabet order. For example, pressing "ก" announces "ก 1", "ฮ" announces "ฮ 42". This also works for vowels and tone marks. Press Escape to exit the sorter mode.
    </div>
</div>

<div class="section">
    <h2>Detailed Feature Breakdown</h2>
    
    <h3>1. Definition Lookup (F1)</h3>
    <p>The definition engine extracts text from the current cursor position. It respects text selections first: if you have highlighted text, that exact string is used. If no selection exists, the add-on expands to the word boundary at the caret. It also falls back to retrieving the value property of editable controls (like input fields or spreadsheet cells) when standard text navigation fails. Each definition is cleaned of JSON formatting artifacts and presented as plain, readable Thai.</p>
    
    <h3>2. Spelling Correction Engine (F2)</h3>
    <p>When you press F2 on a word, SiamSquare compares it against every entry in the dictionary. The matching algorithm prioritizes longer prefix matches: if the misspelled word shares the first four characters with a dictionary word, that candidate rises to the top. If no four-character match exists, it falls back to two-character prefix matching. The system then displays up to ten suggestions in a dialog. Upon selection, the replacement is performed using either a character-by-character simulation (for single words) or clipboard-based paste (for multi-word phrases). The original clipboard content is restored after the operation.</p>
    
    <h3>3. Character-by-Character Spelling (F3)</h3>
    <p>Unlike simple letter reading, SiamSquare inserts explicit separators between each character. This forces the speech synthesizer to pause slightly, making vowel and tone mark distinctions clearer. For example, the word "สวัสดี" is spoken as "ส, , ว, , ั, , ส, , ด, , ี" with clear breaks. This is especially valuable for learners who need to distinguish between similar-looking consonants or vowel diacritics.</p>
    
    <h3>4. Siam Center Dictionary Manager (F4)</h3>
    <p>The Siam Center is a complete wxPython-based graphical interface that operates entirely with keyboard navigation. It consists of three synchronized panels:</p>
    <ul>
        <li><strong>Category panel:</strong> Lists all 44 Thai initial consonants (ก, ข, ค, ฆ, ง, จ, ฉ, ช, ซ, ฌ, ญ, ฎ, ฏ, ฐ, ฑ, ฒ, ณ, ด, ต, ถ, ท, ธ, น, บ, ป, ผ, ฝ, พ, ฟ, ภ, ม, ย, ร, ล, ว, ศ, ษ, ส, ห, ฬ, อ, ฮ). Selecting a category filters the word list.</li>
        <li><strong>Word list:</strong> Displays all dictionary entries whose first consonant (after optional leading vowels like เ, แ, โ, ใ, ไ) matches the selected category. Words are sorted alphabetically. You can type Thai characters to jump directly to entries starting with that prefix.</li>
        <li><strong>Definition panel:</strong> Shows all definitions associated with the selected word. Multiple definitions per word are supported.</li>
    </ul>
    <p>From within Siam Center, you can add new words (specifying both word and definition), edit existing entries, and copy individual definitions or entire word-definition pairs to the clipboard. All user modifications are saved immediately to the user configuration directory, ensuring they survive add-on updates.</p>
    
    <h3>5. Personal Dictionary Persistence</h3>
    <p>User-added words are never overwritten during add-on updates. SiamSquare stores custom entries in <code>%APPDATA%\nvda\ChaiChaimee\SiamSquare\dictionary</code> (Windows) or the equivalent NVDA user config path on other operating systems. The data is organized as separate JSON files per consonant category, following the same structure as the base dictionary. When loading, the add-on merges base dictionary entries with user entries, giving user definitions priority in case of conflicts.</p>
    
    <h3>6. Thai Sorter Mode (Character Order Reference)</h3>
    <p>While in layered mode, pressing any Thai character activates a specialized mode where SiamSquare announces that character's ordinal position in the standard sorting order. This covers four character groups:</p>
    <ul>
        <li><strong>Consonants (44 characters):</strong> Position 1 (ก) through 42 (ฮ). Note that ฃ and ฅ are excluded as they are obsolete.</li>
        <li><strong>Vowels (18 characters):</strong> Includes short/long vowels and vowel-like symbols such as ะ, า, ิ, ี, ึ, ื, ุ, ู, เ, แ, โ, ใ, ไ, ๅ, ํ, ั, ำ, ๆ.</li>
        <li><strong>Tone marks (5 characters):</strong> ่, ้, ๊, ๋, ็.</li>
        <li><strong>Other marks (6 characters):</strong> ฯ, ๎, ์, ๚, ๛.</li>
    </ul>
    <p>This feature is valuable for students learning the Thai alphabet order, for sorting Thai text manually, or for anyone who needs to reference the traditional sequence without memorization.</p>
    
    <h3>7. Clipboard Safety and Restoration</h3>
    <p>When SiamSquare performs a word replacement using clipboard paste (Shift+Insert or WM_PASTE), it automatically saves the existing clipboard content before the operation. After a 150-millisecond delay, the original clipboard content is restored. This prevents accidental data loss when you have important text stored in the clipboard.</p>
</div>

<div class="section">
    <h2>Practical Use Cases</h2>
    
    <p><strong>For students reading Thai textbooks or web pages:</strong> Place the cursor on any unfamiliar word. Press Control+F1, then F1. The definition is spoken without leaving your reading context. No need to switch to another application or type the word manually.</p>
    
    <p><strong>For writers and editors:</strong> When you suspect a spelling error, press Control+F1 followed by F2. The suggestion dialog appears. Navigate the list with up/down arrows. Press Enter to replace the misspelled word with the correct version. The replacement happens inline, preserving your document's formatting.</p>
    
    <p><strong>For language learners building vocabulary:</strong> Open Siam Center with Control+F1 then F4. Browse words by consonant category. When you find a word you want to study, press the context menu key (or right-click) on the definition panel to copy the word and definition to the clipboard. Paste it into your flashcard application.</p>
    
    <p><strong>For technical documentation where precise spelling is critical:</strong> Place the cursor on a technical term. Press Control+F1 then F3. The add-on spells each character clearly, allowing you to verify that every vowel and tone mark is correct. This is especially useful for API names, medical terms, or legal documents.</p>
    
    <p><strong>For teachers creating custom vocabulary lists:</strong> Use the Add Word function in Siam Center to enter domain-specific terminology with custom definitions. These entries are saved immediately and become searchable via the F1 lookup. You can share your JSON dictionary files with students by copying the user dictionary folder.</p>
</div>

<div class="section">
    <h2>Technical Notes for Advanced Users</h2>
    <p>SiamSquare is compatible with NVDA versions 2019.3 and later (Python 3). The dictionary is structured as individual JSON files per initial consonant. The base dictionary is read-only and stored inside the add-on installation directory. User modifications are written to the NVDA user configuration directory, preserving changes across add-on updates. The add-on automatically removes invalid JSON files (those not matching the expected consonant filenames) during initialization to prevent corruption.</p>
    <p>When looking up words, the add-on attempts multiple methods to extract text: from the current selection first, then from the caret's word boundary, then from the focused object's value property. This ensures compatibility with a wide range of applications including web browsers, Microsoft Word, Notepad, editable text fields, and even some custom controls.</p>
</div>

<br>

<div class="footer-note">
<p>Copyright (C) 2026 Chai Chaimee. Licensed under the GNU General Public License. You are free to use, modify, and distribute this add-on under the terms of the GPL.</p>
<p>Project repository: <a href="https://github.com/chaichaimee/siamSquare">https://github.com/chaichaimee/siamSquare</a><br>
Language data source: <a href="https://kaikki.org">https://kaikki.org</a> — Open linguistic resources for public benefit.</p>
</div>

</div>
</body>
</html>