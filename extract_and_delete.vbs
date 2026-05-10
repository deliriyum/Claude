On Error Resume Next

Set args = WScript.Arguments
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

' Exit if no arguments
If args.Count = 0 Then
    WScript.Quit
End If

' Use a temp folder for collecting files
tempFolder = shell.ExpandEnvironmentStrings("%TEMP%") & "\extract_and_delete_" & Year(Now) & Month(Now) & Day(Now) & Hour(Now) & Minute(Now)
lockFile = tempFolder & "\processing.lock"

' Create temp folder if it doesn't exist
If Not fso.FolderExists(tempFolder) Then
    fso.CreateFolder tempFolder
End If

' Create a unique marker file for this file
timestamp = Timer * 1000
markerFile = tempFolder & "\" & timestamp & ".txt"
Set f = fso.CreateTextFile(markerFile, True)
f.WriteLine args(0)
f.Close

' Wait for all instances to create their marker files
WScript.Sleep 2000

' Try to acquire lock (with retry to avoid race condition)
lockAcquired = False
For retry = 1 To 5
    If Not fso.FileExists(lockFile) Then
        On Error Resume Next
        fso.CreateTextFile(lockFile, True).Close
        If Err.Number = 0 Then
            lockAcquired = True
            Exit For
        End If
        On Error GoTo 0
    End If
    WScript.Sleep 100
Next

' Only the lock holder processes all files
If lockAcquired Then
    ' Wait a bit more for any final stragglers
    WScript.Sleep 1500

    ' Collect all files from marker files
    Set folder = fso.GetFolder(tempFolder)
    Set files = folder.Files

    psCommand = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""C:\Scripts\extract_and_delete.ps1"""

    For Each file In files
        If LCase(fso.GetExtensionName(file.Name)) = "txt" Then
            Set f = fso.OpenTextFile(file.Path, 1)
            filePath = f.ReadLine
            f.Close
            If Trim(filePath) <> "" Then
                psCommand = psCommand & " """ & filePath & """"
            End If
        End If
    Next

    ' Run PowerShell with all collected files
    shell.Run psCommand, 1, True

    ' Cleanup - delete the entire temp folder
    On Error Resume Next
    fso.DeleteFolder tempFolder, True
    On Error GoTo 0
End If
