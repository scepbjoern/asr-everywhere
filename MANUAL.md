# ASR Everywhere - Benutzerhandbuch / User Manual

Eine vollständige Anleitung zur Bedienung von ASR Everywhere.

A complete guide for using ASR Everywhere.

---

## Inhaltsverzeichnis / Table of Contents

1. [Einführung / Introduction](#einführung--introduction)
2. [Installation](#installation)
3. [Erste Schritte / Getting Started](#erste-schritte--getting-started)
4. [System Tray Menü / System Tray Menu](#system-tray-menü--system-tray-menu)
5. [Einstellungen / Settings](#einstellungen--settings)
6. [Sprachsteuerung / Voice Commands](#sprachsteuerung--voice-commands)
7. [Wörterbuch / Dictionary](#wörterbuch--dictionary)
8. [Provider und Modelle / Providers and Models](#provider-und-modelle--providers-and-models)
9. [Tipps und Tricks / Tips and Tricks](#tipps-und-tricks--tips-and-tricks)
10. [Fehlerbehebung / Troubleshooting](#fehlerbehebung--troubleshooting)

---

## Einführung / Introduction

### Deutsch

**ASR Everywhere** ist eine Windows-Desktop-Anwendung für sprachgesteuerte Texteingabe. Drücken Sie eine Tastenkombination, sprechen Sie Ihren Text, und er wird automatisch an der Cursorposition eingefügt - in jeder Anwendung.

**Hauptfunktionen:**
- Systemweite Sprach-zu-Text-Diktierung
- Mehrere ASR-Anbieter (OpenAI, Together.ai, Hugging Face, lokal)
- Optionale LLM-Nachbearbeitung für bessere Textqualität
- Sprachbefehle für Zeichensetzung und Formatierung
- Wörterbuch für Fachbegriffe und Eigennamen
- Automatischer Start mit Windows

### English

**ASR Everywhere** is a Windows desktop application for voice-to-text dictation. Press a hotkey, speak your text, and it's automatically inserted at the cursor position - in any application.

**Key Features:**
- System-wide speech-to-text dictation
- Multiple ASR providers (OpenAI, Together.ai, Hugging Face, local)
- Optional LLM post-processing for better text quality
- Voice commands for punctuation and formatting
- Dictionary for technical terms and proper nouns
- Auto-start with Windows

---

## Installation

### Option 1: Installer (Empfohlen für Endanwender)

1. Laden Sie `asr-everywhere-setup.exe` von der [Releases-Seite](https://github.com/scepbjoern/asr-everywhere/releases) herunter
2. Führen Sie den Installer aus
3. Starten Sie die Anwendung über das Startmenü oder Desktop-Verknüpfung

### Option 2: PyPI (Für Python-Benutzer)

```powershell
pip install asr-everywhere
asr-everywhere
```

### Option 3: Aus dem Quellcode

```powershell
git clone https://github.com/scepbjoern/asr-everywhere.git
cd asr-everywhere
pip install -e .
python -m asr_everywhere
```

---

## Erste Schritte / Getting Started

### Schritt 1: Anwendung starten

Nach der Installation erscheint ein Mikrofon-Symbol im System Tray (neben der Uhr).

### Schritt 2: API-Schlüssel konfigurieren

1. Rechtsklick auf das Tray-Symbol → **Settings**
2. Im Tab **ASR Provider**: Wählen Sie Ihren Anbieter und geben Sie den API-Schlüssel ein
3. Klicken Sie **Save**

### Schritt 3: Diktieren

1. Platzieren Sie den Cursor in einem Textfeld (z.B. Word, Browser, E-Mail)
2. Drücken Sie **STRG+ALT+U** (oder Ihre konfigurierte Tastenkombination)
3. Sprechen Sie Ihren Text
4. Drücken Sie erneut **STRG+ALT+U** zum Beenden
5. Der transkribierte Text wird automatisch eingefügt

---

## System Tray Menü / System Tray Menu

Rechtsklick auf das Tray-Symbol öffnet das Menü:

| Menüpunkt | Funktion |
|-----------|----------|
| **Settings** | Öffnet das Einstellungsfenster |
| **Help** | Öffnet dieses Handbuch im Browser |
| **Quit** | Beendet die Anwendung |

### Tray-Symbol Status

| Symbol | Bedeutung |
|--------|-----------|
| 🎤 Grau | Bereit / Idle |
| 🎤 Rot | Aufnahme läuft |
| 🎤 Orange | Verarbeitung läuft |

---

## Einstellungen / Settings

### ASR Provider Tab

**Provider:** Wählt den Spracherkennungs-Anbieter

| Anbieter | Beschreibung | Kosten |
|----------|--------------|--------|
| **OpenAI** | GPT-4o-transcribe Modelle | ~$0.18-0.36/1M Tokens |
| **Together.ai** | Whisper Modelle | ~$0.09/1M Tokens |
| **Hugging Face** | Whisper Turbo | In Plus-Plan enthalten |
| **Local** | Lokale APIs (Ollama, etc.) | Kostenlos |

**API Key:** Ihr API-Schlüssel für den gewählten Anbieter

**Model:** Das zu verwendende Spracherkennungsmodell

**Base URL:** (Optional) Für lokale APIs oder alternative Endpunkte

### LLM Tab

**Enable LLM Post-Processing:** Aktiviert die Textnachbearbeitung

**Enable Voice Commands:** Aktiviert Sprachbefehle für Zeichensetzung

**Provider / Model:** Wählt den LLM-Anbieter für die Nachbearbeitung

**Custom Instructions:** Zusätzliche Anweisungen für den LLM

**Verfügbare Sprachbefehle / Available Voice Commands:**

| Gesagt / Spoken | Ergebnis / Result |
|-----------------|-------------------|
| "Neuer Absatz" / "New paragraph" | Neuer Absatz (2 Zeilenumbrüche) |
| "Neue Zeile" / "New line" | Neue Zeile |
| "Punkt" / "Period" | `.` |
| "Komma" / "Comma" | `,` |
| "Fragezeichen" / "Question mark" | `?` |
| "Ausrufezeichen" / "Exclamation mark" | `!` |
| "Doppelpunkt" / "Colon" | `:` |
| "Semikolon" / "Semicolon" | `;` |
| "Anführungszeichen" / "Quote" | `"` |
| "Ende Anführungszeichen" / "End quote" | `"` |
| "Lösche das" / "Delete that" | Letzten Satz löschen |
| "Lösche letztes Wort" / "Delete last word" | Letztes Wort löschen |

### Dictionary Tab

Fügen Sie Fachbegriffe, Eigennamen und Abkürzungen hinzu, die korrekt erkannt werden sollen.

**Beispiel:**
- Prozessdigitalisierung
- AnnaLena
- Kubernetes

### Hotkeys Tab

**Dictation Hotkey:** Die Tastenkombination zum Starten/Stoppen der Aufnahme

**Mode:**
- **Toggle:** Einmal drücken zum Starten, nochmal drücken zum Stoppen
- **Push-to-Talk:** Gedrückt halten zum Sprechen, loslassen zum Stoppen

### Audio Tab

**Device:** Wählt das Mikrofon

**Sample Rate:** Audioqualität (16000 Hz empfohlen)

### Language Tab

**Autostart with Windows:** Startet die Anwendung automatisch beim Windows-Start (nur im EXE-Modus verfügbar)

---

## Sprachsteuerung / Voice Commands

Sprachbefehle funktionieren nur, wenn **LLM Post-Processing** aktiviert ist.

### Beispiele / Examples

**Deutsch:**
```
Gesagt: "Hallo Punkt Wie geht es dir Fragezeichen"
Ergebnis: "Hallo. Wie geht es dir?"
```

```
Gesagt: "Dies ist ein Test Neuer Absatz Und hier geht es weiter Punkt"
Ergebnis: "Dies ist ein Test.

Und hier geht es weiter."
```

**English:**
```
Spoken: "Hello period How are you question mark"
Result: "Hello. How are you?"
```

### Tipps für Sprachbefehle

1. **Klar sprechen:** Sagen Sie die Befehle deutlich
2. **Natürliche Pausen:** Kurze Pausen vor und nach Befehlen helfen
3. **Kontext beachten:** Bei Zweideutigkeit wird der Text wörtlich übernommen

---

## Wörterbuch / Dictionary

### Wann ist ein Wörterbuch nützlich?

- Eigennamen (Fridoôina, Jéeena)
- Fachbegriffe (Kubernetes, FastAPI)
- Abkürzungen (API, SDK, CAS)
- Produktnamen

### Warnungen bei nicht unterstützten Anbietern

Einige ASR-Anbieter (Together.ai, Hugging Face) unterstützen keine Wörterbuch-Hinweise. In diesem Fall erscheint eine Warnung im Settings-Fenster.

**Lösung:** Aktivieren Sie LLM Post-Processing. Der LLM nutzt das Wörterbuch für die Korrektur.

---

## Provider und Modelle / Providers and Models

### OpenAI

**ASR Modelle:**
- `gpt-4o-transcribe` - Höchste Genauigkeit
- `gpt-4o-mini-transcribe` - Günstiger

**LLM Modelle:**
- `gpt-5-mini` - Schnell und günstig
- `gpt-5-nano` - Günstigste Option
- `gpt-5.2` - Höchste Qualität

### Together.ai

**ASR Modelle:**
- `openai/whisper-large-v3` - Whisper Modell

**LLM Modelle:**
- `Qwen/Qwen2.5-7B-Instruct-Turbo` - Schnell und günstig
- `meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` - Höhere Qualität
- `google/gemma-3n-E4B-it` - Sehr günstig

### Hugging Face

**ASR Modelle:**
- `openai/whisper-large-v3-turbo` - Turbo-Variante
- `openai/whisper-large-v3` - Standard Whisper

### Lokale APIs

Für lokale Modelle (Ollama, vLLM, etc.):
1. Setzen Sie **Base URL** auf `http://localhost:11434/v1`
2. Lassen Sie **API Key** leer oder setzen Sie einen Dummy-Wert

---

## Tipps und Tricks / Tips and Tricks

### Für bessere Transkription

1. **Gutes Mikrofon:** Ein Headset-Mikrofon liefert bessere Ergebnisse
2. **Ruhige Umgebung:** Minimieren Sie Hintergrundgeräusche
3. **Klare Aussprache:** Sprechen Sie natürlich, aber deutlich
4. **Spracheinstellung:** "Auto" erkennt automatisch Deutsch/Englisch

### Für schnelleres Arbeiten

1. **Push-to-Talk:** Halten Sie die Taste nur während des Sprechens gedrückt
2. **Sprachbefehle:** Nutzen Sie "Punkt" und "Neuer Absatz" statt manueller Korrektur
3. **Wörterbuch:** Fügen Sie häufige Fachbegriffe hinzu

### Für Kosteneffizienz

1. **Together.ai:** Günstigere Alternative zu OpenAI
2. **Hugging Face Plus:** Flatrate für viele Modelle
3. **Lokale Modelle:** Keine API-Kosten, aber eigene Hardware nötig

---

## Fehlerbehebung / Troubleshooting

### "No API key configured"

**Lösung:** 
1. Öffnen Sie Settings → ASR Provider
2. Geben Sie Ihren API-Schlüssel ein
3. Klicken Sie Save

### Text wird nicht eingefügt

**Mögliche Ursachen:**
1. Cursor ist nicht in einem Textfeld
2. Zielanwendung blockiert Ctrl+V
3. Zwischenablage-Fehler

**Lösung:**
- Testen Sie in einem anderen Textfeld (z.B. Notepad)
- Deaktivieren Sie Clipboard-Restore in Settings

### Sprachbefehle funktionieren nicht

**Voraussetzungen:**
1. LLM Post-Processing muss aktiviert sein
2. Voice Commands müssen aktiviert sein
3. Ein LLM-Modell muss ausgewählt sein

**Lösung:**
- Prüfen Sie, ob "Enable LLM" und "Enable Voice Commands" aktiviert sind
- Wählen Sie ein LLM-Modell im Dropdown

### Mikrofon wird nicht erkannt

**Lösung:**
1. Öffnen Sie Settings → Audio
2. Wählen Sie das korrekte Gerät im Dropdown
3. Prüfen Sie die Windows-Berechtigungen für Mikrofonzugriff

### Anwendung startet nicht mit Windows

**Voraussetzung:** Funktioniert nur im EXE-Modus (Installer-Version)

**Lösung:**
1. Installieren Sie die Anwendung mit dem Installer
2. Aktivieren Sie "Autostart with Windows" in Settings → Language

### Transkription ist langsam

**Mögliche Ursachen:**
- Große Modelle (gpt-4o-transcribe) sind langsamer
- OpenAI LLM-Modelle haben höhere Latenz
- Internetverbindung

**Lösung:**
- Verwenden Sie schnellere Modelle (gpt-4o-mini-transcribe, Qwen)
- Together.ai ist oft schneller als OpenAI

---

## Support

- **GitHub Issues:** [github.com/scepbjoern/asr-everywhere/issues](https://github.com/scepbjoern/asr-everywhere/issues)
- **Konfigurationsdatei:** `%APPDATA%\asr-everywhere\config.json`

---

## Lizenz / License

MIT License - Siehe [LICENSE](https://github.com/scepbjoern/asr-everywhere/blob/main/LICENSE)
