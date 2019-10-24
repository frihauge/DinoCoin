
rem ftp open web3.gigahost.dk
rem pyinstaller.exe --windowed --onefile DinoPay.py
pyinstaller.exe --onefile -p ../Modules DinoPay.py
md .\dist\img
copy .\img\*.png .\dist\img\ /y
"c:\Program Files (x86)\Inno Setup 5\iscc.exe"  .\Installer\Installer.iss

ftpuse f: web3.gigahost.dk/www/dinocoin.frihauge.dk/dcfile Esj,0811 /USER:frihaugedk
pause
copy .\Installer\Output\DinoPaySetup.exe  f: /y
rem ftpuse f: /delete