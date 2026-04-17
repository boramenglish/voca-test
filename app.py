import streamlit as st
import pandas as pd
import random

# [설정] 기존 로직 유지
SECRET_PASSWORD = "0000"
SHEET_URLS = {
    "1학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=0&single=true&output=csv",
    "2학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=840773385&single=true&output=csv",
    "3학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=893402083&single=true&output=csv"
}

st.set_page_config(page_title="BORAM VOCA ARCHIVE", page_icon="📝", layout="centered")

# --- 🖼️ 현대미술관(MoMA) 스타일 CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@200;400;700&family=Inter:wght@300;400;600&display=swap');

    /* 전체 배경: 완벽한 화이트 & 깔끔한 폰트 */
    .stApp {
        background-color: #ffffff;
        font-family: 'Inter', sans-serif;
    }

    /* 타이틀: 고급스러운 세리프체 */
    .studio-title {
        font-family: 'Noto Serif KR', serif;
        color: #1a1a1a;
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.05em;
        margin-bottom: 40px;
        border-bottom: 2px solid #1a1a1a;
        display: inline-block;
        padding-bottom: 10px;
    }

    /* 단어 카드: 여백과 선의 조화 */
    .word-canvas {
        font-family: 'Noto Serif KR', serif;
        font-size: clamp(2.5rem, 8vw, 4rem);
        text-align: center;
        padding: 80px 20px;
        background: #f9f9f9;
        border: 1px solid #eeeeee;
        color: #1a1a1a;
        margin-bottom: 50px;
        font-weight: 400;
    }

    /* 버튼: 미니멀한 블랙 & 화이트 디자인 */
    div.stButton > button {
        border-radius: 0px; /* 각진 디자인이 더 세련됨 */
        border: 1px solid #1a1a1a;
        background-color: #ffffff;
        color: #1a1a1a;
        font-size: 1rem !important;
        min-height: 55px;
        transition: all 0.3s ease;
    }

    div.stButton > button:hover {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }

    /* 진행 바: 아주 얇고 심플하게 */
    .stProgress > div > div > div > div {
        background-color: #1a1a1a;
    }

    /* 기타 텍스트 */
    .sub-text {
        text-align: center;
        color: #888888;
        font-size: 0.9rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_words(url):
    try:
        df = pd.read_csv(url)
        df = df.dropna(how='all')
        return dict(zip(df.iloc[:, 0].astype(str).str.strip(), df.iloc[:, 1].astype(str).str.strip()))
    except: return {}

# 세션 상태 초기화
for key in ['authenticated', 'page', 'score', 'current_q', 'incorrect_list', 'review_mode']:
    if key not in st.session_state:
        st.session_state[key] = False if 'mode' in key or 'auth' in key else (0 if 'score' in key or 'q' in key else ('main' if key == 'page' else []))

def start_session(word_list, is_review=False):
    st.session_state.test_words = word_list
    st.session_state.current_q = 0
    st.session_state.review_mode = is_review
    st.session_state.feedback = False
    if not is_review:
        st.session_state.score = 0
        st.session_state.incorrect_list = []
    st.session_state.page = 'test'

# --- 1. Security (Minimal) ---
if not st.session_state.authenticated:
    st.markdown("<div style='text-align:center; margin-top:150px;'>", unsafe_allow_html=True)
    st.markdown("<div class='studio-title'>ARCHIVE ACCESS</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        pwd = st.text_input("PASSWORD", type="password", help="현장 암호를 입력하세요.")
        if st.button("CONFIRM") or (pwd == SECRET_PASSWORD):
            if pwd == SECRET_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
    st.stop()

# --- 2. Main Menu ---
if st.session_state.page == 'main':
    st.markdown("<div style='text-align:center; margin-top:50px;'>", unsafe_allow_html=True)
    st.markdown("<p class='sub-text'>Vocabulary Training System</p>", unsafe_allow_html=True)
    st.markdown("<div class='studio-title'>BORAM ENGLISH</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        grade = st.selectbox("SELECT GRADE", ["1학년", "2학년", "3학년"])
        st.session_state.selected_grade = grade
        words = load_words(SHEET_URLS[grade])
        
        st.markdown(f"<p style='text-align:center; color:#1a1a1a; margin-top:20px;'>{len(words)} Words Registered</p>", unsafe_allow_html=True)
        
        if st.button("START TRAINING", use_container_width=True):
            if len(words) >= 4:
                word_keys = random.sample(list(words.keys()), len(words))
                start_session(word_keys)
                st.rerun()

# --- 3. Test Screen ---
elif st.session_state.page == 'test':
    words = load_words(SHEET_URLS[st.session_state.selected_grade])
    word = st.session_state.test_words[st.session_state.current_q]
    
    st.markdown(f"<p class='sub-text'>Sequence: {st.session_state.current_q+1} / {len(st.session_state.test_words)}</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='word-canvas'>{word}</div>", unsafe_allow_html=True)

    if st.session_state.get('feedback', False):
        if st.session_state.is_correct: 
            st.markdown("<p style='text-align:center; color:#1a1a1a; font-weight:600;'>CORRECT</p>", unsafe_allow_html=True)
        else: 
            st.markdown(f"<p style='text-align:center; color:#e63946;'>ERROR: {st.session_state.ans}</p>", unsafe_allow_html=True)
        
        if st.button("CONTINUE", use_container_width=True):
            st.session_state.feedback = False
            st.session_state.current_q += 1
            if st.session_state.current_q >= len(st.session_state.test_words):
                st.session_state.page = 'result'
            st.rerun()
    else:
        ans = words[word]
        others = [v for k, v in words.items() if v != ans]
        opts = random.sample(others, min(len(others), 5)) + [ans]
        random.shuffle(opts)
        
        cols = st.columns(2)
        for i, opt in enumerate(opts):
            if cols[i%2].button(opt, key=f"btn_{i}", use_container_width=True):
                st.session_state.feedback = True
                st.session_state.ans = ans
                if opt == ans:
                    if not st.session_state.review_mode: st.session_state.score += 1
                    st.session_state.is_correct = True
                else:
                    st.session_state.is_correct = False
                    if word not in st.session_state.incorrect_list:
                        st.session_state.incorrect_list.append(word)
                st.rerun()

# --- 4. Result Screen ---
elif st.session_state.page == 'result':
    st.markdown("<div style='text-align:center; margin-top:50px;'>", unsafe_allow_html=True)
    st.markdown("<div class='studio-title'>COMPLETED</div>", unsafe_allow_html=True)
    
    score_pct = int((st.session_state.score / len(st.session_state.test_words)) * 100) if not st.session_state.review_mode else 100
    
    st.markdown(f"<p style='font-size:3rem; font-weight:200;'>{score_pct}%</p>", unsafe_allow_html=True)
    st.write("---")

    if st.session_state.incorrect_list:
        st.markdown("<p class='sub-text'>Incorrect Data</p>", unsafe_allow_html=True)
        words_dict = load_words(SHEET_URLS[st.session_state.selected_grade])
        error_data = [{"Word": w, "Meaning": words_dict.get(w, "")} for w in st.session_state.incorrect_list]
        st.table(error_data)
        
        if st.button("REVIEW INCORRECT WORDS", use_container_width=True):
            review_words = list(st.session_state.incorrect_list)
            st.session_state.incorrect_list = []
            start_session(review_words, is_review=True)
            st.rerun()

    if st.button("BACK TO ARCHIVE", use_container_width=True):
        st.session_state.page = 'main'
        st.session_state.review_mode = False
        st.rerun()
