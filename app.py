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

# --- 🖼️ 다크모드 방지 CSS (강력 수정 버전) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700&family=Inter:wght@400;600&display=swap');
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    h1, h2, h3, p, span, div, label, li {
        color: #1a1a1a !important;
        -webkit-text-fill-color: #1a1a1a !important;
    }
    .studio-title {
        font-family: 'Noto Serif KR', serif;
        text-align: center; font-size: 1.8rem; font-weight: 700; margin-bottom: 20px;
    }
    .word-canvas {
        font-family: 'Noto Serif KR', serif;
        font-size: clamp(2rem, 10vw, 3.5rem);
        text-align: center; padding: 60px 10px;
        background: #f8f9fa !important;
        border: 2px solid #1a1a1a !important;
        border-radius: 15px; margin-bottom: 30px; font-weight: 700;
    }
    div.stButton > button {
        border-radius: 8px; border: 2px solid #1a1a1a !important;
        background-color: #ffffff !important; color: #1a1a1a !important;
        -webkit-text-fill-color: #1a1a1a !important;
        font-weight: 600 !important; min-height: 55px; width: 100%;
    }
    div[data-baseweb="input"], div[data-baseweb="select"] { background-color: #ffffff !important; }
    input { color: #1a1a1a !important; -webkit-text-fill-color: #1a1a1a !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_words(url):
    try:
        df = pd.read_csv(url, on_bad_lines='skip')
        df = df.dropna(subset=[df.columns[0], df.columns[1]])
        return dict(zip(df.iloc[:, 0].astype(str).str.strip(), df.iloc[:, 1].astype(str).str.strip()))
    except: return {}

# 세션 초기화
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'page' not in st.session_state:
    st.session_state.update({'page': 'main', 'score': 0, 'current_q': 0, 'incorrect_list': [], 'test_words': [], 'current_options': [], 'feedback': False})

# --- 1. 보안 게이트 ---
if not st.session_state.authenticated:
    st.markdown("<div style='margin-top:50px;'></div><h2 style='text-align:center;'>🔒 보람T 어휘 훈련소 입장</h2>", unsafe_allow_html=True)
    pwd = st.text_input("현장 암호를 입력하세요", type="password")
    if st.button("🚪 입장하기", use_container_width=True) or (pwd == SECRET_PASSWORD):
        if pwd == SECRET_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        elif pwd: st.error("❌ 암호가 틀렸습니다!")
    st.stop()

# --- 2. 메인 메뉴 ---
if st.session_state.page == 'main':
    st.markdown("<div class='studio-title'>어휘 무한 훈련소</div>", unsafe_allow_html=True)
    grade = st.selectbox("📚 학년을 선택하세요", list(SHEET_URLS.keys()))
    words = load_words(SHEET_URLS[grade])
    st.info(f"🍃 등록된 어휘: {len(words)}개")
    if st.button("🚀 훈련 시작하기", use_container_width=True):
        if len(words) >= 4:
            st.session_state.update({'selected_grade': grade, 'test_words': random.sample(list(words.keys()), len(words)), 'current_q': 0, 'score': 0, 'incorrect_list': [], 'page': 'test', 'current_options': [], 'feedback': False})
            st.rerun()

# --- 3. 테스트 화면 ---
elif st.session_state.page == 'test':
    all_words = load_words(SHEET_URLS[st.session_state.selected_grade])
    current_word = st.session_state.test_words[st.session_state.current_q]
    correct_answer = all_words[current_word]

    st.markdown(f"<p style='text-align:center;'>{st.session_state.current_q+1} / {len(st.session_state.test_words)}</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='word-canvas'>{current_word}</div>", unsafe_allow_html=True)

    # 선택지 생성
    if not st.session_state.feedback and not st.session_state.current_options:
        others = [v for k, v in all_words.items() if v.strip() != correct_answer.strip()]
        opts = random.sample(others, min(len(others), 3)) + [correct_answer]
        random.shuffle(opts)
        st.session_state.current_options = opts

    if st.session_state.feedback:
        if st.session_state.is_correct: st.success("🎯 정답입니다!")
        else: st.error(f"⚠️ 오답! 정답: {correct_answer}")
        
        if st.button("다음 문제 ➡️", use_container_width=True):
            st.session_state.feedback = False
            st.session_state.current_options = []
            st.session_state.current_q += 1
            if st.session_state.current_q >= len(st.session_state.test_words): st.session_state.page = 'result'
            st.rerun()
    else:
        for i, opt in enumerate(st.session_state.current_options):
            if st.button(opt, key=f"btn_{i}"):
                # [수정 핵심] 공백 제거 후 비교하여 정확도 향상
                is_correct = opt.strip() == correct_answer.strip()
                st.session_state.is_correct = is_correct
                st.session_state.feedback = True
                if is_correct:
                    st.session_state.score += 1
                else:
                    st.session_state.incorrect_list.append(current_word)
                st.rerun()

# --- 4. 결과 화면 ---
elif st.session_state.page == 'result':
    st.markdown("<div class='studio-title'>🎊 테스트 완료</div>", unsafe_allow_html=True)
    total = len(st.session_state.test_words)
    pct = int((st.session_state.score / total) * 100)
    st.markdown(f"<h1 style='text-align:center;'>{pct}점</h1>", unsafe_allow_html=True)
    if st.session_state.incorrect_list:
        with st.expander("📝 틀린 단어 복습"):
            all_words = load_words(SHEET_URLS[st.session_state.selected_grade])
            for w in st.session_state.incorrect_list: st.write(f"❌ **{w}** : {all_words[w]}")
    if st.button("🔄 메인으로 돌아가기", use_container_width=True):
        st.session_state.page = 'main'
        st.rerun()
