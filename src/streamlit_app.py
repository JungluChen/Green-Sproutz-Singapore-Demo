import streamlit as st

st.set_page_config(
    page_title="YouTube currentTime",  # 页面标题
    page_icon="▶️",                   # 页面图标
    layout="centered",                # 页面布局：居中
    initial_sidebar_state="collapsed", # 侧边栏初始状态：折叠
    menu_items=None                   # 不显示菜单项
)
# 使用markdown注入CSS：设置背景色为#0e1117，文字颜色为#000000
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    </style>
    """, unsafe_allow_html=True)
st.title("🎓 E-Learning Interactive Learning Platform")


pg = st.navigation(["setting.py", "test.py", "forum.py"])
pg.run()