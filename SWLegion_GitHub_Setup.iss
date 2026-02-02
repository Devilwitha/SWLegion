[Setup]
AppName=Star Wars Legion: All-in-One Tool Suite
AppVersion=1.0
AppPublisher=BolliSoft (Nico Bollhalder)
AppPublisherURL=https://github.com/Devilwitha/SWLegion
AppSupportURL=https://github.com/Devilwitha/SWLegion/issues
AppUpdatesURL=https://github.com/Devilwitha/SWLegion/releases
DefaultDirName={autopf}\Star Wars Legion Tool Suite
DefaultGroupName=Star Wars Legion Tool Suite
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=SWLegion_Installer
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
SetupIconFile=bilder\SW_legion_logo.ico
UninstallDisplayIcon={app}\SWLegion.exe
UninstallDisplayName=Star Wars Legion Tool Suite
VersionInfoVersion=1.0.0.0
VersionInfoCompany=BolliSoft
VersionInfoDescription=Star Wars Legion: All-in-One Tool Suite
VersionInfoCopyright=Copyright (C) 2026 BolliSoft
WizardStyle=modern
ShowLanguageDialog=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; Copy all files and subfolders from the PyInstaller dist directory
Source: "pyinstaller_dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Create shortcuts
Name: "{group}\Star Wars Legion Tool Suite"; Filename: "{app}\SWLegion.exe"; IconFilename: "{app}\_internal\bilder\SW_legion_logo.ico"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,Star Wars Legion Tool Suite}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Star Wars Legion Tool Suite"; Filename: "{app}\SWLegion.exe"; Tasks: desktopicon; IconFilename: "{app}\_internal\bilder\SW_legion_logo.ico"; WorkingDir: "{app}"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Star Wars Legion Tool Suite"; Filename: "{app}\SWLegion.exe"; Tasks: quicklaunchicon; IconFilename: "{app}\_internal\bilder\SW_legion_logo.ico"; WorkingDir: "{app}"

[Run]
; Run the program after installation
Filename: "{app}\SWLegion.exe"; Description: "{cm:LaunchProgram,Star Wars Legion Tool Suite}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up log files and other generated files
Type: files; Name: "{app}\legion_app.log"
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\_internal\*.log"
Type: dirifempty; Name: "{app}"

[Messages]
english.WelcomeLabel1=Welcome to the [name] Setup Wizard
english.WelcomeLabel2=This will install [name/ver] on your computer.%n%nStar Wars Legion Tool Suite is a comprehensive digital companion for the Star Wars: Legion tabletop game, featuring army building, mission generation, and AI gameplay assistance.
german.WelcomeLabel1=Willkommen zum [name] Setup-Assistenten  
german.WelcomeLabel2=Dieses Programm wird [name/ver] auf Ihrem Computer installieren.%n%nStar Wars Legion Tool Suite ist ein umfassendes digitales Begleitprogramm für das Star Wars: Legion Tabletop-Spiel mit Armeeaufbau, Missionsgenerierung und KI-Spielhilfe.

[Code]
function InitializeSetup(): Boolean;
begin
  // Check Windows version (minimum Windows 10)
  if not IsWindows10OrLater then begin
    MsgBox('This application requires Windows 10 or later.', mbError, MB_OK);
    Result := False;
  end else
    Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then begin
    // Create application data directories if they don't exist
    CreateDir(ExpandConstant('{app}\_internal\db'));
    CreateDir(ExpandConstant('{app}\_internal\Armeen'));
    CreateDir(ExpandConstant('{app}\_internal\Missions'));
    CreateDir(ExpandConstant('{app}\_internal\maps'));
  end;
end;