; Script generated by the Inno Script Studio Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "DC_Service_App"
#define MyAppVersion "1.0"
#define MyAppPublisher "DinoCoin"
#define MyAppURL "http://www.DinoCoin.dk"
#define MyAppExeName "DinoPrint.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{B8C9D120-1A19-467D-B549-F5B60AA8A1EC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\DinoCoin DC_Service_App
DefaultGroupName={#MyAppName}
OutputBaseFilename=DinoPrintSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin 
VersionInfoVersion=1.0
VersionInfoCompany=Dinocoin ApS
VersionInfoDescription=DinoPrint service app
VersionInfoCopyright=Dino
VersionInfoProductName=DinoPrint 
VersionInfoProductVersion=1.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\DinoPrint.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\workspace\project\Dinocoin\SW\DinoCoin\client_sw\MainSetup.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\DinoPrint.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\*.ttf"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
