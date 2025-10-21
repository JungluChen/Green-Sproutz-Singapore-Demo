import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval
import json, re

st.set_page_config(page_title="🎥 Interactive Video Quiz", layout="wide")

# === 1️⃣ Load state ===
video_url = st.session_state.get("video_url", None)
cleaned_df = st.session_state.get("quiz_table", None)

if not video_url or cleaned_df is None:
    st.warning("⚠️ Please go to Settings first to configure the video link and upload the quiz table.")
    st.stop()

# === 2️⃣ Convert to checkpoints ===
def time_to_sec(t: str):
    try:
        m, s = t.split(":")
        return int(m)*60 + int(s)
    except:
        return 0

checkpoints = []
for i, row in cleaned_df.iterrows():
    choices = [v for v in [row.get("Option A"), row.get("Option B"), row.get("Option C")] if isinstance(v, str) and v.strip()]
    checkpoints.append({
        "id": f"q{i}",
        "at_seconds": time_to_sec(row["Time"]),
        "prompt": row["Question"],
        "choices": choices,
        "answer": row["Correct Answer"]
    })

# === 3️⃣ Extract YouTube ID ===
video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:[?&].*)?$", video_url)
video_id = video_id_match.group(1) if video_id_match else video_url

# === 4️⃣ Render HTML player + record panel (frontend, instant) ===
html_code = """
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      margin: 0; background: #0e1117; color: white;
      font-family: -apple-system, BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial;
    }}
    #player-container {{ max-width:720px; margin:16px auto; position:relative; }}
    #player {{ width:100%; height:405px; }}
    #question-box {{
      position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
      background:rgba(20,20,20,0.95); border:2px solid #00ffaa; border-radius:10px;
      padding:20px; width:90%; max-width:420px; text-align:center; z-index:999;
    }}
    #record-panel {{
      max-width:720px; margin:8px auto 24px; padding:12px 16px; background:#12151d; border:1px solid #293241; border-radius:10px;
    }}
    .stats {{ display:flex; gap:12px; margin-bottom:10px; }}
    .stat {{ background:#1b1f2a; padding:10px 12px; border-radius:8px; }}
    .stat strong {{ color:#00ffaa; }}
    .record-item {{ padding:8px 6px; border-bottom:1px dashed #2a2f3a; }}
    .record-item:last-child {{ border-bottom:none; }}
    .ok {{ color:#00ffaa; }}
    .bad {{ color:#ff5555; }}
    button {{ background:#00ffaa; border:none; border-radius:6px; padding:8px 12px; margin-top:6px; cursor:pointer; }}
  </style>
</head>
<body>
  <div id="player-container">
    <div id="player"></div>
    <div id="question-box" style="display:none"></div>
  </div>

  <div id="record-panel">
    <div class="stats" id="stats"></div>
    <div id="records"></div>
  </div>

  <script>
    const checkpoints = __CHECKPOINTS_JSON__;
    let player; let lastShownAt = {{}};
    const COOLDOWN_MS = 2000; // cooldown for unanswered popup

    // Map for quick lookup
    const promptMap = Object.fromEntries(checkpoints.map(cp => [cp.id, cp.prompt]));
    const correctMap = Object.fromEntries(checkpoints.map(cp => [cp.id, cp.answer]));

    function getAnswers() {{
      try {{
        const raw = localStorage.getItem('yt_question_answers');
        return raw ? JSON.parse(raw) : [];
      }} catch(e) {{ return []; }}
    }}
    function setAnswers(arr) {{
      try {{ localStorage.setItem('yt_question_answers', JSON.stringify(arr)); }} catch(e) {{}}
    }}
    function isAlreadyAnswered(qid) {{
      const arr = getAnswers();
      return !!arr.find(a => a.questionId === qid);
    }}

    function renderRecordPanel() {{
      const arr = getAnswers();
      const statsEl = document.getElementById('stats');
      const recEl = document.getElementById('records');
      recEl.innerHTML = '';
      // Stats
      const total = arr.length;
      const correct = arr.filter(a => a.choice === (correctMap[a.questionId] || '')).length;
      const acc = total > 0 ? (correct/total*100).toFixed(1) : '0.0';
      statsEl.innerHTML = `
        <div class=\"stat\"><strong>Answered</strong><br>${{total}}</div>
        <div class=\"stat\"><strong>Correct</strong><br>${{correct}}</div>
        <div class=\"stat\"><strong>Accuracy</strong><br>${{acc}}%</div>
      `;
      // Records
      for (const a of arr) {{
        const ok = a.choice === (correctMap[a.questionId] || '');
        const prompt = promptMap[a.questionId] || a.questionId;
        const ts = a.answered_at || '';
        const line = document.createElement('div');
        line.className = 'record-item';
        line.innerHTML = `Question: <strong>${{prompt}}</strong> — Answer: <strong>${{a.choice}}</strong> ${{ ok ? '<span class=\"ok\">✅</span>' : '<span class=\"bad\">❌</span>' }}`;
        recEl.appendChild(line);
      }}
      // 动态调整容器高度
      const panel = document.getElementById('record-panel');
      if (panel) {
        panel.style.height = 'auto';  // 先重置
        panel.style.height = panel.scrollHeight + 'px';
      }
    }}

    function showQuestion(cp) {{
      const box = document.getElementById('question-box');
      try {{ player.pauseVideo(); }} catch(e) {{}}
      box.style.display = 'block';
      box.innerHTML = '';

      let prevChoice = null;
      try {{
        const arr = getAnswers();
        const prev = arr.find(a => a.questionId === cp.id);
        if (prev) prevChoice = prev.choice;
      }} catch(e) {{}}

      let html = `<h3>${{cp.prompt}}</h3>`;
      if (prevChoice) {{
        html += `<p>Previous choice: <strong>${{prevChoice}}</strong></p>`;
      }}
      for (const c of cp.choices) {{
        const highlight = (prevChoice === c) ? ' style="background:#ffaa00;color:#000"' : '';
        html += `<button${{highlight}} onclick="answer('${{cp.id}}','${{c}}','${{cp.answer}}')">${{c}}</button><br>`;
      }}
      box.innerHTML = html;
    }}

    function closeQuestion() {{
      const box = document.getElementById('question-box');
      box.style.display = 'none';
      box.innerHTML = '';
    }}

    function answer(qid, choice, correct) {{
      const rec = {{
        questionId: qid,
        choice: choice,
        correct: choice === correct,
        answered_at: new Date().toISOString()
      }};
      let arr = getAnswers();
      const idx = arr.findIndex(a => a.questionId === qid);
      if (idx >= 0) {{ arr[idx] = rec; }} else {{ arr.push(rec); }}
      setAnswers(arr);
      closeQuestion();
      try {{ player.playVideo(); }} catch(e) {{}}
      renderRecordPanel();
      // notify parent page (only triggers single Python rerun, no value dependency)
      try {{ (window.top || window.parent || window).postMessage({{ type: 'yt-quiz-answer', payload: rec }}, '*'); }} catch(e) {{}}
    }}

    function onYouTubeIframeAPIReady() {{
      player = new YT.Player('player', {{
        height: '405', width: '720',
        videoId: '__VIDEO_ID__',
        events: {{ 'onReady': onPlayerReady }}
      }});
    }}

    function onPlayerReady() {{
      // restore playback time
      try {{
        const last = parseFloat(localStorage.getItem('yt_current_time') || '0');
        if (!isNaN(last) && last > 0) {{ player.seekTo(last, true); }}
      }} catch(e) {{}}
      try {{ player.playVideo(); }} catch(e) {{}}
      renderRecordPanel();
      setInterval(() => {{
        const t = player.getCurrentTime();
        try {{ localStorage.setItem('yt_current_time', t.toFixed(2)); }} catch(e) {{}}
        for (const cp of checkpoints) {{
          if (Math.abs(t - cp.at_seconds) < 0.3) {{
            const box = document.getElementById('question-box');
            if (box && box.style.display === 'block') {{ continue; }}
            const last = lastShownAt[cp.id] || 0;
            if (Date.now() - last > COOLDOWN_MS) {{
              lastShownAt[cp.id] = Date.now();
              showQuestion(cp);
              break;
            }}
          }}
        }}
      }}, 300);
    }}

    const tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    document.body.appendChild(tag);
  </script>
</body>
</html>
"""
html_code = html_code.replace("__CHECKPOINTS_JSON__", json.dumps(checkpoints)).replace("__VIDEO_ID__", video_id)
# convert paired braces back to single braces to avoid Python f-string conflicts
html_code = html_code.replace("{{", "{").replace("}}", "}")

components.html(html_code, height=900, scrolling=True)

# === 5️⃣ JS→Python bridge for single rerun per answer (no polling) ===
update_event = streamlit_js_eval(
    js_expressions="""
    try {
      if (!window._ytBridgeAttached) {
        window._ytBridgeAttached = true;
        window.addEventListener('message', function(e) {
          if (e && e.data && e.data.type === 'yt-quiz-answer') {
            try { Streamlit.setComponentValue('answers_updated'); } catch(err) {}
          }
        });
      }
    } catch(e) {}
    return 'ready';
    """,
    key="yt_answer_bridge"
)

# read answers from localStorage after rerun (records still rendered by frontend)
signal = streamlit_js_eval(js_expressions="""'noop'""", key="yt_answer_signal")
if update_event == "answers_updated":
    js_answers = streamlit_js_eval(
        js_expressions="""
        try {
            const answers = localStorage.getItem('yt_question_answers');
            return answers ? JSON.parse(answers) : [];
        } catch (e) { return []; }
        """,
        key="yt_read_answers"
    )
    if js_answers and isinstance(js_answers, list):
        st.session_state["answers"] = js_answers
