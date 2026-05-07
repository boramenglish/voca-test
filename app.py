import streamlit as st
import pandas as pd
import random

# [설정] 기존 데이터 및 암호 유지
SECRET_PASSWORD = "0501"
SHEET_URLS = {
    "1학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=0&single=true&output=csv",
    "2학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=840773385&single=true&output=csv",
    "3학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=893402083&single=true&output=csv"
}

st.set_page_config(page_title="🌳 보람T 어휘 훈련소", page_icon="🌳", layout="centered")

# --- 🖼️ 모바일 가독성 강화 CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700&family=Inter:wght@400;600&display=swap');

    /* 배경색과 기본 글자색 강제 지정 */
    .stApp { 
        background-color: #ffffff !important; 
    }

    /* 모든 텍스트 기본 색상을 진한 검정으로 고정 */
    h1, h2, h3, p, span, div, label {
        color: #1a1a1a !important;
        font-family: 'Inter', sans-serif;
    }

    /* 타이틀 디자인 */
    .studio-title {
        font-family: 'Noto Serif KR', serif;
        color: #1a1a1a !important;
        text-align: center;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 20px;
    }

    /* 단어 카드 디자인 - 모바일에서 대비 강조 */
    .word-canvas {
        font-family: 'Noto Serif KR', serif;
        font-size: clamp(2rem, 10vw, 3.5rem);
        text-align: center;
        padding: 60px 10px;
        background: #f1f1f1 !important; /* 조금 더 진한 회색 배경 */
        border: 2px solid #1a1a1a;
        color: #1a1a1a !important;
        margin-bottom: 30px;
        font-weight: 700;
    }

    /* 버튼 가독성 - 검은 테두리 강조 */
    div.stButton > button {
        border-radius: 4px;
        border: 2px solid #1a1a1a !important;
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        font-weight: 600 !important;
        min-height: 50px;
    }

    /* 입력창 글자색 고정 */
    input {
        color: #1a1a1a !important;
        background-color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_words(url):
    try:
        df = pd.read_csv(url, on_bad_lines='skip')
        df = df.dropna(subset=[df.columns[0], df.columns[1]])
        return dict(zip(
            df.iloc[:, 0].astype(str).str.strip(), 
            df.iloc[:, 1].astype(str).str.strip()
        ))
    except: return {}

# 세션 초기화
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'page' not in st.session_state:
    st.session_state.update({'page': 'main', 'score': 0, 'current_q': 0, 'incorrect_list': [], 'review_mode': False})

def start_session(word_list, is_review=False):
    st.session_state.test_words = word_list
    st.session_state.current_q = 0
    st.session_state.review_mode = is_review
    st.session_state.feedback = False
    if not is_review:
        st.session_state.score = 0
        st.session_state.incorrect_list = []
    st.session_state.page = 'test'

# --- 1. 보안 게이트 ---
if not st.session_state.authenticated:
    st.markdown("<div style='margin-top:50px;'></div>", unsafe_allow_html=True)
    # 인라인 스타일로 색상 한 번 더 강제 적용
    st.markdown("<h2 style='text-align:center; color:#1a1a1a !important;'>🔒 보람T 어휘 훈련소 입장</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col2:
        pwd = st.text_input("현장 암호를 입력하세요", type="password", help="암호를 입력 후 입장하기를 누르세요.")
        if st.button("🚪 입장하기", use_container_width=True) or (pwd == SECRET_PASSWORD):
            if pwd == SECRET_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            elif pwd: st.error("❌ 암호가 틀렸습니다!")
    st.stop()

# --- 2. 메인 메뉴 ---
if st.session_state.page == 'main':
    st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='studio-title'>어휘 무한 훈련소</div>", unsafe_allow_html=True)
    st.write("---")
    
    grade = st.selectbox("📚 학년을 선택하세요", list(SHEET_URLS.keys()))
    st.session_state.selected_grade = grade
    words = load_words(SHEET_URLS[grade])
    st.markdown(f"<p style='text-align:center; font-weight:bold;'>🍃 등록된 어휘: {len(words)}개</p>", unsafe_allow_html=True)
    
    if st.button("🚀 훈련 시작하기", use_container_width=True):
        if len(words) >= 4:
            word_keys = random.sample(list(words.keys()), len(words))
            start_session(word_keys)
            st.rerun()

# --- 3. 테스트 화면 ---
elif st.session_state.page == 'test':
    words = load_words(SHEET_URLS[st.session_state.selected_grade])
    word = st.session_state.test_words[st.session_state.current_q]
    
    st.markdown(f"<p style='text-align:center; font-weight:bold;'>{st.session_state.current_q+1} / {len(st.session_state.test_words)}</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='word-canvas'>{word}</div>", unsafe_allow_html=True)

    if st.session_state.get('feedback', False):
        if st.session_state.is_correct: st.markdown("<h3 style='text-align:center; color:#1a1a1a !important;'>🎯 정답입니다!</h3>", unsafe_allow_html=True)
        else: st.markdown(f"<h3 style='text-align:center; color:#e63946 !important;'>⚠️ 오답! 정답: {st.session_state.ans}</h3>", unsafe_allow_html=True)
        
        if st.button("다음 문제 ➡️", use_container_width=True):
            st.session_state.feedback = False
            st.session_state.current_q += 1
            if st.session_state.current_q >= len(st.session_state.test_words): st.session_state.page = 'result'
            st.rerun()
    else:
        ans = words[word]
        others = [v for k, v in words.items() if v.strip() != ans.strip()]
        opts = random.sample(others, min(len(others), 3)) + [ans]
        random.shuffle(opts)
        
        for i, opt in enumerate(opts):
            if st.button(opt, key=f"btn_{i}", use_container_width=True):
                st.session_state.feedback = True
                st.session_state.ans = ans
                if opt.strip() == ans.strip():
                    if not st.session_state.review_mode: st.session_state.score += 1
                    st.session_state.is_correct = True
                else:
                    st.session_state.is_correct = False
                    if word not in st.session_state.incorrect_list: st.session_state.incorrect_list.append(word)
                st.rerun()

# --- 4. 결과 화면 ---
elif st.session_state.page == 'result':
    st.markdown("<div class='studio-title'>🎊 테스트 완료</div>", unsafe_allow_html=True)
    total_count = len(st.session_state.test_words)
    score_pct = int((st.session_state.score / total_count) * 100) if not st.session_state.review_mode else 100
    
    st.markdown(f"<h1 style='text-align:center;'>{score_pct}%</h1>", unsafe_allow_html=True)
    
    if st.button("🔄 메인으로 돌아가기", use_container_width=True):
        st.session_state.page = 'main'
        st.rerun()
