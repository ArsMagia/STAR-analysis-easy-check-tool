@echo off
chcp 65001 >nul
echo ========================================
echo Janome Quick Setup
echo ========================================
echo.
echo 最新の形態素解析エンジンJanomeをインストールします
echo （MeCabの現代的な代替手段）
echo.

echo Step 1: Janomeインストール...
pip install janome
if errorlevel 1 (
    echo 通常のインストールに失敗しました。ユーザー専用でインストールを試行...
    pip install --user janome
    if errorlevel 1 (
        echo エラー: Janomeインストールに失敗しました
        echo.
        echo 解決方法:
        echo 1. Pythonが正しくインストールされているか確認
        echo 2. pipが最新版か確認: python -m pip install --upgrade pip
        echo 3. 管理者権限でコマンドプロンプトを実行
        echo.
        pause
        exit /b 1
    )
)

echo ✅ Janomeインストール完了
echo.

echo Step 2: インストール確認...
python -c "
try:
    from janome.tokenizer import Tokenizer
    print('✅ Janome正常にインストールされました')
    tokenizer = Tokenizer()
    result = list(tokenizer.tokenize('テスト文章です', wakati=True))
    print(f'✅ 動作テスト成功: {result}')
except Exception as e:
    print(f'❌ エラー: {e}')
    exit(1)
"

if errorlevel 1 (
    echo ❌ Janome動作確認に失敗しました
    pause
    exit /b 1
)

echo.
echo ========================================
echo Janome セットアップ完了！
echo ========================================
echo.
echo 次回STAR分析システム起動時から、
echo 高精度な形態素解析が自動的に使用されます。
echo.
echo 確認方法: システム起動時に
echo 「✅ Janome形態素解析を使用します」
echo と表示されればOKです。
echo.
pause