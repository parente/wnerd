;--------------------------------
;Include Modern UI

  !include "MUI.nsh"

;--------------------------------
;Configuration

  ;General
  Name "Wrestling Nerd 3.0"
  OutFile "WrestlingNerd-3.0-win32.exe"
  Icon ".\WrestlingNerd_wdr\nerd.ico"

  ;Folder selection page
  InstallDir "$PROGRAMFILES\WrestlingNerd"
  
  ;Get install folder from registry if available
  InstallDirRegKey HKCU "Software\WrestlingNerd" ""

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_LICENSE ".\LICENSE.txt"
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Program" SecProgram

  SetOutPath "$INSTDIR"
  
  ;Grab the appropriate files
  File /r ".\dist\WrestlingNerd\*.*"
  
  ;Store install folder
  WriteRegStr HKLM "Software\WrestlingNerd" "" $INSTDIR
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WrestlingNerd" "DisplayName" "Wrestling Nerd"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WrestlingNerd" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WrestlingNerd" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WrestlingNerd" "NoRepair" 1
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Shortcuts"
  CreateDirectory "$SMPROGRAMS\Wrestling Nerd"
  CreateShortcut "$SMPROGRAMS\Wrestling Nerd\Wrestling Nerd 3.0.lnk" "$INSTDIR\WrestlingNerd.exe"
  CreateShortcut "$DESKTOP\Wrestling Nerd 3.0.lnk" "$INSTDIR\WrestlingNerd.exe"
SectionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"
  ; delete files
  RMDir /r "$INSTDIR"

  ; delete registry keys
  DeleteRegKey HKLM "Software\WrestlingNerd"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WrestlingNerd"

  ; delete shortcuts
  Delete "$SMPROGRAMS\Wrestling Nerd\Wrestling Nerd 3.0.lnk"
  Delete "$DESKTOP\Wrestling Nerd\Wrestling Nerd 3.0.lnk"
  RMDir "$SMPROGRAMS\Wrestling Nerd"
SectionEnd