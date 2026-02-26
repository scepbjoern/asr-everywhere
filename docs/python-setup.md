# Python Installation Guide for Windows

This guide explains how to install and configure Python on Windows for developing ASR Everywhere.

## Requirements

- **Python ≥ 3.11** (3.11 or 3.12 recommended)
- **pip** (included with Python)
- Windows 10 or 11

---

## Option 1: Official Python Installer (Recommended)

### Step 1: Download Python

1. Visit [python.org/downloads](https://www.python.org/downloads/)
2. Click "Download Python 3.x.x" (latest version)
3. Run the downloaded `.exe` installer

### Step 2: Install Python

**Important:** During installation, check these options:

- ✅ **"Add Python to PATH"** — Essential for command-line access
- ✅ **"Install pip"** — Package manager (usually pre-selected)
- ✅ **"Install for all users"** (optional, recommended)

Click "Install Now" or customize installation path if needed.

### Step 3: Verify Installation

Open **PowerShell** or **Command Prompt**:

```powershell
python --version
pip --version
```

Expected output:
```
Python 3.11.x
pip 24.x from ...
```

---

## Option 2: Microsoft Store

1. Open **Microsoft Store** from Start menu
2. Search for "Python 3.11" or "Python 3.12"
3. Click **Get** or **Install**
4. Verify: `python --version` in PowerShell

**Note:** Store version has some path limitations. Official installer is preferred for development.

---

## Option 3: winget (Windows Package Manager)

If you have winget installed (Windows 11 has it by default):

```powershell
winget install Python.Python.3.11
```

---

## Virtual Environments

Always use virtual environments for Python projects to isolate dependencies.

### Create Virtual Environment

```powershell
cd C:\path\to\asr-everywhere_windows
python -m venv .venv
```

### Activate Virtual Environment

**PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Command Prompt:**
```cmd
.\.venv\Scripts\activate.bat
```

### Deactivate

```powershell
deactivate
```

---

## Troubleshooting

### "python" not recognized

**Cause:** Python not in PATH.

**Solution:**
1. Reinstall with "Add Python to PATH" checked
2. Or add manually:
   - Search "Environment Variables" in Start menu
   - Edit "Path" variable
   - Add: `C:\Users\<YourUser>\AppData\Local\Programs\Python\Python311\`
   - Add: `C:\Users\<YourUser>\AppData\Local\Programs\Python\Python311\Scripts\`

### Execution Policy Error (PowerShell)

If you get:
```
.\.venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then retry activation.

### Multiple Python Versions

If you have multiple Python versions:

```powershell
# Check all installed versions
py --list

# Run specific version
py -3.11 --version

# Create venv with specific version
py -3.11 -m venv .venv
```

### pip Upgrade

Keep pip updated:

```powershell
python -m pip install --upgrade pip
```

---

## Development Tools (Optional)

### pipx — Run Python apps in isolated environments

```powershell
pip install pipx
pipx ensurepath
```

### ruff — Fast Python linter/formatter (used in this project)

```powershell
pip install ruff
```

---

## Verify Development Setup

After installation, verify everything works:

```powershell
# Check Python version (must be ≥ 3.11)
python --version

# Check pip
pip --version

# Create test venv
python -m venv test-env
.\test-env\Scripts\Activate.ps1
pip install pytest
deactivate
Remove-Item -Recurse test-env
```

---

## Next Steps

1. Follow `.windsurf/workflows/init-project.md` to set up the project
2. Create virtual environment: `python -m venv .venv`
3. Install dependencies: `pip install -e ".[dev]"`

---

## Resources

- [Official Python Documentation](https://docs.python.org/3/)
- [Python on Windows FAQ](https://docs.python.org/3/using/windows.html)
- [Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
