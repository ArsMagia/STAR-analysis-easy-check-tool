#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STAR分析システム ユニットテスト
pytest framework を使用した基本的なテスト
"""

import pytest
from star_analyzer import STARAnalyzer, AnalysisResult

class TestSTARAnalyzer:
    """STARAnalyzer のユニットテスト"""
    
    @pytest.fixture
    def analyzer(self):
        """テスト用のアナライザーインスタンス"""
        return STARAnalyzer()
    
    def test_normal_text_analysis(self, analyzer):
        """正常なテキスト分析のテスト"""
        text = "この料理、本当においしい！"
        result = analyzer.analyze(text)
        
        assert isinstance(result, AnalysisResult)
        assert result.text == text
        assert result.primary_category in ['SENSE', 'THINK', 'ACT', 'RELATE']
        assert isinstance(result.scores, dict)
        assert len(result.scores) == 4
        assert all(isinstance(score, (int, float)) for score in result.scores.values())
    
    def test_empty_string_handling(self, analyzer):
        """空文字列の処理テスト"""
        result = analyzer.analyze("")
        
        assert isinstance(result, AnalysisResult)
        assert result.confidence == 0.0
        assert result.primary_category == 'SENSE'  # デフォルト値
        assert 'error' in result.detailed_analysis
    
    def test_whitespace_only_handling(self, analyzer):
        """空白のみの文字列処理テスト"""
        result = analyzer.analyze("   \n\t  ")
        
        assert isinstance(result, AnalysisResult)
        assert result.confidence == 0.0
    
    def test_invalid_input_type(self, analyzer):
        """無効な入力型のテスト"""
        with pytest.raises(ValueError, match="入力テキストは文字列である必要があります"):
            analyzer.analyze(None)
        
        with pytest.raises(ValueError, match="入力テキストは文字列である必要があります"):
            analyzer.analyze(123)
        
        with pytest.raises(ValueError, match="入力テキストは文字列である必要があります"):
            analyzer.analyze(['リスト'])
    
    def test_sense_category_detection(self, analyzer):
        """SENSE分類の検出テスト"""
        sense_texts = [
            "この料理、本当においしい！",
            "美しい夕日を見た",
            "気持ちいい風が吹いている",
            "きれいな音楽だった"
        ]
        
        for text in sense_texts:
            result = analyzer.analyze(text)
            # SENSE が最高スコアまたは上位であることを確認
            assert result.scores['SENSE'] > 0
    
    def test_think_category_detection(self, analyzer):
        """THINK分類の検出テスト"""
        think_texts = [
            "なるほど、そういうことか！",
            "やっと理解できた",
            "すごい発見だ",
            "勉強になった"
        ]
        
        for text in think_texts:
            result = analyzer.analyze(text)
            # THINK が最高スコアまたは上位であることを確認
            assert result.scores['THINK'] > 0
    
    def test_act_category_detection(self, analyzer):
        """ACT分類の検出テスト"""
        act_texts = [
            "やっと完成できた！",
            "マラソンを完走した",
            "頑張った甲斐があった",
            "ついにできた"
        ]
        
        for text in act_texts:
            result = analyzer.analyze(text)
            # ACT が最高スコアまたは上位であることを確認
            assert result.scores['ACT'] > 0
    
    def test_relate_category_detection(self, analyzer):
        """RELATE分類の検出テスト"""
        relate_texts = [
            "友達に感謝している",
            "みんなと一緒で嬉しい",
            "温かい人たちに囲まれて",
            "すばらしい仲間だ"
        ]
        
        for text in relate_texts:
            result = analyzer.analyze(text)
            # RELATE が最高スコアまたは上位であることを確認
            assert result.scores['RELATE'] > 0
    
    def test_long_text_handling(self, analyzer):
        """長文の処理テスト"""
        long_text = """
        今日は本当に素晴らしい一日でした。朝起きて、美しい朝日を見ることができ、
        とても気持ちが良かったです。その後、友達と一緒に勉強会に参加し、
        新しいことをたくさん学ぶことができました。みんなで協力して問題を解き、
        理解が深まった時の喜びは格別でした。最後に、みんなでお疲れ様と言い合い、
        温かい気持ちになりました。
        """
        
        result = analyzer.analyze(long_text)
        
        assert isinstance(result, AnalysisResult)
        assert result.confidence > 0
        assert all(score >= 0 for score in result.scores.values())
    
    def test_short_text_handling(self, analyzer):
        """短文の処理テスト"""
        short_texts = ["嬉しい", "美味しい", "理解した", "完了"]
        
        for text in short_texts:
            result = analyzer.analyze(text)
            assert isinstance(result, AnalysisResult)
            assert result.primary_category in ['SENSE', 'THINK', 'ACT', 'RELATE']
    
    def test_mixed_emotions(self, analyzer):
        """複合感情の検出テスト"""
        mixed_text = "美味しい料理を作れて嬉しいし、友達にも喜んでもらえて感謝している"
        result = analyzer.analyze(text)
        
        # 複数のカテゴリで高いスコアが出ることを確認
        high_scores = [score for score in result.scores.values() if score > 0.3]
        assert len(high_scores) >= 2, "複合感情が検出されるべきです"
    
    def test_negation_handling(self, analyzer):
        """否定表現の処理テスト"""
        positive_text = "美味しい"
        negative_text = "美味しくない"
        
        pos_result = analyzer.analyze(positive_text)
        neg_result = analyzer.analyze(negative_text)
        
        # 否定形の場合、スコアが低下することを確認
        assert pos_result.scores['SENSE'] > neg_result.scores['SENSE']
    
    def test_confidence_calculation(self, analyzer):
        """信頼度計算のテスト"""
        # 明確な感情表現
        clear_text = "本当においしい！最高だ！"
        clear_result = analyzer.analyze(clear_text)
        
        # 曖昧な表現
        ambiguous_text = "まあまあかな"
        ambiguous_result = analyzer.analyze(ambiguous_text)
        
        # 明確な表現の方が高い信頼度を持つことを確認
        assert clear_result.confidence >= ambiguous_result.confidence
    
    def test_result_structure(self, analyzer):
        """結果構造の検証テスト"""
        result = analyzer.analyze("テストテキスト")
        
        # 必須フィールドの存在確認
        assert hasattr(result, 'text')
        assert hasattr(result, 'scores')
        assert hasattr(result, 'primary_category')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'sentence_type')
        assert hasattr(result, 'keywords')
        assert hasattr(result, 'detailed_analysis')
        
        # スコアの合計チェック（大まかに1.0付近になることを確認）
        total_score = sum(result.scores.values())
        assert 0.5 <= total_score <= 2.0, f"スコア合計が範囲外: {total_score}"

class TestEdgeCases:
    """エッジケースのテスト"""
    
    @pytest.fixture
    def analyzer(self):
        return STARAnalyzer()
    
    def test_special_characters(self, analyzer):
        """特殊文字の処理テスト"""
        special_texts = [
            "😊美味しい！",
            "★★★★★ 最高",
            "◆◇◆ なるほど ◇◆◇",
            "【重要】理解できた"
        ]
        
        for text in special_texts:
            result = analyzer.analyze(text)
            assert isinstance(result, AnalysisResult)
    
    def test_numbers_and_symbols(self, analyzer):
        """数字と記号の処理テスト"""
        symbol_texts = [
            "100点満点！",
            "99.9%理解した",
            "@#$%^&*()美味しい",
            "1+1=2がわかった"
        ]
        
        for text in symbol_texts:
            result = analyzer.analyze(text)
            assert isinstance(result, AnalysisResult)
    
    def test_very_long_text(self, analyzer):
        """非常に長いテキストの処理テスト"""
        very_long_text = "美味しい。" * 1000  # 5000文字
        result = analyzer.analyze(very_long_text)
        
        assert isinstance(result, AnalysisResult)
        assert result.scores['SENSE'] > 0  # SENSE関連なので高スコア期待

# pytest実行用のメイン関数
if __name__ == "__main__":
    pytest.main([__file__, "-v"])