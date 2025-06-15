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
matplotlib.use('TkAgg')  # GUIバックエンドを使用

# 日本語フォント設定
import matplotlib.font_manager as fm
import platform

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
                print(f"日本語フォント設定完了: {font_name}")
                break
            except:
                continue
        else:
            # フォールバック設定
            plt.rcParams['font.family'] = 'DejaVu Sans'
            print("警告: 日本語フォントが見つからないため、英語フォントを使用します")
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
                'bg': '#3a3a3a',
                'fg': '#e0e0e0',
                'accent': '#5dade2',
                'panel_bg': '#4a4a4a',
                'panel_fg': '#e0e0e0',
                'input_bg': '#4a4a4a',
                'input_fg': '#e0e0e0',
                'button_bg': '#5a5a5a',
                'chart_colors': ['#e74c3c', '#1abc9c', '#3498db', '#f39c12']
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
                        print(f"日本語フォントを設定: {font}")
                        break
                
            except Exception as e:
                print(f"フォント設定エラー: {e}")
                self.font_family = "Arial"
        
        print(f"使用フォント: {self.font_family}")
    
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
        self.setup_quick_actions()
        
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
                                                  relief=tk.SOLID, borderwidth=2)
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
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
                                      font=self.get_safe_font(12, 'bold'),
                                      bg='#4a90e2', fg='white',
                                      padx=20, pady=8, relief=tk.FLAT)
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # クリアボタン
        self.clear_button = tk.Button(button_frame, text="🗑️ クリア", 
                                    command=self.clear_text,
                                    font=self.get_safe_font(10),
                                    bg='#dc3545', fg='white',
                                    padx=15, pady=8, relief=tk.FLAT)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 詳細入力支援ボタン（短文対応）
        self.enhance_button = tk.Button(button_frame, text="💡 詳しく入力", 
                                      command=self.show_enhancement_dialog,
                                      font=self.get_safe_font(10),
                                      bg='#17a2b8', fg='white',
                                      padx=15, pady=8, relief=tk.FLAT)
        self.enhance_button.pack(side=tk.LEFT, padx=(0, 10))
        
        
        # エクスポートボタン（メモ保存の隣に移動）
        self.export_button = tk.Button(button_frame, text="📤 エクスポート", 
                                     command=self.export_results,
                                     font=self.get_safe_font(10),
                                     bg='#fd7e14', fg='white',
                                     padx=15, pady=8, relief=tk.FLAT)
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 右側：情報表示エリア
        info_frame = tk.Frame(control_frame, bg='#f0f0f0')
        info_frame.pack(side=tk.RIGHT)
        
        # 文字数カウント
        self.char_count_label = tk.Label(info_frame, text="文字数: 0", 
                                       font=self.get_safe_font(10),
                                       bg='#f0f0f0', fg='#666666')
        self.char_count_label.pack(side=tk.RIGHT, padx=(0, 15))
        
        # 文字数更新バインド
        self.text_input.bind('<KeyRelease>', self.update_char_count)
        self.text_input.bind('<Button-1>', self.update_char_count)
        
    
    def setup_tabbed_results(self):
        """段階2: 統合結果表示エリア（一画面表示）"""
        # 結果セクションフレーム
        results_section = tk.LabelFrame(self.results_panel, text="📊 分析結果", 
                                      font=self.get_safe_font(14, 'bold'), bg='#f0f0f0', fg='#2c3e50',
                                      padx=10, pady=10)
        results_section.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 結果を横に3分割（概要・詳細・グラフ）
        theme = self.themes[self.current_theme]
        main_results_frame = tk.Frame(results_section, bg=theme['bg'])
        main_results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左側：概要結果（コンパクト・固定幅）
        self.overview_frame = tk.LabelFrame(main_results_frame, text="🎯 概要", 
                                          font=self.get_safe_font(11, 'bold'), bg=theme['panel_bg'], fg=theme['panel_fg'],
                                          width=250)
        self.overview_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 5))
        self.overview_frame.pack_propagate(False)  # 固定幅を維持
        
        # 中央：詳細分析（拡大表示）
        self.details_frame = tk.LabelFrame(main_results_frame, text="🔍 詳細", 
                                         font=self.get_safe_font(13, 'bold'), bg=theme['panel_bg'], fg=theme['panel_fg'])
        self.details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 右側：グラフ（拡大表示）
        self.charts_frame = tk.LabelFrame(main_results_frame, text="📊 グラフ", 
                                        font=self.get_safe_font(13, 'bold'), bg=theme['panel_bg'], fg=theme['panel_fg'])
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
                                          font=self.get_safe_font(12, 'bold'), 
                                          bg=theme['input_bg'], fg=theme['input_fg'])
        self.main_category_label.pack(pady=8)
        
        # 信頼度表示
        self.confidence_label = tk.Label(result_card, text="", 
                                       font=self.get_safe_font(9), 
                                       bg=theme['input_bg'], fg=theme['input_fg'])
        self.confidence_label.pack(pady=(0, 8))
        
        # スコアバー表示（コンパクト）
        theme = self.themes[self.current_theme]
        self.score_bars_frame = tk.Frame(self.overview_frame, bg=theme['panel_bg'])
        self.score_bars_frame.pack(fill=tk.X, padx=8, pady=3)
        
        # 簡潔な解説（文字サイズ拡大）
        theme = self.themes[self.current_theme]
        self.quick_explanation = tk.Text(self.overview_frame, height=3, font=self.get_safe_font(11), 
                                       wrap=tk.WORD, bg=theme['input_bg'], fg=theme['input_fg'],
                                       relief=tk.SOLID, borderwidth=1, state=tk.DISABLED)
        self.quick_explanation.pack(fill=tk.BOTH, expand=True, padx=8, pady=(3, 8))
        
    def setup_details_section(self):
        """詳細セクション - コンパクト表示"""
        theme = self.themes[self.current_theme]
        
        # キーワード分析（拡大表示）
        keywords_frame = tk.LabelFrame(self.details_frame, text="🔑 キーワード", 
                                     font=self.get_safe_font(12, 'bold'), bg=theme['panel_bg'], fg=theme['panel_fg'])
        keywords_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.detailed_keywords_text = tk.Text(keywords_frame, height=4, font=self.get_safe_font(11),
                                            wrap=tk.WORD, bg=theme['input_bg'], fg=theme['input_fg'],
                                            relief=tk.FLAT, state=tk.DISABLED)
        self.detailed_keywords_text.pack(fill=tk.X, padx=5, pady=5)
        
        # 文構造解析（拡大表示）
        structure_frame = tk.LabelFrame(self.details_frame, text="📝 文構造", 
                                      font=self.get_safe_font(12, 'bold'), bg=theme['panel_bg'], fg=theme['panel_fg'])
        structure_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # スクロール可能なテキストエリア
        structure_frame_container = tk.Frame(structure_frame, bg=theme['panel_bg'])
        structure_frame_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.structure_text = tk.Text(structure_frame_container, height=4, font=self.get_safe_font(11),
                                    wrap=tk.WORD, bg=theme['input_bg'], fg=theme['input_fg'],
                                    relief=tk.FLAT, state=tk.DISABLED)
        structure_scrollbar = tk.Scrollbar(structure_frame_container, orient=tk.VERTICAL, command=self.structure_text.yview)
        self.structure_text.config(yscrollcommand=structure_scrollbar.set)
        
        self.structure_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        structure_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 感情強度解析（拡大表示）
        intensity_frame = tk.LabelFrame(self.details_frame, text="💝 感情強度", 
                                      font=self.get_safe_font(12, 'bold'), bg=theme['panel_bg'], fg=theme['panel_fg'])
        intensity_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.intensity_text = tk.Text(intensity_frame, height=5, font=self.get_safe_font(11),
                                    wrap=tk.WORD, bg=theme['input_bg'], fg=theme['input_fg'],
                                    relief=tk.FLAT, state=tk.DISABLED)
        self.intensity_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def setup_charts_section(self):
        """グラフセクション - コンパクト表示"""
        # グラフ表示エリア
        theme = self.themes[self.current_theme]
        self.charts_container = tk.Frame(self.charts_frame, bg=theme['panel_bg'])
        self.charts_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_memo_section(self, parent):
        """メモセクション - 下部に配置"""
        # メモセクションフレーム（下部に配置）
        memo_section = tk.LabelFrame(parent, text="📝 メモ・履歴", 
                                   font=self.get_safe_font(11, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        memo_section.pack(fill=tk.X, pady=(10, 0))
        
        # メモ操作ボタン（水平配置）
        memo_controls = tk.Frame(memo_section, bg='#f0f0f0')
        memo_controls.pack(fill=tk.X, padx=10, pady=5)
        
        # メモ保存ボタン
        self.save_memo_button = tk.Button(memo_controls, text="💾 保存", 
                                        command=self.save_current_analysis,
                                        font=self.get_safe_font(9),
                                        bg='#28a745', fg='white', relief=tk.FLAT,
                                        padx=10, pady=3)
        self.save_memo_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # タグ入力（コンパクト）
        tk.Label(memo_controls, text="🏷️", font=self.get_safe_font(9), 
                bg='#f0f0f0', fg='#2c3e50').pack(side=tk.LEFT, padx=(10, 2))
        
        theme = self.themes[self.current_theme]
        self.tag_entry = tk.Entry(memo_controls, font=self.get_safe_font(8), width=15,
                                bg=theme['input_bg'], fg=theme['input_fg'], relief=tk.SOLID, borderwidth=1)
        self.tag_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.tag_entry.insert(0, "タグをカンマ区切りで...")
        self.tag_entry.bind("<FocusIn>", self.clear_tag_placeholder)
        self.tag_entry.bind("<FocusOut>", self.add_tag_placeholder)
        self.tag_placeholder_active = True
        
        # 検索入力（コンパクト）
        tk.Label(memo_controls, text="🔍", font=self.get_safe_font(9), 
                bg='#f0f0f0', fg='#2c3e50').pack(side=tk.LEFT, padx=(10, 2))
        
        self.search_entry = tk.Entry(memo_controls, font=self.get_safe_font(8), width=15,
                                   bg=theme['input_bg'], fg=theme['input_fg'], relief=tk.SOLID, borderwidth=1)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry.bind('<KeyRelease>', self.on_search_changed)
        
        # カテゴリ選択（コンパクト）
        self.search_category_var = tk.StringVar(value="すべて")
        category_combo = ttk.Combobox(memo_controls, textvariable=self.search_category_var,
                                    values=["すべて", "SENSE", "THINK", "ACT", "RELATE"],
                                    width=8, state="readonly", font=self.get_safe_font(8))
        category_combo.pack(side=tk.LEFT)
        category_combo.bind('<<ComboboxSelected>>', self.on_search_changed)
        
    def setup_memo_tab(self):
        """メモ・履歴タブ - メモ機能"""
        theme = self.themes[self.current_theme]
        memo_frame = tk.Frame(self.results_notebook, bg=theme['panel_bg'])
        self.results_notebook.add(memo_frame, text="📝 メモ")
        
        # メモ操作エリア
        memo_operations = tk.Frame(memo_frame, bg=theme['panel_bg'])
        memo_operations.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        # メモ保存ボタン
        self.save_memo_button = tk.Button(memo_operations, text="💾 この分析をメモに保存", 
                                        command=self.save_current_analysis,
                                        font=self.get_safe_font(11),
                                        bg='#28a745', fg='white', relief=tk.FLAT,
                                        padx=15, pady=8)
        self.save_memo_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # タグ入力エリア
        tag_frame = tk.Frame(memo_operations, bg=theme['panel_bg'])
        tag_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Label(tag_frame, text="🏷️", font=self.get_safe_font(12), 
                bg=theme['panel_bg'], fg=theme['panel_fg']).pack(side=tk.LEFT)
        
        theme = self.themes[self.current_theme]
        self.tag_entry = tk.Entry(tag_frame, font=self.get_safe_font(10), width=20,
                                bg=theme['input_bg'], fg=theme['input_fg'], relief=tk.SOLID, borderwidth=1)
        self.tag_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.tag_entry.insert(0, "タグをカンマ区切りで入力...")
        self.tag_entry.bind("<FocusIn>", self.clear_tag_placeholder)
        self.tag_entry.bind("<FocusOut>", self.add_tag_placeholder)
        self.tag_placeholder_active = True
        
        # メモ一覧更新ボタン
        refresh_button = tk.Button(memo_operations, text="🔄 更新", 
                                 command=self.refresh_memo_list,
                                 font=self.get_safe_font(10),
                                 bg='#6c757d', fg='white', relief=tk.FLAT,
                                 padx=10, pady=8)
        refresh_button.pack(side=tk.LEFT)
        
        # 検索機能エリア
        search_frame = tk.Frame(memo_frame, bg=theme['panel_bg'])
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(search_frame, text="🔍 検索:", font=self.get_safe_font(10, 'bold'),
                bg=theme['panel_bg'], fg=theme['panel_fg']).pack(side=tk.LEFT, padx=(0, 10))
        
        # 検索入力
        theme = self.themes[self.current_theme]
        self.search_entry = tk.Entry(search_frame, font=self.get_safe_font(10), width=30,
                                   bg=theme['input_bg'], fg=theme['input_fg'], relief=tk.SOLID, borderwidth=1)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search_changed)
        
        # 検索オプション
        self.search_category_var = tk.StringVar(value="すべて")
        category_combo = ttk.Combobox(search_frame, textvariable=self.search_category_var,
                                    values=["すべて", "SENSE", "THINK", "ACT", "RELATE"],
                                    width=10, state="readonly")
        category_combo.pack(side=tk.LEFT, padx=(0, 10))
        category_combo.bind('<<ComboboxSelected>>', self.on_search_changed)
        
        # 検索クリアボタン
        clear_search_btn = tk.Button(search_frame, text="✕", 
                                   command=self.clear_search,
                                   font=self.get_safe_font(10),
                                   bg='#dc3545', fg='white', relief=tk.FLAT,
                                   width=3)
        clear_search_btn.pack(side=tk.LEFT)
        
        # クイックタグボタン
        quick_tags_frame = tk.Frame(memo_frame, bg=theme['panel_bg'])
        quick_tags_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(quick_tags_frame, text="よく使うタグ:", font=self.get_safe_font(10, 'bold'),
                bg=theme['panel_bg'], fg=theme['panel_fg']).pack(side=tk.LEFT, padx=(0, 10))
        
        # STARカテゴリベースのクイックタグ
        quick_tag_buttons = [
            ("感覚", "#感覚"), ("学び", "#学び"), ("達成", "#達成"), ("感謝", "#感謝"),
            ("美的体験", "#美的体験"), ("気づき", "#気づき"), ("成長", "#成長"), ("つながり", "#つながり")
        ]
        
        for tag_label, tag_value in quick_tag_buttons:
            btn = tk.Button(quick_tags_frame, text=tag_label, 
                          command=lambda t=tag_value: self.add_quick_tag(t),
                          font=self.get_safe_font(8),
                          bg='#e8f4fd', fg='#2c3e50', relief=tk.FLAT,
                          padx=8, pady=2)
            btn.pack(side=tk.LEFT, padx=2)
        
        # メモ一覧表示
        memo_list_frame = tk.LabelFrame(memo_frame, text="📚 保存された分析メモ", 
                                      font=self.get_safe_font(11, 'bold'), bg=theme['panel_bg'], fg=theme['panel_fg'])
        memo_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # メモリストボックス
        memo_list_container = tk.Frame(memo_list_frame, bg=theme['panel_bg'])
        memo_list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # スクロールバー付きリストボックス
        list_scroll_frame = tk.Frame(memo_list_container, bg=theme['panel_bg'])
        list_scroll_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        theme = self.themes[self.current_theme]
        self.memo_listbox = tk.Listbox(list_scroll_frame, font=self.get_safe_font(10),
                                     bg=theme['input_bg'], fg=theme['input_fg'], relief=tk.SOLID, borderwidth=1)
        memo_scrollbar = tk.Scrollbar(list_scroll_frame, orient=tk.VERTICAL, command=self.memo_listbox.yview)
        self.memo_listbox.config(yscrollcommand=memo_scrollbar.set)
        
        self.memo_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        memo_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # メモ詳細表示
        memo_detail_frame = tk.Frame(memo_list_container, bg=theme['panel_bg'])
        memo_detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.memo_detail_text = tk.Text(memo_detail_frame, font=self.get_safe_font(10),
                                      wrap=tk.WORD, bg=theme['input_bg'], fg=theme['input_fg'],
                                      relief=tk.SOLID, borderwidth=1, state=tk.DISABLED)
        self.memo_detail_text.pack(fill=tk.BOTH, expand=True)
        
        # メモ選択イベント
        self.memo_listbox.bind('<<ListboxSelect>>', self.on_memo_select)
        
    def setup_quick_actions(self):
        """段階3: クイックアクションエリア（移動されたボタンのため削除）"""
        # ボタンはヘッダーと入力エリアに移動したため、ここは空にする
        pass
    
    # 新しいUIのヘルパーメソッド
    def clear_placeholder(self, event):
        """プレースホルダーテキストのクリア"""
        if self.placeholder_active:
            self.text_input.delete("1.0", tk.END)
            theme = self.themes[self.current_theme]
            self.text_input.config(fg=theme['input_fg'], insertbackground=theme['input_fg'])
            self.placeholder_active = False
            self.update_char_count()
    
    def add_placeholder(self, event):
        """プレースホルダーテキストの追加"""
        if not self.text_input.get("1.0", tk.END).strip():
            placeholder_text = "例: この料理、本当においしい！素晴らしい味でした。"
            self.text_input.insert("1.0", placeholder_text)
            self.text_input.config(fg='#999999', insertbackground='#999999')
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
• メモ：分析結果の保存・管理

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
        result_text = f"""STAR分析結果エクスポート
        
分析日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
入力テキスト: {self.text_input.get('1.0', tk.END).strip()}

主要カテゴリ: {self.current_result.primary_category}
信頼度: {self.current_result.confidence:.2f}

カテゴリ別スコア:
- SENSE: {self.current_result.scores['SENSE']:.2f}
- THINK: {self.current_result.scores['THINK']:.2f}  
- ACT: {self.current_result.scores['ACT']:.2f}
- RELATE: {self.current_result.scores['RELATE']:.2f}

文型: {self.current_result.sentence_type}
検出キーワード: {', '.join(self.current_result.keywords)}
"""
        
        try:
            filename = f"star_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result_text)
            messagebox.showinfo("エクスポート完了", f"結果を {filename} に保存しました。")
        except Exception as e:
            messagebox.showerror("エクスポートエラー", f"エクスポートに失敗しました: {e}")
    
    def show_settings(self):
        """設定ダイアログの表示"""
        settings_text = """⚙️ 設定オプション

🎨 テーマ：
現在のテーマ: """ + ("ダークモード" if self.current_theme == "dark" else "ライトモード") + """
ヘッダーの🌙ボタンで切り替え可能

💾 メモ保存：
保存場所: star_analysis_memo.json
自動保存: 有効

🔧 分析エンジン：
形態素解析: Janome (現代的エンジン)
分析精度: 高精度モード

📚 理論基準：
STAR分析フレームワーク.md
感動のStar分析とはなにか.md"""
        
        messagebox.showinfo("設定 - STAR分析システム", settings_text)
    
    def on_memo_select(self, event):
        """メモ選択時の詳細表示"""
        selection = self.memo_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.memos):
                memo = self.memos[index]
                
                # 詳細情報を表示
                self.memo_detail_text.config(state=tk.NORMAL)
                self.memo_detail_text.delete("1.0", tk.END)
                
                # タグ情報（下位互換性対応）
                tags = memo.get('tags', [])
                tag_section = f"\n🏷️ タグ:\n{', '.join(tags)}\n" if tags else "\n🏷️ タグ: なし\n"
                
                detail = f"""📅 分析日時: {memo['timestamp']}

📝 入力テキスト:
{memo['text']}
{tag_section}
🎯 分析結果:
主要カテゴリ: {memo['analysis']['primary_category']}
信頼度: {memo['analysis']['confidence']:.2f}

📊 カテゴリ別スコア:
SENSE: {memo['analysis']['scores']['SENSE']:.2f}
THINK: {memo['analysis']['scores']['THINK']:.2f}
ACT: {memo['analysis']['scores']['ACT']:.2f}
RELATE: {memo['analysis']['scores']['RELATE']:.2f}

📋 詳細情報:
文型: {memo['analysis']['sentence_type']}
キーワード: {', '.join(memo['analysis']['keywords'])}"""
                
                self.memo_detail_text.insert("1.0", detail)
                self.memo_detail_text.config(state=tk.DISABLED)
    
    def refresh_memo_list(self):
        """メモ一覧の更新"""
        self.load_memos()
        self.update_memo_display()
        
    def setup_star_theory_section(self, parent):
        """STAR理論説明セクションのセットアップ"""
        theory_frame = tk.LabelFrame(parent, text="📚 STAR理論の基礎", 
                                   font=('Arial', 12, 'bold'), bg='#f0f0f0', fg='#333')
        theory_frame.pack(fill=tk.X, pady=(0, 15))
        
        # STAR要素のボタンを横に配置
        buttons_frame = tk.Frame(theory_frame, bg='#f0f0f0')
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # STAR理論原典に基づく詳細情報
        star_tooltips = {
            'SENSE': """🔸 SENSE + FEEL（五感による感動）

【文型】SV型（主語＋動詞）
【定義】五感を通じた直接体験による感動
【サブカテゴリ】美、味、匂い、触、心地よさ

【代表的キーワード】
• きれい、美しい、おいしい、気持ちいい、かぐわしい
• さっぱり、すっきり、香ばしい、鮮やか、明るい

【理論的背景】
景色に美しさを感じる、料理に美味しさを感じるなど、
感覚的体験により感動が生まれます。""",

            'THINK': """🔸 THINK + FEEL（知見拡大による感動）

【文型】SV型（主語＋動詞）
【定義】知見の拡大として感じた後の感動
【サブカテゴリ】理解、納得、発見、圧倒

【代表的キーワード】
• わかった、なるほど、すごい、へー、知らなかった
• 面白い、理解できた、発見した、気づいた

【理論的背景】
数式がわかった、人の行動の理由がわかったなど、
何らかの情報に発見や理解を感じる感動です。""",

            'ACT': """🔸 ACT + FEEL（体験拡大による感動）

【文型】SOV型（主語＋目的語＋動詞）
【定義】体験の拡大として感じた後の感動
【サブカテゴリ】努力、上達、成長、進歩、達成、特別感、稀有、遭遇、幸運

【代表的キーワード】
• できた、やった、よかった、達成、成長、頑張った
• 成功した、完走した、突破した、挑戦した

【理論的背景】
努力の結果や成長、挑戦の成功など、
体験の拡大により感動が生まれます。""",

            'RELATE': """🔸 RELATE + FEEL（関係拡大による感動）

【文型】SOV型（主語＋目的語＋動詞）
【定義】関係性の拡大として感じた後の感動
【サブカテゴリ】愛、つながり、やさしさ、親近感、愛着、調和、一体感、感謝、承認、尊敬

【代表的キーワード】
• すばらしい、ありがたい、一緒だ、うれしい、愛おしい
• 感謝している、助かった、支えられた、温かい

【理論的背景】
愛情、感謝、つながりなど関係性の拡大により
感動が生まれます。"""
        }
        
        # 各STAR要素のボタンを作成
        colors = {'SENSE': '#FF6B6B', 'THINK': '#4ECDC4', 'ACT': '#45B7D1', 'RELATE': '#96CEB4'}
        
        for i, (category, tooltip_text) in enumerate(star_tooltips.items()):
            btn = tk.Button(buttons_frame, text=f"{category}\n({category} + FEEL)", 
                           bg=colors[category], fg='white', font=('Arial', 10, 'bold'),
                           width=15, height=3, relief=tk.RAISED, bd=2)
            btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
            
            # ツールチップを追加
            ToolTip(btn, tooltip_text, self)
        
    def setup_input_section(self, parent):
        """入力セクションのセットアップ"""
        input_frame = tk.LabelFrame(parent, text="感想文入力", font=('Arial', 12, 'bold'),
                                   bg='#f0f0f0', fg='#333', padx=10, pady=10)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # テキスト入力エリア
        tk.Label(input_frame, text="分析したい感想文を入力してください:", 
                bg='#f0f0f0', font=('Arial', 10)).pack(anchor=tk.W, pady=(0, 5))
        
        self.text_input = scrolledtext.ScrolledText(input_frame, height=4, width=80,
                                                   font=('Arial', 11), wrap=tk.WORD)
        self.text_input.pack(fill=tk.X, pady=(0, 10))
        
        # ボタンフレーム
        button_frame = tk.Frame(input_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X)
        
        # 分析ボタン
        self.analyze_button = tk.Button(button_frame, text="STAR分析実行", 
                                       command=self.analyze_text,
                                       bg='#4CAF50', fg='white', font=('Arial', 12, 'bold'),
                                       padx=20, pady=5)
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # サンプルテキストボタン
        sample_button = tk.Button(button_frame, text="サンプルテキスト", 
                                 command=self.load_sample_text,
                                 bg='#2196F3', fg='white', font=('Arial', 10),
                                 padx=15, pady=5)
        sample_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 保存ボタン
        self.save_button = tk.Button(button_frame, text="💾 結果を保存", 
                                    command=self.save_analysis_result,
                                    bg='#FF9800', fg='white', font=('Arial', 10),
                                    padx=15, pady=5, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # メモ履歴ボタン
        history_button = tk.Button(button_frame, text="📝 メモ履歴", 
                                  command=self.show_memo_history,
                                  bg='#9C27B0', fg='white', font=('Arial', 10),
                                  padx=15, pady=5)
        history_button.pack(side=tk.LEFT)
        
        # クリアボタン
        clear_button = tk.Button(button_frame, text="クリア", 
                                command=self.clear_input,
                                bg='#FF9800', fg='white', font=('Arial', 10),
                                padx=15, pady=5)
        clear_button.pack(side=tk.LEFT)
        
    def setup_result_section(self, parent):
        """結果表示セクションのセットアップ"""
        result_frame = tk.Frame(parent, bg='#f0f0f0')
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左側：グラフ表示
        left_frame = tk.LabelFrame(result_frame, text="STAR分析結果（視覚化）", 
                                  font=('Arial', 12, 'bold'), bg='#f0f0f0', fg='#333')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Matplotlibキャンバス
        self.setup_plot_canvas(left_frame)
        
        # 右側：詳細結果と教育パネル
        right_frame = tk.Frame(result_frame, bg='#f0f0f0')
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # 教育的解説パネル
        self.setup_educational_panel(right_frame)
        
        # キーワード一覧パネル
        self.setup_keywords_panel(right_frame)
        
        # 詳細結果表示
        detail_frame = tk.LabelFrame(right_frame, text="詳細分析結果", 
                                   font=('Arial', 12, 'bold'), bg='#f0f0f0', fg='#333')
        detail_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 結果表示エリア
        self.result_text = scrolledtext.ScrolledText(detail_frame, width=50, height=20,
                                                    font=('Arial', 10), wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def setup_educational_panel(self, parent):
        """教育的解説パネルのセットアップ"""
        # 解説パネルフレーム
        edu_frame = tk.LabelFrame(parent, text="🔍 なぜこの分類？（STAR理論解説）", 
                                 font=('Arial', 11, 'bold'), bg='#f0f0f0', fg='#2c3e50',
                                 relief=tk.RAISED, bd=2)
        edu_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 解説テキストエリア
        self.explanation_text = tk.Text(edu_frame, height=8, font=('Arial', 9), 
                                       wrap=tk.WORD, bg='#f8f9fa', fg='#2c3e50',
                                       relief=tk.FLAT, bd=1)
        self.explanation_text.pack(fill=tk.X, padx=10, pady=10)
        
        # 初期メッセージ
        initial_message = """📚 STAR分析の基本

STAR理論では、感動は以下の4つに分類されます：

🔸 SENSE + FEEL：五感による直接体験（美しい、おいしい等）
🔸 THINK + FEEL：知見の拡大（わかった、なるほど等）  
🔸 ACT + FEEL：体験の拡大（できた、やった等）
🔸 RELATE + FEEL：関係の拡大（ありがたい、一緒等）

分析実行後、具体的な分類理由を表示します。"""
        
        self.explanation_text.insert("1.0", initial_message)
        self.explanation_text.config(state=tk.DISABLED)
        
    def setup_keywords_panel(self, parent):
        """キーワード一覧パネルのセットアップ"""
        keywords_frame = tk.LabelFrame(parent, text="🔑 検出キーワード & 理論キーワード", 
                                     font=('Arial', 11, 'bold'), bg='#f0f0f0', fg='#2c3e50',
                                     relief=tk.RAISED, bd=2)
        keywords_frame.pack(fill=tk.X, pady=(10, 0))
        
        # ノートブック（タブ）を作成
        self.keywords_notebook = ttk.Notebook(keywords_frame)
        self.keywords_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # タブ1: 検出されたキーワード
        detected_frame = tk.Frame(self.keywords_notebook, bg='#f8f9fa')
        self.keywords_notebook.add(detected_frame, text="検出")
        
        self.detected_keywords_text = tk.Text(detected_frame, height=4, font=('Arial', 9),
                                            wrap=tk.WORD, bg='#f8f9fa', fg='#2c3e50',
                                            relief=tk.FLAT, bd=1)
        self.detected_keywords_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # タブ2: 理論キーワード一覧
        theory_frame = tk.Frame(self.keywords_notebook, bg='#f8f9fa')
        self.keywords_notebook.add(theory_frame, text="理論")
        
        self.theory_keywords_text = tk.Text(theory_frame, height=4, font=('Arial', 9),
                                          wrap=tk.WORD, bg='#f8f9fa', fg='#2c3e50',
                                          relief=tk.FLAT, bd=1)
        self.theory_keywords_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 初期状態：理論キーワードを表示
        self.display_theory_keywords()
        
        # 初期状態：検出キーワードメッセージ
        self.detected_keywords_text.insert("1.0", "分析実行後、検出されたキーワードが表示されます。")
        self.detected_keywords_text.config(state=tk.DISABLED)
        
    def display_theory_keywords(self):
        """STAR理論のキーワード一覧表示"""
        theory_text = """📝 STAR理論キーワード一覧（原典準拠）

🔸 SENSE（五感）の代表キーワード：
きれい、美しい、おいしい、気持ちいい、かぐわしい、さっぱり、すっきり等

🔸 THINK（知見）の代表キーワード：
わかった、なるほど、すごい、へー、知らなかった、面白い、理解できた等

🔸 ACT（体験）の代表キーワード：
できた、やった、よかった、達成、成長、頑張った、成功した等

🔸 RELATE（関係）の代表キーワード：
すばらしい、ありがたい、一緒だ、うれしい、愛おしい、感謝している等"""
        
        self.theory_keywords_text.insert("1.0", theory_text)
        self.theory_keywords_text.config(state=tk.DISABLED)
        
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
        ax.text(0.5, 0.5, 'テキストを入力して\n「STAR分析実行」ボタンを\nクリックしてください', 
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
            
            # 現在の結果を保存（保存機能用）
            self.current_result = result
            self.save_memo_button.config(state=tk.NORMAL)
            
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
        dialog.geometry("550x500")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # ダイアログの中央配置
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"550x500+{x}+{y}")
        
        # テーマ適用
        theme = self.themes[self.current_theme]
        dialog.configure(bg=theme['bg'])
        
        # 説明ラベル
        info_label = tk.Label(dialog, 
                            text="感動体験をより詳しく教えてください（STAR理論に基づく質問）",
                            font=self.get_safe_font(11, 'bold'),
                            bg=theme['bg'], fg=theme['fg'], wraplength=500)
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
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
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
                             font=self.get_safe_font(10, 'bold'),
                             bg=theme['bg'], fg=theme['fg'], anchor='w')
            q_label.pack(fill=tk.X, pady=(10, 2))
            
            # 入力フィールド
            entry = tk.Text(questions_frame, height=3, font=self.get_safe_font(9),
                          bg=theme['input_bg'], fg=theme['input_fg'],
                          relief=tk.SOLID, borderwidth=1, wrap=tk.WORD)
            entry.pack(fill=tk.X, pady=(0, 5), padx=10)
            
            # ヒント
            hint_label = tk.Label(questions_frame, text=f"例: {hint}",
                                font=self.get_safe_font(8), 
                                bg=theme['bg'], fg='#888888', anchor='w')
            hint_label.pack(fill=tk.X, pady=(0, 5))
            
            self.enhancement_entries.append(entry)
        
        # ボタンフレーム
        button_frame = tk.Frame(dialog, bg=theme['bg'])
        button_frame.pack(fill=tk.X, pady=10)
        
        # 適用ボタン
        apply_button = tk.Button(button_frame, text="📝 詳細情報を追加",
                               command=lambda: self.apply_enhancement(dialog),
                               font=self.get_safe_font(10, 'bold'),
                               bg='#28a745', fg='white', relief=tk.FLAT,
                               padx=20, pady=8)
        apply_button.pack(side=tk.LEFT, padx=(20, 10))
        
        # キャンセルボタン  
        cancel_button = tk.Button(button_frame, text="キャンセル",
                                command=dialog.destroy,
                                font=self.get_safe_font(10),
                                bg='#6c757d', fg='white', relief=tk.FLAT,
                                padx=20, pady=8)
        cancel_button.pack(side=tk.LEFT)
    
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
    
    def save_as_memo_placeholder(self):
        """メモ保存機能のプレースホルダー（後日実装）"""
        messagebox.showinfo("準備中", "メモ保存機能は近日中に実装予定です。")
    
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
                           f"構造: {result.structure_pattern[:50]}...\n" \
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
    
    def update_overview_tab(self, result):
        """概要タブの更新"""
        # 主要カテゴリ表示
        category_emoji = {
            'SENSE': '🎨', 'THINK': '💡', 'ACT': '🎯', 'RELATE': '🤝'
        }
        emoji = category_emoji.get(result.primary_category, '🎯')
        self.main_category_label.config(
            text=f"{emoji} {result.primary_category} + FEEL",
            fg=self.themes[self.current_theme]['accent']
        )
        
        # 信頼度表示
        confidence_text = f"信頼度: {result.confidence} | 感情強度: {result.detailed_analysis.get('emotion_intensity', 0):.1f}"
        self.confidence_label.config(text=confidence_text)
        
        # 一言解説
        self.quick_explanation.config(state=tk.NORMAL)
        self.quick_explanation.delete("1.0", tk.END)
        
        explanation = self.generate_quick_explanation(result)
        self.quick_explanation.insert("1.0", explanation)
        self.quick_explanation.config(state=tk.DISABLED)
        
        # スコアバーの更新
        self.update_score_bars(result)
    
    def update_detailed_tab(self, result):
        """詳細分析タブの更新"""
        # キーワード分析
        self.detailed_keywords_text.config(state=tk.NORMAL)
        self.detailed_keywords_text.delete("1.0", tk.END)
        
        keyword_analysis = f"""🔍 検出されたキーワード ({len(result.keywords)}個):
{', '.join(result.keywords) if result.keywords else 'なし'}

📊 カテゴリ別分析:
• SENSE: {result.scores['SENSE']:.2f}
• THINK: {result.scores['THINK']:.2f}
• ACT: {result.scores['ACT']:.2f}
• RELATE: {result.scores['RELATE']:.2f}"""
        
        self.detailed_keywords_text.insert("1.0", keyword_analysis)
        self.detailed_keywords_text.config(state=tk.DISABLED)
        
        # 文構造解析
        self.structure_text.config(state=tk.NORMAL)
        self.structure_text.delete("1.0", tk.END)
        
        structure_analysis = f"""📝 文型分析: {result.sentence_type}

🔧 構造パターン:
{result.structure_pattern}

📏 テキスト情報:
• 長さ: {result.detailed_analysis['text_length']}文字
• キーワード密度: {result.detailed_analysis['keyword_count']}/{result.detailed_analysis['text_length']}"""
        
        self.structure_text.insert("1.0", structure_analysis)
        self.structure_text.config(state=tk.DISABLED)
        
        # 感情強度解析
        self.intensity_text.config(state=tk.NORMAL)
        self.intensity_text.delete("1.0", tk.END)
        
        feel_score = result.detailed_analysis.get('feel_score', 0)
        feel_indicators = result.detailed_analysis.get('feel_indicators', [])
        
        intensity_analysis = f"""💝 FEEL要素分析:
感情スコア: {feel_score:.2f}/2.0

🎭 検出された感情表現:
{', '.join(feel_indicators) if feel_indicators else 'なし'}

📈 感情強度: {result.detailed_analysis['emotion_intensity']:.2f}

🔍 検出パターン:
{', '.join(result.detailed_analysis.get('detected_patterns', [])) if result.detailed_analysis.get('detected_patterns') else 'なし'}

💡 分析の解釈:
{self.get_interpretation(result)}"""
        
        self.intensity_text.insert("1.0", intensity_analysis)
        self.intensity_text.config(state=tk.DISABLED)
    
    def update_charts_tab(self, result):
        """グラフタブの更新"""
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
            
            tk.Label(label_frame, text=category, font=self.get_safe_font(10, 'bold'),
                    bg=theme['panel_bg'], fg=theme['panel_fg'], width=8).pack(side=tk.LEFT)
            
            # スコアバー
            bar_frame = tk.Frame(label_frame, bg='#e0e0e0', height=20, relief=tk.SUNKEN, borderwidth=1)
            bar_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
            
            if score > 0:
                bar_width = int((score / max_score) * 200) if max_score > 0 else 0
                score_bar = tk.Frame(bar_frame, bg=color, height=18)
                score_bar.place(x=1, y=1, width=bar_width)
            
            # スコア値
            tk.Label(label_frame, text=f"{score:.2f}", font=self.get_safe_font(9),
                    bg=theme['panel_bg'], fg=theme['panel_fg'], width=6).pack(side=tk.RIGHT)
    
    def save_current_analysis(self):
        """現在の分析結果をメモに保存（タグ機能付き）"""
        if not self.current_result:
            messagebox.showwarning("警告", "保存する分析結果がありません。")
            return
        
        try:
            # ユーザー入力タグの取得
            user_tags = self.get_tags_from_input()
            
            # 自動タグの生成
            auto_tags = self.generate_auto_tags(self.current_result)
            
            # タグの統合（重複除去）
            all_tags = list(set(user_tags + auto_tags))
            
            # メモデータの作成
            memo_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "text": self.text_input.get("1.0", tk.END).strip(),
                "tags": all_tags,  # タグフィールド追加
                "custom_note": "",  # カスタムノート（将来拡張用）
                "analysis": {
                    "primary_category": self.current_result.primary_category,
                    "confidence": self.current_result.confidence,
                    "scores": dict(self.current_result.scores),
                    "sentence_type": self.current_result.sentence_type,
                    "keywords": list(self.current_result.keywords),
                    "detailed_analysis": dict(self.current_result.detailed_analysis)
                }
            }
            
            # メモリストに追加
            self.memos.append(memo_data)
            
            # ファイルに保存
            with open(self.memo_file, 'w', encoding='utf-8') as f:
                json.dump(self.memos, f, ensure_ascii=False, indent=2)
            
            # メモ表示の更新
            self.update_memo_display()
            
            # タグ入力欄をクリア
            self.tag_entry.delete(0, tk.END)
            self.add_tag_placeholder(None)
            
            # 保存完了メッセージ（タグ情報付き）
            tag_info = f"\n追加されたタグ: {', '.join(all_tags)}" if all_tags else ""
            messagebox.showinfo("保存完了", f"分析結果をメモに保存しました。{tag_info}")
            
        except Exception as e:
            messagebox.showerror("保存エラー", f"メモ保存中にエラーが発生しました：\n{str(e)}")
    
    def update_memo_display(self):
        """メモ表示の更新（検索フィルター対応）"""
        # 検索フィルターが有効な場合はそれを適用
        if hasattr(self, 'search_entry') and (self.search_entry.get().strip() or self.search_category_var.get() != "すべて"):
            self.apply_search_filter()
        else:
            # 全メモを表示（従来の動作）
            self.memo_listbox.delete(0, tk.END)
            
            # メモを新しい順で表示
            for memo in reversed(self.memos):
                timestamp = datetime.datetime.fromisoformat(memo['timestamp']).strftime('%m/%d %H:%M')
                text_preview = memo['text'][:25] + "..." if len(memo['text']) > 25 else memo['text']
                category = memo['analysis']['primary_category']
                
                # タグ情報を追加（下位互換性のため）
                tags = memo.get('tags', [])
                tag_display = f" 🏷️{len(tags)}" if tags else ""
                
                display_text = f"[{timestamp}] {category}{tag_display} | {text_preview}"
                self.memo_listbox.insert(tk.END, display_text)
    
    # タグ機能のヘルパーメソッド
    def clear_tag_placeholder(self, event):
        """タグ入力のプレースホルダークリア"""
        if self.tag_placeholder_active:
            self.tag_entry.delete(0, tk.END)
            self.tag_entry.config(fg='#2c3e50')
            self.tag_placeholder_active = False
    
    def add_tag_placeholder(self, event):
        """タグ入力のプレースホルダー追加"""
        if not self.tag_entry.get().strip():
            self.tag_entry.delete(0, tk.END)
            self.tag_entry.insert(0, "タグをカンマ区切りで入力...")
            self.tag_entry.config(fg='#999999')
            self.tag_placeholder_active = True
    
    def add_quick_tag(self, tag):
        """クイックタグの追加"""
        current_text = self.tag_entry.get()
        
        # プレースホルダーの場合はクリア
        if self.tag_placeholder_active:
            self.tag_entry.delete(0, tk.END)
            self.tag_entry.insert(0, tag)
            self.tag_entry.config(fg='#2c3e50')
            self.tag_placeholder_active = False
        else:
            # 既存のタグに追加
            tags = [t.strip() for t in current_text.split(',') if t.strip()]
            if tag not in tags:
                tags.append(tag)
                self.tag_entry.delete(0, tk.END)
                self.tag_entry.insert(0, ', '.join(tags))
    
    def get_tags_from_input(self):
        """タグ入力欄からタグリストを取得"""
        if self.tag_placeholder_active:
            return []
        
        tag_text = self.tag_entry.get().strip()
        if not tag_text:
            return []
        
        # カンマ区切りでタグを分割・清理
        tags = [tag.strip() for tag in tag_text.split(',') if tag.strip()]
        return tags
    
    def generate_auto_tags(self, result):
        """分析結果に基づく自動タグ生成"""
        auto_tags = []
        
        # 主カテゴリに基づくタグ
        category_tags = {
            'SENSE': ['#感覚', '#美的体験'],
            'THINK': ['#学び', '#気づき'],
            'ACT': ['#達成', '#成長'],
            'RELATE': ['#感謝', '#つながり']
        }
        
        if result.primary_category in category_tags:
            auto_tags.extend(category_tags[result.primary_category])
        
        # 感情強度に基づくタグ
        emotion_intensity = result.detailed_analysis.get('emotion_intensity', 0)
        if emotion_intensity > 1.5:
            auto_tags.append('#強い感動')
        elif emotion_intensity > 1.0:
            auto_tags.append('#感動')
        
        # 文型に基づくタグ
        if result.sentence_type == 'SV型':
            auto_tags.append('#直接体験')
        elif result.sentence_type == 'SOV型':
            auto_tags.append('#体験の拡大')
        
        return auto_tags
    
    # 検索機能のヘルパーメソッド
    def on_search_changed(self, event=None):
        """検索条件変更時の処理"""
        self.apply_search_filter()
    
    def clear_search(self):
        """検索条件のクリア"""
        self.search_entry.delete(0, tk.END)
        self.search_category_var.set("すべて")
        self.apply_search_filter()
    
    def apply_search_filter(self):
        """検索フィルターを適用してメモ一覧を更新"""
        search_text = self.search_entry.get().lower().strip()
        selected_category = self.search_category_var.get()
        
        # メモリストボックスをクリア
        self.memo_listbox.delete(0, tk.END)
        
        # フィルター済みメモを表示
        filtered_memos = []
        for memo in reversed(self.memos):  # 新しい順
            # テキスト検索
            text_match = True
            if search_text:
                text_match = (
                    search_text in memo['text'].lower() or
                    search_text in memo['analysis']['primary_category'].lower() or
                    any(search_text in tag.lower() for tag in memo.get('tags', []))
                )
            
            # カテゴリフィルター
            category_match = True
            if selected_category != "すべて":
                category_match = memo['analysis']['primary_category'] == selected_category
            
            if text_match and category_match:
                filtered_memos.append(memo)
        
        # 検索結果を表示
        for memo in filtered_memos:
            timestamp = datetime.datetime.fromisoformat(memo['timestamp']).strftime('%m/%d %H:%M')
            text_preview = memo['text'][:25] + "..." if len(memo['text']) > 25 else memo['text']
            category = memo['analysis']['primary_category']
            
            # タグ情報を追加
            tags = memo.get('tags', [])
            tag_display = f" 🏷️{len(tags)}" if tags else ""
            
            display_text = f"[{timestamp}] {category}{tag_display} | {text_preview}"
            self.memo_listbox.insert(tk.END, display_text)
        
        # 検索結果数を表示（オプション）
        total_count = len(self.memos)
        filtered_count = len(filtered_memos)
        if search_text or selected_category != "すべて":
            print(f"検索結果: {filtered_count}/{total_count} 件")
    
    def search_by_tag(self, tag):
        """特定タグでの検索"""
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, tag)
        self.apply_search_filter()
            
    def display_results(self, result):
        """詳細結果の表示"""
        self.result_text.delete("1.0", tk.END)
        
        results_text = f"""
【分析対象テキスト】
{result.text}

【STAR分析結果】
主分類: {result.primary_category} ({result.primary_category} + FEEL)
信頼度: {result.confidence}
文型: {result.sentence_type}

【各要素のスコア】
SENSE（五感）: {result.scores['SENSE']:.2f}
THINK（知見）: {result.scores['THINK']:.2f}
ACT（体験）: {result.scores['ACT']:.2f}
RELATE（関係）: {result.scores['RELATE']:.2f}

【FEEL要素（感情の高ぶり）】
FEELスコア: {result.detailed_analysis.get('feel_score', 0):.2f}
FEEL指標: {', '.join(result.detailed_analysis.get('feel_indicators', [])) if result.detailed_analysis.get('feel_indicators') else 'なし'}

【検出されたキーワード】
{', '.join(result.keywords) if result.keywords else 'なし'}

【感動の基本構造文パターン】
{result.structure_pattern}

【詳細分析】
テキスト長: {result.detailed_analysis['text_length']}文字
キーワード数: {result.detailed_analysis['keyword_count']}個
感情強度: {result.detailed_analysis['emotion_intensity']:.2f}
検出パターン: {', '.join(result.detailed_analysis['detected_patterns']) if result.detailed_analysis['detected_patterns'] else 'なし'}

【理論的背景】
• 感動は必ず {result.primary_category} + FEEL で構成されます
• {result.sentence_type}の文型により {result.primary_category} 分類が決定されました
• FEEL要素（感情の高ぶり）により感動体験が完成します

【分析の解釈】
{self.get_interpretation(result)}
"""
        
        self.result_text.insert("1.0", results_text)
        
    def get_interpretation(self, result):
        """分析結果の解釈生成"""
        category = result.primary_category
        confidence = result.confidence
        
        interpretations = {
            'SENSE': f"この感想は主に五感的な体験による感動です。美しさ、味覚、心地よさなどの感覚的な要素が強く表現されています。",
            'THINK': f"この感想は主に知的な発見や理解による感動です。新しい知識の獲得や気づきが感動の源泉となっています。",
            'ACT': f"この感想は主に体験や達成による感動です。努力の結果や成長、挑戦の成功が感動を生み出しています。",
            'RELATE': f"この感想は主に人間関係や絆による感動です。愛情、感謝、つながりなどの関係性が感動の核となっています。"
        }
        
        base_interpretation = interpretations.get(category, "分類が困難な感想です。")
        
        if confidence == "高":
            confidence_note = "この分析結果は高い信頼度を持っています。"
        elif confidence == "中":
            confidence_note = "この分析結果は中程度の信頼度です。"
        else:
            confidence_note = "この分析結果は低い信頼度です。より多くの感情表現があると正確性が向上します。"
            
        return f"{base_interpretation}\n{confidence_note}"
        
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
        ax3.set_title(f'感動の構成要素: {result.primary_category} + FEEL', 
                     fontsize=10, fontweight='bold', color=text_color, pad=20)
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
        
    def load_sample_text(self):
        """サンプルテキストの読み込み"""
        import random
        sample = random.choice(self.sample_texts)
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert("1.0", sample)
        
    def clear_input(self):
        """入力のクリア"""
        self.text_input.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)
        self.plot_initial_state()

    def update_educational_explanation(self, result):
        """教育的解説の更新（STAR理論原典に基づく）"""
        self.explanation_text.config(state=tk.NORMAL)
        self.explanation_text.delete("1.0", tk.END)
        
        category = result.primary_category
        sentence_type = result.sentence_type
        keywords = result.keywords
        confidence = result.confidence
        
        # STAR理論原典に基づく解説生成
        explanation = self.generate_theory_based_explanation(category, sentence_type, keywords, confidence)
        
        self.explanation_text.insert("1.0", explanation)
        self.explanation_text.config(state=tk.DISABLED)
        
    def generate_theory_based_explanation(self, category, sentence_type, keywords, confidence):
        """STAR理論原典に基づく解説生成"""
        # 基本的な分類理由
        category_explanations = {
            'SENSE': {
                'definition': 'SENSE + FEEL（五感による感動）',
                'rule': 'SV型（主語＋動詞）の文型で、五感に関するキーワードが検出されました。',
                'theory': '美しさ、味、匂い、触覚、音などの感覚的体験により感動が生まれています。',
                'keywords': ['きれい', '美しい', 'おいしい', '気持ちいい', 'かぐわしい']
            },
            'THINK': {
                'definition': 'THINK + FEEL（知見拡大による感動）',
                'rule': 'SV型（主語＋動詞）の文型で、知的活動に関するキーワードが検出されました。',
                'theory': '理解、発見、納得、学習などの知見の拡大により感動が生まれています。',
                'keywords': ['わかった', 'なるほど', 'すごい', 'へー', '知らなかった']
            },
            'ACT': {
                'definition': 'ACT + FEEL（体験拡大による感動）',
                'rule': 'SOV型（主語＋目的語＋動詞）の文型で、行動・体験に関するキーワードが検出されました。',
                'theory': '努力、達成、成長、挑戦などの体験の拡大により感動が生まれています。',
                'keywords': ['できた', 'やった', 'よかった', '達成', '成長', '頑張った']
            },
            'RELATE': {
                'definition': 'RELATE + FEEL（関係拡大による感動）',
                'rule': 'SOV型（主語＋目的語＋動詞）の文型で、人間関係に関するキーワードが検出されました。',
                'theory': '愛、絆、感謝、共感などの関係性の拡大により感動が生まれています。',
                'keywords': ['すばらしい', 'ありがたい', '一緒だ', 'うれしい', '愛おしい']
            }
        }
        
        info = category_explanations.get(category, {})
        
        explanation = f"""🎯 分析結果：{info.get('definition', '')}

📋 分類理由：
{info.get('rule', '')}

📚 理論的背景：
{info.get('theory', '')}

🔍 検出されたキーワード：
{', '.join(keywords) if keywords else 'なし'}

📊 文型判定：{sentence_type}
• SV型 → SENSE/THINK（感動事象の主体のみ）
• SOV型 → ACT/RELATE（主体＋対象＋動詞）

⚡ FEEL要素：
感情の高ぶりを伴って感動体験が完成します。

✅ 信頼度：{confidence}
"""

        # 代表的なキーワード例も表示
        if info.get('keywords'):
            explanation += f"\n📝 {category}の代表的表現例：\n"
            explanation += f"{', '.join(info['keywords'][:5])} など"
            
        return explanation

    def update_detected_keywords(self, result):
        """検出されたキーワードの更新"""
        self.detected_keywords_text.config(state=tk.NORMAL)
        self.detected_keywords_text.delete("1.0", tk.END)
        
        # 検出されたキーワードを分析結果から取得
        keywords = result.keywords
        category = result.primary_category
        
        if keywords:
            # カテゴリ別にキーワードを分類
            categorized_keywords = {'SENSE': [], 'THINK': [], 'ACT': [], 'RELATE': []}
            
            # 各キーワードがどのカテゴリに属するかチェック
            for keyword in keywords:
                for cat in categorized_keywords.keys():
                    if self._keyword_belongs_to_category(keyword, cat):
                        categorized_keywords[cat].append(keyword)
                        break
                else:
                    # どのカテゴリにも属さない場合は主分類に追加
                    categorized_keywords[category].append(keyword)
            
            detected_text = f"🎯 検出されたキーワード（主分類: {category}）\n\n"
            
            for cat, kws in categorized_keywords.items():
                if kws:
                    detected_text += f"🔸 {cat}: {', '.join(kws)}\n"
            
            detected_text += f"\n📊 合計 {len(keywords)} 個のキーワードが検出されました。"
            
        else:
            detected_text = "❌ 感動表現のキーワードが検出されませんでした。\n\n" \
                          "より感情的な表現を含む文章を入力してみてください。"
        
        self.detected_keywords_text.insert("1.0", detected_text)
        self.detected_keywords_text.config(state=tk.DISABLED)
        
    def _keyword_belongs_to_category(self, keyword, category):
        """キーワードが特定のカテゴリに属するかチェック"""
        if category in self.analyzer.keywords:
            for keyword_type, keyword_list in self.analyzer.keywords[category].items():
                if keyword in keyword_list:
                    return True
        return False

    def load_memos(self):
        """保存されたメモの読み込み"""
        try:
            if os.path.exists(self.memo_file):
                with open(self.memo_file, 'r', encoding='utf-8') as f:
                    self.memos = json.load(f)
            else:
                self.memos = []
        except Exception as e:
            print(f"メモファイル読み込みエラー: {e}")
            self.memos = []

    def save_analysis_result(self):
        """分析結果の保存"""
        if not self.current_result:
            messagebox.showwarning("警告", "保存する分析結果がありません。")
            return
            
        # メモ入力ダイアログ
        memo_dialog = self.create_memo_dialog()
        
    def create_memo_dialog(self):
        """メモ入力ダイアログの作成"""
        dialog = tk.Toplevel(self.root)
        dialog.title("分析結果の保存")
        dialog.geometry("500x400")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # メインフレーム
        main_frame = tk.Frame(dialog, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # タイトル
        title_label = tk.Label(main_frame, text="📝 分析結果の保存", 
                              font=('Arial', 14, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=(0, 15))
        
        # 分析テキスト表示
        tk.Label(main_frame, text="分析対象テキスト:", font=('Arial', 10, 'bold'), 
                bg='#f0f0f0').pack(anchor=tk.W)
        
        text_display = tk.Text(main_frame, height=3, font=('Arial', 9), 
                              wrap=tk.WORD, bg='#f8f9fa', state=tk.DISABLED)
        text_display.pack(fill=tk.X, pady=(5, 15))
        text_display.config(state=tk.NORMAL)
        text_display.insert("1.0", self.current_result.text)
        text_display.config(state=tk.DISABLED)
        
        # 分析結果表示
        tk.Label(main_frame, text="分析結果:", font=('Arial', 10, 'bold'), 
                bg='#f0f0f0').pack(anchor=tk.W)
        
        result_text = f"分類: {self.current_result.primary_category} | 信頼度: {self.current_result.confidence}"
        tk.Label(main_frame, text=result_text, font=('Arial', 9), 
                bg='#f0f0f0', fg='#666').pack(anchor=tk.W, pady=(5, 15))
        
        # メモ入力
        tk.Label(main_frame, text="メモ（オプション）:", font=('Arial', 10, 'bold'), 
                bg='#f0f0f0').pack(anchor=tk.W)
        
        memo_entry = tk.Text(main_frame, height=6, font=('Arial', 9), wrap=tk.WORD)
        memo_entry.pack(fill=tk.X, pady=(5, 15))
        
        # ボタンフレーム
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X)
        
        # 保存ボタン
        save_btn = tk.Button(button_frame, text="💾 保存", 
                            command=lambda: self.save_memo(dialog, memo_entry.get("1.0", tk.END).strip()),
                            bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                            padx=20, pady=5)
        save_btn.pack(side=tk.LEFT)
        
        # キャンセルボタン
        cancel_btn = tk.Button(button_frame, text="キャンセル", 
                              command=dialog.destroy,
                              bg='#f44336', fg='white', font=('Arial', 10),
                              padx=20, pady=5)
        cancel_btn.pack(side=tk.RIGHT)
        
    def save_memo(self, dialog, memo_text):
        """メモの保存実行"""
        try:
            # 新しいメモエントリを作成
            memo_entry = {
                'id': len(self.memos) + 1,
                'timestamp': datetime.datetime.now().isoformat(),
                'text': self.current_result.text,
                'analysis_result': {
                    'primary_category': self.current_result.primary_category,
                    'confidence': self.current_result.confidence,
                    'sentence_type': self.current_result.sentence_type,
                    'keywords': self.current_result.keywords,
                    'scores': self.current_result.scores,
                    'emotion_intensity': self.current_result.emotion_intensity
                },
                'memo': memo_text,
                'tags': []  # 後でタグ機能実装時に使用
            }
            
            # メモリストに追加
            self.memos.append(memo_entry)
            
            # ファイルに保存
            with open(self.memo_file, 'w', encoding='utf-8') as f:
                json.dump(self.memos, f, ensure_ascii=False, indent=2)
            
            dialog.destroy()
            messagebox.showinfo("成功", "分析結果が保存されました。")
            
        except Exception as e:
            messagebox.showerror("エラー", f"保存中にエラーが発生しました：\n{str(e)}")
            
    def show_memo_history(self):
        """メモ履歴の表示"""
        if not self.memos:
            messagebox.showinfo("情報", "保存されたメモがありません。")
            return
            
        # 履歴表示ウィンドウ
        history_window = tk.Toplevel(self.root)
        history_window.title("📝 メモ履歴")
        history_window.geometry("800x600")
        history_window.configure(bg='#f0f0f0')
        
        # メインフレーム
        main_frame = tk.Frame(history_window, bg='#f0f0f0', padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # タイトル
        title_label = tk.Label(main_frame, text="📝 保存されたメモ履歴", 
                              font=('Arial', 14, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=(0, 15))
        
        # リストボックスとスクロールバー
        list_frame = tk.Frame(main_frame, bg='#f0f0f0')
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        history_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                    font=('Arial', 10), height=20)
        history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=history_listbox.yview)
        
        # メモリストを表示
        for i, memo in enumerate(reversed(self.memos)):  # 新しい順
            timestamp = datetime.datetime.fromisoformat(memo['timestamp']).strftime('%Y-%m-%d %H:%M')
            text_preview = memo['text'][:50] + "..." if len(memo['text']) > 50 else memo['text']
            category = memo['analysis_result']['primary_category']
            
            display_text = f"[{timestamp}] {category} | {text_preview}"
            history_listbox.insert(tk.END, display_text)

    def toggle_theme(self):
        """ダークモード/ライトモードの切り替え"""
        # テーマを切り替え
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        
        # テーマを適用
        self.apply_theme()
        
        # ボタンテキストを更新
        if self.current_theme == "dark":
            self.theme_button.config(text="☀️ ライトモード")
        else:
            self.theme_button.config(text="🌙 ダークモード")
            
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
                self.text_input.config(bg=theme['input_bg'], fg=theme['input_fg'])
            
            # 検索エリア
            if hasattr(self, 'search_entry'):
                self.search_entry.config(bg=theme['input_bg'], fg=theme['input_fg'])
            
            # タグ入力エリア
            if hasattr(self, 'tag_entry'):
                self.tag_entry.config(bg=theme['input_bg'], fg=theme['input_fg'])
            
            # メモ関連
            if hasattr(self, 'memo_listbox'):
                self.memo_listbox.config(bg=theme['input_bg'], fg=theme['input_fg'])
            if hasattr(self, 'memo_detail_text'):
                self.memo_detail_text.config(bg=theme['input_bg'], fg=theme['input_fg'])
            
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
                elif widget_class == 'Listbox':
                    widget.configure(bg=theme['input_bg'], fg=theme['input_fg'])
                elif widget_class == 'Scrollbar':
                    # スクロールバーの色調整
                    if self.current_theme == 'dark':
                        widget.configure(bg=theme['panel_bg'], troughcolor=theme['bg'])
                    else:
                        widget.configure(bg=theme['panel_bg'], troughcolor=theme['bg'])
                elif widget_class == 'TNotebook':
                    # ttkのNotebook用
                    try:
                        style = ttk.Style()
                        if self.current_theme == 'dark':
                            style.configure('TNotebook', background=theme['bg'])
                            style.configure('TNotebook.Tab', background=theme['panel_bg'], 
                                          foreground=theme['fg'])
                        else:
                            style.configure('TNotebook', background=theme['bg'])
                            style.configure('TNotebook.Tab', background=theme['panel_bg'], 
                                          foreground=theme['fg'])
                    except:
                        pass
                        
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
        print("\nアプリケーションが中断されました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        # 確実にPythonプロセスを終了
        try:
            root.quit()
            root.destroy()
        except:
            pass


if __name__ == "__main__":
    main()