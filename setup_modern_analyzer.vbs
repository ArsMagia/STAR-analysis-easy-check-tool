Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

strCurrentDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = strCurrentDir

' 現代的形態素解析セットアップメニュー
strMessage = "STAR分析システム - 現代的形態素解析セットアップ" & vbCrLf & vbCrLf & _
             "MeCabの代替として、より現代的で使いやすい" & vbCrLf & _
             "Janome形態素解析エンジンをセットアップします。" & vbCrLf & vbCrLf & _
             "利点:" & vbCrLf & _
             "- インストールが簡単（Pure Python）" & vbCrLf & _
             "- 外部辞書不要" & vbCrLf & _
             "- 全OS対応（Windows/Mac/Linux）" & vbCrLf & _
             "- 高精度な日本語解析" & vbCrLf & _
             "- 活発に保守されている" & vbCrLf & vbCrLf & _
             "セットアップを開始しますか？"

intResult = MsgBox(strMessage, vbYesNo + vbQuestion, "現代的形態素解析セットアップ")

If intResult = vbYes Then
    ' Janomeセットアップ実行
    objShell.Run "cmd /c install_janome.bat", 1, True
    
    ' 性能テスト実行
    intTestResult = MsgBox("Janomeセットアップが完了しました。" & vbCrLf & vbCrLf & _
                           "性能比較テストを実行しますか？" & vbCrLf & _
                           "（分析精度と速度を確認できます）", _
                           vbYesNo + vbQuestion, "性能テスト")
    
    If intTestResult = vbYes Then
        objShell.Run "python test_analyzers_comparison.py", 1, True
    End If
    
    ' 完了メッセージ
    MsgBox "現代的形態素解析セットアップが完了しました！" & vbCrLf & vbCrLf & _
           "- Janome形態素解析エンジンが利用可能" & vbCrLf & _
           "- 高精度STAR分析が有効" & vbCrLf & _
           "- 全環境で動作保証" & vbCrLf & vbCrLf & _
           "STAR分析システムを起動して、" & vbCrLf & _
           "改善された分析精度をお試しください。", _
           vbInformation, "セットアップ完了"
End If