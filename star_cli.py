#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STAR分析 コマンドライン版
感想文をSTAR分類で分析し、結果を表示するCLIツール
"""

import sys
from star_analyzer import STARAnalyzer
from logger_config import get_logger

# ロガー初期化
logger = get_logger('cli')

class STARAnalysisCLI:
    """STAR分析コマンドラインインターフェース"""
    
    def __init__(self):
        self.analyzer = STARAnalyzer()
        logger.info("STAR分析CLIアプリケーションを初期化しました")
        self.sample_texts = [
            "この料理、本当においしい！素晴らしい味でした。",
            "やっと数学の問題が解けた！理解できて嬉しい。",
            "マラソンを完走できて本当に嬉しい。頑張った甲斐があった。",
            "友達が励ましてくれて心から感謝している。温かい気持ちになった。",
            "夕日がとても美しく、心が洗われるような気持ちになった。"
        ]
    
    def display_header(self):
        """ヘッダー表示"""
        print("=" * 60)
        print("🌟 STAR分析システム - 感動の分類分析ツール 🌟")
        print("=" * 60)
        print("感想文をSTAR分類（SENSE, THINK, ACT, RELATE）で分析します")
        print()
    
    def display_menu(self):
        """メニュー表示"""
        print("\n" + "-" * 40)
        print("📋 メニュー")
        print("-" * 40)
        print("1. 感想文を入力して分析")
        print("2. サンプルテキストで分析")
        print("3. 使い方・STAR分析について")
        print("4. 終了")
        print("-" * 40)
    
    def analyze_input_text(self):
        """ユーザー入力テキストの分析"""
        print("\n📝 感想文を入力してください（複数行可能、終了は空行）:")
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        
        text = " ".join(lines).strip()
        if not text:
            print("❌ テキストが入力されていません。")
            return
        
        self.analyze_and_display(text)
    
    def analyze_sample_text(self):
        """サンプルテキストの分析"""
        print("\n📚 サンプルテキスト一覧:")
        for i, sample in enumerate(self.sample_texts, 1):
            print(f"{i}. {sample}")
        
        try:
            choice = int(input("\n番号を選択してください (1-5): "))
            if 1 <= choice <= len(self.sample_texts):
                text = self.sample_texts[choice - 1]
                print(f"\n📄 選択されたテキスト: {text}")
                self.analyze_and_display(text)
            else:
                print("❌ 無効な番号です。")
        except ValueError:
            print("❌ 数字を入力してください。")
    
    def analyze_and_display(self, text):
        """分析実行と結果表示"""
        print("\n🔄 分析中...")
        
        try:
            result = self.analyzer.analyze(text)
            self.display_results(result)
        except Exception as e:
            print(f"❌ 分析エラー: {str(e)}")
    
    def display_results(self, result):
        """分析結果の詳細表示"""
        print("\n" + "=" * 60)
        print("📊 STAR分析結果")
        print("=" * 60)
        
        # 基本情報
        print(f"📄 分析対象: {result.text}")
        print(f"🎯 主分類: {result.primary_category}")
        print(f"🔍 信頼度: {result.confidence}")
        print(f"📝 文型: {result.sentence_type}")
        
        # スコア表示
        print("\n📈 各要素のスコア:")
        for category, score in result.scores.items():
            bar = self.create_bar_chart(score)
            icon = self.get_category_icon(category)
            print(f"  {icon} {category:6}: {score:4.2f} {bar}")
        
        # キーワード
        print(f"\n🔑 検出キーワード: {', '.join(result.keywords) if result.keywords else 'なし'}")
        
        # 構造文パターン
        print(f"\n📐 感動の基本構造文パターン:")
        print(f"  {result.structure_pattern}")
        
        # FEEL要素の表示
        print(f"\n💖 FEEL要素（感情の高ぶり）:")
        feel_score = result.detailed_analysis.get('feel_score', 0)
        feel_indicators = result.detailed_analysis.get('feel_indicators', [])
        print(f"  • FEELスコア: {feel_score:.2f}")
        print(f"  • FEEL指標: {', '.join(feel_indicators) if feel_indicators else 'なし'}")
        
        # 詳細分析
        print(f"\n📋 詳細情報:")
        print(f"  • テキスト長: {result.detailed_analysis['text_length']}文字")
        print(f"  • キーワード数: {result.detailed_analysis['keyword_count']}個")
        print(f"  • 感情強度: {result.detailed_analysis['emotion_intensity']:.2f}")
        print(f"  • 検出パターン: {', '.join(result.detailed_analysis['detected_patterns']) if result.detailed_analysis['detected_patterns'] else 'なし'}")
        
        # 理論的背景
        print(f"\n📚 理論的背景:")
        print(f"  • 感動構成: {result.primary_category} + FEEL")
        print(f"  • 文型分類: {result.sentence_type} → {result.primary_category} 決定")
        print(f"  • 感動原理: STAR分析理論に基づく分類")
        
        # 解釈
        print(f"\n💡 分析の解釈:")
        print(f"  {self.get_interpretation(result)}")
        
        print("=" * 60)
    
    def create_bar_chart(self, score, max_width=20):
        """テキストベースの棒グラフ作成"""
        if score == 0:
            return "░" * max_width
        
        filled = int(score * max_width)
        empty = max_width - filled
        return "█" * filled + "░" * empty
    
    def get_category_icon(self, category):
        """カテゴリのアイコン取得"""
        icons = {
            'SENSE': '👁️',
            'THINK': '🧠',
            'ACT': '💪',
            'RELATE': '❤️'
        }
        return icons.get(category, '❓')
    
    def get_interpretation(self, result):
        """分析結果の解釈生成"""
        category = result.primary_category
        confidence = result.confidence
        
        interpretations = {
            'SENSE': "五感的な体験による感動です。美しさ、味覚、心地よさなどの感覚的要素が強く表現されています。",
            'THINK': "知的な発見や理解による感動です。新しい知識の獲得や気づきが感動の源泉となっています。",
            'ACT': "体験や達成による感動です。努力の結果や成長、挑戦の成功が感動を生み出しています。",
            'RELATE': "人間関係や絆による感動です。愛情、感謝、つながりなどの関係性が感動の核となっています。"
        }
        
        base_interpretation = interpretations.get(category, "分類が困難な感想です。")
        
        if confidence == "高":
            confidence_note = "\n  この分析結果は高い信頼度を持っています。"
        elif confidence == "中":
            confidence_note = "\n  この分析結果は中程度の信頼度です。"
        else:
            confidence_note = "\n  この分析結果は低い信頼度です。より多くの感情表現があると正確性が向上します。"
            
        return base_interpretation + confidence_note
    
    def show_help(self):
        """使い方とSTAR分析の説明"""
        print("\n" + "=" * 60)
        print("📖 STAR分析について")
        print("=" * 60)
        print("""
STAR分析は、感動体験を4つの要素で分類する分析手法です：

👁️  SENSE（感覚）: 五感による感動
    例：「おいしい」「きれい」「気持ちいい」
    
🧠 THINK（思考）: 知見の拡張による感動
    例：「わかった」「なるほど」「すごい発見」
    
💪 ACT（行動）: 体験・達成による感動
    例：「できた」「やった」「成長した」
    
❤️  RELATE（関係）: 人間関係による感動
    例：「ありがたい」「愛おしい」「つながり」

感動の基本構造文：
• SENSE/THINK: SV型（主語＋動詞）
• ACT/RELATE: SOV型（主語＋目的語＋動詞）

このツールは、入力された感想文を分析して、どの感動要素が
最も強く表現されているかを判定します。
        """)
        print("=" * 60)
    
    def run(self):
        """メインループ"""
        self.display_header()
        
        while True:
            self.display_menu()
            
            try:
                choice = input("\n選択してください (1-4): ").strip()
                
                if choice == "1":
                    self.analyze_input_text()
                elif choice == "2":
                    self.analyze_sample_text()
                elif choice == "3":
                    self.show_help()
                elif choice == "4":
                    print("\n👋 ありがとうございました！")
                    break
                else:
                    print("❌ 無効な選択です。1-4の数字を入力してください。")
                    
            except KeyboardInterrupt:
                print("\n\n👋 終了します。")
                break
            except Exception as e:
                print(f"❌ エラーが発生しました: {str(e)}")


def main():
    """メイン関数"""
    cli = STARAnalysisCLI()
    cli.run()


if __name__ == "__main__":
    main()