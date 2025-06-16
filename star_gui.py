#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STAR分析GUI アプリケーション
感想文をSTAR分類で分析し、視覚的に表示するGUIツール
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from star_analyzer import STARAnalyzer
import matplotlib
import platform
matplotlib.use('TkAgg')  # GUIバックエンドを使用

# 日本語フォント設定
import matplotlib.font_manager as fm

def setup_japanese_font():
    """日本語フォント設定"""
    if platform.system() == 'Windows':
        # Windows環境での日本語フォント設定
        font_candidates = ['Yu Gothic', 'Meiryo', 'MS Gothic', 'DejaVu Sans']
        for font_name in font_candidates:
            try:
                plt.rcParams['font.family'] = font_name
                # テスト文字を描画して確認
                fig, ax = plt.subplots(figsize=(1, 1))
                ax.text(0.5, 0.5, 'テスト', ha='center', va='center')
                plt.close(fig)
                pass  # 日本語フォント設定完了
                break
            except:
                continue
        else:
            # フォールバック設定
            plt.rcParams['font.family'] = 'DejaVu Sans'
            pass  # 日本語フォントフォールバック
    else:
        # Linux/Mac環境での設定
        plt.rcParams['font.family'] = 'DejaVu Sans'
    
    plt.rcParams['axes.unicode_minus'] = False

# フォント設定の初期化
setup_japanese_font()

class ToolTip:
    """ツールチップクラス（STAR理論解説用）"""
    def __init__(self, widget, text, gui_instance=None):
        self.widget = widget
        self.text = text
        self.gui_instance = gui_instance
        self.tipwindow = None
        
        # マウスイベントをバインド
        self.widget.bind('<Enter>', self.show_tooltip)
        self.widget.bind('<Leave>', self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """ツールチップ表示"""
        if self.tipwindow or not self.text:
            return
            
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 20
        
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # テーマに応じた色設定
        if self.gui_instance and hasattr(self.gui_instance, 'themes'):
            theme = self.gui_instance.themes[self.gui_instance.current_theme]
            bg_color = theme['input_bg']
            fg_color = theme['input_fg']
        else:
            # フォールバック色
            bg_color = "#ffffe0"
            fg_color = "#333333"
        
        # ツールチップの内容
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background=bg_color, relief=tk.SOLID, borderwidth=1,
                        font=("Arial", 9), fg=fg_color, wraplength=350)
        label.pack(ipadx=5, ipady=3)
    
    def hide_tooltip(self, event=None):
        """ツールチップ非表示"""
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class STARAnalysisGUI:
    """STAR分析GUIアプリケーション"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("STAR分析システム")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # 適切な終了処理を設定
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # フォント設定の安全な初期化
        self.setup_fonts()
        
        # 分析エンジンの初期化
        self.analyzer = STARAnalyzer()
        
        # 分析結果保存
        self.current_result = None
        
        # テーマ管理の初期化
        self.current_theme = "light"
        self.themes = {
            'light': {
                'bg': '#f0f0f0',
                'fg': '#333333',
                'accent': '#4a90e2',
                'panel_bg': '#ffffff',
                'panel_fg': '#2c3e50',
                'input_bg': '#ffffff',
                'input_fg': '#333333',
                'button_bg': '#e8e8e8',
                'chart_colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            },
            'dark': {
                'bg': '#1e1e1e',        # VS Codeメイン背景
                'fg': '#d4d4d4',        # VS Codeメインテキスト
                'accent': '#007acc',    # VS Codeアクセントブルー
                'panel_bg': '#2d2d30',  # VS Codeサイドバー/パネル
                'panel_fg': '#cccccc',  # VS Codeパネルテキスト
                'input_bg': '#1e1e1e',  # VS Codeエディタ背景
                'input_fg': '#d4d4d4',  # VS Codeエディタテキスト
                'button_bg': '#0e639c', # VS Codeボタン背景
                'chart_colors': ['#f48771', '#4fc1ff', '#ffcc02', '#73c991']  # VS Codeテーマ色
            }
        }
        
        # サンプルテキスト
        self.sample_texts = [
            "この料理、本当においしい！素晴らしい味でした。",
            "やっと数学の問題が解けた！理解できて嬉しい。",
            "マラソンを完走できて本当に嬉しい。頑張った甲斐があった。",
            "友達が励ましてくれて心から感謝している。温かい気持ちになった。",
            "夕日がとても美しく、心が洗われるような気持ちになった。"
        ]
        
        self.setup_ui()
    
    def setup_fonts(self):
        """フォント設定の安全な初期化"""
        # デフォルトフォント設定
        self.font_family = "Arial"
        
        if platform.system() == 'Windows':
            try:
                import tkinter.font as tkfont
                
                # システムのデフォルトフォントを取得
                default_font = tkfont.nametofont("TkDefaultFont")
                self.font_family = default_font.actual()["family"]
                
                # 利用可能な日本語フォントを確認
                available_fonts = list(tkfont.families())
                
                # 優先順位でフォントを選択
                font_candidates = ["Yu Gothic UI", "Meiryo UI", "MS UI Gothic", "Arial"]
                for font in font_candidates:
                    if font in available_fonts:
                        self.font_family = font
                        pass  # 日本語フォントを設定
                        break
                
            except Exception as e:
                pass  # フォント設定エラー
                self.font_family = "Arial"
        
        pass  # 使用フォント設定完了
    
    def get_safe_font(self, size=9, weight='normal'):
        """安全なフォント指定を返すヘルパーメソッド"""
        try:
            if weight == 'bold':
                return (self.font_family, size, 'bold')
            else:
                return (self.font_family, size)
        except:
            # フォント指定に失敗した場合はシステムデフォルトを使用
            if weight == 'bold':
                return ("TkDefaultFont", size, 'bold')
            else:
                return ("TkDefaultFont", size)
        
    def setup_ui(self):
        """直感的なUIセットアップ（改善版）"""
        # メインフレーム
        self.main_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # ヘッダーフレーム（タイトル + 設定ボタン）
        self.setup_header_section()
        
        # メイン作業エリア（3段構成）
        self.setup_main_work_area()
        
    def setup_header_section(self):
        """ヘッダーセクション（シンプル化）"""
        self.header_frame = tk.Frame(self.main_frame, bg='#f0f0f0')
        self.header_frame.pack(fill=tk.X, pady=(0, 25))
        
        # タイトル（さらにサイズ縮小）
        self.title_label = tk.Label(self.header_frame, text="✨ STAR感動分析", 
                                   font=self.get_safe_font(14, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        self.title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 設定ボタンエリア
        settings_frame = tk.Frame(self.header_frame, bg='#f0f0f0')
        settings_frame.pack(side=tk.RIGHT)
        
        # ダークモード切り替えボタン（サイズ縮小）
        self.theme_button = tk.Button(settings_frame, text="🌙", 
                                     command=self.toggle_theme,
                                     bg='#555555', fg='white', font=('Arial', 10),
                                     width=2, height=1, relief=tk.FLAT)
        self.theme_button.pack(side=tk.RIGHT, padx=(5, 10))
        
        # STAR理論学習ボタン（ヘルプボタンの近くに移動）
        self.theory_button = tk.Button(settings_frame, text="📚", 
                                     command=self.show_theory_help,
                                     bg='#17a2b8', fg='white', font=('Arial', 10),
                                     width=2, height=1, relief=tk.FLAT)
        self.theory_button.pack(side=tk.RIGHT, padx=(0, 5))
        ToolTip(self.theory_button, "STAR理論を学ぶ", self)
        
        # ヘルプボタン（サイズ縮小）
        self.help_button = tk.Button(settings_frame, text="❓", 
                                    command=self.show_help,
                                    bg='#4a90e2', fg='white', font=('Arial', 10),
                                    width=2, height=1, relief=tk.FLAT)
        self.help_button.pack(side=tk.RIGHT, padx=(0, 5))
        
    def setup_main_work_area(self):
        """メイン作業エリア（リサイズ可能な分割ウィンドウ）"""
        # PanedWindowで上下分割（リサイズ可能）
        self.main_paned = tk.PanedWindow(self.main_frame, orient=tk.VERTICAL, sashwidth=8, 
                                        sashrelief=tk.RAISED, bg='#e0e0e0')
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # 上部パネル：入力エリア
        self.input_panel = tk.Frame(self.main_paned, bg='#f0f0f0')
        self.main_paned.add(self.input_panel, minsize=150)  # 最小サイズ150px
        
        # 下部パネル：結果エリア
        self.results_panel = tk.Frame(self.main_paned, bg='#f0f0f0')
        self.main_paned.add(self.results_panel, minsize=200)  # 最小サイズ200px
        
        # 各エリアのセットアップ
        self.setup_input_area()
        self.setup_tabbed_results()
        
    def setup_input_area(self):
        """段階1: 直感的な入力エリア"""
        # 入力セクションフレーム
        input_section = tk.LabelFrame(self.input_panel, text="📝 感動体験を入力してください", 
                                    font=self.get_safe_font(14, 'bold'), bg='#f0f0f0', fg='#2c3e50',
                                    padx=20, pady=15)
        input_section.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # テキスト入力エリア（リサイズ可能）
        text_frame = tk.Frame(input_section, bg='#f0f0f0')
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 10))
        
        # 入力ボックス（リサイズ可能）
        theme = self.themes[self.current_theme]
        self.text_input = scrolledtext.ScrolledText(text_frame, 
                                                  height=4, 
                                                  font=self.get_safe_font(12),
                                                  wrap=tk.WORD,
                                                  bg=theme['input_bg'], fg=theme['input_fg'],
                                                  relief=tk.SOLID, borderwidth=2,
                                                  insertwidth=2)  # カーソルの太さを設定
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # IME入力時のフォントを統一するための設定
        try:
            # Windows環境でのIME設定を統一
            self.text_input.tk.call('tk', 'scaling', 1.0)  # スケーリングを統一
            # フォントの明示的な設定
            font_config = self.get_safe_font(12)
            if isinstance(font_config, tuple):
                self.text_input.configure(font=font_config)
        except Exception:
            pass  # フォント設定エラーをスキップ
        
        # プレースホルダーテキスト（灰色で表示）
        placeholder_text = "例: この料理、本当においしい！素晴らしい味でした。"
        self.text_input.insert("1.0", placeholder_text)
        self.text_input.config(fg='#999999', insertbackground='#999999')  # 灰色で表示
        self.text_input.bind("<FocusIn>", self.clear_placeholder)
        self.text_input.bind("<FocusOut>", self.add_placeholder)
        self.text_input.bind("<KeyPress>", self.on_key_press)  # キー入力時の処理
        self.placeholder_active = True
        
        # ボタンと情報エリア
        control_frame = tk.Frame(input_section, bg='#f0f0f0')
        control_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 左側：ボタンエリア
        button_frame = tk.Frame(control_frame, bg='#f0f0f0')
        button_frame.pack(side=tk.LEFT)
        
        # 分析ボタン
        self.analyze_button = tk.Button(button_frame, text="🔍 感動を分析する", 
                                      command=self.analyze_text,
                                      font=self.get_safe_font(14, 'bold'),
                                      bg='#4a90e2', fg='white',
                                      padx=20, pady=8, relief=tk.FLAT)
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # クリアボタン
        self.clear_button = tk.Button(button_frame, text="🗑️ クリア", 
                                    command=self.clear_text,
                                    font=self.get_safe_font(12),
                                    bg='#dc3545', fg='white',
                                    padx=15, pady=8, relief=tk.FLAT)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 詳細入力支援ボタン（短文対応）
        self.enhance_button = tk.Button(button_frame, text="💡 詳しく入力", 
                                      command=self.show_enhancement_dialog,
                                      font=self.get_safe_font(12),
                                      bg='#17a2b8', fg='white',
                                      padx=15, pady=8, relief=tk.FLAT)
        self.enhance_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # エクスポートボタン（メモ保存の隣に移動）
        self.export_button = tk.Button(button_frame, text="📤 エクスポート", 
                                     command=self.export_results,
                                     font=self.get_safe_font(12),
                                     bg='#fd7e14', fg='white',
                                     padx=15, pady=8, relief=tk.FLAT)
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # エクスポート先表示ラベル
        self.export_status_label = tk.Label(button_frame, text="出力先: analysis/", 
                                           font=self.get_safe_font(12),
                                           bg='#f0f0f0', fg='#666666')
        self.export_status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 右側：情報表示エリア
        info_frame = tk.Frame(control_frame, bg='#f0f0f0')
        info_frame.pack(side=tk.RIGHT)
        
        # 文字数カウント
        self.char_count_label = tk.Label(info_frame, text="文字数: 0", 
                                       font=self.get_safe_font(12),
                                       bg='#f0f0f0', fg='#666666')
        self.char_count_label.pack(side=tk.RIGHT, padx=(0, 15))
        
        # 文字数更新バインド
        self.text_input.bind('<KeyRelease>', self.update_char_count)
        self.text_input.bind('<Button-1>', self.update_char_count)
        
    def setup_tabbed_results(self):
        """段階2: 統合結果表示エリア（一画面表示）"""
        # 結果セクションフレーム
        results_section = tk.LabelFrame(self.results_panel, text="📊 分析結果", 
                                      font=self.get_safe_font(15, 'bold'), bg='#f0f0f0', fg='#2c3e50',
                                      padx=10, pady=10)
        results_section.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 結果を横に3分割（概要・詳細・グラフ）
        theme = self.themes[self.current_theme]
        main_results_frame = tk.Frame(results_section, bg=theme['bg'])
        main_results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左側：概要結果（コンパクト・固定幅）
        self.overview_frame = tk.LabelFrame(main_results_frame, text="🎯 概要", 
                                          font=self.get_safe_font(13, 'bold'), bg=theme['panel_bg'], fg=theme['panel_fg'],
                                          width=250)
        self.overview_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 5))
        self.overview_frame.pack_propagate(False)  # 固定幅を維持
        
        # 中央：詳細分析（拡大表示）
        self.details_frame = tk.LabelFrame(main_results_frame, text="🔍 詳細", 
                                         font=self.get_safe_font(14, 'bold'), bg=theme['panel_bg'], fg=theme['panel_fg'])
        self.details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 右側：グラフ（拡大表示）
        self.charts_frame = tk.LabelFrame(main_results_frame, text="📊 グラフ", 
                                        font=self.get_safe_font(14, 'bold'), bg=theme['panel_bg'], fg=theme['panel_fg'])
        self.charts_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 各セクションのセットアップ
        self.setup_overview_section()
        self.setup_details_section()
        self.setup_charts_section()
        
    def setup_overview_section(self):
        """概要セクション - コンパクト表示"""
        theme = self.themes[self.current_theme]
        # メイン結果表示（コンパクト）
        result_card = tk.Frame(self.overview_frame, bg=theme['input_bg'], relief=tk.RAISED, borderwidth=1)
        result_card.pack(fill=tk.X, padx=8, pady=8)
        
        # 主要カテゴリ表示（サイズ縮小）
        self.main_category_label = tk.Label(result_card, text="分析結果がここに表示されます", 
                                          font=self.get_safe_font(13, 'bold'), 
                                          bg=theme['input_bg'], fg=theme['input_fg'])
        self.main_category_label.pack(pady=8)
        
        # 信頼度表示
        self.confidence_label = tk.Label(result_card, text="", 
                                       font=self.get_safe_font(12), 
                                       bg=theme['input_bg'], fg=theme['input_fg'])
        self.confidence_label.pack(pady=(0, 8))
        
        # スコアバー表示（コンパクト）
        theme = self.themes[self.current_theme]
        self.score_bars_frame = tk.Frame(self.overview_frame, bg=theme['panel_bg'])
        self.score_bars_frame.pack(fill=tk.X, padx=8, pady=3)
        
        # 簡潔な解説（文字サイズ拡大）
        theme = self.themes[self.current_theme]
        self.quick_explanation = tk.Text(self.overview_frame, height=3, font=self.get_safe_font(12), 
                                       wrap=tk.WORD, bg=theme['input_bg'], fg=theme['input_fg'],
                                       relief=tk.SOLID, borderwidth=1, state=tk.DISABLED)
        self.quick_explanation.pack(fill=tk.BOTH, expand=True, padx=8, pady=(3, 8))
        
    def setup_details_section(self):
        """詳細セクション - コンパクト表示"""
        theme = self.themes[self.current_theme]
        
        # キーワード分析（拡大表示）
        keywords_frame = tk.LabelFrame(self.details_frame, text="🔑 キーワード", 
                                     font=self.get_safe_font(13, 'bold'), bg=theme['panel_bg'], fg=theme['panel_fg'])
        keywords_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.detailed_keywords_text = tk.Text(keywords_frame, height=4, font=self.get_safe_font(12),
                                            wrap=tk.WORD, bg=theme['input_bg'], fg=theme['input_fg'],
                                            relief=tk.FLAT, state=tk.DISABLED)
        self.detailed_keywords_text.pack(fill=tk.X, padx=5, pady=5)
        
        # 文構造解析（拡大表示）
        structure_frame = tk.LabelFrame(self.details_frame, text="📝 文構造", 
                                      font=self.get_safe_font(13, 'bold'), bg=theme['panel_bg'], fg=theme['panel_fg'])
        structure_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # スクロール可能なテキストエリア
        structure_frame_container = tk.Frame(structure_frame, bg=theme['panel_bg'])
        structure_frame_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.structure_text = tk.Text(structure_frame_container, height=4, font=self.get_safe_font(12),
                                    wrap=tk.WORD, bg=theme['input_bg'], fg=theme['input_fg'],
                                    relief=tk.FLAT, state=tk.DISABLED)
        structure_scrollbar = tk.Scrollbar(structure_frame_container, orient=tk.VERTICAL, command=self.structure_text.yview)
        self.structure_text.config(yscrollcommand=structure_scrollbar.set)
        
        self.structure_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        structure_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 感情強度解析（拡大表示）
        intensity_frame = tk.LabelFrame(self.details_frame, text="💝 感情強度", 
                                      font=self.get_safe_font(13, 'bold'), bg=theme['panel_bg'], fg=theme['panel_fg'])
        intensity_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.intensity_text = tk.Text(intensity_frame, height=5, font=self.get_safe_font(12),
                                    wrap=tk.WORD, bg=theme['input_bg'], fg=theme['input_fg'],
                                    relief=tk.FLAT, state=tk.DISABLED)
        self.intensity_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def setup_charts_section(self):
        """グラフセクション - コンパクト表示"""
        # グラフ表示エリア
        theme = self.themes[self.current_theme]
        self.charts_container = tk.Frame(self.charts_frame, bg=theme['panel_bg'])
        self.charts_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # 新しいUIのヘルパーメソッド
    def clear_placeholder(self, event):
        """プレースホルダーテキストのクリア"""
        if self.placeholder_active:
            self.text_input.delete("1.0", tk.END)
            theme = self.themes[self.current_theme]
            self.text_input.config(fg=theme['input_fg'], insertbackground=theme['input_fg'],
                                 font=self.get_safe_font(12), insertwidth=2)
            self.placeholder_active = False
            self.update_char_count()
    
    def add_placeholder(self, event):
        """プレースホルダーテキストの追加"""
        if not self.text_input.get("1.0", tk.END).strip():
            placeholder_text = "例: この料理、本当においしい！素晴らしい味でした。"
            self.text_input.insert("1.0", placeholder_text)
            self.text_input.config(fg='#999999', insertbackground='#999999',
                                 font=self.get_safe_font(12), insertwidth=2)
            self.placeholder_active = True
            self.update_char_count()
    
    def on_key_press(self, event):
        """キー入力時の処理"""
        if self.placeholder_active:
            self.clear_placeholder(event)
    
    def clear_text(self):
        """テキストのクリア"""
        self.text_input.delete("1.0", tk.END)
        self.add_placeholder(None)
        self.update_char_count()
    
    def update_char_count(self, event=None):
        """文字数カウントの更新"""
        text = self.text_input.get("1.0", tk.END).strip()
        if self.placeholder_active:
            count = 0
        else:
            count = len(text)
        self.char_count_label.config(text=f"文字数: {count}")
        return count
    
    def show_help(self):
        """ヘルプダイアログの表示"""
        help_text = """✨ STAR感動分析システム ヘルプ

🎯 本システムの目的：
このツールは感動体験の分類・分析を専門としており、
感動を含まない一般的な文章の分析には適していません。

📝 使い方：
1. 感動体験を入力欄に入力してください
2. 「感動を分析する」ボタンをクリック
3. 結果を確認（概要・詳細・グラフ）

📊 画面の説明：
• 概要：主要な分析結果と信頼度
• 詳細：キーワードと文構造の詳細分析  
• グラフ：STAR分類の視覚的表示

📚 STAR理論：
感動を4つの要素で分類する理論
• SENSE：五感による感動
• THINK：知見拡大による感動
• ACT：体験拡大による感動
• RELATE：関係拡大による感動

📖 参考文献：
『感動のメカニズム 心を動かすWork&Lifeのつくり方』
前野 隆司 (著)

このシステムは上記理論に基づいて開発されています。"""
        
        messagebox.showinfo("ヘルプ - STAR分析システム", help_text)
    
    def show_theory_help(self):
        """STAR理論の詳細ヘルプ"""
        theory_text = """📚 STAR理論の詳細解説

🎯 STAR + FEEL理論とは：
感動体験を4つの基本要素に分類する理論です。

🔸 SENSE + FEEL（五感による感動）
• 文型：SV型（主語＋動詞）
• 特徴：美、味、匂い、触覚、音などの感覚的体験
• 例：「この料理、おいしい！」

🔸 THINK + FEEL（知見拡大による感動）  
• 文型：SV型（主語＋動詞）
• 特徴：理解、発見、納得、学習による感動
• 例：「やっと問題が解けた！」

🔸 ACT + FEEL（体験拡大による感動）
• 文型：SOV型（主語＋目的語＋動詞）
• 特徴：努力、達成、成長、挑戦による感動
• 例：「マラソンを完走できた！」

🔸 RELATE + FEEL（関係拡大による感動）
• 文型：SOV型（主語＋目的語＋動詞）
• 特徴：愛、絆、感謝、共感による感動
• 例：「友達に励まされて嬉しい」

📖 理論的根拠：
「感動のStar分析とはなにか」「STAR分析フレームワーク」に基づく"""
        
        messagebox.showinfo("STAR理論 - 詳細解説", theory_text)
    
    def export_results(self):
        """分析結果のエクスポート"""
        if not self.current_result:
            messagebox.showwarning("エクスポート", "エクスポートする分析結果がありません。")
            return
        
        # 簡単なテキストエクスポート
        import datetime
        import os
        
        result_text = f"""STAR分析結果エクスポート
        
分析日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
入力テキスト: {self.text_input.get('1.0', tk.END).strip()}

主要カテゴリ: {self.current_result.primary_category}
信頼度: {self.current_result.confidence}

カテゴリ別スコア:
- SENSE: {self.current_result.scores['SENSE']:.2f}
- THINK: {self.current_result.scores['THINK']:.2f}  
- ACT: {self.current_result.scores['ACT']:.2f}
- RELATE: {self.current_result.scores['RELATE']:.2f}

文型: {self.current_result.sentence_type}
検出キーワード: {', '.join(self.current_result.keywords)}
"""
        
        try:
            # analysisフォルダが存在しない場合は作成
            analysis_dir = "analysis"
            if not os.path.exists(analysis_dir):
                os.makedirs(analysis_dir)
            
            filename = f"star_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join(analysis_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(result_text)
            
            # 絶対パスを取得
            absolute_path = os.path.abspath(filepath)
            
            # CUIにログ出力（C:からの絶対パス）
            pass  # エクスポート完了
            
            # エクスポート先表示ラベルを更新
            self.export_status_label.config(text=f"出力先: {filepath}")
            
            messagebox.showinfo("エクスポート完了", f"結果を {filepath} に保存しました。")
        except Exception as e:
            # エラー時もCUIにログ出力
            pass  # エクスポートエラー
            messagebox.showerror("エクスポートエラー", f"エクスポートに失敗しました: {e}")
    
    def setup_plot_canvas(self, parent):
        """グラフ表示キャンバスのセットアップ"""
        # Matplotlib Figure（横幅を縮小）
        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 初期状態のプロット
        self.plot_initial_state()
        
    def plot_initial_state(self):
        """初期状態のプロット表示"""
        # figが存在しない場合は何もしない
        if not hasattr(self, 'fig') or self.fig is None:
            return
            
        # テーマに応じた色設定
        theme = self.themes[self.current_theme]
        self.fig.patch.set_facecolor(theme['bg'])
        
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(theme['panel_bg'])
        
        bbox_color = theme['accent'] if self.current_theme == 'dark' else 'lightblue'
        ax.text(0.5, 0.5, 'テキストを入力して\n「感動を分析する」ボタンを\nクリックしてください', 
                ha='center', va='center', fontsize=14, color=theme['fg'],
                bbox=dict(boxstyle="round,pad=0.3", facecolor=bbox_color, alpha=0.8))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        self.canvas.draw()
        
    def analyze_text(self):
        """テキスト分析の実行（新UI対応）"""
        text = self.text_input.get("1.0", tk.END).strip()
        
        # プレースホルダーテキストの確認
        if self.placeholder_active or not text:
            messagebox.showwarning("警告", "分析するテキストを入力してください。")
            return
            
        try:
            # 分析実行
            result = self.analyzer.analyze(text)
            
            # 現在の結果を保存（エクスポート機能用）
            self.current_result = result
            
            # 分析品質チェックと対応提案
            self.check_analysis_quality(result)
            
            # 新しい統合レイアウトで結果を表示
            self.update_overview_section(result)
            self.update_details_section(result)
            self.update_charts_section(result)
            
        except Exception as e:
            messagebox.showerror("エラー", f"分析中にエラーが発生しました：\n{str(e)}")
    
    def check_analysis_quality(self, result):
        """分析品質チェックと改善提案"""
        quality = result.detailed_analysis.get('analysis_quality', {})
        
        if quality.get('text_category') == 'short' and quality.get('reliability') == 'low':
            # 短文で信頼度が低い場合の通知
            response = messagebox.askyesno(
                "分析精度について",
                "短いテキストのため分析精度が限定的です。\n\n「💡 詳しく入力」ボタンで詳細な情報を追加しませんか？",
                icon='question'
            )
            if response:
                self.show_enhancement_dialog()
                
        elif 'segment_analysis' in quality.get('alternative_approaches', []):
            # 長文で複数感情混在の場合
            messagebox.showinfo(
                "分析結果について", 
                "複数の感動体験が混在している可能性があります。\n\n文章を分けて個別に分析することをお勧めします。"
            )
    
    def show_enhancement_dialog(self):
        """入力内容詳細化ダイアログ（STAR理論準拠）"""
        dialog = tk.Toplevel(self.root)
        dialog.title("感動体験の詳細入力")
        dialog.geometry("900x600")  # 横幅を大幅に拡大（750→900）
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # ダイアログの中央配置
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (900 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"900x600+{x}+{y}")
        
        # テーマ適用
        theme = self.themes[self.current_theme]
        dialog.configure(bg=theme['bg'])
        
        # 説明ラベル
        info_label = tk.Label(dialog, 
                            text="感動体験をより詳しく教えてください（STAR理論に基づく質問）",
                            font=self.get_safe_font(13, 'bold'),
                            bg=theme['bg'], fg=theme['fg'], wraplength=800)
        info_label.pack(pady=10)
        
        # スクロール可能なフレーム
        canvas = tk.Canvas(dialog, bg=theme['bg'])
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=theme['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 5))
        scrollbar.pack(side="right", fill="y", padx=(0, 15))
        
        # 質問フレーム（スクロール可能フレーム内）
        questions_frame = scrollable_frame
        
        # STAR理論に基づく質問
        questions = [
            ("🎨 どのような感覚的な体験でしたか？", "感覚・美しさ・味・音・触感など"),
            ("💡 どのような発見や理解がありましたか？", "新しい知識・気づき・納得など"), 
            ("🎯 どのような行動や達成がありましたか？", "努力・成果・成長・挑戦など"),
            ("🤝 どのような人との関わりがありましたか？", "感謝・協力・絆・共感など")
        ]
        
        self.enhancement_entries = []
        
        for i, (question, hint) in enumerate(questions):
            # 質問ラベル
            q_label = tk.Label(questions_frame, text=question,
                             font=self.get_safe_font(12, 'bold'),
                             bg=theme['bg'], fg=theme['fg'], anchor='w')
            q_label.pack(fill=tk.X, pady=(10, 2))
            
            # 入力フィールド
            entry = tk.Text(questions_frame, height=3, font=self.get_safe_font(12),
                          bg=theme['input_bg'], fg=theme['input_fg'],
                          relief=tk.SOLID, borderwidth=1, wrap=tk.WORD,
                          insertwidth=2)
            entry.pack(fill=tk.X, pady=(0, 5), padx=(10, 15))
            
            # IME入力時のフォントを統一するための設定
            try:
                font_config = self.get_safe_font(12)
                if isinstance(font_config, tuple):
                    entry.configure(font=font_config)
            except:
                pass
            
            # ヒント
            hint_label = tk.Label(questions_frame, text=f"例: {hint}",
                                font=self.get_safe_font(12), 
                                bg=theme['bg'], fg='#888888', anchor='w')
            hint_label.pack(fill=tk.X, pady=(0, 5))
            
            self.enhancement_entries.append(entry)
        
        # ボタンフレーム（縦配置）
        button_frame = tk.Frame(dialog, bg=theme['bg'])
        button_frame.pack(fill=tk.X, pady=15)
        
        # ボタンを中央に配置するためのコンテナ
        button_container = tk.Frame(button_frame, bg=theme['bg'])
        button_container.pack()
        
        # 統一されたボタンサイズ設定
        button_width = 12
        button_height = 2
        
        # 適用ボタン
        apply_button = tk.Button(button_container, text="📝 追加",
                               command=lambda: self.apply_enhancement(dialog),
                               font=self.get_safe_font(12),
                               bg='#28a745', fg='white', relief=tk.FLAT,
                               width=button_width, height=button_height)
        apply_button.pack(pady=(0, 8))
        
        # キャンセルボタン
        cancel_button = tk.Button(button_container, text="キャンセル",
                                command=dialog.destroy,
                                font=self.get_safe_font(12),
                                bg='#6c757d', fg='white', relief=tk.FLAT,
                                width=button_width, height=button_height)
        cancel_button.pack()
    
    def apply_enhancement(self, dialog):
        """詳細情報の適用"""
        # 現在のテキストを取得
        current_text = self.text_input.get("1.0", tk.END).strip()
        if self.placeholder_active:
            current_text = ""
        
        # 各カテゴリの入力を収集
        enhancements = []
        categories = ["SENSE", "THINK", "ACT", "RELATE"]
        
        for i, entry in enumerate(self.enhancement_entries):
            content = entry.get("1.0", tk.END).strip()
            if content:
                enhancements.append(f"【{categories[i]}】{content}")
        
        if enhancements:
            # 詳細情報を元のテキストに追加
            if current_text:
                enhanced_text = current_text + "\n\n" + "\n".join(enhancements)
            else:
                enhanced_text = "\n".join(enhancements)
            
            # テキストエリアに設定
            self.text_input.delete("1.0", tk.END)
            self.text_input.insert("1.0", enhanced_text)
            
            # プレースホルダー状態を解除
            theme = self.themes[self.current_theme]
            self.text_input.config(fg=theme['input_fg'], insertbackground=theme['input_fg'])
            self.placeholder_active = False
            
            # 文字数更新
            self.update_char_count()
            
            dialog.destroy()
            
            # 自動分析実行
            messagebox.showinfo("完了", "詳細情報が追加されました。\n分析を実行します。")
            self.analyze_text()
        else:
            messagebox.showwarning("警告", "少なくとも1つの項目に入力してください。")
    
    def update_overview_section(self, result):
        """概要セクションの更新"""
        # 主要カテゴリ表示
        category_emoji = {
            'SENSE': '🎨', 'THINK': '💡', 'ACT': '🎯', 'RELATE': '🤝'
        }
        emoji = category_emoji.get(result.primary_category, '🎯')
        self.main_category_label.config(
            text=f"{emoji} {result.primary_category} + FEEL",
            fg=self.themes[self.current_theme]['accent']
        )
        
        # 信頼度表示（詳細化）
        confidence_details = getattr(self.analyzer, 'last_confidence_details', {})
        confidence_text = f"信頼度: {result.confidence}"
        
        # 詳細情報がある場合は追加表示
        if confidence_details:
            score_diff = confidence_details.get('score_diff', 0)
            keyword_count = confidence_details.get('keyword_count', 0)
            confidence_text += f" (差: {score_diff:.2f}, キーワード: {keyword_count}個)"
            
        self.confidence_label.config(text=confidence_text)
        
        # 一言解説
        self.quick_explanation.config(state=tk.NORMAL)
        self.quick_explanation.delete("1.0", tk.END)
        
        explanation = self.generate_quick_explanation(result)
        self.quick_explanation.insert("1.0", explanation)
        self.quick_explanation.config(state=tk.DISABLED)
        
        # スコアバーの更新
        self.update_score_bars(result)
    
    def update_details_section(self, result):
        """詳細セクションの更新"""
        # キーワード分析
        self.detailed_keywords_text.config(state=tk.NORMAL)
        self.detailed_keywords_text.delete("1.0", tk.END)
        
        keyword_analysis = f"検出: {', '.join(result.keywords[:3]) if result.keywords else 'なし'}...\n" \
                          f"SENSE: {result.scores['SENSE']:.1f} | THINK: {result.scores['THINK']:.1f}\n" \
                          f"ACT: {result.scores['ACT']:.1f} | RELATE: {result.scores['RELATE']:.1f}"
        
        self.detailed_keywords_text.insert("1.0", keyword_analysis)
        self.detailed_keywords_text.config(state=tk.DISABLED)
        
        # 文構造解析
        self.structure_text.config(state=tk.NORMAL)
        self.structure_text.delete("1.0", tk.END)
        
        structure_analysis = f"文型: {result.sentence_type}\n" \
                           f"構造: {result.structure_pattern}\n" \
                           f"長さ: {result.detailed_analysis['text_length']}文字"
        
        self.structure_text.insert("1.0", structure_analysis)
        self.structure_text.config(state=tk.DISABLED)
        
        # 感情強度解析
        self.intensity_text.config(state=tk.NORMAL)
        self.intensity_text.delete("1.0", tk.END)
        
        feel_score = result.detailed_analysis.get('feel_score', 0)
        feel_indicators = result.detailed_analysis.get('feel_indicators', [])
        
        # 信頼度詳細情報を追加
        confidence_details = getattr(self.analyzer, 'last_confidence_details', {})
        analysis_factors = []
        
        if confidence_details:
            analysis_factors.append(f"スコア差: {confidence_details.get('score_diff', 0):.3f}")
            analysis_factors.append(f"最高スコア: {confidence_details.get('max_score', 0):.3f}")
            analysis_factors.append(f"検出キーワード: {confidence_details.get('keyword_count', 0)}個")
        
        intensity_analysis = f"FEEL: {feel_score:.2f}/2.0\n" \
                           f"感情表現: {', '.join(feel_indicators[:2]) if feel_indicators else 'なし'}...\n" \
                           f"強度: {result.detailed_analysis['emotion_intensity']:.2f}\n" \
                           f"分析根拠: {', '.join(analysis_factors[:2]) if analysis_factors else 'パターンベース'}"
        
        self.intensity_text.insert("1.0", intensity_analysis)
        self.intensity_text.config(state=tk.DISABLED)
    
    def update_charts_section(self, result):
        """グラフセクションの更新"""
        # 既存のチャートをクリア
        for widget in self.charts_container.winfo_children():
            widget.destroy()
        
        # 新しいグラフを作成
        self.setup_plot_canvas(self.charts_container)
        self.plot_results(result)
    
    def generate_quick_explanation(self, result):
        """クイック解説の生成"""
        category = result.primary_category
        sentence_type = result.sentence_type
        
        explanations = {
            'SENSE': f"五感による感動体験です。{sentence_type}の文型で、美しさや味覚などの感覚的な要素が表現されています。",
            'THINK': f"知的発見による感動体験です。{sentence_type}の文型で、理解や納得などの知見拡大が感動の源泉です。",
            'ACT': f"達成による感動体験です。{sentence_type}の文型で、努力の結果や成長が感動を生み出しています。",
            'RELATE': f"関係性による感動体験です。{sentence_type}の文型で、人とのつながりや絆が感動の核となっています。"
        }
        
        base_explanation = explanations.get(category, "感動体験が検出されました。")
        
        # 信頼度詳細を追加
        confidence_details = getattr(self.analyzer, 'last_confidence_details', {})
        confidence_note = ""
        
        if result.confidence == "低":
            if confidence_details.get('short_text_penalty'):
                confidence_note = "短いテキストのため分析精度が限定的です。"
            elif confidence_details.get('no_keywords_penalty'):
                confidence_note = "キーワードが少ないため推定結果です。"
            else:
                confidence_note = "複数カテゴリの可能性があります。"
        
        feel_score = result.detailed_analysis.get('feel_score', 0)
        if feel_score > 1.5:
            feel_note = "非常に強い感情の高ぶりが感じられます。"
        elif feel_score > 1.0:
            feel_note = "適度な感情の高ぶりが表現されています。"
        else:
            feel_note = "穏やかな感情表現です。"
        
        explanation = f"{base_explanation}\n\n{feel_note}\n\nFEEL要素（感情の高ぶり）により、{category}の体験が感動として完成しています。"
        
        if confidence_note:
            explanation += f"\n\n【注意】{confidence_note}"
        
        return explanation
    
    def update_score_bars(self, result):
        """スコアバーの更新"""
        # 既存のスコアバーをクリア
        for widget in self.score_bars_frame.winfo_children():
            widget.destroy()
        
        categories = ['SENSE', 'THINK', 'ACT', 'RELATE']
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        max_score = max(result.scores.values()) if any(result.scores.values()) else 1
        
        for i, (category, color) in enumerate(zip(categories, colors)):
            score = result.scores[category]
            
            # カテゴリラベル
            theme = self.themes[self.current_theme]
            label_frame = tk.Frame(self.score_bars_frame, bg=theme['panel_bg'])
            label_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(label_frame, text=category, font=self.get_safe_font(12, 'bold'),
                    bg=theme['panel_bg'], fg=theme['panel_fg'], width=8).pack(side=tk.LEFT)
            
            # スコアバー
            bar_frame = tk.Frame(label_frame, bg='#e0e0e0', height=20, relief=tk.SUNKEN, borderwidth=1)
            bar_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
            
            if score > 0:
                bar_width = int((score / max_score) * 200) if max_score > 0 else 0
                score_bar = tk.Frame(bar_frame, bg=color, height=18)
                score_bar.place(x=1, y=1, width=bar_width)
            
            # スコア値
            tk.Label(label_frame, text=f"{score:.2f}", font=self.get_safe_font(12),
                    bg=theme['panel_bg'], fg=theme['panel_fg'], width=6).pack(side=tk.RIGHT)
            
    def plot_results(self, result):
        """分析結果のグラフ表示（FEEL要素を含む）"""
        # figが存在しない場合は何もしない
        if not hasattr(self, 'fig') or self.fig is None:
            return
            
        self.fig.clear()
        
        # テーマに応じた色とスタイル設定
        theme = self.themes[self.current_theme]
        colors = theme['chart_colors']
        text_color = theme['fg']
        
        # 図全体の背景色設定
        self.fig.patch.set_facecolor(theme['bg'])
        
        # 3つのサブプロット作成
        ax1 = self.fig.add_subplot(2, 2, 1)
        ax2 = self.fig.add_subplot(2, 2, 2)
        ax3 = self.fig.add_subplot(2, 1, 2)
        
        # サブプロットの背景色とテキスト色設定
        for ax in [ax1, ax2, ax3]:
            ax.set_facecolor(theme['panel_bg'])
            ax.tick_params(colors=text_color)
            ax.spines['bottom'].set_color(text_color)
            ax.spines['top'].set_color(text_color)
            ax.spines['right'].set_color(text_color)
            ax.spines['left'].set_color(text_color)
        
        # 円グラフ - STAR要素
        categories = list(result.scores.keys())
        values = list(result.scores.values())
        
        # 0でない値のみ表示
        non_zero_indices = [i for i, v in enumerate(values) if v > 0]
        if non_zero_indices:
            filtered_categories = [categories[i] for i in non_zero_indices]
            filtered_values = [values[i] for i in non_zero_indices]
            filtered_colors = [colors[i] for i in non_zero_indices]
            
            wedges, texts, autotexts = ax1.pie(filtered_values, labels=filtered_categories, 
                                              colors=filtered_colors, autopct='%1.1f%%',
                                              startangle=90, textprops={'color': text_color})
            ax1.set_title(f'STAR分析結果\n(主分類: {result.primary_category})', 
                         fontsize=10, fontweight='bold', color=text_color)
        else:
            ax1.text(0.5, 0.5, '感動要素が\n検出されませんでした', ha='center', va='center', color=text_color)
            ax1.set_title('STAR分析結果', fontsize=10, fontweight='bold', color=text_color)
        
        # FEEL要素の可視化
        feel_score = result.detailed_analysis.get('feel_score', 0)
        feel_max = 2.0  # 最大値
        
        # FEEL要素のドーナツチャート
        if feel_score > 0:
            feel_values = [feel_score, feel_max - feel_score]
            feel_colors = ['#FF69B4', '#E0E0E0'] if self.current_theme == 'light' else ['#FF69B4', '#555555']
            feel_labels = ['FEEL', '']
            
            wedges, texts, autotexts = ax2.pie(feel_values, labels=feel_labels,
                                              colors=feel_colors, autopct='',
                                              startangle=90, 
                                              wedgeprops=dict(width=0.5),
                                              textprops={'color': text_color})
            ax2.text(0, 0, f'FEEL\n{feel_score:.2f}', ha='center', va='center', 
                    fontsize=12, fontweight='bold', color=text_color)
            ax2.set_title('FEEL要素\n（感情の高ぶり）', fontsize=10, fontweight='bold', color=text_color)
        else:
            ax2.text(0.5, 0.5, 'FEEL要素\n検出なし', ha='center', va='center', color=text_color)
            ax2.set_title('FEEL要素', fontsize=10, fontweight='bold', color=text_color)
        
        # 総合棒グラフ - STARとFEELの組み合わせ
        all_categories = categories + ['FEEL']
        all_values = values + [feel_score]
        all_colors = colors + ['#FF69B4']
        
        bars = ax3.bar(all_categories, all_values, color=all_colors, alpha=0.7)
        # タイトルを下側に配置（X軸ラベルとして使用）
        ax3.set_xlabel(f'感動の構成要素: {result.primary_category} + FEEL', 
                      fontsize=10, fontweight='bold', color=text_color, labelpad=10)
        ax3.set_ylabel('スコア', color=text_color)
        ax3.set_ylim(0, max(all_values) * 1.2 if max(all_values) > 0 else 1)
        
        # X軸のラベル色を設定
        ax3.tick_params(axis='x', colors=text_color)
        ax3.tick_params(axis='y', colors=text_color)
        
        # バーの上に値を表示（適切な間隔を保つ）
        max_bar_height = max(all_values) if all_values else 0
        for bar, value in zip(bars, all_values):
            if value > 0:
                # タイトルとの重なりを避けるため、高い値の場合は少し下げる
                y_offset = 0.01 if value < max_bar_height * 0.8 else -0.05
                va_align = 'bottom' if value < max_bar_height * 0.8 else 'top'
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + y_offset,
                        f'{value:.2f}', ha='center', va=va_align, color=text_color, fontsize=9)
        
        # 文型判定の表示（テーマ対応）
        bbox_color = theme['accent'] if self.current_theme == 'dark' else 'lightblue'
        ax3.text(0.02, 0.98, f'文型: {result.sentence_type}', 
                transform=ax3.transAxes, va='top', ha='left', color=text_color,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=bbox_color, alpha=0.8))
        
        plt.tight_layout()
        self.canvas.draw()
        
    def toggle_theme(self):
        """ダークモード/ライトモードの切り替え"""
        # テーマを切り替え
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        
        # テーマを適用
        self.apply_theme()
        
        # ボタンテキストを更新
        if self.current_theme == "dark":
            self.theme_button.config(text="☀️")
        else:
            self.theme_button.config(text="🌙")
            
    def apply_theme(self):
        """選択されたテーマを全UIコンポーネントに適用"""
        theme = self.themes[self.current_theme]
        
        # メインウィンドウとフレーム
        self.root.configure(bg=theme['bg'])
        self.main_frame.configure(bg=theme['bg'])
        self.header_frame.configure(bg=theme['bg'])
        
        # タイトル
        self.title_label.configure(bg=theme['bg'], fg=theme['fg'])
        
        # 各セクションのテーマ適用
        self.apply_theme_to_widgets()
        
        # グラフの再描画（テーマ適用）
        if hasattr(self, 'current_result') and self.current_result:
            self.plot_results(self.current_result)
            
    def apply_theme_to_widgets(self):
        """すべてのウィジェットにテーマを適用"""
        theme = self.themes[self.current_theme]
        
        # 手動で主要コンポーネントに直接適用（確実性重視）
        try:
            # テキスト入力エリア
            if hasattr(self, 'text_input'):
                self.text_input.config(bg=theme['input_bg'], fg=theme['input_fg'], 
                                     font=self.get_safe_font(12), insertwidth=2)
            
            # エクスポート状態ラベル
            if hasattr(self, 'export_status_label'):
                self.export_status_label.config(bg=theme['bg'], fg='#666666')
            
            # 詳細タブのテキストエリア
            if hasattr(self, 'detailed_keywords_text'):
                self.detailed_keywords_text.config(bg=theme['input_bg'], fg=theme['input_fg'])
            if hasattr(self, 'structure_text'):
                self.structure_text.config(bg=theme['input_bg'], fg=theme['input_fg'])
            if hasattr(self, 'intensity_text'):
                self.intensity_text.config(bg=theme['input_bg'], fg=theme['input_fg'])
            if hasattr(self, 'quick_explanation'):
                self.quick_explanation.config(bg=theme['input_bg'], fg=theme['input_fg'])
            
            # メインフレームと各セクション
            widgets_to_theme = [
                self.main_frame, self.header_frame, 
            ]
            
            # 各セクションのフレームも手動で追加
            for widget in self.main_frame.winfo_children():
                if widget.winfo_class() in ['Frame', 'LabelFrame']:
                    widgets_to_theme.append(widget)
                    
            # フレームの背景色を直接設定
            for widget in widgets_to_theme:
                try:
                    if widget.winfo_class() == 'LabelFrame':
                        widget.configure(bg=theme['bg'], fg=theme['fg'])
                    else:
                        widget.configure(bg=theme['bg'])
                except:
                    pass
                    
        except:
            pass
        
        # 結果セクションの特別対応
        try:
            if hasattr(self, 'overview_frame'):
                self.overview_frame.configure(bg=theme['panel_bg'], fg=theme['panel_fg'])
            if hasattr(self, 'details_frame'):
                self.details_frame.configure(bg=theme['panel_bg'], fg=theme['panel_fg'])
            if hasattr(self, 'charts_frame'):
                self.charts_frame.configure(bg=theme['panel_bg'], fg=theme['panel_fg'])
            if hasattr(self, 'score_bars_frame'):
                self.score_bars_frame.configure(bg=theme['panel_bg'])
            if hasattr(self, 'charts_container'):
                self.charts_container.configure(bg=theme['panel_bg'])
        except:
            pass
            
        # 再帰的にウィジェットを探してテーマを適用
        def apply_to_widget(widget):
            try:
                widget_class = widget.winfo_class()
                
                if widget_class == 'Frame':
                    # 結果エリア内のフレームは特別な背景色を使用
                    if hasattr(self, 'score_bars_frame') and widget == self.score_bars_frame:
                        widget.configure(bg=theme['panel_bg'])
                    elif hasattr(self, 'charts_container') and widget == self.charts_container:
                        widget.configure(bg=theme['panel_bg'])
                    else:
                        widget.configure(bg=theme['bg'])
                elif widget_class == 'Label':
                    # テーマボタン以外のラベル
                    if widget != self.theme_button:
                        # 結果エリア内のラベルは特別な背景色を使用
                        parent = widget.master
                        if (hasattr(self, 'overview_frame') and self._is_descendant_of(widget, self.overview_frame)) or \
                           (hasattr(self, 'details_frame') and self._is_descendant_of(widget, self.details_frame)) or \
                           (hasattr(self, 'charts_frame') and self._is_descendant_of(widget, self.charts_frame)):
                            widget.configure(bg=theme['panel_bg'], fg=theme['panel_fg'])
                        else:
                            widget.configure(bg=theme['bg'], fg=theme['fg'])
                elif widget_class == 'LabelFrame':
                    # 結果セクションのLabelFrameは特別な背景色を使用
                    if widget in [getattr(self, 'overview_frame', None), 
                                getattr(self, 'details_frame', None), 
                                getattr(self, 'charts_frame', None)]:
                        widget.configure(bg=theme['panel_bg'], fg=theme['panel_fg'])
                    else:
                        widget.configure(bg=theme['bg'], fg=theme['fg'])
                elif widget_class == 'Text':
                    # テキストウィジェットのフォントも統一
                    if widget == getattr(self, 'text_input', None):
                        widget.configure(bg=theme['input_bg'], fg=theme['input_fg'], 
                                       insertbackground=theme['fg'], 
                                       font=self.get_safe_font(12), insertwidth=2)
                    else:
                        # その他のテキストウィジェット
                        current_font = widget.cget('font')
                        if current_font and ('9' in str(current_font) or '10' in str(current_font)):
                            widget.configure(bg=theme['input_bg'], fg=theme['input_fg'], 
                                           insertbackground=theme['fg'], 
                                           font=self.get_safe_font(12), insertwidth=2)
                        else:
                            widget.configure(bg=theme['input_bg'], fg=theme['input_fg'], 
                                           insertbackground=theme['fg'])
                elif widget_class == 'Entry':
                    widget.configure(bg=theme['input_bg'], fg=theme['input_fg'], 
                                   insertbackground=theme['fg'])
                elif widget_class == 'Button':
                    # テーマボタンと機能ボタンの区別
                    if widget == self.theme_button:
                        # テーマボタンは専用色を維持
                        if self.current_theme == "dark":
                            widget.configure(bg='#555555', fg='white')
                        else:
                            widget.configure(bg='#555555', fg='white')
                    else:
                        # その他のボタンは機能色を維持するかテーマに合わせるか判断
                        current_bg = widget.cget('bg')
                        # 基本的な背景色のボタンのみテーマに合わせる
                        if current_bg in ['#f0f0f0', '#2c3e50', '#e8e8e8', '#454f5b', 'SystemButtonFace']:
                            widget.configure(bg=theme['button_bg'], fg=theme['fg'])
                elif widget_class == 'Scrollbar':
                    # スクロールバーの色調整
                    if self.current_theme == 'dark':
                        widget.configure(bg=theme['panel_bg'], troughcolor=theme['bg'])
                    else:
                        widget.configure(bg=theme['panel_bg'], troughcolor=theme['bg'])
                        
                # 子ウィジェットに再帰適用
                for child in widget.winfo_children():
                    apply_to_widget(child)
                    
            except tk.TclError:
                # 一部のウィジェットは設定できない属性がある場合があるのでスキップ
                pass
        
        apply_to_widget(self.root)
    
    def _is_descendant_of(self, widget, parent):
        """ウィジェットが指定した親の子孫かどうかチェック"""
        try:
            current = widget
            while current:
                if current == parent:
                    return True
                current = current.master
            return False
        except:
            return False
    
    def on_closing(self):
        """ウィンドウが閉じられる時の処理"""
        try:
            # matplotlibのfigureがあれば閉じる
            if hasattr(self, 'fig') and self.fig is not None:
                plt.close(self.fig)
            
            # 開いているダイアログがあれば閉じる
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
        except:
            pass
        finally:
            # Tkinterアプリケーションを適切に終了
            self.root.quit()  # mainloopを終了
            self.root.destroy()  # ウィンドウを破棄


def main():
    """メイン関数"""
    try:
        root = tk.Tk()
        app = STARAnalysisGUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        pass  # アプリケーション中断
    except Exception as e:
        pass  # アプリケーションエラー
    finally:
        # 確実にPythonプロセスを終了
        try:
            root.quit()
            root.destroy()
        except:
            pass


if __name__ == "__main__":
    main()