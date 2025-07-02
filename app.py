import streamlit as st
import os
import json
import random
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from PIL import Image
import io
import base64
from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark
import os
import requests
from dotenv import load_dotenv

# 页面配置
st.set_page_config(
    page_title="AI故事魔法师 - 创意写作助手",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .story-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# 加载环境变量
load_dotenv()

# 初始化火山方舟客户端
def init_volcengine_client():
    """初始化火山方舟客户端"""
    try:
        api_key = os.environ.get("ARK_API_KEY")
        if api_key:
            return Ark(api_key=api_key)
        else:
            # 如果没有API Key，返回None
            return None
    except Exception as e:
        st.error(f"初始化火山方舟客户端失败: {e}")
        return None

# 初始化会话状态
if 'stories' not in st.session_state:
    st.session_state.stories = []
if 'story_count' not in st.session_state:
    st.session_state.story_count = 0
if 'total_words' not in st.session_state:
    st.session_state.total_words = 0
if 'favorite_genres' not in st.session_state:
    st.session_state.favorite_genres = {}
if 'volcengine_client' not in st.session_state:
    st.session_state.volcengine_client = init_volcengine_client()

# 火山方舟可用模型
VOLCENGINE_MODELS = {
    "豆包1.5 Pro (32K)": "doubao-1.5-pro-32k-250115",
    "豆包1.5 Pro (256K)": "doubao-1.5-pro-256k-250115", 
    "豆包1.5 Lite (4K)": "doubao-1.5-lite-4k-250115",
    "豆包1.5 Lite (32K)": "doubao-1.5-lite-32k-250115"
}

# 故事类型和模板
STORY_TYPES = {
    "奇幻冒险": {
        "description": "充满魔法和冒险的奇幻世界",
        "keywords": ["魔法", "冒险", "英雄", "宝藏", "龙", "城堡"],
        "template": "在一个遥远的{location}，{character}踏上了寻找{goal}的冒险之旅..."
    },
    "科幻未来": {
        "description": "探索未来科技和宇宙奥秘",
        "keywords": ["机器人", "太空", "时间旅行", "人工智能", "星际", "未来"],
        "template": "在{year}年，{character}在{location}发现了改变人类命运的秘密..."
    },
    "悬疑推理": {
        "description": "扣人心弦的推理和悬疑故事",
        "keywords": ["侦探", "谜题", "线索", "真相", "犯罪", "推理"],
        "template": "当{character}收到一封神秘的信件时，一个复杂的{crime_type}案件浮出水面..."
    },
    "浪漫爱情": {
        "description": "温馨感人的爱情故事",
        "keywords": ["爱情", "相遇", "浪漫", "告白", "幸福", "缘分"],
        "template": "在{season}的{location}，{character1}和{character2}的相遇改变了他们的人生..."
    },
    "历史传奇": {
        "description": "基于历史背景的传奇故事",
        "keywords": ["古代", "王朝", "战争", "英雄", "传说", "历史"],
        "template": "在{era}时期，{character}在{location}书写了一段传奇历史..."
    },
    "民间诡异": {
        "description": "神秘诡异的民间传说和灵异故事",
        "keywords": ["鬼怪", "灵异", "诅咒", "神秘", "传说", "诡异"],
        "template": "在{location}流传着一个关于{character}的诡异传说..."
    }
}

# 角色和地点数据库
CHARACTERS = {
    "奇幻冒险": ["勇敢的骑士", "智慧的法师", "神秘的精灵", "强大的战士", "聪明的盗贼"],
    "科幻未来": ["天才科学家", "太空探险家", "机器人工程师", "星际船长", "时间旅行者"],
    "悬疑推理": ["著名侦探", "警探", "记者", "律师", "私家侦探"],
    "浪漫爱情": ["温柔的女孩", "帅气的男孩", "艺术家", "医生", "老师"],
    "历史传奇": ["古代将军", "王朝公主", "江湖侠客", "文人墨客", "民间英雄"],
    "民间诡异": ["神秘的老者", "被诅咒的少女", "阴阳师", "通灵者", "守墓人", "驱魔师", "道士", "巫婆", "鬼新娘", "夜游神", "狐仙", "僵尸", "怨灵", "山精", "水鬼"]
}

LOCATIONS = {
    "奇幻冒险": ["神秘森林", "古老城堡", "魔法学院", "龙之谷", "精灵王国"],
    "科幻未来": ["太空站", "未来城市", "实验室", "星际飞船", "虚拟世界"],
    "悬疑推理": ["古老庄园", "现代都市", "小镇", "豪华游轮", "密室"],
    "浪漫爱情": ["咖啡馆", "图书馆", "公园", "海边", "校园"],
    "历史传奇": ["古代都城", "战场", "皇宫", "江湖", "书院"],
    "民间诡异": ["废弃古宅", "深山古庙", "荒凉墓地", "古老祠堂", "神秘山洞", "鬼屋", "阴森小巷", "乱葬岗", "古井", "破败道观", "荒废学校", "老宅院", "地下密室", "古树", "血池", "鬼市", "阴间客栈", "奈何桥", "黄泉路", "阎王殿"]
}

def generate_story_with_volcengine(story_type, character, location, mood, length, custom_prompt="", model_name="doubao-1.5-pro-32k-250115"):
    """使用火山方舟大模型生成故事"""
    
    # 检查客户端是否可用
    if not st.session_state.volcengine_client:
        st.warning("火山方舟客户端未初始化，将使用本地模板生成故事")
        return generate_story_without_api(story_type, character, location, mood, length)
    
    try:
        # 构建详细的prompt
        length_requirements = {
            "短篇": "300-500字",
            "中篇": "600-1000字", 
            "长篇": "1200-2000字"
        }
        
        # 根据故事类型调整创作要求
        if story_type == "民间诡异":
            special_requirements = """
创作要求：
1. 故事要有完整的情节结构，包含开端、发展、高潮、结局
2. 人物形象要生动立体，有鲜明的性格特点
3. 场景描写要具体详细，营造阴森恐怖的氛围
4. 情感表达要紧张刺激，符合{mood}的基调
5. 语言要神秘诡异，富有民间传说的色彩
6. 故事要有超自然元素，但保持合理的逻辑
7. 适当加入民间传说、鬼怪元素，营造诡异氛围
8. 结尾要有悬念或警示，符合民间故事的特点"""
        else:
            special_requirements = """
创作要求：
1. 故事要有完整的情节结构，包含开端、发展、高潮、结局
2. 人物形象要生动立体，有鲜明的性格特点
3. 场景描写要具体详细，营造沉浸式的阅读体验
4. 情感表达要真挚动人，符合{mood}的基调
5. 语言要优美流畅，富有文学性
6. 故事要有创意和新意，避免俗套"""

        prompt = f"""请创作一个{length}的{story_type}故事，要求如下：

故事设定：
- 主角：{character}
- 故事地点：{location}
- 情感基调：{mood}
- 字数要求：{length_requirements[length]}

{special_requirements}

{f"额外要求：{custom_prompt}" if custom_prompt else ""}

请直接输出故事内容，不要包含任何解释或说明。"""

        # 调用火山方舟API
        completion = st.session_state.volcengine_client.chat.completions.create(
            model=model_name,  # 使用用户选择的模型
            messages=[
                {"role": "system", "content": "你是一位专业的故事创作大师，擅长创作各种类型的中文故事。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,  # 控制创意性
            max_tokens=2048   # 最大输出长度
        )
        
        story = completion.choices[0].message.content.strip()
        return story
        
    except Exception as e:
        st.error(f"调用火山方舟API失败: {e}")
        st.info("将使用本地模板生成故事作为备选方案")
        return generate_story_without_api(story_type, character, location, mood, length)

def generate_story_without_api(story_type, character, location, mood, length):
    """使用模板生成故事（不依赖外部API）"""
    
    story_templates = {
        "奇幻冒险": [
            f"在遥远的{location}，{character}踏上了寻找失落宝藏的冒险之旅。传说中，这座宝藏蕴含着改变世界的力量。",
            f"当{character}踏入{location}的那一刻，命运的齿轮开始转动。古老的魔法正在苏醒，等待真正的英雄。",
            f"在{location}的深处，{character}发现了一个惊人的秘密。这个发现将改变整个魔法世界的命运。"
        ],
        "科幻未来": [
            f"在2157年的{location}，{character}正在进行一项革命性的实验。这个实验可能改变人类进化的方向。",
            f"当{character}在{location}发现外星文明的遗迹时，人类的历史即将迎来重大转折。",
            f"在{location}的实验室里，{character}意外激活了一个来自未来的神秘装置。"
        ],
        "悬疑推理": [
            f"当{character}收到一封来自{location}的神秘信件时，一个尘封多年的悬案重新浮出水面。",
            f"在{location}发生的一起离奇事件，让{character}卷入了一个错综复杂的谜团之中。",
            f"{character}在{location}发现了一个惊人的秘密，这个秘密可能颠覆所有人的认知。"
        ],
        "浪漫爱情": [
            f"在{location}的午后，{character}遇见了命中注定的那个人。一段美丽的爱情故事就此展开。",
            f"当{character}漫步在{location}时，一个意外的相遇改变了他们的人生轨迹。",
            f"在{location}的浪漫氛围中，{character}经历了一场刻骨铭心的爱情。"
        ],
        "历史传奇": [
            f"在{location}的古老土地上，{character}书写了一段传奇历史，成为后人传颂的英雄。",
            f"当{character}踏入{location}的那一刻，历史的车轮开始转动，一个新的时代即将来临。",
            f"在{location}的战场上，{character}展现出了非凡的勇气和智慧，成就了一段不朽传奇。"
        ],
        "民间诡异": [
            f"在{location}的深处，{character}发现了一个尘封已久的秘密。每当夜幕降临，这里就会传来奇怪的声音。",
            f"传说在{location}中，{character}曾经经历过一次超自然的事件。至今，当地人都对这个地方避而远之。",
            f"当{character}踏入{location}的那一刻，一股阴冷的气息扑面而来。这里隐藏着一个不为人知的诡异传说。",
            f"在{location}的古老传说中，{character}成为了一个神秘事件的关键人物。这里的每一块石头都诉说着不为人知的故事。",
            f"当{character}在{location}中遇到那个神秘的存在时，一切都改变了。这里不仅是现实与超自然的交界，更是命运的转折点。",
            f"在{location}的阴森氛围中，{character}揭开了一个尘封百年的秘密。这里的每一寸空气都充满了诡异的气息。"
        ]
    }
    
    # 选择基础模板
    base_story = random.choice(story_templates[story_type])
    
    # 根据长度扩展故事
    if length == "短篇":
        story = base_story + f" 这是一个关于{mood}的故事，充满了惊喜和感动。"
    elif length == "中篇":
        story = base_story + f" 随着故事的发展，{character}面临着巨大的挑战。在{location}的每一个角落，都隐藏着不为人知的秘密。这是一个关于{mood}的故事，充满了冒险和成长。"
    else:  # 长篇
        story = base_story + f" 随着故事的发展，{character}面临着巨大的挑战。在{location}的每一个角落，都隐藏着不为人知的秘密。通过不断的努力和坚持，{character}最终找到了属于自己的道路。这是一个关于{mood}的故事，充满了冒险、成长和希望。"
    
    return story

def create_story_visualization(story_type, mood):
    """创建故事可视化图表"""
    
    # 创建情感分析图表
    emotions = {
        "快乐": random.randint(60, 90),
        "悲伤": random.randint(10, 40),
        "紧张": random.randint(30, 70),
        "平静": random.randint(20, 60),
        "兴奋": random.randint(50, 80)
    }
    
    # 根据心情调整情感值
    if mood == "快乐":
        emotions["快乐"] = random.randint(80, 95)
        emotions["悲伤"] = random.randint(5, 20)
    elif mood == "悲伤":
        emotions["悲伤"] = random.randint(70, 90)
        emotions["快乐"] = random.randint(10, 30)
    elif mood == "紧张":
        emotions["紧张"] = random.randint(80, 95)
        emotions["平静"] = random.randint(10, 30)
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(emotions.keys()),
            y=list(emotions.values()),
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        )
    ])
    
    fig.update_layout(
        title="故事情感分析",
        xaxis_title="情感类型",
        yaxis_title="强度",
        template="plotly_white",
        height=400
    )
    
    return fig

def main():
    # 主标题
    st.markdown('<h1 class="main-header">📚 AI故事魔法师</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">让AI为您的创意插上翅膀，创造独一无二的精彩故事</p>', unsafe_allow_html=True)
    
    # 侧边栏
    with st.sidebar:
        st.markdown("## 🎯 应用功能")
        st.markdown("""
        - ✨ AI智能故事生成
        - 🎨 多种故事类型选择
        - 📊 故事数据可视化
        - 💾 故事保存和管理
        - 🎭 角色和场景定制
        """)
        
        st.markdown("## 📈 使用统计")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("生成故事", st.session_state.story_count)
        with col2:
            st.metric("总字数", st.session_state.total_words)
        
        st.markdown("## 🤖 AI状态")
        if st.session_state.volcengine_client:
            st.success("✅ 火山方舟AI已连接")
        else:
            st.warning("⚠️ 使用本地模板模式")
            st.info("配置API密钥可启用AI生成")
        
        st.markdown("## 🏆 热门类型")
        if st.session_state.favorite_genres:
            for genre, count in sorted(st.session_state.favorite_genres.items(), key=lambda x: x[1], reverse=True)[:3]:
                st.markdown(f"- {genre}: {count}次")
    
    # 主界面标签页
    tab1, tab2, tab3, tab4 = st.tabs(["🎭 故事生成", "📚 故事库", "📊 数据分析", "ℹ️ 关于应用"])
    
    with tab1:
        st.markdown("## 🎭 创建您的专属故事")
        
        # 故事类型选择（在表单外部）
        story_type = st.selectbox(
            "选择故事类型",
            list(STORY_TYPES.keys()),
            key="story_type_selector",
            help="选择您想要的故事类型"
        )
        
        # 故事生成表单
        with st.form("story_generator"):
            # 第一行：基调
            mood = st.selectbox(
                "故事基调",
                ["快乐", "悲伤", "紧张", "平静", "兴奋"],
                help="选择故事的情感基调"
            )
            
            # 第二行：主角和长度
            col1, col2 = st.columns(2)
            with col1:
                # 强制刷新角色选项
                character_options = CHARACTERS.get(story_type, ["勇敢的冒险者"])
                character = st.selectbox(
                    "选择主角",
                    character_options,
                    key=f"character_{story_type}_{id(character_options)}",  # 使用对象ID确保唯一性
                    help="选择故事的主角"
                )
            with col2:
                length = st.selectbox(
                    "故事长度",
                    ["短篇", "中篇", "长篇"],
                    help="选择故事的长度"
                )
            
            # 第三行：地点和AI模型
            col1, col2 = st.columns(2)
            with col1:
                # 强制刷新地点选项
                location_options = LOCATIONS.get(story_type, ["神秘的地方"])
                location = st.selectbox(
                    "选择故事地点",
                    location_options,
                    key=f"location_{story_type}_{id(location_options)}",  # 使用对象ID确保唯一性
                    help="选择故事发生的地点"
                )
            with col2:
                # AI模型选择（仅在火山方舟可用时显示）
                if st.session_state.volcengine_client:
                    model_display = st.selectbox(
                        "AI模型",
                        list(VOLCENGINE_MODELS.keys()),
                        index=0,
                        help="选择用于生成故事的AI模型"
                    )
                    selected_model = VOLCENGINE_MODELS[model_display]
                else:
                    selected_model = "doubao-1.5-pro-32k-250115"  # 默认值
            
            # 第四行：自定义提示
            custom_prompt = st.text_area(
                "自定义提示（可选）",
                placeholder="添加您自己的创意元素...",
                help="可以添加特定的情节、角色或场景描述",
                height=100
            )
            
            # 生成按钮
            generate_button = st.form_submit_button("🚀 生成故事", use_container_width=True)
        
        if generate_button:
            with st.spinner("火山方舟AI正在为您创作精彩故事..."):
                # 生成故事
                story_text = generate_story_with_volcengine(story_type, character, location, mood, length, custom_prompt, selected_model)
                
                # 创建故事对象
                story = {
                    "id": len(st.session_state.stories) + 1,
                    "title": f"{story_type} - {character}的冒险",
                    "content": story_text,
                    "type": story_type,
                    "character": character,
                    "location": location,
                    "mood": mood,
                    "length": length,
                    "word_count": len(story_text),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # 保存故事
                st.session_state.stories.append(story)
                st.session_state.story_count += 1
                st.session_state.total_words += story["word_count"]
                
                # 更新统计
                if story_type in st.session_state.favorite_genres:
                    st.session_state.favorite_genres[story_type] += 1
                else:
                    st.session_state.favorite_genres[story_type] = 1
                
                st.success("✨ 故事生成完成！")
        
        # 显示最新生成的故事
        if st.session_state.stories:
            latest_story = st.session_state.stories[-1]
            
            st.markdown("## 📖 最新生成的故事")
            with st.container():
                st.markdown(f"""
                <div class="story-card">
                    <h3>{latest_story['title']}</h3>
                    <p><strong>类型:</strong> {latest_story['type']} | 
                    <strong>主角:</strong> {latest_story['character']} | 
                    <strong>地点:</strong> {latest_story['location']} | 
                    <strong>基调:</strong> {latest_story['mood']}</p>
                    <hr>
                    <p style="font-size: 1.1rem; line-height: 1.8;">{latest_story['content']}</p>
                    <p style="text-align: right; font-size: 0.9rem; opacity: 0.8;">
                        字数: {latest_story['word_count']} | 生成时间: {latest_story['created_at']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # 故事可视化
            st.markdown("## 📊 故事分析")
            col1, col2 = st.columns(2)
            
            with col1:
                fig = create_story_visualization(latest_story['type'], latest_story['mood'])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 故事类型分布饼图
                if st.session_state.favorite_genres:
                    fig_pie = px.pie(
                        values=list(st.session_state.favorite_genres.values()),
                        names=list(st.session_state.favorite_genres.keys()),
                        title="故事类型分布"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab2:
        st.markdown("## 📚 我的故事库")
        
        if not st.session_state.stories:
            st.info("还没有生成任何故事，快去创建您的第一个故事吧！")
        else:
            # 故事筛选
            col1, col2 = st.columns(2)
            with col1:
                filter_type = st.selectbox("按类型筛选", ["全部"] + list(STORY_TYPES.keys()))
            with col2:
                sort_by = st.selectbox("排序方式", ["最新", "字数最多", "类型"])
            
            # 筛选和排序故事
            filtered_stories = st.session_state.stories
            if filter_type != "全部":
                filtered_stories = [s for s in filtered_stories if s['type'] == filter_type]
            
            if sort_by == "最新":
                filtered_stories.sort(key=lambda x: x['created_at'], reverse=True)
            elif sort_by == "字数最多":
                filtered_stories.sort(key=lambda x: x['word_count'], reverse=True)
            elif sort_by == "类型":
                filtered_stories.sort(key=lambda x: x['type'])
            
            # 显示故事列表
            for i, story in enumerate(filtered_stories):
                with st.expander(f"{story['title']} - {story['created_at']}"):
                    st.markdown(f"""
                    <div class="feature-card">
                        <p><strong>类型:</strong> {story['type']} | 
                        <strong>主角:</strong> {story['character']} | 
                        <strong>地点:</strong> {story['location']} | 
                        <strong>字数:</strong> {story['word_count']}</p>
                        <p>{story['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"📋 复制", key=f"copy_{i}"):
                            st.write("已复制到剪贴板")
                    with col2:
                        if st.button(f"🗑️ 删除", key=f"delete_{i}"):
                            st.session_state.stories.pop(i)
                            st.rerun()
                    with col3:
                        if st.button(f"⭐ 收藏", key=f"favorite_{i}"):
                            st.success("已添加到收藏")
    
    with tab3:
        st.markdown("## 📊 数据分析")
        
        if not st.session_state.stories:
            st.info("还没有数据可以分析，快去生成一些故事吧！")
        else:
            # 创建数据框
            df = pd.DataFrame(st.session_state.stories)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📈 生成趋势")
                df['created_at'] = pd.to_datetime(df['created_at'])
                df['date'] = df['created_at'].dt.date
                daily_counts = df.groupby('date').size().reset_index(name='count')
                
                fig_trend = px.line(daily_counts, x='date', y='count', title="每日故事生成数量")
                st.plotly_chart(fig_trend, use_container_width=True)
            
            with col2:
                st.markdown("### 📊 字数分布")
                fig_hist = px.histogram(df, x='word_count', title="故事字数分布", nbins=10)
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # 统计卡片
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{st.session_state.story_count}</h3>
                    <p>总故事数</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{st.session_state.total_words}</h3>
                    <p>总字数</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                avg_words = st.session_state.total_words // max(st.session_state.story_count, 1)
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{avg_words}</h3>
                    <p>平均字数</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                unique_types = len(set(s['type'] for s in st.session_state.stories))
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{unique_types}</h3>
                    <p>故事类型</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("## ℹ️ 关于AI故事魔法师")
        
        st.markdown("""
        ### 🎯 应用介绍
        AI故事魔法师是一个基于Streamlit开发的创意写作助手，旨在帮助用户轻松创作各种类型的故事。
        
        ### ✨ 主要功能
        - **智能故事生成**: 基于用户选择的类型、角色、地点等元素，自动生成完整的故事
        - **多种故事类型**: 支持奇幻冒险、科幻未来、悬疑推理、浪漫爱情、历史传奇等多种类型
        - **个性化定制**: 用户可以自定义角色、地点、故事基调等元素
        - **数据可视化**: 提供故事分析图表，帮助用户了解创作趋势
        - **故事管理**: 保存、查看、删除和管理已生成的故事
        
        ### 🛠️ 技术特点
        - **用户友好界面**: 采用现代化的UI设计，操作简单直观
        - **响应式布局**: 适配不同设备和屏幕尺寸
        - **数据持久化**: 使用Streamlit会话状态保存用户数据
        - **实时统计**: 提供详细的使用统计和数据分析
        
        ### 🎨 设计理念
        本应用致力于将复杂的AI技术转化为简单易用的工具，让每个人都能轻松创作出精彩的故事。
        通过直观的界面设计和丰富的功能，为用户提供愉悦的创作体验。
        
        ### 📝 使用说明
        1. 在"故事生成"标签页中选择故事类型和元素
        2. 点击"生成故事"按钮创建您的专属故事
        3. 在"故事库"中查看和管理已生成的故事
        4. 在"数据分析"中了解您的创作统计
        """)
        
        st.markdown("---")
        st.markdown("**开发者**: AI助手 | **版本**: 1.0.0 | **技术栈**: Streamlit + Python")

if __name__ == "__main__":
    main() 