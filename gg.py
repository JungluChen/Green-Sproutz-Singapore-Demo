import re
import streamlit as st
import streamlit.components.v1 as components
import time
import json
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="YouTube currentTime", page_icon="▶️", layout="centered", initial_sidebar_state="collapsed", menu_items=None)
st.title("🎓 E-Learning Interactive Learning Platform")
st.write("created by Innovaction XLab")
# 定義檢查點
checkpoints = [ 
    {"at": "0:10", "id": "q1", "prompt": "Video 0:10: What topic is being discussed?", "choices": ["A", "B", "C"], "answer": "A"}, 
    {"at": "0:25", "id": "q2", "prompt": "Video 0:25: What is the keyword?", "choices": ["Alpha", "Beta", "Gamma"], "answer": "Beta"}, 
    {"at": "0:45", "id": "q3", "prompt": "Video 0:45: Which statement is correct?", "choices": ["Yes", "No"], "answer": "Yes"}, 
]

# 將字串時間轉換為秒數
def time_to_seconds(time_str):
    if isinstance(time_str, (int, float)):
        return float(time_str)
    
    parts = time_str.split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + int(seconds)
    elif len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    return 0

# 處理檢查點，確保所有時間都是秒數格式
for checkpoint in checkpoints:
    if isinstance(checkpoint["at"], str):
        checkpoint["at_seconds"] = time_to_seconds(checkpoint["at"])
    else:
        checkpoint["at_seconds"] = float(checkpoint["at"])
        
# 按時間排序檢查點
checkpoints.sort(key=lambda x: x["at_seconds"])

video_url = st.text_input("Paste YouTube link:", "https://www.youtube.com/watch?v=4dCrkp8qgLU")

def extract_video_id(url: str) -> str:
    m = re.search(r"(?:v=|/)([0-9A-Za-z_-]{11})(?:[?&].*)?$", url)
    return m.group(1) if m else url

video_id = extract_video_id(video_url)

# 包含捕捉按鈕的完整播放器
html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ margin: 0; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
        #player-container {{ max-width: 720px; margin: 0 auto; }}
        #time-display {{
            margin-top: 12px;
            padding: 12px 16px;
            background: #f0f2f6;
            border-radius: 8px;
            font-size: 16px;
        }}
        .time-value {{ font-weight: bold; color: #ff0000; font-size: 18px; }}
        #capture-btn {{
            margin-top: 12px;
            padding: 12px 24px;
            background: #0066cc;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: background 0.3s;
        }}
        #capture-btn:hover {{
            background: #0052a3;
        }}
        #captured {{
            margin-top: 12px;
            padding: 16px;
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            color: #155724;
            display: none;
        }}
        .captured-time {{
            font-size: 24px;
            font-weight: bold;
            color: #155724;
        }}
    </style>
</head>
<body>
    <div id="player-container">
        <div id="player"></div>
        <div id="time-display">
            <span>⏱️ Current time:</span>
            <span class="time-value" id="current">00:00</span>
            <span style="opacity: 0.6;"> / </span>
            <span id="duration">00:00</span>
        </div>
        

        
        <div id="captured">
            <strong>✅ Captured time:</strong><br>
            <span class="captured-time" id="captured-time">0:00</span>
            <span style="opacity: 0.7;">（<span id="captured-seconds">0.00</span> seconds）</span>
        </div>
    </div>

    <script>
        var tag = document.createElement('script');
        tag.src = "https://www.youtube.com/iframe_api";
        var firstScriptTag = document.getElementsByTagName('script')[0];
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

        let player = null;
        let currentTime = 0;

        function formatTime(seconds) {{
            if (!seconds || seconds < 0) return "00:00";
            const sec = Math.floor(seconds);
            const m = Math.floor(sec / 60);
            const s = sec % 60;
            return m + ":" + String(s).padStart(2, "0");
        }}

        function onYouTubeIframeAPIReady() {{
            player = new YT.Player('player', {{
                height: '405',
                width: '720',
                videoId: '{video_id}',
                playerVars: {{
                    'rel': 0,
                    'modestbranding': 1
                }},
                events: {{
                    'onReady': onPlayerReady
                }}
            }});
        }}

        // 檢查點數據
        const checkpoints = {json.dumps(checkpoints)};
        let activeCheckpoint = null;
        let lastTriggerTime = 0;
        
        function checkTimepoints(currentTime) {{
            // 檢查是否達到任何檢查點
            for (const checkpoint of checkpoints) {{
                const atSeconds = checkpoint.at_seconds;
                
                // 如果當前時間在檢查點時間的前後 0.5 秒內
                // 且與上次觸發時間相差超過 2 秒（避免連續多次觸發）
                const now = Date.now();
                if (Math.abs(currentTime - atSeconds) < 0.5 && (now - lastTriggerTime > 2000)) {{
                    // 設置當前檢查點和觸發時間
                    activeCheckpoint = checkpoint;
                    lastTriggerTime = now;
                    
                    // 發送檢查點事件到父窗口
                    window.parent.postMessage({{
                        type: 'CHECKPOINT_REACHED',
                        checkpoint: checkpoint,
                        currentTime: currentTime
                    }}, '*');
                    
                    // 儲存到 localStorage 以便 Streamlit 讀取
                    localStorage.setItem('yt_active_checkpoint', JSON.stringify(checkpoint));
                    
                    // 顯示檢查點問題
                    showCheckpointQuestion(checkpoint);
                    
                    // 如果正在播放，暫停影片
                    if (player.getPlayerState() === 1) {{
                        player.pauseVideo();
                    }}
                    
                    break;
                }}
            }}
        }}
        
        function showCheckpointQuestion(checkpoint) {{
            // 移除舊的問題容器（如果存在）
            let oldContainer = document.getElementById('question-container');
            if (oldContainer) {{
                oldContainer.remove();
            }}
            
            // 創建新的問題容器
            let questionContainer = document.createElement('div');
            questionContainer.id = 'question-container';
            questionContainer.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 20px;
                border-radius: 10px;
                z-index: 1000;
                width: 80%;
                max-width: 500px;
                text-align: center;
                display: block;
            `;
            document.getElementById('player-container').appendChild(questionContainer);
            
            // 設置問題內容
            questionContainer.innerHTML = `
                <h3 style="margin-top: 0; color: #fff;">${{checkpoint.prompt}}</h3>
                <div id="choices" style="margin: 20px 0;">
                    ${{checkpoint.choices.map((choice, index) => `
                        <button 
                            onclick="answerQuestion('${{choice}}', '${{checkpoint.id}}')"
                            style="
                                margin: 5px;
                                padding: 10px 15px;
                                background: #0066cc;
                                color: white;
                                border: none;
                                border-radius: 5px;
                                cursor: pointer;
                                font-size: 16px;
                            "
                        >${{choice}}</button>
                    `).join('')}}
                </div>
                <button 
                    onclick="closeQuestion()"
                    style="
                        padding: 8px 15px;
                        background: #666;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        margin-top: 10px;
                    "
                >關閉</button>
            `;
            
            // 確保問題容器可見
            setTimeout(() => {{
                const container = document.getElementById('question-container');
                if (container) {{
                    container.style.display = 'block';
                }}
            }}, 100);
        }}
        
        // 回答問題
        window.answerQuestion = function(choice, questionId) {{
            const answer = {{
                questionId: questionId,
                choice: choice,
                timestamp: Date.now()
            }};
            
            // 儲存答案
            let answers = JSON.parse(localStorage.getItem('yt_question_answers') || '[]');
            answers.push(answer);
            localStorage.setItem('yt_question_answers', JSON.stringify(answers));
            
            // 發送答案到父窗口
            window.parent.postMessage({{
                type: 'QUESTION_ANSWERED',
                answer: answer
            }}, '*');
            
            // 關閉問題
            closeQuestion();
            
            // 繼續播放
            player.playVideo();
        }};
        
        // 關閉問題
        window.closeQuestion = function() {{
            const questionContainer = document.getElementById('question-container');
            if (questionContainer) {{
                // 完全移除問題容器，而不只是隱藏
                questionContainer.remove();
            }}
            
            // 繼續播放
            player.playVideo();
        }};
        
        function onPlayerReady(event) {{
            setTimeout(() => {{
                const duration = player.getDuration();
                if (duration > 0) {{
                    document.getElementById('duration').textContent = formatTime(duration);
                }}
            }}, 500);
            
            // 持續更新時間顯示並檢查檢查點
            setInterval(() => {{
                if (!player || typeof player.getCurrentTime !== 'function') return;
                try {{
                    const time = player.getCurrentTime();
                    if (typeof time === 'number' && !isNaN(time) && time >= 0) {{
                        currentTime = time;
                        document.getElementById('current').textContent = formatTime(time);
                        
                        // 檢查是否達到任何檢查點
                        checkTimepoints(time);
                    }}
                }} catch (e) {{}}
            }}, 100);
        }}

        function captureTime() {{
            if (currentTime > 0) {{
                // 顯示已捕捉訊息
                const capturedDiv = document.getElementById('captured');
                capturedDiv.style.display = 'block';
                document.getElementById('captured-time').textContent = formatTime(currentTime);
                document.getElementById('captured-seconds').textContent = currentTime.toFixed(2);
                
                // 發送到 parent window
                window.parent.postMessage({{
                    type: 'CAPTURE_TIME',
                    time: currentTime,
                    videoId: '{video_id}'
                }}, '*');
                
                // 按鈕反饋
                const btn = document.getElementById('capture-btn');
                const originalText = btn.textContent;
                btn.textContent = '✅ 已捕捉！';
                btn.style.background = '#28a745';
                setTimeout(() => {{
                    btn.textContent = originalText;
                    btn.style.background = '#0066cc';
                }}, 1000);
            }}
        }}
    </script>
</body>
</html>
"""

# 渲染播放器
components.html(html, height=620)

# 監聽 postMessage
listener = """
<script>
window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'CAPTURE_TIME') {
        // 使用表單提交的方式傳遞數據
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = window.location.href;
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'captured_time';
        input.value = event.data.time;
        
        form.appendChild(input);
        document.body.appendChild(form);
        
        // 儲存到 localStorage 讓 Streamlit 可以讀取
        localStorage.setItem('yt_captured_time', event.data.time);
        
        // 觸發 Streamlit 刷新
        window.location.hash = 'time=' + event.data.time;
    }
    else if (event.data && event.data.type === 'CHECKPOINT_REACHED') {
        // 儲存當前檢查點到 localStorage
        localStorage.setItem('yt_active_checkpoint', JSON.stringify(event.data.checkpoint));
        
        // 觸發 Streamlit 刷新
        window.location.hash = 'checkpoint=' + event.data.checkpoint.id + '&time=' + Date.now();
    }
    else if (event.data && event.data.type === 'QUESTION_ANSWERED') {
        // 儲存答案
        let answers = JSON.parse(localStorage.getItem('yt_question_answers') || '[]');
        answers.push(event.data.answer);
        localStorage.setItem('yt_question_answers', JSON.stringify(answers));
        
        // 觸發 Streamlit 刷新
        window.location.hash = 'answer=' + event.data.answer.questionId + '&time=' + Date.now();
    }
});
</script>
"""

components.html(listener, height=0)

# st.markdown("---")

# 方法 1: 從 URL hash 讀取
import urllib.parse
from streamlit.runtime.scriptrunner import get_script_run_ctx

# 檢查 URL 參數
query_params = st.query_params
if 'time' in query_params:
    try:
        time = float(query_params['time'])
        st.session_state.captured_time = time
    except:
        pass

# 檢查點和問題回答處理
# st.markdown("### 📊 Python 端數據")

# 顯示捕捉的時間
if 'captured_time' in st.session_state:
    time = st.session_state.captured_time
    
    # 這就是你要的 print(time)！
    print(f"捕捉的時間: {time:.2f} 秒")
    
    minutes = int(time // 60)
    seconds = int(time % 60)
    
    st.success("✅ **已成功捕捉時間到 Python！**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("時間", f"{minutes}:{seconds:02d}")
    with col2:
        st.metric("總秒數", f"{time:.2f}s")
    with col3:
        st.metric("分鐘", f"{minutes}m")
    
    # 顯示如何在 Python 中使用
    st.code(f"""# Python 變數
time = {time}  # {time:.2f} 秒
minutes = {minutes}
seconds = {seconds}

# 使用範例
print(f"播放時間: {{time:.2f}} 秒")
print(f"格式化: {{minutes}}:{{seconds:02d}}")
""", language="python")
    
    # 清除按鈕
    if st.button("🗑️ 清除記錄"):
        del st.session_state.captured_time
        st.rerun()
        
# else:
#     st.info("👆 點擊影片上方的「📍 捕捉當前時間到 Python」按鈕")
#     st.write("播放影片後，想記錄某個時間點時點擊按鈕，時間就會傳到 Python 中")

# # 檢查點問題和回答
# st.markdown("### 📝 檢查點問題")

# 從 localStorage 讀取問題回答
js_answers = streamlit_js_eval(
    js_expressions="""
    try {
        const answers = localStorage.getItem('yt_question_answers');
        return answers ? JSON.parse(answers) : [];
    } catch (e) {
        return [];
    }
    """,
    key="read_answers"
)

# 初始化 session_state 中的答案
if 'question_answers' not in st.session_state:
    st.session_state.question_answers = []

# 更新 session_state 中的答案
if js_answers and isinstance(js_answers, list):
    # 合併新答案，避免重複
    existing_ids = {a.get('questionId') for a in st.session_state.question_answers}
    for answer in js_answers:
        if answer.get('questionId') not in existing_ids:
            st.session_state.question_answers.append(answer)
            existing_ids.add(answer.get('questionId'))

# 顯示檢查點和回答
if st.session_state.question_answers:
    # 按問題 ID 分組
    answers_by_question = {}
    for answer in st.session_state.question_answers:
        q_id = answer.get('questionId')
        if q_id not in answers_by_question:
            answers_by_question[q_id] = []
        answers_by_question[q_id].append(answer)
    
    # 找出每個問題的正確答案
    correct_answers = {cp['id']: cp['answer'] for cp in checkpoints}
    
    # 顯示每個問題的回答
    for q_id, answers in answers_by_question.items():
        # 找到對應的檢查點
        checkpoint = next((cp for cp in checkpoints if cp['id'] == q_id), None)
        if not checkpoint:
            continue
            
        # 顯示問題
        st.subheader(f"問題 {q_id}: {checkpoint['prompt']}")
        
        # 顯示選項
        st.write("選項:")
        for choice in checkpoint['choices']:
            is_correct = choice == checkpoint['answer']
            if is_correct:
                st.success(f"✓ {choice} (正確答案)")
            else:
                st.write(f"- {choice}")
        
        # 顯示用戶回答
        st.write("你的回答:")
        for i, answer in enumerate(answers):
            choice = answer.get('choice')
            is_correct = choice == correct_answers.get(q_id)
            if is_correct:
                st.success(f"✓ 回答 {i+1}: {choice} (正確)")
            else:
                st.error(f"✗ 回答 {i+1}: {choice} (錯誤，正確答案是 {correct_answers.get(q_id)})")
        
        # st.markdown("---")
    
    # 顯示統計
    correct_count = sum(1 for answer in st.session_state.question_answers 
                      if answer.get('choice') == correct_answers.get(answer.get('questionId')))
    total_count = len(st.session_state.question_answers)
    
    st.subheader("📊 答題統計")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("總題數", len(answers_by_question))
    with col2:
        st.metric("回答次數", total_count)
    with col3:
        if total_count > 0:
            accuracy = correct_count / total_count * 100
            st.metric("正確率", f"{accuracy:.1f}%")
        else:
            st.metric("正確率", "N/A")
    
    # 清除按鈕
    if st.button("🗑️ 清除所有回答", key="clear_answers"):
        st.session_state.question_answers = []
        streamlit_js_eval(js_expressions="localStorage.removeItem('yt_question_answers'); return true;")
        st.rerun()
# else:
#     # st.info("👀 觀看影片時，會在特定時間點出現問題，回答後會顯示在這裡")
    
#     # 顯示檢查點列表
#     st.subheader("⏱️ 檢查點列表")
#     for i, cp in enumerate(checkpoints):
#         at_str = cp['at'] if isinstance(cp['at'], str) else f"{int(cp['at'] // 60)}:{int(cp['at'] % 60):02d}"
#         st.write(f"{i+1}. 時間點 **{at_str}**: {cp['prompt']}")

# 顯示所有記錄
# st.markdown("### 📝 時間記錄")

# if st.button("➕ 添加當前時間到列表", type="primary"):
#     if 'captured_time' in st.session_state:
#         if 'time_list' not in st.session_state:
#             st.session_state.time_list = []
        
#         time = st.session_state.captured_time
#         st.session_state.time_list.append(time)
#         st.success(f"已添加 {time:.2f} 秒")
#         st.rerun()

if 'time_list' in st.session_state and st.session_state.time_list:
    st.write("**已記錄的時間點：**")
    for i, t in enumerate(st.session_state.time_list, 1):
        m = int(t // 60)
        s = int(t % 60)
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"{i}. **{m}:{s:02d}** ({t:.2f} 秒)")
        with col2:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.time_list.pop(i-1)
                st.rerun()
    
    # Python 使用範例
    st.code(f"""# 所有記錄的時間
time_list = {st.session_state.time_list}

# 遍歷
for time in time_list:
    print(f"時間點: {{time:.2f}} 秒")
""", language="python")
