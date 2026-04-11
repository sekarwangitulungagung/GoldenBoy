;NSIS Script for Sekar Wangi Tally Pro Control v4.1
;This script creates a Windows installer for the application

!define APPNAME "Sekar Wangi Tally Pro Control"
!define COMPANYNAME "SekarWangi"
!define DESCRIPTION "Professional MIDI Tally Light Management System with OBS & vMix Support"
!define VERSIONMAJOR 4
!define VERSIONMINOR 1
!define VERSIONBUILD 0
!define HELPURL "https://github.com/sekarwangitulungagung/GoldenBoy"
!define UPDATEURL "https://github.com/sekarwangitulungagung/GoldenBoy"
!define ABOUTURL "https://github.com/sekarwangitulungagung/GoldenBoy"
!define INSTALLSIZE 40000

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\${APPNAME}"
Name "${APPNAME}"
outFile "${APPNAME} v${VERSIONMAJOR}.${VERSIONMINOR} Setup.exe"

!include LogicLib.nsh
!include nsDialogs.nsh
!include WinMessages.nsh

page directory
page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin" ;Require admin rights on NT4+
    messageBox mb_iconstop "Administrator rights required!"
    setErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
    quit
${EndIf}
!macroend

function .onInit
    setShellVarContext all
    !insertmacro VerifyUserIsAdmin
functionEnd

section "install"
    # Files for the install directory - to build the installer, these should be in the same directory as the install script (this file)
    setOutPath $INSTDIR

    # Copy the executable
    file "build\SekarWangi_TallyPro_v4.1.exe"

    # Copy configuration and documentation files
    file "README.md"
    file ".env"
    file "requirements.txt"

    # Registry information for add/remove programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\SekarWangi_TallyPro_v4.1.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}

    # Create desktop shortcut
    createShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\SekarWangi_TallyPro_v4.1.exe" "" "$INSTDIR\SekarWangi_TallyPro_v4.1.exe"

    # Create start-menu entries
    createDirectory "$SMPROGRAMS\${APPNAME}"
    createShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\SekarWangi_TallyPro_v4.1.exe" "" "$INSTDIR\SekarWangi_TallyPro_v4.1.exe"
    createShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe"

    # Create uninstaller
    writeUninstaller "$INSTDIR\uninstall.exe"

    # Show success message
    MessageBox MB_OK "Installation completed successfully!$\n$\n${APPNAME} has been installed to:$\n$INSTDIR$\n$\nConfiguration file (.env) is included for easy setup."
sectionEnd

section "uninstall"
    # Stop the application if running
    ExecWait 'taskkill /f /im "SekarWangi_TallyPro_v4.1.exe" /t'

    # Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"

    # Remove files
    delete "$INSTDIR\SekarWangi_TallyPro_v4.1.exe"
    delete "$INSTDIR\README.md"
    delete "$INSTDIR\.env"
    delete "$INSTDIR\requirements.txt"
    delete "$INSTDIR\uninstall.exe"

    # Remove shortcuts
    delete "$DESKTOP\${APPNAME}.lnk"
    delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    delete "$SMPROGRAMS\${APPNAME}\Uninstall.lnk"

    # Remove directories
    rmDir "$SMPROGRAMS\${APPNAME}"
    rmDir "$INSTDIR"

    # Show uninstall message
    MessageBox MB_OK "Uninstallation completed successfully!"
sectionEnd