# -*- coding: utf-8 -*-
"""
修复搜索问题
主要问题：
1. 分词问题："乔老师"被分成"乔"和"老师"，"乔"被过滤掉
2. 停用词过滤过于严格
3. BM25索引缺少关键词
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'code'))

from search_interface import SearchInterface
from advanced_search_system import AdvancedSearchSystem
import jieba
import jieba.analyse

def fix_search_issues():
    """
    修复搜索问题
    """
    print("=" * 60)
    print("修复搜索问题")
    print("=" * 60)
    
    print("\n问题分析:")
    print("1. 分词问题：'乔老师'被分成'乔'和'老师'，'乔'被过滤掉")
    print("2. 停用词过滤过于严格，单字符被过滤")
    print("3. BM25索引缺少关键词")
    print("4. 向量搜索能找到相关文档，但综合评分时被BM25拖累")
    
    print("\n解决方案:")
    print("1. 修改预处理函数，保留重要的单字符（如人名）")
    print("2. 添加自定义词典")
    print("3. 调整权重配置")
    
    # 测试当前分词效果
    print("\n" + "=" * 40)
    print("当前分词效果测试")
    print("=" * 40)
    
    test_queries = [
        "乔老师的手机",
        "技术真的可以拉开差距吗",
        "乔梁老师",
        "手机号码"
    ]
    
    # 添加自定义词典
    print("\n添加自定义词典...")
    jieba.add_word("乔老师", freq=1000, tag='nr')
    jieba.add_word("乔梁", freq=1000, tag='nr')
    jieba.add_word("手机号", freq=500, tag='n')
    
    for query in test_queries:
        print(f"\n查询: {query}")
        
        # 原始jieba分词
        words_original = jieba.lcut(query)
        print(f"  原始分词: {words_original}")
        
        # 关键词抽取
        keywords = jieba.analyse.extract_tags(query, topK=5, withWeight=True)
        print(f"  关键词抽取: {keywords}")
        
        # 模拟改进的预处理
        words_improved = improved_preprocess_text(query)
        print(f"  改进预处理: {words_improved}")
    
    print("\n" + "=" * 40)
    print("测试改进后的搜索效果")
    print("=" * 40)
    
    # 初始化搜索接口
    search_interface = SearchInterface("balanced")
    
    if not search_interface.initialize():
        print("❌ 搜索系统初始化失败")
        return
    
    # 临时修改搜索系统的预处理函数
    original_preprocess = search_interface.search_system.preprocess_text
    search_interface.search_system.preprocess_text = improved_preprocess_text
    
    # 重新构建BM25索引
    print("\n重新构建BM25索引...")
    search_interface.search_system.build_global_bm25_index()
    
    # 测试改进后的搜索
    test_queries_detailed = [
        ("乔老师的手机", "应该找到乔梁老师的手机号信息"),
        ("技术真的可以拉开差距吗", "应该找到chap02中关于技术差距的讨论")
    ]
    
    for query, expected in test_queries_detailed:
        print(f"\n测试查询: {query}")
        print(f"期望结果: {expected}")
        
        try:
            result = search_interface.search(query, top_k=5)
            
            print(f"结果数量: {result.get('total_results', 0)}")
            print(f"搜索时间: {result.get('search_time', 0):.3f}秒")
            print(f"提取关键词: {result.get('keywords_extracted', [])}")
            
            if result.get('results'):
                print("\n搜索结果:")
                for i, res in enumerate(result['results'][:3]):
                    print(f"\n结果{i+1}:")
                    print(f"  文档ID: {res['document_id']}")
                    print(f"  综合得分: {res['score']:.4f}")
                    print(f"  来源文件: {res['metadata'].get('source_file', '未知')}")
                    print(f"  内容: {res['content'][:100]}...")
                    print(f"  得分详情: vector={res['scores']['vector_score']:.4f}, bm25={res['scores']['bm25_score']:.4f}, exact={res['scores']['exact_score']:.4f}")
                    
                    # 检查是否符合期望
                    content = res['content'].lower()
                    if query == "乔老师的手机" and ('乔' in content or '手机' in content):
                        print(f"  ✅ 符合期望：包含相关内容")
                    elif query == "技术真的可以拉开差距吗" and ('技术' in content or '差距' in content):
                        print(f"  ✅ 符合期望：包含相关内容")
                    else:
                        print(f"  ❓ 相关性待确认")
            else:
                print("❌ 没有找到相关结果")
                
        except Exception as e:
            print(f"查询失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 恢复原始预处理函数
    search_interface.search_system.preprocess_text = original_preprocess
    
    print("\n" + "=" * 60)
    print("修复测试完成")
    print("=" * 60)
    
    print("\n建议的永久修复方案:")
    print("1. 修改 advanced_search_system.py 中的 preprocess_text 方法")
    print("2. 添加自定义词典文件")
    print("3. 调整搜索权重配置")
    print("4. 考虑使用更好的中文分词模型")

def improved_preprocess_text(text: str) -> list:
    """
    改进的文本预处理函数
    """
    import re
    
    # 基本清理
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 分词
    words = jieba.lcut(text)
    
    # 改进的停用词过滤
    stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
    
    # 重要的单字符保留列表（主要是人名、地名等）
    important_single_chars = {'乔', '梁', '李', '王', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴', '徐', '孙', '马', '朱', '胡', '郭', '何', '高'}
    
    filtered_words = []
    for word in words:
        # 保留长度大于1的词
        if len(word) > 1 and word not in stop_words:
            filtered_words.append(word)
        # 保留重要的单字符
        elif len(word) == 1 and word in important_single_chars:
            filtered_words.append(word)
        # 保留数字和英文
        elif len(word) == 1 and (word.isdigit() or word.isalpha()):
            filtered_words.append(word)
    
    return filtered_words

if __name__ == "__main__":
    fix_search_issues()