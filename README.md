# Py_RAM_GUI
Fun Ram GUI - with fidget resolution option


## 🛠️ RAM Usage Monitor GUI

Author: Nathan Herling  
Description:  
A simple, visual RAM usage monitor built with PyQt6. Includes a resolution toggle to adjust the color granularity of the usage bar (Low / Med / High).  

---

## 📦 Features

- Real-time RAM usage tracking using `psutil`
- Clean, modern PyQt6 GUI
- Adjustable color resolution for the usage bar
- Compact and themed interface
- Suitable for creating a standalone `.exe` app

---

## 🧰 Requirements

Make sure the following Python packages are installed:

```bash
pip install pyqt6 psutil pyinstaller
```


## 🚀 Want to make an an executable?
# Build executable with PyInstaller

# 1. Install PyInstaller (if not already installed)
pip install pyinstaller

# 2. Create the executable (one-file bundle, console hidden)
pyinstaller --onefile --windowed --icon=stonks_up.ico RAM_gui.py

# Explanation:
# --onefile       : Bundles everything into a single .exe file
# --windowed      : Prevents a console window from opening (for GUI apps)
# --icon          : Sets the application icon (make sure stonks_up.ico is in the same folder)
# RAM_gui.py      : Your main Python script

# 3. After running, the executable will be located in the 'dist' folder.
#    You can run it directly from there:
#    dist\RAM_gui.exe
