; Inno Setup Script for ASR Everywhere
; Requires Inno Setup 6.x (https://jrsoftware.org/isinfo.php)
;
; Build command: iscc installer\setup.iss
; Output: dist\installer\asr-everywhere-setup.exe

#define AppName "ASR Everywhere"
#define AppVersion "0.2.0"
#define AppPublisher "ASR Everywhere Contributors"
#define AppURL "https://github.com/scepbjoern/asr-everywhere"
#define AppExeName "asr-everywhere.exe"
#define AppGUID "{{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}"

[Setup]
AppId={#AppGUID}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
; Output directory relative to project root
OutputDir=..\dist\installer
OutputBaseFilename=asr-everywhere-setup
SetupIconFile=..\assets\icon_idle.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
; Require admin rights for Program Files installation
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
; Uninstall settings
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}
; License file (optional, uncomment if you add a license)
; LicenseFile=LICENSE
; Architecture
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable (built by PyInstaller)
Source: "..\dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Icon files (for tray icons)
Source: "..\assets\*.ico"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
; Start Menu shortcuts
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#AppName}}"; Filename: "{#AppURL}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
; Desktop shortcut (optional)
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon
; Quick Launch shortcut (optional)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunchicon

[Run]
; Offer to launch the app after installation
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up any remaining files
Type: filesandordirs; Name: "{app}"
