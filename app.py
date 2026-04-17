import streamlit as st
import pandas as pd
import random
import time

# [설정 1] 현장 암호
SECRET_PASSWORD = "0000"

# [설정 2] 학년별 구글 시트 CSV 링크
SHEET_URLS = {
    "1학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=0&single=true&output=csv",
    "2학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=840773385&single=true&output=csv",
    "3학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=893402083&single=true&output=csv"
}

st.set_page_config(page_title="🌳 보람T 어휘 훈련소", page_icon="🌳", layout="centered")

# --- 🍏 Apple Style CSS 디자인 ---
st.markdown("""
<style>
/* 폰트 및 기본 배경 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #FBFBFD; /* 애플 공식 배경색 느낌 */
}

/* 메인 카드 디자인 */
.main-card {
    background-color: white;
    padding: 40px;
    border-radius: 24px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.04);
    margin-bottom: 30px;
    text-align: center;
}

/* 문제 단어 스타일 */
.big-word {
    font-size: clamp(2.5rem, 8vw, 4.5rem) !important;
    font-weight: 800;
    color: #1D1D1F;
    letter-spacing: -0.02em;
    margin: 40px 0;
    word-break: keep-all;
}

/* 버튼 디자인 (Apple 스타일) */
div.stButton > button {
    background-color: #F5f5f7;
    color: #1D1D1F;
    border: none;
    border-radius: 14px;
    padding: 16px 20px !important;
    font-size: 1.1rem !important;
    font-weight: 600;
    transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
    height: auto !important;
    min-height: 70px;
}

div.stButton > button:hover {
    background-color: #E8E8ED;
    transform: scale(1.02);
    color: #0071E3; /* 애플 블루 */
}

/* 강조 버튼 (다음 문제 등) */
div.stButton > button[kind="primary"] {
    background-color: #0071E3;
    color: white;
}

/* 피드백 배너 */
.review-banner {
    padding: 15px;
    background-color: #FFF2F2;
    color: #FF3B30; /* 애플 시스템 레드 */
    border-radius: 12px;
    font-weight: 600;
    text-align: center;
    margin-bottom: 20px;
}

/* 입력창 둥글게 */
input {
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_words(url):
    try:
        df = pd.read_csv(url)
        df = df.dropna(how='all')
        if len(df) < 8: return {}
        return dict(zip(df.iloc[:, 0].astype(str).str.strip(), df.iloc[:, 1].astype(str).str.strip()))
    except: return {}

# 세션 관리
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'page' not in st.session_state:
    st.session_state.page = 'main'
    st.session_state.score = 0
    st.session_state.current_q = 0
    st.session_state.incorrect_list = []
    st.session_state.review_mode = False

def start_session(word_list, is_review=False):
    st.session_state.test_words = word_list
    st.session_state.current_q = 0
    st.session_state.review_mode = is_review
    if not is_review:
        st.session_state.score = 0
        st.session_state.incorrect_list = []
    st.session_state.page = 'test'

# --- 1. 보안 게이트 ---
if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-weight:800; color:#1D1D1F;'>남보람T의 출구시험</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("Passcode", type="password", placeholder="현장 암호를 입력하세요")
        if st.button("Continue", use_container_width=True) or (pwd == SECRET_PASSWORD):
            if pwd == SECRET_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            elif pwd: st.error("암호가 올바르지 않습니다.")
    st.stop()

# --- 2. 메인 메뉴 ---
if st.session_state.page == 'main':
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center; color:#86868B; font-weight:400;'>Nam Boram English</h4>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; font-weight:800; color:#1D1D1F; font-size:3rem;'>어휘 무한 훈련소</h1>", unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        grade = st.selectbox("Select Grade", ["1학년", "2학년", "3학년"])
        st.session_state.selected_grade = grade
        words = load_words(SHEET_URLS[grade])
        st.markdown(f"<p style='text-align:center; color:#86868B;'>{len(words)}개의 어휘가 준비되었습니다.</p>", unsafe_allow_html=True)
        
        if st.button("Start Training", use_container_width=True):
            if len(words) >= 8:
                word_keys = random.sample(list(words.keys()), len(words))
                start_session(word_keys)
                st.rerun()
            else: st.error("어휘를 8개 이상 등록해 주세요.")

# --- 3. 테스트 화면 ---
elif st.session_state.page == 'test':
    words = load_words(SHEET_URLS[st.session_state.selected_grade])
    word = st.session_state.test_words[st.session_state.current_q]
    
    if st.session_state.review_mode:
        st.markdown("<div class='review-banner'>Review Mode: 틀린 어휘 정복 중</div>", unsafe_allow_html=True)
    
    st.markdown(f"<p style='text-align:center; color:#86868B;'>{st.session_state.current_q+1} of {len(st.session_state.test_words)}</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='big-word'>{word}</div>", unsafe_allow_html=True)

    if st.session_state.get('feedback', False):
        if st.session_state.is_correct: st.success("Correct")
        else: st.error(f"Incorrect: {st.session_state.ans}")
        
        if st.button("Next ➡️", use_container_width=True):
            st.session_state.feedback = False
            st.session_state.current_q += 1
            if st.session_state.current_q >= len(st.session_state.test_words):
                st.session_state.page = 'result'
            st.rerun()
    else:
        ans = words[word]
        others = [v for k, v in words.items() if v != ans]
        opts = random.sample(others, min(len(others), 7)) + [ans]
        random.shuffle(opts)
        
        cols = st.columns(2)
        for i, opt in enumerate(opts):
            if cols[i%2].button(opt, key=f"btn_{i}"):
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

# --- 4. 결과 화면 ---
elif st.session_state.page == 'result':
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-weight:800;'>Well Done!</h2>", unsafe_allow_html=True)
    
    if not st.session_state.review_mode:
        st.markdown(f"<h1 style='text-align:center; color:#0071E3;'>{st.session_state.score} / {len(st.session_state.test_words)}</h1>", unsafe_allow_html=True)
    
    st.write("<br>", unsafe_allow_html=True)
    
    if st.session_state.incorrect_list:
        st.markdown(f"<p style='text-align:center;'>{len(st.session_state.incorrect_list)}개의 어휘를 놓쳤습니다.</p>", unsafe_allow_html=True)
        if st.button("Review Mistakes", use_container_width=True):
            review_words = random.sample(st.session_state.incorrect_list, len(st.session_state.incorrect_list))
            st.session_state.incorrect_list = []
            start_session(review_words, is_review=True)
            st.rerun()
    else:
        st.balloons()
        st.success("Perfect! 모든 어휘를 마스터했습니다.")

    if st.button("Back to Home", use_container_width=True):
        st.session_state.page = 'main'
        st.session_state.review_mode = False
        st.rerun()
