; Windows installer, built by build.py with Inno Setup 6 (ISCC.exe)
; installs for the current user only (no administrator rights), with start menu entry and desktop shortcut
; build.py passes AppVersion, SourceDir (packaged app folder), OutputDir and RootDir (project folder)

#ifndef AppVersion
  #define AppVersion "dev"
#endif

[Setup]
; never change the AppId: an update finds the earlier installation by it
AppId={{27D18530-A0BB-47ED-9FDC-1A5B72731CA1}
AppName=Mitgliederverwaltung
AppVersion={#AppVersion}
AppPublisher=Thomas Egen
AppPublisherURL=https://tomegen.github.io/member-admin/
AppSupportURL=https://github.com/tomegen/member-admin
; with PrivilegesRequired=lowest this is %LOCALAPPDATA%\Programs\Mitgliederverwaltung
DefaultDirName={autopf}\Mitgliederverwaltung
PrivilegesRequired=lowest
DisableDirPage=yes
DisableProgramGroupPage=yes
DisableReadyPage=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir={#OutputDir}
OutputBaseFilename=Mitgliederverwaltung-Windows-Setup
SetupIconFile={#RootDir}\member.ico
UninstallDisplayIcon={app}\Mitgliederverwaltung.exe
UninstallDisplayName=Mitgliederverwaltung
WizardStyle=modern
Compression=lzma2
SolidCompression=yes
CloseApplications=yes

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[InstallDelete]
; program files of an earlier version (a config.ini changed by the user stays)
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Excludes: "config.ini"; Flags: recursesubdirs ignoreversion
Source: "{#SourceDir}\config.ini"; DestDir: "{app}"; Flags: onlyifdoesntexist

[Icons]
Name: "{autoprograms}\Mitgliederverwaltung"; Filename: "{app}\Mitgliederverwaltung.exe"
Name: "{autodesktop}\Mitgliederverwaltung"; Filename: "{app}\Mitgliederverwaltung.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Mitgliederverwaltung.exe"; Description: "{cm:LaunchProgram,Mitgliederverwaltung}"; Flags: nowait postinstall skipifsilent
