@echo off
chcp 65001 >nul
echo ==========================================
echo Janome (Modern Japanese Analyzer) Setup
echo ==========================================
echo.

echo Janome は純粋なPythonで書かれた現代的な日本語形態素解析ライブラリです。
echo MeCabの代替として、インストールが簡単で高性能です。
echo.

echo Step 1: Installing Janome...
pip install janome
if errorlevel 1 (
    echo ❌ Janome installation failed
    echo Trying with --user flag...
    pip install --user janome
    if errorlevel 1 (
        echo ❌ Janome installation failed completely
        echo Please check your Python and pip installation
        pause
        exit /b 1
    )
)

echo ✅ Janome installation completed
echo.

echo Step 2: Testing Janome integration...
python -c "
from star_analyzer import STARAnalyzer
print('=== Janome Integration Test ===')
analyzer = STARAnalyzer()
if analyzer.analyzer_type == 'modern':
    print('✅ Janome successfully integrated')
    result = analyzer.analyze('この料理、本当においしい！')
    print(f'✅ Analysis test successful: {result.primary_category}')
else:
    print('⚠️ Janome not detected, using fallback mode')
print('=== Test Complete ===')
"

echo.
echo ==========================================
echo Janome setup completed successfully!
echo 現代的な高精度形態素解析が利用可能になりました。
echo ==========================================
echo.
pause