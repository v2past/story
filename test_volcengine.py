#!/usr/bin/env python3
"""
火山方舟API连接测试脚本
用于验证API密钥配置是否正确
"""

import os
from dotenv import load_dotenv

def test_volcengine_connection():
    """测试火山方舟连接"""
    print("🔍 测试火山方舟API连接...")
    
    # 加载环境变量
    load_dotenv()
    
    # 检查API密钥
    api_key = os.environ.get("ARK_API_KEY")
    if not api_key:
        print("❌ 未找到ARK_API_KEY环境变量")
        print("💡 请在.env文件中设置您的API密钥")
        return False
    
    print(f"✅ 找到API密钥: {api_key[:10]}...")
    
    try:
        # 尝试导入火山方舟SDK
        from volcenginesdkarkruntime import Ark
        print("✅ 火山方舟SDK导入成功")
        
        # 初始化客户端
        client = Ark(api_key=api_key)
        print("✅ 火山方舟客户端初始化成功")
        
        # 测试简单对话
        print("🔄 测试API调用...")
        completion = client.chat.completions.create(
            model="doubao-1.5-pro-32k-250115",
            messages=[
                {"role": "user", "content": "你好，请简单介绍一下你自己"}
            ],
            max_tokens=100
        )
        
        response = completion.choices[0].message.content
        print(f"✅ API调用成功！")
        print(f"📝 响应内容: {response[:50]}...")
        
        return True
        
    except ImportError as e:
        print(f"❌ 火山方舟SDK导入失败: {e}")
        print("💡 请运行: pip install 'volcengine-python-sdk[ark]'")
        return False
        
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        print("💡 请检查API密钥是否正确，网络连接是否正常")
        return False

if __name__ == "__main__":
    print("🚀 火山方舟API连接测试")
    print("=" * 50)
    
    success = test_volcengine_connection()
    
    print("=" * 50)
    if success:
        print("🎉 测试通过！您可以正常使用火山方舟AI功能")
    else:
        print("⚠️ 测试失败，请检查配置后重试")
        print("\n📋 配置步骤:")
        print("1. 在火山引擎控制台获取API密钥")
        print("2. 在项目根目录创建.env文件")
        print("3. 在.env文件中添加: ARK_API_KEY=your_api_key")
        print("4. 安装依赖: pip install -r requirements.txt")
        print("5. 重新运行此测试脚本") 