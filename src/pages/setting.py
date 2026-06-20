import re
import json
import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval, set_cookie, get_cookie
import pandas as pd

# 设置页面配置：标题为“YouTube currentTime”，图标为▶️，布局居中，侧边栏初始状态为折叠，不显示菜单项


video_url = st.text_input("Paste YouTube link:", "https://www.youtube.com/watch?v=4dCrkp8qgLU")
st.session_state["video_url"] = video_url
st.video(video_url)

st.markdown('<h2>Questions</h2>', unsafe_allow_html=True)

# 默认检查点数据
checkpoints = [
    {"Time": "0:10", "Time": "0:10","Question":" What topic is being discussed?", "choices": ["A. AI Applications", "B. Cloud Computing Trends", "C. Cybersecurity Basics"], "answer": "A. AI Applications"},
    {"Time": "0:25", "Time": "0:25","Question":" What is the keyword?", "choices": ["Alpha", "Beta", "Gamma"], "answer": "Beta"},
    {"Time": "0:45", "Time": "0:45","Question":" Which statement is correct?", "choices": ["Yes", "No"], "answer": "Yes"},
    {"Time": "0:55", "Time": "0:55","Question":" Is this feature useful?", "choices": ["Very Useful", "Slightly Useful", "Not Useful"], "answer": "Very Useful"},
]

# 将检查点数据转换为DataFrame
data_rows = []
for idx, cp in enumerate(checkpoints):
    row = {
        "Time": cp["Time"],
        "Question": cp["Question"],
        "Option A": cp["choices"][0] if len(cp["choices"]) > 0 else "",
        "Option B": cp["choices"][1] if len(cp["choices"]) > 1 else "",
        "Option C": cp["choices"][2] if len(cp["choices"]) > 2 else "",
        "Correct Answer": cp["answer"]
    }
    data_rows.append(row)
df = pd.DataFrame(data_rows)

# 使用streamlit的data_editor让用户可编辑，并允许动态添加行
edited_df = st.data_editor(df, num_rows="dynamic", width="stretch")

# 清理空行
cleaned_df = edited_df.dropna(how='all')
if st.button("Save Table"):
    st.session_state["quiz_table"] = cleaned_df
    st.success("Table saved!")
    st.write("Final Questions Table:")
    st.dataframe(st.session_state["quiz_table"], width="stretch")
