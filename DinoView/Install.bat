rem pyinstaller.exe --windowed --onefile --icon=DinoPrint.ico DinoView.py
pyinstaller.exe --onefile --icon=DinoPrint.ico -p ../Modules  DinoView.py 

"c:\Program Files (x86)\Inno Setup 5\iscc.exe"  .\Installer\Installer.iss

ftpuse f: web3.gigahost.dk/www/dinocoin.frihauge.dk/dcfile Esj,0811 /USER:frihaugedk
pause
copy .\Installer\Output\DinoViewSetup.exe  f: /y
ftpuse f: /delete