#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
形態素解析エンジン性能テストスクリプト
Janome vs 基本分析の性能比較
"""

import time
from star_analyzer import STARAnalyzer, MORPHOLOGICAL_ANALYZER, ANALYZER_TYPE

def test_analysis_performance():
    """分析性能テスト"""
    print("=" * 60)
    print("STAR分析システム - 形態素解析エンジン性能テスト")
    print("=" * 60)
    
    # 現在の解析エンジン状態
    print(f"🔍 検出された解析エンジン: {MORPHOLOGICAL_ANALYZER}")
    print(f"🔧 分析器タイプ: {ANALYZER_TYPE}")
    print()
    
    # テストケース
    test_cases = [
        {
            'text': 'この料理、本当においしい！素晴らしい味でした。',
            'expected': 'SENSE',
            'description': 'SENSE系感動（五感・味覚）'
        },
        {
            'text': 'やっと数学の問題が解けた！理解できて嬉しい。',
            'expected': 'THINK',
            'description': 'THINK系感動（知見拡大）'
        },
        {
            'text': 'マラソンを完走できて本当に嬉しい。頑張った甲斐があった。',
            'expected': 'ACT',
            'description': 'ACT系感動（体験拡大）'
        },
        {
            'text': '友達が励ましてくれて心から感謝している。温かい気持ちになった。',
            'expected': 'RELATE',
            'description': 'RELATE系感動（関係拡大）'
        },
        {
            'text': '夕日がとても美しく、心が洗われるような気持ちになった。',
            'expected': 'SENSE',
            'description': 'SENSE系感動（視覚・美的体験）'
        }
    ]
    
    # 分析器初期化
    try:
        analyzer = STARAnalyzer()
        print(f"✅ 分析器初期化成功")
        print(f"   - エンジン: {analyzer.analyzer_type}")
        print(f"   - 解析器: {'あり' if analyzer.morphological_analyzer else 'なし'}")
        print()
    except Exception as e:
        print(f"❌ 分析器初期化失敗: {e}")
        return
    
    # 各テストケースの実行
    correct_predictions = 0
    total_time = 0
    
    print("📊 分析結果:")
    print("-" * 80)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nテストケース {i}: {case['description']}")
        print(f"入力: {case['text']}")
        
        # 分析実行
        start_time = time.time()
        try:
            result = analyzer.analyze(case['text'])
            end_time = time.time()
            analysis_time = (end_time - start_time) * 1000  # ミリ秒
            total_time += analysis_time
            
            # 結果表示
            is_correct = result.primary_category == case['expected']
            if is_correct:
                correct_predictions += 1
                status = "✅ 正解"
            else:
                status = "❌ 不正解"
            
            print(f"予想: {case['expected']} | 結果: {result.primary_category} | {status}")
            print(f"信頼度: {result.confidence} | 処理時間: {analysis_time:.2f}ms")
            print(f"スコア: {result.scores}")
            
            # 形態素解析結果があれば表示
            if result.morphological_analysis:
                morpheme_count = len(result.morphological_analysis)
                print(f"形態素数: {morpheme_count}個")
            else:
                print("形態素解析: なし（基本分析）")
                
        except Exception as e:
            print(f"❌ 分析エラー: {e}")
            continue
        
        print("-" * 80)
    
    # 総合結果
    accuracy = (correct_predictions / len(test_cases)) * 100
    avg_time = total_time / len(test_cases)
    
    print(f"\n📈 総合結果:")
    print(f"正解率: {correct_predictions}/{len(test_cases)} ({accuracy:.1f}%)")
    print(f"平均処理時間: {avg_time:.2f}ms")
    print(f"分析エンジン: {ANALYZER_TYPE}")
    
    # 推奨事項
    print(f"\n💡 推奨事項:")
    if ANALYZER_TYPE == "modern":
        print("✅ Janome使用中 - 最適な設定です")
    else:
        print("🔧 基本分析モード - より高精度な分析のためJanomeインストールを推奨")
        print("   コマンド: pip install janome")
        print("   または: quick_janome_setup.bat を実行")

def main():
    """メイン関数"""
    try:
        test_analysis_performance()
    except KeyboardInterrupt:
        print("\n🛑 テスト中断")
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
    finally:
        input("\nEnterキーで終了...")

if __name__ == "__main__":
    main()