# -*- coding: utf-8 -*-
"""
验证chap02检测逻辑修复
"""

import sys
sys.path.append('code')

from search_interface import SearchInterface

def verify_chap02_detection():
    print("=== 验证chap02检测逻辑修复 ===")
    
    # 创建搜索接口
    search_interface = SearchInterface()
    
    # 初始化（这里会显示chap02检测结果）
    success = search_interface.initialize()
    
    if success:
        print("\n✅ 搜索接口初始化成功")
    else:
        print("\n❌ 搜索接口初始化失败")
    
    return success

if __name__ == "__main__":
    verify_chap02_detection()