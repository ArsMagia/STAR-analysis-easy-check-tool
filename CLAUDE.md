# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
STAR Analysis System - A Japanese text analysis application that categorizes emotional expressions into STAR classification (SENSE, THINK, ACT, RELATE) with GUI and CLI interfaces.

## Development Commands

### Running the Applications

#### コマンドラインから実行
```bash
# Run GUI version
python star_gui.py

# Run CLI version  
python star_cli.py

# Run analyzer module directly
python -c "from star_analyzer import STARAnalyzer; analyzer = STARAnalyzer(); print(analyzer.analyze('テストテキスト'))"
```

#### デスクトップアイコンから実行

**Windows環境でのデスクトップショートカット作成**
1. `create_shortcut.vbs` をダブルクリック
2. デスクトップに「STAR Analysis System」アイコンが作成される
3. 作成されたアイコンをダブルクリックしてGUIを起動

**手動起動ファイル**
- `start_star_gui.bat`: コマンドプロンプト付きで起動
- `start_star_gui_silent.vbs`: バックグラウンドで起動（推奨）

**文字化け対策**
- 全てのPythonファイルにUTF-8エンコーディング宣言を追加
- Windows環境でのChcp 65001 (UTF-8) 設定
- 日本語フォント自動検出・設定機能

### Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

### Testing the System
```bash
# Quick functionality test
python -c "
from star_analyzer import STARAnalyzer
analyzer = STARAnalyzer()
result = analyzer.analyze('この料理、本当においしい！')
print(f'Primary category: {result.primary_category}')
print(f'Scores: {result.scores}')
"
```

### 形態素解析エンジンについて

**Janome（推奨）- 現代的な日本語形態素解析**
- Pure Python実装でインストールが簡単
- Windows/Linux/Mac全環境で動作
- 高精度な日本語解析
- 辞書の別途インストール不要

**インストール方法**
```bash
# Janome (推奨)
pip install janome

# または自動インストール
install_janome.bat  # Windows用
```

**対応解析エンジン**
1. **Janome** (推奨): 現代的、高精度、インストール簡単
2. **基本分析**: 解析エンジンなし、キーワードベース

**環境別の対応**
- 推奨: Janome形態素解析による高精度分析
- フォールバック: 基本分析機能（キーワードベース分析）
- 両モードでSTAR分析の基本機能は完全動作

## Architecture Overview

The system consists of three main components:

1. **star_analyzer.py** - Core analysis engine implementing STAR+FEEL theory
   - `STARAnalyzer` class: Main analysis logic with keyword-based classification
   - `AnalysisResult` dataclass: Structured output with scores, categories, and detailed analysis
   - Implements Japanese sentence type detection (SV型/SOV型) for classification rules

2. **star_gui.py** - tkinter-based GUI application  
   - Three-panel visualization: pie chart, donut chart, and bar chart
   - Interactive text input with sample texts
   - Real-time analysis results display with detailed breakdown

3. **star_cli.py** - Command-line interface
   - Interactive menu system with sample text options
   - Detailed console output with theoretical background explanations

## Core Analysis Theory

The system implements STAR+FEEL theory for Japanese emotional text analysis:

- **SENSE + FEEL**: Sensory experiences (きれい, おいしい, 気持ちいい)
- **THINK + FEEL**: Knowledge expansion (わかった, なるほど, すごい)  
- **ACT + FEEL**: Experience expansion (できた, やった, よかった)
- **RELATE + FEEL**: Relationship expansion (すばらしい, ありがたい, 一緒だ)

### Classification Rules
- **SV型** (Subject+Verb) → SENSE or THINK
- **SOV型** (Subject+Object+Verb) → ACT or RELATE

### Key Implementation Details

The analyzer uses keyword-based scoring with specific Japanese expressions mapped to each STAR category. The system detects sentence patterns and applies classification rules based on Japanese grammatical structures.

FEEL elements are quantified through exclamation marks and emotional expressions, providing a confidence score for the primary category assignment.

## Project Status

This is a completed Japanese text analysis system implementing STAR+FEEL theory. The system includes:

### Core Functionality (100% Complete)
- ✅ Functional STAR classification engine with Japanese language support
- ✅ CLI interface with interactive menu and detailed analysis output
- ✅ Sentence type detection (SV型/SOV型) for classification rules
- ✅ FEEL element detection and quantification
- ✅ Automatic generation of emotional structure patterns

### Phase 1 Improvements (100% Complete)
- ✅ Enhanced analysis accuracy with Janome morphological analysis
- ✅ Expanded keyword dictionary based on STAR theory documents
- ✅ Context weighting system and negation detection
- ✅ Emotion intensity tracking and mixed emotion detection

### Phase 2 Modern UI/UX (100% Complete)
- ✅ Completely redesigned intuitive layout with 3-tier structure
- ✅ Tabbed results interface (Overview, Details, Charts, Memo)
- ✅ Card-based sample text selection system
- ✅ Educational UI components with STAR theory explanations
- ✅ Dark mode with comprehensive theme system
- ✅ Modern memo functionality with tagging and search
- ✅ Auto-tag generation based on analysis results
- ✅ Full-text search with category filtering
- ✅ Desktop launcher and simplified startup scripts

### Technical Achievements
- ✅ MeCab → Janome migration for modern morphological analysis
- ✅ Project folder organization (35 → 16 files)
- ✅ Font handling improvements for Japanese text
- ✅ Theme-aware UI components throughout
- ✅ Backward compatible memo storage format

### Project Completion: 100%
All planned features have been successfully implemented. The system is production-ready with modern UI/UX, comprehensive functionality, and excellent user experience. Last updated: 2025-06-15.

## 重要な作業指針

**STAR理論基準の遵守**
- 全ての機能実装において「STAR分析フレームワーク.md」と「感動のStar分析とはなにか.md」に記載の基準に合致しているかを常に確認すること
- キーワード辞書、分析ロジック、UI表示等の変更時は必ず原典理論との整合性をチェック

**変更管理**
- 指示にない新機能や変更は勝手に実装せず、必ず提案という形を取ること
- 実装前に必ずユーザーの承認を得ること
- 既存機能の変更は慎重に行い、影響範囲を事前確認すること

これらの指針はClaude Codeセッション再起動後も継続して適用される重要なルールです。