#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STAR分析エンジン
感想文をSTAR分類（SENSE, THINK, ACT, RELATE）に分析するシステム
"""

import re
import json
import platform
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

# 形態素解析ライブラリの導入（Janome専用）
MORPHOLOGICAL_ANALYZER = None
ANALYZER_TYPE = None

# Janome (現代的な日本語形態素解析)
try:
    from janome.tokenizer import Tokenizer
    MORPHOLOGICAL_ANALYZER = "janome"
    ANALYZER_TYPE = "modern"
    print("✅ Janome形態素解析を使用します")
except ImportError:
    ANALYZER_TYPE = "basic"
    print("注意: Janomeが利用できません。基本分析機能のみ使用します。")
    print("推奨: pip install janome でインストールしてください。")

@dataclass
class AnalysisResult:
    """分析結果を格納するデータクラス"""
    text: str
    scores: Dict[str, float]  # STAR各要素のスコア
    primary_category: str
    confidence: str
    sentence_type: str  # SV型 or SOV型
    keywords: List[str]
    structure_pattern: str
    detailed_analysis: Dict[str, any]
    # 新機能：形態素解析結果
    morphological_analysis: Optional[List[Dict]] = None
    emotion_intensity: float = 0.0
    detected_pos_tags: List[str] = None

class STARAnalyzer:
    """STAR分析エンジン"""
    
    def __init__(self):
        # キーワード辞書と設定の初期化
        self._setup_keywords_and_config()
        
        # 形態素解析器の初期化
        self.morphological_analyzer = None
        self.analyzer_type = ANALYZER_TYPE
        
        if MORPHOLOGICAL_ANALYZER == "janome":
            self.morphological_analyzer = self._initialize_janome()
        else:
            self.morphological_analyzer = None
            print("基本分析機能のみ使用します")
    
    def _initialize_janome(self):
        """Janome形態素解析器の初期化"""
        try:
            tokenizer = Tokenizer()
            # 簡単なテスト実行
            test_result = list(tokenizer.tokenize("テスト", wakati=True))
            if test_result:
                print("Janome初期化成功 - 高精度分析が利用可能です")
                return tokenizer
            else:
                print("Janome初期化失敗: テスト解析が失敗")
                return None
        except Exception as e:
            print(f"Janome初期化エラー: {e}")
            return None
    
    def _setup_keywords_and_config(self):
        """キーワード辞書と設定の初期化"""
        # STAR理論原典に基づく実感の形容表現と分析要素
        self.keywords = {
            'SENSE': {
                'feeling_expressions': [
                    # 原典の基本表現（最重要）
                    'きれい', 'おいしい', '気持ちいい', 'かぐわしい',
                    # 基本表現の表記バリエーション
                    '綺麗', '美しい', '美味しい', '美味い', 'うまい', '心地よい', 'いい匂い',
                    # 五感の基本的感覚表現（原典のサブカテゴリに準拠）
                    'さっぱり', 'すっきり', '香ばしい', '鮮やか', '明るい', '温かい', '冷たい',
                    '柔らかい', '滑らか', '静か', '澄んだ', '清潔', '新鮮', '爽快'
                ],
                'objects': [
                    # 原典サブカテゴリに基づく対象（美、味、匂い、触、心地よさ）
                    '美', '味', '匂い', '触覚', '音', '心地よさ',
                    # 五感の具体的対象
                    '景色', '風景', '色', '花', '料理', '食べ物', '飲み物', '香り',
                    '肌触り', '質感', '音楽', '声', '自然音'
                ],
                'perceptual_verbs': [
                    # 原典の知覚動詞（SV型感動事象用）
                    '見る', '聞く', '味わう', '触る', '嗅ぐ', '感じる',
                    # 基本的なバリエーション
                    '見つめる', '眺める', '聴く', '食べる', '飲む', '触れる'
                ],
                'subcategories': ['美', '味', '匂い', '触', '心地よさ']
            },
            'THINK': {
                'feeling_expressions': [
                    # 原典の基本表現（最重要）
                    'わかった', 'なるほど', 'すごい',
                    # 基本表現のバリエーション
                    'へー', '知らなかった', '面白い', '理解できた', '納得', '発見した', 
                    '気づいた', '勉強になる', '解けた', '興味深い', 
                    # 知見拡大に関する表現
                    '判明した', 'ひらめいた', '学んだ', '覚えた', '驚いた', 'びっくりした',
                    '目から鱗', '想像以上', '意外', '新しい発見'
                ],
                'objects': [
                    # 原典サブカテゴリに基づく対象（理解、発見、納得、圧倒、学習、気づき）
                    '理解', '発見', '納得', '圧倒', '学習', '気づき',
                    # 知見拡大の具体的対象
                    '知識', '情報', '事実', '真実', '問題', '課題', '謎', '疑問', '答え',
                    '解決策', '方法', 'コツ', '仕組み', '原理', 'アイデア'
                ],
                'cognitive_verbs': [
                    # 原典の認知動詞（SV型感動事象用）
                    '理解する', '発見する', '学ぶ', '気づく', '知る',
                    # 基本的なバリエーション
                    'わかる', '解く', '解ける', '覚える', '見つける', '察する'
                ],
                'subcategories': ['理解', '納得', '発見', '圧倒']
            },
            'ACT': {
                'feeling_expressions': [
                    # 原典の基本表現（最重要）
                    'できた', 'やった', 'よかった', 'すごい',
                    # 体験拡大に関する基本表現
                    '達成', '成長', '頑張った', '成功', '完走', 'クリア', '突破', '進歩',
                    # 体験拡大のバリエーション
                    '成功した', '達成した', '完成した', '完走した', '突破した', '挑戦した',
                    '努力した', '成長した', '進歩した', '上達した', '体験した', '経験した',
                    '満足した', '充実した', '特別だった', '貴重だった', '幸運だった'
                ],
                'objects': [
                    # 原典サブカテゴリに基づく対象（努力、上達、進歩、達成、挑戦、経験、成功、特別感、稀有、遭遇、幸運）
                    '努力', '上達', '進歩', '達成', '挑戦', '経験', '成功', '完走', '成長',
                    '特別感', '稀有', '遭遇', '幸運',
                    # 体験拡大の具体的対象
                    '活動', '行動', '実践', 'トライ', '試み', '取り組み', '体験', '出来事',
                    '機会', 'チャンス', '価値', '意義', 'やりがい', '充実感', '満足感'
                ],
                'action_verbs': [
                    # 原典の行為動詞（SOV型感動事象用）
                    '頑張る', '挑戦する', '達成する', '成長する', '経験する',
                    # 基本的なバリエーション
                    '完走する', 'クリアする', '突破する', '努力する', '成功する',
                    '体験する', '乗り越える'
                ],
                'subcategories': ['努力', '上達', '成長', '進歩', '達成', '特別感', '稀有', '遭遇', '幸運']
            },
            'RELATE': {
                'feeling_expressions': [
                    # 原典の基本表現（最重要）
                    'すばらしい', 'ありがたい', '一緒だ',
                    # 関係性拡大に関する基本表現
                    'うれしい', '愛おしい', '温かい', 'つながり', '感謝', '愛情', '絆', '支え',
                    # 関係性拡大のバリエーション
                    '感謝している', '助かった', '救われた', '支えられた', '共感する',
                    '理解される', '心が通う', '親近感を覚える', 'やさしい', '思いやりがある',
                    '尊敬する', '認められる', '褒められる', '安らぎがある'
                ],
                'objects': [
                    # 原典サブカテゴリに基づく対象（愛、絆、感謝、共感、支援、協力、理解、やさしさ、親近感、愛着、調和、一体感、承認、尊敬）
                    '愛', '絆', '感謝', '共感', '支援', '協力', '理解', '友情', '家族',
                    'やさしさ', '親近感', '愛着', '調和', '一体感', '承認', '尊敬',
                    # 関係性拡大の具体的対象
                    '愛情', '思いやり', '優しさ', '温かさ', '心', 'つながり', '関係',
                    '友達', '仲間', '恩', '人情', '情', '同情', 'お礼', '謝意'
                ],
                'relationship_verbs': [
                    # 原典の関係動詞（SOV型感動事象用）
                    '助ける', '支える', '共感する', '愛する', '感謝する',
                    # 基本的なバリエーション
                    '励ます', '応援する', '理解する', '受け入れる', '協力する',
                    '思いやる', '気遣う', '認める', '褒める', '尊敬する'
                ],
                'subcategories': ['愛', 'つながり', 'やさしさ', '親近感', '愛着', '調和', '一体感', '感謝', '承認', '尊敬']
            }
        }
        
        # 感動表現の強度
        self.intensity_words = {
            '非常に': 2.0, 'とても': 1.8, 'すごく': 1.7, '本当に': 1.5, 
            'かなり': 1.3, 'まあまあ': 0.8, '少し': 0.6, 'ちょっと': 0.5
        }
        
        # 文脈重み付けシステム
        self.context_weights = {
            # 同一カテゴリ内での重複強化
            'same_category_bonus': 1.3,
            # 異なるカテゴリでの競合時の調整
            'cross_category_penalty': 0.9,
            # 文型との一致度による重み
            'sentence_type_match_bonus': 1.2,
            'sentence_type_mismatch_penalty': 0.8
        }
        
        # 否定表現パターン
        self.negation_patterns = [
            'ない', 'なかった', 'ません', 'ませんでした',
            'じゃない', 'ではない', 'くない', 'ではなかった'
        ]

    def analyze(self, text: str) -> AnalysisResult:
        """メイン分析メソッド"""
        # 前処理
        text = self._preprocess(text)
        
        # 形態素解析（利用可能な場合）
        morphological_analysis = self._morphological_analyze(text)
        
        # 感情強度分析
        emotion_intensity = self._analyze_emotion_intensity(text, morphological_analysis)
        
        # STAR各要素のスコア計算（形態素解析結果を活用）
        scores = self._calculate_scores_enhanced(text, morphological_analysis)
        
        # 主分類の決定
        primary_category = max(scores, key=scores.get)
        
        # 信頼度評価
        confidence = self._calculate_confidence(scores, text)
        
        # 文型判定
        sentence_type = self._determine_sentence_type(text)
        
        # キーワード抽出
        keywords = self._extract_keywords(text)
        
        # 基本構造文パターン判定
        structure_pattern = self._determine_structure_pattern(primary_category, sentence_type)
        
        # 感情変化の追跡
        emotion_progression = self._track_emotion_progression(text)
        
        # 複合感情の検出
        mixed_emotions = self._detect_mixed_emotions(text, scores)
        
        # 詳細分析
        detailed_analysis = self._detailed_analysis(text, scores, keywords)
        detailed_analysis['emotion_progression'] = emotion_progression
        detailed_analysis['mixed_emotions'] = mixed_emotions
        
        # 短文・長文への対応強化
        analysis_quality = self._assess_analysis_quality(text, scores, morphological_analysis)
        detailed_analysis['analysis_quality'] = analysis_quality
        
        # 品詞タグ抽出
        detected_pos_tags = []
        if morphological_analysis:
            detected_pos_tags = [item['pos'] for item in morphological_analysis if 'pos' in item]
        
        return AnalysisResult(
            text=text,
            scores=scores,
            primary_category=primary_category,
            confidence=confidence,
            sentence_type=sentence_type,
            keywords=keywords,
            structure_pattern=structure_pattern,
            detailed_analysis=detailed_analysis,
            morphological_analysis=morphological_analysis,
            emotion_intensity=emotion_intensity,
            detected_pos_tags=detected_pos_tags
        )

    def _preprocess(self, text: str) -> str:
        """テキストの前処理"""
        # 改行や余分な空白を除去
        text = re.sub(r'\s+', ' ', text.strip())
        return text

    def _calculate_scores(self, text: str) -> Dict[str, float]:
        """STAR各要素のスコア計算（FEEL要素を考慮）"""
        scores = {'SENSE': 0.0, 'THINK': 0.0, 'ACT': 0.0, 'RELATE': 0.0}
        
        for category, keywords in self.keywords.items():
            score = 0.0
            
            # 各カテゴリのキーワードをチェック
            for word_type, word_list in keywords.items():
                for word in word_list:
                    if word in text:
                        # 実感の形容表現は高い重み
                        if word_type == 'feeling_expressions':
                            base_score = 2.0
                        else:
                            base_score = 1.0
                        
                        # 強度修飾語による重み付け
                        for intensity, multiplier in self.intensity_words.items():
                            if intensity + word in text or word + intensity in text:
                                base_score *= multiplier
                                break
                        
                        score += base_score
            
            scores[category] = score
        
        # FEEL要素（感情の高ぶり）のボーナス
        feel_score = self._calculate_feel_score(text)
        for category in scores:
            if scores[category] > 0:
                scores[category] += feel_score
        
        # 正規化
        total_score = sum(scores.values())
        if total_score > 0:
            scores = {k: v / total_score for k, v in scores.items()}
        
        return scores
    
    def _count_keywords_in_text(self, text: str) -> int:
        """テキスト内のキーワード数カウント"""
        count = 0
        for category_keywords in self.keywords.values():
            for keyword_list in category_keywords.values():
                for keyword in keyword_list:
                    if keyword in text:
                        count += 1
        return count

    def _calculate_confidence(self, scores: Dict[str, float], text: str) -> str:
        """信頼度評価（詳細化）"""
        max_score = max(scores.values())
        second_max = sorted(scores.values(), reverse=True)[1] if len(scores) > 1 else 0
        
        # スコア差による信頼度判定
        score_diff = max_score - second_max
        
        # 詳細な信頼度情報を格納
        confidence_details = {
            'score_diff': score_diff,
            'max_score': max_score,
            'second_max': second_max,
            'text_length': len(text),
            'keyword_count': self._count_keywords_in_text(text)
        }
        
        # 基本信頼度判定
        if score_diff > 0.5 and max_score > 0.3:
            basic_confidence = "高"
        elif score_diff > 0.2 and max_score > 0.2:
            basic_confidence = "中"
        else:
            basic_confidence = "低"
            
        # 追加要因による調整
        if len(text) < 10:
            confidence_details['short_text_penalty'] = True
        if confidence_details['keyword_count'] == 0:
            confidence_details['no_keywords_penalty'] = True
            
        # 信頼度詳細を属性として保存（GUI表示用）
        self.last_confidence_details = confidence_details
        
        return basic_confidence

    def _determine_sentence_type(self, text: str) -> str:
        """文型判定（SV型 or SOV型）- 理論に基づく精密な判定"""
        
        # SOV型の判定（主語+目的語+動詞パターン）
        # ACT・RELATEの感動事象は主体と対象から構成される
        sov_patterns = [
            # 典型的なSOV構造
            r'(.+?)が(.+?)を(.+?)(?:する|した|している|してる)',
            r'(.+?)が(.+?)に(.+?)(?:する|した|している|してる)', 
            r'(.+?)が(.+?)と(.+?)(?:する|した|している|してる)',
            
            # 助詞「を」「に」「と」を含む行為表現
            r'(.+?)を(.+?)(?:する|した|できる|できた|やる|やった)',
            r'(.+?)に(.+?)(?:する|した|なる|なった|与える|与えた)',
            r'(.+?)と(.+?)(?:する|した|いる|いた|なる|なった)',
            
            # 完走、達成、克服等の行為
            r'(.+?)を(?:完走|達成|克服|成功|クリア)',
            r'(.+?)に(?:挑戦|参加|貢献|協力)',
            
            # 関係性を表す動詞
            r'(.+?)(?:を|に)(?:助け|支え|励まし|応援|理解)',
            r'(.+?)(?:から|に)(?:助けられ|支えられ|励まされ|応援され)'
        ]
        
        # SV型の判定（主語+動詞パターン）
        # SENSE・THINKの感動事象は主体のみで構成される
        sv_indicators = [
            # 知覚動詞（見る、聞く、感じる等）
            r'(.+?)(?:を|が)(?:見|聞|感じ|味わ|触|嗅)',
            r'(.+?)(?:が|は)(?:美し|きれ|おいし|心地よ|かぐわし)',
            
            # 理解・発見系
            r'(.+?)(?:が|を)(?:わか|理解|発見|解|判明)',
            r'(.+?)(?:が|は)(?:すご|面白|興味深|素晴らし)',
            
            # 状態変化（主語のみの変化）
            r'(.+?)(?:が|は)(?:なっ|変わっ|見え|聞こえ)'
        ]
        
        # SOV型の優先判定（より明確な構造があるため）
        for pattern in sov_patterns:
            if re.search(pattern, text):
                return "SOV型"
        
        # SV型の判定
        for pattern in sv_indicators:
            if re.search(pattern, text):
                return "SV型"
        
        # 助詞による簡易判定
        if any(particle in text for particle in ['を', 'に', 'と']) and \
           any(verb in text for verb in ['する', 'した', 'やる', 'やった', 'できた']):
            return "SOV型"
        
        # デフォルトはSV型（SENSE/THINKの方が基本的）
        return "SV型"

    def _extract_keywords(self, text: str) -> List[str]:
        """キーワード抽出"""
        found_keywords = set()
        
        for category, keywords in self.keywords.items():
            for word_type, word_list in keywords.items():
                for word in word_list:
                    if word in text:
                        found_keywords.add(word)
        
        return list(found_keywords)

    def _determine_structure_pattern(self, category: str, sentence_type: str) -> str:
        """感動の基本構造文パターン判定"""
        if category == 'SENSE':
            return "SENSE型（SV構造）: 私は【感動事象の主体】を【知覚動詞】した。その結果、【美・味・匂い等】に対して【きれい・おいしい等】と感じて感動した。"
        elif category == 'THINK':
            return "THINK型（SV構造）: 私は【感動事象の主体】を【知覚動詞】した。その結果、【理解・発見・納得等】に対して【わかった・なるほど等】と感じて感動した。"
        elif category == 'ACT':
            return "ACT型（SOV構造）: 私は【感動事象の主体】が【感動事象の対象】に【行為動詞】するのを【知覚動詞】した。その結果、【努力・達成・成長等】に対して【できた・やった等】と感じて感動した。"
        else:  # RELATE
            return "RELATE型（SOV構造）: 私は【感動事象の主体】が【感動事象の対象】に【関係動詞】するのを【知覚動詞】した。その結果、【愛・絆・感謝等】に対して【ありがたい・すばらしい等】と感じて感動した。"

    def _calculate_feel_score(self, text: str) -> float:
        """FEEL要素（感情の高ぶり）のスコア計算"""
        feel_indicators = [
            '感動', '心が動く', '胸が熱く', '涼しく', '心が温かく', 
            '気持ちがいい', '心が踊る', '感情', '心が満たされる'
        ]
        
        score = 0.0
        for indicator in feel_indicators:
            if indicator in text:
                score += 0.5
        
        # 感嘆符によるFEELスコア加算
        score += (text.count('!') + text.count('！')) * 0.2
        
        return min(score, 2.0)  # 上限設定

    def _detect_feel_indicators(self, text: str) -> List[str]:
        """FEEL要素（感情の高ぶり）の検出"""
        indicators = []
        
        feel_expressions = [
            '感動', '心が動く', '胸が熱く', '涼しく', '心が温かく',
            '気持ちがいい', '心が踊る', '感情', '心が満たされる'
        ]
        
        for expression in feel_expressions:
            if expression in text:
                indicators.append(expression)
        
        # 感嘆符
        exclamation_count = text.count('!') + text.count('！')
        if exclamation_count > 0:
            indicators.append(f'感嘆符({exclamation_count}個)')
        
        return indicators

    def _detailed_analysis(self, text: str, scores: Dict[str, float], keywords: List[str]) -> Dict[str, any]:
        """詳細分析（FEEL要素を含む）"""
        return {
            'text_length': len(text),
            'keyword_count': len(keywords),
            'emotion_intensity': self._calculate_emotion_intensity(text),
            'feel_score': self._calculate_feel_score(text),
            'score_distribution': scores,
            'detected_patterns': self._detect_emotion_patterns(text),
            'feel_indicators': self._detect_feel_indicators(text)
        }
    
    def _assess_analysis_quality(self, text: str, scores: Dict[str, float], morphological_analysis) -> Dict[str, any]:
        """分析品質の評価（短文・長文対応）"""
        text_length = len(text)
        max_score = max(scores.values())
        keyword_count = self._count_keywords_in_text(text)
        
        quality_assessment = {
            'text_category': 'normal',
            'reliability': 'medium',
            'suggestions': [],
            'alternative_approaches': []
        }
        
        # 短文判定と対応
        if text_length < 15:
            quality_assessment['text_category'] = 'short'
            quality_assessment['reliability'] = 'low' if keyword_count == 0 else 'medium'
            quality_assessment['suggestions'].append('より詳細な感動体験の記述をお試しください')
            quality_assessment['alternative_approaches'].append('interactive_enhancement')
            
        # 長文判定と対応  
        elif text_length > 200:
            quality_assessment['text_category'] = 'long'
            # 複数感情の混在チェック
            high_scores = [k for k, v in scores.items() if v > 0.2]
            if len(high_scores) > 2:
                quality_assessment['suggestions'].append('複数の感動体験が混在している可能性があります')
                quality_assessment['alternative_approaches'].append('segment_analysis')
        
        # キーワード不足への対応
        if keyword_count == 0:
            quality_assessment['suggestions'].append('STAR理論のキーワードが検出されませんでした')
            quality_assessment['alternative_approaches'].append('guided_input')
            
        # スコアが低い場合の対応
        if max_score < 0.1:
            quality_assessment['reliability'] = 'very_low'
            quality_assessment['suggestions'].append('感動体験の表現が不明確な可能性があります')
            quality_assessment['alternative_approaches'].append('manual_categorization')
            
        return quality_assessment

    def _calculate_emotion_intensity(self, text: str) -> float:
        """感情強度の計算"""
        intensity = 1.0
        
        # 感嘆符による強度アップ
        intensity += text.count('!') * 0.2
        intensity += text.count('！') * 0.2
        
        # 強調語による強度アップ
        for word, multiplier in self.intensity_words.items():
            if word in text:
                intensity *= multiplier
                break
                
        return min(intensity, 3.0)  # 上限設定

    def _detect_emotion_patterns(self, text: str) -> List[str]:
        """感情パターンの検出"""
        patterns = []
        
        if '!' in text or '！' in text:
            patterns.append('感嘆表現')
        if any(word in text for word in ['とても', 'すごく', '非常に']):
            patterns.append('強調表現')
        if any(word in text for word in ['ありがとう', '感謝']):
            patterns.append('感謝表現')
        if any(word in text for word in ['できた', 'やった', '成功']):
            patterns.append('達成表現')
        
        # FEEL要素の確認
        if self._calculate_feel_score(text) > 0:
            patterns.append('FEEL要素あり')
            
        return patterns

    def _morphological_analyze(self, text: str) -> Optional[List[Dict]]:
        """統合形態素解析メソッド（Janome専用）"""
        if not self.morphological_analyzer:
            return None
        
        try:
            if self.analyzer_type == "modern":  # Janome
                return self._analyze_with_janome(text)
            else:
                return None
                
        except Exception as e:
            print(f"形態素解析エラー: {e}")
            return None
    
    def _analyze_with_janome(self, text: str) -> List[Dict]:
        """Janomeによる形態素解析"""
        result = []
        try:
            for token in self.morphological_analyzer.tokenize(text):
                # Janomeの品詞情報を標準化
                pos_info = token.part_of_speech.split(',')
                pos_main = pos_info[0] if pos_info else "未知"
                
                result.append({
                    'surface': token.surface,          # 表層形
                    'reading': pos_info[7] if len(pos_info) > 7 and pos_info[7] != '*' else token.surface,  # 読み
                    'pos': pos_main,                   # 主品詞
                    'pos_detail': pos_info[1] if len(pos_info) > 1 else '*',  # 品詞詳細
                    'base_form': token.base_form       # 基本形
                })
            return result
        except Exception as e:
            print(f"Janome解析エラー: {e}")
            return []

    def _analyze_emotion_intensity(self, text: str, morphological_analysis: Optional[List[Dict]]) -> float:
        """感情強度分析"""
        intensity = 1.0
        
        # 感嘆符による強度
        intensity += text.count('!') * 0.3
        intensity += text.count('！') * 0.3
        
        # 強調語による強度
        for word, multiplier in self.intensity_words.items():
            if word in text:
                intensity *= multiplier
                break
        
        # 形態素解析結果を活用した強度計算
        if morphological_analysis:
            # 形容詞の数による強度調整
            adjective_count = sum(1 for item in morphological_analysis 
                                if item.get('pos', '').startswith('形容詞'))
            intensity += adjective_count * 0.2
            
            # 感動詞による強度調整
            interjection_count = sum(1 for item in morphological_analysis 
                                   if item.get('pos', '').startswith('感動詞'))
            intensity += interjection_count * 0.4
        
        return min(intensity, 3.0)

    def _calculate_scores_enhanced(self, text: str, morphological_analysis: Optional[List[Dict]]) -> Dict[str, float]:
        """形態素解析を活用した拡張スコア計算"""
        # 基本スコア計算
        scores = self._calculate_scores(text)
        
        # 否定表現の検出と調整
        scores = self._apply_negation_detection(text, scores)
        
        # 文脈重み付けの適用
        scores = self._apply_context_weighting(text, scores)
        
        # 形態素解析による精度向上
        if morphological_analysis:
            for item in morphological_analysis:
                surface = item.get('surface', '')
                pos = item.get('pos', '')
                base_form = item.get('base_form', surface)
                
                # 品詞別の重み調整
                pos_weight = 1.0
                if pos.startswith('形容詞'):
                    pos_weight = 1.2  # 形容詞は感情表現として重要
                elif pos.startswith('動詞'):
                    pos_weight = 1.1  # 動詞も重要
                elif pos.startswith('名詞'):
                    pos_weight = 0.9  # 名詞は少し軽く
                
                # 各カテゴリでのマッチング確認
                for category, keywords_dict in self.keywords.items():
                    for keyword_type, keyword_list in keywords_dict.items():
                        if base_form in keyword_list or surface in keyword_list:
                            scores[category] += 0.3 * pos_weight
        
        return scores

    def _apply_negation_detection(self, text: str, scores: Dict[str, float]) -> Dict[str, float]:
        """否定表現の検出と感情スコアの調整"""
        adjusted_scores = scores.copy()
        
        # 否定表現の検出
        has_negation = any(pattern in text for pattern in self.negation_patterns)
        
        if has_negation:
            # 否定表現がある場合、感情スコアを大幅に減少
            for category in adjusted_scores:
                adjusted_scores[category] *= 0.3
        
        return adjusted_scores

    def _apply_context_weighting(self, text: str, scores: Dict[str, float]) -> Dict[str, float]:
        """文脈重み付けシステムの適用"""
        adjusted_scores = scores.copy()
        
        # 各カテゴリでのキーワード出現数をカウント
        category_keyword_counts = {}
        category_matches = {}
        
        for category, keywords_dict in self.keywords.items():
            category_keyword_counts[category] = 0
            category_matches[category] = []
            
            for keyword_type, keyword_list in keywords_dict.items():
                for keyword in keyword_list:
                    if keyword in text:
                        category_keyword_counts[category] += 1
                        category_matches[category].append(keyword)
        
        # 同一カテゴリ内での複数キーワード検出時のボーナス
        for category in adjusted_scores:
            if category_keyword_counts[category] > 1:
                bonus = min(category_keyword_counts[category] * 0.2, 0.8)  # 最大0.8のボーナス
                adjusted_scores[category] *= (1 + bonus)
                
        # 文型との一致度による重み調整
        sentence_type = self._determine_sentence_type(text)
        
        # SV型 → SENSE/THINK優遇、SOV型 → ACT/RELATE優遇
        if sentence_type == 'SV型':
            adjusted_scores['SENSE'] *= self.context_weights['sentence_type_match_bonus']
            adjusted_scores['THINK'] *= self.context_weights['sentence_type_match_bonus']
            adjusted_scores['ACT'] *= self.context_weights['sentence_type_mismatch_penalty']
            adjusted_scores['RELATE'] *= self.context_weights['sentence_type_mismatch_penalty']
        elif sentence_type == 'SOV型':
            adjusted_scores['ACT'] *= self.context_weights['sentence_type_match_bonus']
            adjusted_scores['RELATE'] *= self.context_weights['sentence_type_match_bonus']
            adjusted_scores['SENSE'] *= self.context_weights['sentence_type_mismatch_penalty']
            adjusted_scores['THINK'] *= self.context_weights['sentence_type_mismatch_penalty']
        
        return adjusted_scores

    def _track_emotion_progression(self, text: str) -> List[Dict]:
        """文章内での感情変化の追跡"""
        progression = []
        
        # 文を句読点や接続詞で分割
        sentence_parts = self._split_into_parts(text)
        
        for i, part in enumerate(sentence_parts):
            if len(part.strip()) < 2:
                continue
                
            # 各部分での感情分析
            part_scores = {}
            for category in ['SENSE', 'THINK', 'ACT', 'RELATE']:
                part_scores[category] = 0.0
                
                # キーワードマッチング
                for keyword_type, keyword_list in self.keywords[category].items():
                    for keyword in keyword_list:
                        if keyword in part:
                            part_scores[category] += 1.0
            
            # 最大スコアのカテゴリを特定
            max_category = max(part_scores, key=part_scores.get) if max(part_scores.values()) > 0 else None
            
            if max_category:
                progression.append({
                    'position': i,
                    'text_part': part,
                    'dominant_emotion': max_category,
                    'score': part_scores[max_category],
                    'all_scores': part_scores
                })
        
        return progression

    def _split_into_parts(self, text: str) -> List[str]:
        """文章を意味のある部分に分割"""
        import re
        
        # 句読点、接続詞、感嘆符で分割
        separators = ['。', '、', 'が', 'けれど', 'しかし', 'でも', 'そして', 'また', 'そこで', '！', '!']
        
        parts = [text]
        for sep in separators:
            new_parts = []
            for part in parts:
                new_parts.extend(part.split(sep))
            parts = [p.strip() for p in new_parts if p.strip()]
        
        return parts

    def _detect_mixed_emotions(self, text: str, scores: Dict[str, float]) -> List[Dict]:
        """複合感情の検出"""
        mixed_emotions = []
        
        # 閾値以上のスコアを持つカテゴリを特定
        threshold = 0.5
        significant_categories = {cat: score for cat, score in scores.items() if score >= threshold}
        
        if len(significant_categories) > 1:
            # 複数のカテゴリが閾値を超えている場合
            sorted_categories = sorted(significant_categories.items(), key=lambda x: x[1], reverse=True)
            
            for i, (category, score) in enumerate(sorted_categories):
                mixed_emotions.append({
                    'category': category,
                    'score': score,
                    'rank': i + 1,
                    'ratio': score / sorted_categories[0][1] if sorted_categories[0][1] > 0 else 0
                })
        
        return mixed_emotions


# テスト用の関数
def test_analyzer():
    """分析器のテスト"""
    analyzer = STARAnalyzer()
    
    test_cases = [
        "この料理、本当においしい！",
        "やっと問題が解けた！",
        "マラソンを完走できて嬉しい",
        "友達が励ましてくれて感謝している",
        "夕日がとても美しく見えた"
    ]
    
    for text in test_cases:
        result = analyzer.analyze(text)
        print(f"\n分析対象: {text}")
        print(f"主分類: {result.primary_category}")
        print(f"信頼度: {result.confidence}")
        print(f"文型: {result.sentence_type}")
        print(f"スコア: {result.scores}")
        print(f"キーワード: {result.keywords}")


if __name__ == "__main__":
    test_analyzer()