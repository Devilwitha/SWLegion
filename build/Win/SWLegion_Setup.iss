[Setup]
AppName=Star Wars Legion: All-in-One Tool Suite
AppVersion=1.0
AppPublisher=BolliSoft (Nico Bollhalder)
AppPublisherURL=https://github.com/Devilwitha/SWLegion
AppSupportURL=https://github.com/Devilwitha/SWLegion/issues
AppUpdatesURL=https://github.com/Devilwitha/SWLegion/releases
DefaultDirName={userappdata}\Star Wars Legion Tool Suite
DefaultGroupName=Star Wars Legion Tool Suite
AllowNoIcons=yes
OutputDir=InstallerSetup
OutputBaseFilename=SWLegion_Installer
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
SetupIconFile=..\..\bilder\SW_legion_logo.ico
UninstallDisplayIcon={app}\SWLegion.exe
UninstallDisplayName=Star Wars Legion Tool Suite
VersionInfoVersion=1.0.0.0
VersionInfoCompany=BolliSoft
VersionInfoDescription=Star Wars Legion: All-in-One Tool Suite
VersionInfoCopyright=Copyright (C) 2026 BolliSoft

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copy all files and subfolders from the PyInstaller dist directory
Source: "dist\SWLegion\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Create shortcuts
Name: "{group}\Star Wars Legion Tool Suite"; Filename: "{app}\SWLegion.exe"; IconFilename: "{app}\_internal\bilder\SW_legion_logo.png"
Name: "{group}\{cm:UninstallProgram,Star Wars Legion Tool Suite}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\Star Wars Legion Tool Suite"; Filename: "{app}\SWLegion.exe"; Tasks: desktopicon; IconFilename: "{app}\_internal\bilder\SW_legion_logo.png"

[Run]
; Run the program after installation
Filename: "{app}\SWLegion.exe"; Description: "{cm:LaunchProgram,Star Wars Legion Tool Suite}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up log files and other generated files
Type: files; Name: "{app}\legion_app.log"
Type: files; Name: "{app}\*.log"
Type: dirifempty; Name: "{app}"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  // Add any custom initialization code here
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    // Custom actions during installation
  end;
end;