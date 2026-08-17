Option Explicit

Dim shell, fso, projectDir, pythonPath, pythonwPath
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
projectDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Reuse the project's current `python` command, then select its matching
' windowless interpreter instead of assuming pythonw.exe is on PATH.
pythonPath = ResolveInterpreter("python")
If pythonPath = "" Then pythonPath = ResolveInterpreter("py -3")

If pythonPath <> "" Then
    pythonwPath = fso.BuildPath(fso.GetParentFolderName(pythonPath), "pythonw.exe")
End If

If pythonwPath = "" Or Not fso.FileExists(pythonwPath) Then
    MsgBox "PIE ITR Assistant could not find the matching pythonw.exe. Use run_cli.bat to view diagnostics.", vbExclamation, "PIE ITR Assistant"
    WScript.Quit 1
End If

shell.Run Quote(pythonwPath) & " " & Quote(fso.BuildPath(projectDir, "gui.py")), 0, False

Function Quote(value)
    Quote = Chr(34) & value & Chr(34)
End Function

Function ResolveInterpreter(command)
    Dim probeFile, probeCommand, probeStream
    probeFile = fso.BuildPath(shell.ExpandEnvironmentStrings("%TEMP%"), fso.GetTempName)
    probeCommand = Quote(shell.ExpandEnvironmentStrings("%ComSpec%")) _
        & " /d /c " & command _
        & " -c ""import sys; print(sys.executable)"" > " & Quote(probeFile)
    If shell.Run(probeCommand, 0, True) = 0 And fso.FileExists(probeFile) Then
        Set probeStream = fso.OpenTextFile(probeFile, 1)
        ResolveInterpreter = Trim(probeStream.ReadAll)
        probeStream.Close
    Else
        ResolveInterpreter = ""
    End If
    If fso.FileExists(probeFile) Then fso.DeleteFile probeFile, True
End Function
