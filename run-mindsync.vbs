Set WshShell = CreateObject("WScript.Shell")

projectDir = "C:\Users\user\Desktop\Major project"
WshShell.CurrentDirectory = projectDir

' 1. Check if backend port 8000 is listening
Set oExecB = WshShell.Exec("cmd /c netstat -ano | findstr :8000")
port8000Active = False
Do While oExecB.Status = 0
    WScript.Sleep 100
Loop
outB = Trim(oExecB.StdOut.ReadAll())
If InStr(outB, "LISTENING") > 0 Then
    port8000Active = True
End If

' Launch backend silently if not already running
If Not port8000Active Then
    WshShell.Run "cmd /c python -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000", 0, False
    WScript.Sleep 2000
End If

' 2. Check if frontend port 5173 is listening
Set oExecF = WshShell.Exec("cmd /c netstat -ano | findstr :5173")
port5173Active = False
Do While oExecF.Status = 0
    WScript.Sleep 100
Loop
outF = Trim(oExecF.StdOut.ReadAll())
If InStr(outF, "LISTENING") > 0 Then
    port5173Active = True
End If

' Launch frontend silently if not already running
If Not port5173Active Then
    WshShell.Run "cmd /c npm run dev", 0, False
    WScript.Sleep 3000
End If

' 3. Open the web browser
WshShell.Run "http://localhost:5173", 1, False
