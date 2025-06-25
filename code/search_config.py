#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索系统配置文件
管理高级搜索系统的各种参数和配置
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class SearchConfig:
    """
    搜索系统配置类
    """
    
    # === BM25参数 ===
    bm25_k1: float = 1.5  # BM25参数k1，控制词频饱和度
    bm25_b: float = 0.75  # BM25参数b，控制文档长度归一化
    
    # === 权重配置 ===
    vector_weight: float = 0.4   # 向量匹配权重
    bm25_weight: float = 0.3     # BM25匹配权重
    exact_weight: float = 0.3    # 精确匹配权重
    
    # === 搜索参数 ===
    max_candidates: int = 50     # 最大候选文档数
    default_top_k: int = 10      # 默认返回结果数
    max_context_length: int = 2000  # 最大上下文长度
    
    # === 关键词抽取参数 ===
    max_keywords: int = 10       # 最大关键词数量
    keyword_min_length: int = 2  # 关键词最小长度
    
    # === 停用词列表 ===
    stop_words: List[str] = None
    
    # === 允许的词性 ===
    allowed_pos: List[str] = None
    
    # === 模型配置 ===
    model_name: str = "e:\\PyProjects\\QASystem\\code\\model"
    collection_name: str = "qa_system_chunks"
    chroma_db_path: str = "e:\\PyProjects\\QASystem\\chroma_db"
    
    def __post_init__(self):
        """初始化后处理"""
        if self.stop_words is None:
            self.stop_words = self._load_stopwords()
        
        if self.allowed_pos is None:
            self.allowed_pos = [
                'n',   # 名词
                'nr',  # 人名
                'ns',  # 地名
                'nt',  # 机构名
                'nz',  # 其他专名
                'v',   # 动词
                'vd',  # 副动词
                'vn',  # 名动词
                'a',   # 形容词
                'ad',  # 副形词
                'an',  # 名形词
                'i',   # 成语
                'l',   # 习用语
                'j',   # 简称略语
            ]
    
    def _load_stopwords(self) -> List[str]:
        """从停用词文件加载停用词列表"""
        import os
        stopwords_file = os.path.join(os.path.dirname(__file__), 'stopword.txt')
        stopwords = []
        
        try:
            with open(stopwords_file, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word and not word.startswith('#'):  # 跳过空行和注释行
                        stopwords.append(word)
        except FileNotFoundError:
            print(f"警告：停用词文件 {stopwords_file} 未找到，使用默认停用词")
            # 如果文件不存在，使用默认停用词
            stopwords = [
                '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', 
                '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', 
                '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '里',
                '还', '把', '被', '从', '跟', '对', '为', '以', '所', '可以',
                '能够', '应该', '需要', '可能', '或者', '但是', '然后', '因为',
                '所以', '如果', '虽然', '虽说', '尽管', '无论', '不管', '除了',
                '除非', '只要', '只有', '不仅', '而且', '并且', '以及', '同时'
            ]
        except Exception as e:
            print(f"警告：读取停用词文件时出错 {e}，使用默认停用词")
            stopwords = [
                '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', 
                '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', 
                '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '里',
                '还', '把', '被', '从', '跟', '对', '为', '以', '所', '可以',
                '能够', '应该', '需要', '可能', '或者', '但是', '然后', '因为',
                '所以', '如果', '虽然', '虽说', '尽管', '无论', '不管', '除了',
                '除非', '只要', '只有', '不仅', '而且', '并且', '以及', '同时'
            ]
        
        return stopwords
    
    def validate(self) -> bool:
        """
        验证配置参数的有效性
        
        Returns:
            配置是否有效
        """
        # 检查权重总和
        total_weight = self.vector_weight + self.bm25_weight + self.exact_weight
        if abs(total_weight - 1.0) > 0.01:
            print(f"警告: 权重总和为{total_weight:.3f}，建议调整为1.0")
        
        # 检查BM25参数
        if self.bm25_k1 <= 0:
            print("错误: bm25_k1必须大于0")
            return False
        
        if not (0 <= self.bm25_b <= 1):
            print("错误: bm25_b必须在0-1之间")
            return False
        
        # 检查其他参数
        if self.max_candidates <= 0:
            print("错误: max_candidates必须大于0")
            return False
        
        if self.default_top_k <= 0:
            print("错误: default_top_k必须大于0")
            return False
        
        if self.max_context_length <= 0:
            print("错误: max_context_length必须大于0")
            return False
        
        return True
    
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            配置字典
        """
        return {
            'bm25_k1': self.bm25_k1,
            'bm25_b': self.bm25_b,
            'vector_weight': self.vector_weight,
            'bm25_weight': self.bm25_weight,
            'exact_weight': self.exact_weight,
            'max_candidates': self.max_candidates,
            'default_top_k': self.default_top_k,
            'max_context_length': self.max_context_length,
            'max_keywords': self.max_keywords,
            'keyword_min_length': self.keyword_min_length,
            'model_name': self.model_name,
            'collection_name': self.collection_name,
            'chroma_db_path': self.chroma_db_path,
            'stop_words_count': len(self.stop_words) if self.stop_words else 0,
            'allowed_pos_count': len(self.allowed_pos) if self.allowed_pos else 0
        }
    
    def print_config(self):
        """
        打印配置信息
        """
        print("=== 搜索系统配置 ===")
        print(f"BM25参数: k1={self.bm25_k1}, b={self.bm25_b}")
        print(f"权重配置: 向量={self.vector_weight}, BM25={self.bm25_weight}, 精确={self.exact_weight}")
        print(f"搜索参数: 候选数={self.max_candidates}, 返回数={self.default_top_k}, 上下文长度={self.max_context_length}")
        print(f"关键词: 最大数量={self.max_keywords}, 最小长度={self.keyword_min_length}")
        print(f"模型: {self.model_name}")
        print(f"数据库: {self.chroma_db_path}")
        print(f"停用词数量: {len(self.stop_words)}")
        print(f"允许词性数量: {len(self.allowed_pos)}")
        print("=" * 30)


# === 预定义配置 ===

class PresetConfigs:
    """
    预定义配置集合
    """
    
    @staticmethod
    def balanced() -> SearchConfig:
        """
        平衡配置：各种搜索方法权重相等
        
        Returns:
            平衡配置
        """
        return SearchConfig(
            vector_weight=0.33,
            bm25_weight=0.33,
            exact_weight=0.34,
            bm25_k1=1.5,
            bm25_b=0.75
        )
    
    @staticmethod
    def vector_focused() -> SearchConfig:
        """
        向量优先配置：更重视语义相似性
        
        Returns:
            向量优先配置
        """
        return SearchConfig(
            vector_weight=0.6,
            bm25_weight=0.2,
            exact_weight=0.2,
            bm25_k1=1.2,
            bm25_b=0.75
        )
    
    @staticmethod
    def keyword_focused() -> SearchConfig:
        """
        关键词优先配置：更重视关键词匹配
        
        Returns:
            关键词优先配置
        """
        return SearchConfig(
            vector_weight=0.2,
            bm25_weight=0.6,
            exact_weight=0.2,
            bm25_k1=2.0,
            bm25_b=0.5
        )
    
    @staticmethod
    def exact_focused() -> SearchConfig:
        """
        精确匹配优先配置：更重视精确匹配
        
        Returns:
            精确匹配优先配置
        """
        return SearchConfig(
            vector_weight=0.2,
            bm25_weight=0.2,
            exact_weight=0.6,
            bm25_k1=1.5,
            bm25_b=0.75
        )
    
    @staticmethod
    def fast_search() -> SearchConfig:
        """
        快速搜索配置：减少候选数量，提高速度
        
        Returns:
            快速搜索配置
        """
        return SearchConfig(
            vector_weight=0.5,
            bm25_weight=0.3,
            exact_weight=0.2,
            max_candidates=20,
            default_top_k=3,
            max_context_length=1000,
            max_keywords=5
        )
    
    @staticmethod
    def comprehensive() -> SearchConfig:
        """
        全面搜索配置：更多候选，更详细结果
        
        Returns:
            全面搜索配置
        """
        return SearchConfig(
            vector_weight=0.4,
            bm25_weight=0.3,
            exact_weight=0.3,
            max_candidates=100,
            default_top_k=10,
            max_context_length=3000,
            max_keywords=15
        )


def load_config(config_name: str = "balanced") -> SearchConfig:
    """
    加载预定义配置
    
    Args:
        config_name: 配置名称
        
    Returns:
        搜索配置
    """
    config_map = {
        "balanced": PresetConfigs.balanced,
        "vector": PresetConfigs.vector_focused,
        "keyword": PresetConfigs.keyword_focused,
        "exact": PresetConfigs.exact_focused,
        "fast": PresetConfigs.fast_search,
        "comprehensive": PresetConfigs.comprehensive
    }
    
    if config_name not in config_map:
        print(f"未知配置名称: {config_name}，使用默认平衡配置")
        config_name = "balanced"
    
    config = config_map[config_name]()
    
    if not config.validate():
        print("配置验证失败，使用默认配置")
        config = SearchConfig()
    
    return config


def demo_configs():
    """
    演示不同配置
    """
    print("=== 搜索配置演示 ===")
    
    configs = {
        "平衡配置": PresetConfigs.balanced(),
        "向量优先": PresetConfigs.vector_focused(),
        "关键词优先": PresetConfigs.keyword_focused(),
        "精确匹配优先": PresetConfigs.exact_focused(),
        "快速搜索": PresetConfigs.fast_search(),
        "全面搜索": PresetConfigs.comprehensive()
    }
    
    for name, config in configs.items():
        print(f"\n=== {name} ===")
        config.print_config()
        print(f"配置有效性: {config.validate()}")


if __name__ == "__main__":
    demo_configs()