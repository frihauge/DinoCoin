@echo off
echo user frihaugedk> ftpcmd.dat
echo Esj,0811>> ftpcmd.dat
echo bin>> ftpcmd.dat
echo put setup.exe>> ftpcmd.dat
echo quit>> ftpcmd.dat
ftp -n -s:ftpcmd.dat SERVERNAME.COM
del ftpcmd.dat