#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定管理モジュール
JSON設定ファイルの読み込みと管理を行う
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from logger_config import get_logger

logger = get_logger('config')

class ConfigManager:
    """設定ファイル管理クラス"""
    
    def __init__(self, config_dir: str = "."):
        """
        初期化
        Args:
            config_dir: 設定ファイルのディレクトリパス
        """
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.keywords_file = self.config_dir / "keywords.json"
        
        self._config = {}
        self._keywords = {}
        
        self.load_all_configs()
    
    def load_all_configs(self):
        """すべての設定ファイルを読み込み"""
        try:
            self.load_config()
            self.load_keywords()
            logger.info("設定ファイルの読み込みが完了しました")
        except Exception as e:
            logger.error(f"設定ファイルの読み込みエラー: {e}")
            self._load_default_configs()
    
    def load_config(self):
        """config.jsonの読み込み"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            logger.debug(f"設定ファイルを読み込み: {self.config_file}")
        except FileNotFoundError:
            logger.warning(f"設定ファイルが見つかりません: {self.config_file}")
            self._create_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"設定ファイルのJSON形式エラー: {e}")
            self._create_default_config()
    
    def load_keywords(self):
        """keywords.jsonの読み込み"""
        try:
            with open(self.keywords_file, 'r', encoding='utf-8') as f:
                self._keywords = json.load(f)
            logger.debug(f"キーワードファイルを読み込み: {self.keywords_file}")
        except FileNotFoundError:
            logger.warning(f"キーワードファイルが見つかりません: {self.keywords_file}")
            self._create_default_keywords()
        except json.JSONDecodeError as e:
            logger.error(f"キーワードファイルのJSON形式エラー: {e}")
            self._create_default_keywords()
    
    def get_config(self, key_path: str, default=None) -> Any:
        """
        設定値を取得（ドット記法対応）
        Args:
            key_path: 設定のパス（例: "analysis.confidence_thresholds.high"）
            default: デフォルト値
        Returns:
            設定値
        """
        try:
            keys = key_path.split('.')
            value = self._config
            
            for key in keys:
                value = value[key]
            
            return value
        except (KeyError, TypeError):
            logger.debug(f"設定キー '{key_path}' が見つかりません。デフォルト値を使用: {default}")
            return default
    
    def get_keywords(self) -> Dict[str, Dict[str, List[str]]]:
        """キーワード辞書を取得"""
        # negation_patternsとsentence_patternsを除外
        filtered_keywords = {}
        for key, value in self._keywords.items():
            if key not in ['negation_patterns', 'sentence_patterns']:
                filtered_keywords[key] = value
        return filtered_keywords
    
    def get_negation_patterns(self) -> List[str]:
        """否定パターンを取得"""
        return self._keywords.get('negation_patterns', [])
    
    def get_sentence_patterns(self) -> Dict[str, List[str]]:
        """文型パターンを取得"""
        return self._keywords.get('sentence_patterns', {})
    
    def get_intensity_words(self) -> Dict[str, float]:
        """強度修飾語を取得"""
        return self.get_config('analysis.intensity_words', {})
    
    def get_context_weights(self) -> Dict[str, float]:
        """文脈重みを取得"""
        return self.get_config('analysis.context_weights', {})
    
    def get_gui_config(self) -> Dict[str, Any]:
        """GUI設定を取得"""
        return self.get_config('gui', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """ログ設定を取得"""
        return self.get_config('logging', {})
    
    def save_config(self, key_path: str, value: Any):
        """
        設定値を保存
        Args:
            key_path: 設定のパス
            value: 保存する値
        """
        try:
            keys = key_path.split('.')
            config = self._config
            
            # 最後のキー以外まで辿る
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # 値を設定
            config[keys[-1]] = value
            
            # ファイルに保存
            self._save_config_file()
            logger.info(f"設定を保存しました: {key_path} = {value}")
            
        except Exception as e:
            logger.error(f"設定保存エラー: {e}")
    
    def _save_config_file(self):
        """設定ファイルを保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"設定ファイル保存エラー: {e}")
    
    def _create_default_config(self):
        """デフォルト設定を作成"""
        self._config = {
            "version": "1.0.0",
            "system": {
                "name": "STAR Analysis System",
                "default_analyzer": "janome"
            },
            "analysis": {
                "confidence_thresholds": {
                    "high": 0.7,
                    "medium": 0.4,
                    "low": 0.2
                },
                "intensity_words": {
                    "本当に": 1.5,
                    "とても": 1.3,
                    "すごく": 1.4
                },
                "context_weights": {
                    "sentence_type_match_bonus": 1.3,
                    "sentence_type_mismatch_penalty": 0.8,
                    "negation_penalty": 0.4
                }
            }
        }
        logger.info("デフォルト設定を作成しました")
    
    def _create_default_keywords(self):
        """デフォルトキーワードを作成"""
        self._keywords = {
            "SENSE": {
                "feeling_expressions": ["おいしい", "美しい", "気持ちいい"],
                "core_keywords": ["感じる", "実感", "五感"]
            },
            "THINK": {
                "feeling_expressions": ["なるほど", "わかった", "すごい"],
                "core_keywords": ["考える", "理解", "知る"]
            },
            "ACT": {
                "feeling_expressions": ["できた", "達成", "成功"],
                "core_keywords": ["行動", "実践", "挑戦"]
            },
            "RELATE": {
                "feeling_expressions": ["感謝", "一緒", "温かい"],
                "core_keywords": ["人間関係", "協力", "信頼"]
            },
            "negation_patterns": ["ない", "ません"],
            "sentence_patterns": {
                "SV型": ["は", "が"],
                "SOV型": ["を", "に", "で"]
            }
        }
        logger.info("デフォルトキーワードを作成しました")
    
    def _load_default_configs(self):
        """デフォルト設定をすべて読み込み"""
        self._create_default_config()
        self._create_default_keywords()
    
    def reload_configs(self):
        """設定ファイルを再読み込み"""
        logger.info("設定ファイルを再読み込み中...")
        self.load_all_configs()
    
    def validate_config(self) -> bool:
        """設定の妥当性チェック"""
        try:
            # 必須キーの存在確認
            required_keys = [
                'system.name',
                'analysis.confidence_thresholds',
                'analysis.intensity_words'
            ]
            
            for key in required_keys:
                if self.get_config(key) is None:
                    logger.error(f"必須設定キーが見つかりません: {key}")
                    return False
            
            # キーワード辞書の確認
            keywords = self.get_keywords()
            if not all(category in keywords for category in ['SENSE', 'THINK', 'ACT', 'RELATE']):
                logger.error("STAR分類のキーワードが不完全です")
                return False
            
            logger.info("設定の妥当性チェック完了")
            return True
            
        except Exception as e:
            logger.error(f"設定妥当性チェックエラー: {e}")
            return False

# グローバルインスタンス
config_manager = ConfigManager()

def get_config(key_path: str, default=None) -> Any:
    """設定値を取得する便利関数"""
    return config_manager.get_config(key_path, default)

def get_keywords() -> Dict[str, Dict[str, List[str]]]:
    """キーワード辞書を取得する便利関数"""
    return config_manager.get_keywords()

def reload_configs():
    """設定を再読み込みする便利関数"""
    config_manager.reload_configs()