@echo off
chcp 65001 >nul
echo ==========================================
echo STAR Analysis System - Modern Analyzer Setup
echo ==========================================
echo.
echo MeCabの代替として、より現代的で使いやすい
echo Janome形態素解析エンジンをセットアップします。
echo.
echo 利点:
echo - インストールが簡単（Pure Python）
echo - 外部辞書不要
echo - 全OS対応（Windows/Mac/Linux）
echo - 高精度な日本語解析
echo - 活発に保守されている
echo.

set /p choice="セットアップを開始しますか？ (y/n): "
if /i "%choice%"=="y" goto :install
if /i "%choice%"=="yes" goto :install
echo セットアップを中止しました。
pause
exit /b 0

:install
echo.
echo Step 1: Janome形態素解析エンジンをインストール中...
call install_janome.bat
if errorlevel 1 (
    echo エラー: Janomeインストールに失敗しました
    pause
    exit /b 1
)

echo.
set /p test_choice="性能比較テストを実行しますか？ (y/n): "
if /i "%test_choice%"=="y" goto :test
if /i "%test_choice%"=="yes" goto :test
goto :complete

:test
echo.
echo Step 2: 性能比較テスト実行中...
python test_analyzers_comparison.py
if errorlevel 1 (
    echo 警告: テスト実行でエラーが発生しましたが、セットアップは完了しています
)

:complete
echo.
echo ==========================================
echo 現代的形態素解析セットアップが完了しました！
echo ==========================================
echo.
echo - Janome形態素解析エンジンが利用可能
echo - 高精度STAR分析が有効
echo - 全環境で動作保証
echo.
echo STAR分析システムを起動して、
echo 改善された分析精度をお試しください。
echo.
pause