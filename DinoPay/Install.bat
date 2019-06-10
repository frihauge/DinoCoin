rem pyinstaller.exe --windowed --onefile DinoPay.py
pyinstaller.exe --onefile DinoPay.py

"c:\Program Files (x86)\Inno Setup 5\iscc.exe"  .\Installer\Installer.iss


rem copy .\Installer\Output\DinoViewSetup.exe  C:\Users\esben\"Google Drev"\Programs\ServiceApp