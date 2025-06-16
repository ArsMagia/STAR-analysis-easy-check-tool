#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STAR分析システム用ロギング設定
統一されたログ設定と出力制御
"""

import logging
import os
from datetime import datetime
from pathlib import Path

class STARLogger:
    """STAR分析システム専用ロガー"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            STARLogger._initialized = True
    
    def _setup_logging(self):
        """ログ設定の初期化"""
        # ログディレクトリの作成
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # ログファイル名（日付付き）
        log_filename = f"star_analysis_{datetime.now().strftime('%Y%m%d')}.log"
        log_filepath = log_dir / log_filename
        
        # ログフォーマット
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            datefmt=date_format,
            handlers=[
                logging.FileHandler(log_filepath, encoding='utf-8'),
                logging.StreamHandler()  # コンソール出力も保持
            ]
        )
        
        # 各モジュール用のロガーを作成
        self.analyzer_logger = logging.getLogger('star_analyzer')
        self.gui_logger = logging.getLogger('star_gui')
        self.cli_logger = logging.getLogger('star_cli')
        
        # 初期化完了ログ
        self.analyzer_logger.info("ロギングシステム初期化完了")
    
    def get_logger(self, module_name):
        """モジュール名に対応するロガーを取得"""
        loggers = {
            'analyzer': self.analyzer_logger,
            'gui': self.gui_logger,
            'cli': self.cli_logger
        }
        return loggers.get(module_name, logging.getLogger(module_name))
    
    @staticmethod
    def get_instance():
        """シングルトンインスタンスを取得"""
        if STARLogger._instance is None:
            STARLogger()
        return STARLogger._instance

# 便利な関数
def get_logger(module_name='star'):
    """簡単にロガーを取得するための関数"""
    star_logger = STARLogger.get_instance()
    return star_logger.get_logger(module_name)

# デバッグレベルの設定関数
def set_debug_level(debug=False):
    """デバッグレベルを設定"""
    level = logging.DEBUG if debug else logging.INFO
    logging.getLogger().setLevel(level)
    for handler in logging.getLogger().handlers:
        handler.setLevel(level)