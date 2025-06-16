#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
キーワード検索最適化モジュール
O(n*m) → O(n + m) の高速検索を実現
"""

from collections import defaultdict
import re
from typing import Dict, List, Set, Tuple
from logger_config import get_logger

logger = get_logger('optimizer')

class KeywordSearchOptimizer:
    """高速キーワード検索エンジン"""
    
    def __init__(self, keywords_dict: Dict[str, Dict[str, List[str]]]):
        """
        初期化
        Args:
            keywords_dict: {category: {type: [keywords]}} 形式の辞書
        """
        self.original_keywords = keywords_dict
        self.keyword_index = defaultdict(set)  # keyword -> set of (category, type, weight)
        self.category_weights = defaultdict(float)
        self.max_keyword_length = 0
        
        self._build_search_index()
        logger.info(f"キーワードインデックス構築完了: {len(self.keyword_index)}語")
    
    def _build_search_index(self):
        """検索用インデックスの構築"""
        logger.debug("キーワード検索インデックスを構築中...")
        
        for category, types_dict in self.original_keywords.items():
            for keyword_type, keywords in types_dict.items():
                # キーワードタイプによる重み設定
                type_weight = self._get_type_weight(keyword_type)
                
                for keyword in keywords:
                    # キーワードの正規化
                    normalized_keyword = self._normalize_keyword(keyword)
                    
                    # インデックスに追加
                    self.keyword_index[normalized_keyword].add((category, keyword_type, type_weight))
                    
                    # 最大キーワード長の追跡
                    self.max_keyword_length = max(self.max_keyword_length, len(keyword))
        
        logger.debug(f"インデックス構築完了: 最大キーワード長={self.max_keyword_length}")
    
    def _get_type_weight(self, keyword_type: str) -> float:
        """キーワードタイプによる重み計算"""
        weights = {
            'feeling_expressions': 1.5,    # 感情表現は最重要
            'core_keywords': 1.3,          # コアキーワードは重要
            'auxiliary_expressions': 1.1,   # 補助表現は中程度
            'context_keywords': 0.9,       # 文脈キーワードは軽め
            'modifiers': 0.8               # 修飾語は最軽量
        }
        return weights.get(keyword_type, 1.0)
    
    def _normalize_keyword(self, keyword: str) -> str:
        """キーワードの正規化"""
        # 空白の削除、小文字化などの正規化
        return keyword.strip().lower()
    
    def fast_search(self, text: str) -> Dict[str, float]:
        """
        高速キーワード検索
        O(n + m) の計算量で実行（nはテキスト長、mはキーワード数）
        """
        if not text:
            return {'SENSE': 0.0, 'THINK': 0.0, 'ACT': 0.0, 'RELATE': 0.0}
        
        # 結果初期化
        scores = defaultdict(float)
        matched_keywords = defaultdict(list)
        
        # テキストの正規化
        normalized_text = text.lower()
        text_length = len(normalized_text)
        
        # スライディングウィンドウによる高速検索
        for start_pos in range(text_length):
            # 最大キーワード長まで、または文末まで
            max_end = min(start_pos + self.max_keyword_length, text_length)
            
            for end_pos in range(start_pos + 1, max_end + 1):
                substring = normalized_text[start_pos:end_pos]
                
                # インデックスから一致するキーワードを検索
                if substring in self.keyword_index:
                    for category, keyword_type, weight in self.keyword_index[substring]:
                        scores[category] += weight
                        matched_keywords[category].append(substring)
        
        # デフォルト値の設定
        final_scores = {}
        for category in ['SENSE', 'THINK', 'ACT', 'RELATE']:
            final_scores[category] = scores.get(category, 0.0)
        
        return final_scores
    
    def get_keyword_matches(self, text: str) -> Dict[str, List[str]]:
        """マッチしたキーワードの詳細を取得"""
        matched_keywords = defaultdict(list)
        normalized_text = text.lower()
        text_length = len(normalized_text)
        
        for start_pos in range(text_length):
            max_end = min(start_pos + self.max_keyword_length, text_length)
            
            for end_pos in range(start_pos + 1, max_end + 1):
                substring = normalized_text[start_pos:end_pos]
                
                if substring in self.keyword_index:
                    for category, keyword_type, weight in self.keyword_index[substring]:
                        matched_keywords[category].append({
                            'keyword': substring,
                            'type': keyword_type,
                            'weight': weight,
                            'position': (start_pos, end_pos)
                        })
        
        return dict(matched_keywords)
    
    def benchmark_search(self, text: str, iterations: int = 1000) -> Dict[str, float]:
        """検索性能のベンチマーク"""
        import time
        
        # 従来の線形検索
        start_time = time.time()
        for _ in range(iterations):
            self._linear_search(text)
        linear_time = time.time() - start_time
        
        # 最適化された検索
        start_time = time.time()
        for _ in range(iterations):
            self.fast_search(text)
        optimized_time = time.time() - start_time
        
        speedup = linear_time / optimized_time if optimized_time > 0 else float('inf')
        
        return {
            'linear_time': linear_time,
            'optimized_time': optimized_time,
            'speedup': speedup,
            'iterations': iterations
        }
    
    def _linear_search(self, text: str) -> Dict[str, float]:
        """従来の線形検索（比較用）"""
        scores = defaultdict(float)
        
        for category, types_dict in self.original_keywords.items():
            for keyword_type, keywords in types_dict.items():
                type_weight = self._get_type_weight(keyword_type)
                for keyword in keywords:
                    if keyword.lower() in text.lower():
                        scores[category] += type_weight
        
        final_scores = {}
        for category in ['SENSE', 'THINK', 'ACT', 'RELATE']:
            final_scores[category] = scores.get(category, 0.0)
            
        return final_scores

class AdvancedKeywordMatcher:
    """高度なキーワードマッチング機能"""
    
    def __init__(self, optimizer: KeywordSearchOptimizer):
        self.optimizer = optimizer
        self.fuzzy_threshold = 0.8  # あいまい検索の閾値
    
    def fuzzy_search(self, text: str, threshold: float = None) -> Dict[str, float]:
        """あいまい検索（類似度による検索）"""
        if threshold is None:
            threshold = self.fuzzy_threshold
        
        # 基本検索の結果を取得
        base_scores = self.optimizer.fast_search(text)
        
        # TODO: より高度なあいまい検索の実装
        # 現在は基本検索と同じ結果を返す
        return base_scores
    
    def contextual_search(self, text: str, context_boost: float = 1.2) -> Dict[str, float]:
        """文脈を考慮した検索"""
        scores = self.optimizer.fast_search(text)
        
        # 文脈による重み調整
        # 例：感嘆符がある場合は感情表現を強化
        if '！' in text or '!!' in text:
            scores['SENSE'] *= context_boost
            scores['ACT'] *= context_boost
        
        # 疑問符がある場合は思考表現を強化
        if '？' in text or '??' in text:
            scores['THINK'] *= context_boost
        
        return scores
    
    def pattern_based_search(self, text: str) -> Dict[str, float]:
        """パターンベースの検索"""
        scores = self.optimizer.fast_search(text)
        
        # 文型パターンによる調整
        patterns = {
            'SV型': ['は', 'が', 'を'],  # 簡略化したパターン
            'SOV型': ['を', 'に', 'で']
        }
        
        # パターンマッチングによるスコア調整
        for pattern_type, markers in patterns.items():
            if any(marker in text for marker in markers):
                if pattern_type == 'SV型':
                    scores['SENSE'] *= 1.1
                    scores['THINK'] *= 1.1
                elif pattern_type == 'SOV型':
                    scores['ACT'] *= 1.1
                    scores['RELATE'] *= 1.1
        
        return scores