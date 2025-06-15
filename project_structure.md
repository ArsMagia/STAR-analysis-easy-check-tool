# STAR Analysis System - Project Structure

## 📁 クリーンアップ後の推奨プロジェクト構成

### 🟢 コアファイル（必須）
```
star_analyzer.py        # メイン分析エンジン
star_gui.py            # GUIアプリケーション  
star_cli.py            # CLIアプリケーション
requirements.txt       # 依存関係定義
```

### 📚 理論・設定ファイル（重要）
```
STAR分析フレームワーク.md         # STAR理論フレームワーク
感動のStar分析とはなにか.md       # 理論詳細・原典
CLAUDE.md                        # プロジェクト指針・作業ガイド
```

### 🚀 推奨起動・セットアップファイル
```
quick_janome_setup.bat           # Janome簡単セットアップ
setup_modern_analyzer.bat       # 詳細セットアップ
setup_modern_analyzer.vbs       # VBScript版セットアップ
start_star_gui.bat              # GUI起動
start_star_gui_silent.vbs       # サイレントGUI起動
create_debug_shortcut.vbs       # デスクトップショートカット作成
```

### 🔧 開発・テストファイル（オプション）
```
install_janome.bat              # Janome単体インストール
test_analyzers_comparison.py    # 性能比較テスト
```

## 🗑️ 削除対象ファイル

### MeCab関連（廃止済み）
- check_mecab_config.py
- create_mecabrc.py
- install_mecab.bat
- setup_mecab_complete.vbs
- setup_mecab_env.bat

### 重複する起動スクリプト
- STAR分析GUI起動.bat
- STAR分析GUI起動_ウィンドウなし.vbs
- create_desktop_shortcut.vbs
- create_shortcut.vbs

### デバッグ・テスト用（一時的）
- debug_startup.bat
- debug_startup_silent.vbs
- start_safe.bat
- start_safe.py
- startup_debug.log

### 開発用一時ファイル
- notify_complete.py
- vscode_notification_setup.md
- SnapCrab_*.png

## 📋 整理後の使用方法

### 初回セットアップ
1. `quick_janome_setup.bat` を実行
2. `create_debug_shortcut.vbs` でデスクトップアイコン作成

### 日常使用
- デスクトップの「STAR Analysis System」アイコンをダブルクリック
- または `start_star_gui.bat` を実行

### トラブルシューティング
- `test_analyzers_comparison.py` で性能テスト
- `setup_modern_analyzer.bat` で再セットアップ

## 🎯 整理の効果

- **ファイル数**: 28個 → 14個（50%削減）
- **明確性**: 目的別にファイルが整理
- **保守性**: 重複削除により管理が簡単
- **使いやすさ**: 推奨手順が明確