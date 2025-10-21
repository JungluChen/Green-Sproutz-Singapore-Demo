import streamlit as st
import sqlite3
from pathlib import Path
from datetime import datetime

# ---------- Storage ----------
DB_PATH = Path(__file__).with_name("forum.db")
CATEGORIES = [
    "Accounting",
    "Corporate law",
    "Public finance",
    "Controlling",
    "Acquisition",
    "Education",
    "General",
]


def _conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    with _conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS threads (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT NOT NULL,
              body TEXT NOT NULL,
              category TEXT,
              author TEXT,
              created_at TEXT
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              thread_id INTEGER,
              author TEXT,
              body TEXT,
              created_at TEXT,
              FOREIGN KEY(thread_id) REFERENCES threads(id) ON DELETE CASCADE
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS saves (
              user TEXT,
              thread_id INTEGER,
              PRIMARY KEY(user, thread_id)
            )
            """
        )


init_db()

# ---------- Queries ----------

def create_thread(title: str, body: str, category: str, author: str) -> int:
    ts = datetime.now().isoformat(timespec="seconds")
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO threads (title, body, category, author, created_at) VALUES (?,?,?,?,?)",
            (title, body, category, author, ts),
        )
        return cur.lastrowid


def add_post(thread_id: int, body: str, author: str) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    with _conn() as c:
        c.execute(
            "INSERT INTO posts (thread_id, author, body, created_at) VALUES (?,?,?,?)",
            (thread_id, author, body, ts),
        )


def get_thread(thread_id: int):
    with _conn() as c:
        return c.execute(
            "SELECT id, title, body, category, author, created_at FROM threads WHERE id=?",
            (thread_id,),
        ).fetchone()


def list_posts(thread_id: int):
    with _conn() as c:
        return c.execute(
            "SELECT id, author, body, created_at FROM posts WHERE thread_id=? ORDER BY id ASC",
            (thread_id,),
        ).fetchall()


def post_count(thread_id: int) -> int:
    with _conn() as c:
        return c.execute(
            "SELECT COUNT(*) FROM posts WHERE thread_id=?",
            (thread_id,),
        ).fetchone()[0]


def is_saved(user: str, thread_id: int) -> bool:
    if not user:
        return False
    with _conn() as c:
        return (
            c.execute(
                "SELECT 1 FROM saves WHERE user=? AND thread_id=?",
                (user, thread_id),
            ).fetchone()
            is not None
        )


def toggle_save(user: str, thread_id: int) -> bool:
    with _conn() as c:
        if is_saved(user, thread_id):
            c.execute("DELETE FROM saves WHERE user=? AND thread_id=?", (user, thread_id))
            return False
        else:
            c.execute("INSERT INTO saves (user, thread_id) VALUES (?,?)", (user, thread_id))
            return True


def query_threads(search: str = "", category: str | None = None, author: str | None = None, saved_by: str | None = None, limit: int = 100):
    base = (
        "SELECT id, title, body, category, author, created_at FROM threads"
    )
    params: list = []
    if saved_by:
        base = (
            "SELECT t.id, t.title, t.body, t.category, t.author, t.created_at "
            "FROM threads t JOIN saves s ON t.id=s.thread_id AND s.user=?"
        )
        params.append(saved_by)
    where = []
    if search:
        where.append("(title LIKE ? OR body LIKE ?)")
        params += [f"%{search}%", f"%{search}%"]
    if category and category != "All":
        where.append("category=?")
        params.append(category)
    if author:
        where.append("author=?")
        params.append(author)
    sql = base
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with _conn() as c:
        return c.execute(sql, tuple(params)).fetchall()


# ---------- UI ----------
st.set_page_config(page_title="Community Forum", page_icon="💬", layout="wide")

st.markdown(
    """
    <style>
      .card {background: rgba(255,255,255,0.06); padding: 1rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.12); margin-bottom: 0.8rem;}
      .small {font-size: 0.9rem; opacity: 0.8}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💬 Community Forum")
st.caption("Create threads, discuss, and keep learning together.")
# User identity
with st.expander("User settings", expanded=not bool(st.session_state.get("user"))):
    user = st.text_input("Your display name", value=st.session_state.get("user", ""), placeholder="e.g., Elisabeth May")
    if user:
        st.session_state["user"] = user

# 顶部栏：视图、分类筛选、新建线程
col_top1, col_top2 = st.columns([1, 1])
with col_top1:
    view = st.radio("View", ["Home", "Your threads", "Saved"], index=0, horizontal=True)
with col_top2:
    selected_category = st.selectbox("Category filter", ["All"] + CATEGORIES)

st.markdown("### Create a new thread")
with st.form("new_thread"):
    nt_title = st.text_input("Title")
    nt_cat = st.selectbox("Category", CATEGORIES, index=0)
    nt_body = st.text_area("Body", height=160)
    create_submit = st.form_submit_button("Post")
if create_submit:
    if not st.session_state.get("user"):
        st.warning("Set your display name first.")
    elif nt_title.strip() and nt_body.strip():
        tid = create_thread(nt_title.strip(), nt_body.strip(), nt_cat, st.session_state["user"])
        st.success("Thread created.")
        st.session_state["view_thread_id"] = tid
        st.experimental_rerun()
    else:
        st.warning("Title and body are required.")
search = st.text_input("Type to search", value=st.session_state.get("search", ""), placeholder="Search threads…")
st.session_state["search"] = search

# Thread detail view
if st.session_state.get("view_thread_id"):
    tid = st.session_state.get("view_thread_id")
    t = get_thread(tid)
    if not t:
        st.session_state["view_thread_id"] = None
        st.experimental_rerun()
    if st.button("← Back to all threads"):
        st.session_state["view_thread_id"] = None
        st.experimental_rerun()
    st.markdown(f"<div class='card'><h3>{t[1]}</h3><p class='small'>{t[4]} • {t[5]} • {t[3]}</p><p>{t[2]}</p></div>", unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[0]:
        label = "Unsave" if is_saved(st.session_state.get("user"), tid) else "Save"
        if st.button(label, key=f"save_{tid}"):
            if st.session_state.get("user"):
                flag = toggle_save(st.session_state["user"], tid)
                st.toast("Saved" if flag else "Removed from saved")
                st.experimental_rerun()
            else:
                st.warning("Set your display name to save threads.")
    with cols[1]:
        st.write(f"Responses: {post_count(tid)}")

    st.divider()
    st.subheader("Responses")
    for p in list_posts(tid):
        st.markdown(
            f"<div class='card'><b>{p[1]}</b> · <span class='small'>{p[3]}</span><br>{p[2]}</div>",
            unsafe_allow_html=True,
        )
    with st.form(f"reply_{tid}"):
        reply = st.text_area("Add a response", height=140)
        rsub = st.form_submit_button("Add Response")
    if rsub:
        if not st.session_state.get("user"):
            st.warning("Set your display name first.")
        elif reply.strip():
            add_post(tid, reply.strip(), st.session_state["user"])
            st.success("Response added.")
            st.experimental_rerun()
        else:
            st.warning("Response cannot be empty.")
else:
    # Thread list
    author = st.session_state.get("user") if view == "Your threads" else None
    saved_by = st.session_state.get("user") if view == "Saved" else None
    if view in ("Your threads", "Saved") and not st.session_state.get("user"):
        st.info("Set your display name to use this view.")

    threads = query_threads(search=search.strip(), category=selected_category, author=author, saved_by=saved_by)
    if not threads:
        st.info("No threads yet. Use the form on the left to create one.")
    for t in threads:
        tid, title, body, cat, author, created = t
        preview = body[:260] + ("…" if len(body) > 260 else "")
        st.markdown(
            f"<div class='card'><h4>{title}</h4><p class='small'>{author} • {created} • {cat}</p><p>{preview}</p></div>",
            unsafe_allow_html=True,
        )
        cols = st.columns([0.15, 0.15, 0.7])
        with cols[0]:
            if st.button("Open", key=f"open_{tid}"):
                st.session_state["view_thread_id"] = tid
                st.experimental_rerun()
        with cols[1]:
            label = "Unsave" if is_saved(st.session_state.get("user"), tid) else "Save"
            if st.button(label, key=f"savebtn_{tid}"):
                if st.session_state.get("user"):
                    toggle_save(st.session_state["user"], tid)
                    st.experimental_rerun()
                else:
                    st.warning("Set your display name to save threads.")