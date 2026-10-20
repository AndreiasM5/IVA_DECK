#define AppVersion "5.0.0"
[Setup]
AppId={{B26CE57F-CB7C-4F4D-A258-19EBECF98710}
AppName=IVA DECK
AppVersion={#AppVersion}
AppPublisher=Ioan-Andrei Ivașcu
AppPublisherURL=https://github.com/AndreiasM5/IVA_DECK
AppSupportURL=https://github.com/AndreiasM5/IVA_DECK/issues
AppUpdatesURL=https://github.com/AndreiasM5/IVA_DECK/releases
DefaultDirName={localappdata}\Programs\IVA DECK
DefaultGroupName=IVA DECK
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.19044
OutputDir=..\release
OutputBaseFilename=IVA-DECK-{#AppVersion}-Setup-x64
SetupIconFile=..\iva_key_app\src\assets\iva-deck.ico
UninstallDisplayIcon={app}\IVA-DECK.exe
LicenseFile=..\LICENSE
InfoAfterFile=..\INSTALLATION.txt
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
VersionInfoVersion=5.0.0.0
VersionInfoDescription=IVA DECK Windows installer
[Languages]
Name: "romanian"; MessagesFile: "Romanian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
[Files]
Source: "..\dist\IVA-DECK\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\INSTALLATION.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\IVA DECK"; Filename: "{app}\IVA-DECK.exe"
Name: "{autodesktop}\IVA DECK"; Filename: "{app}\IVA-DECK.exe"; Tasks: desktopicon
Name: "{group}\Dezinstalează IVA DECK"; Filename: "{uninstallexe}"
[Run]
Filename: "{app}\IVA-DECK.exe"; Description: "Pornește IVA DECK"; Flags: nowait postinstall skipifsilent
