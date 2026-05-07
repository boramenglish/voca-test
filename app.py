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

# 페이지 설정
st.set_page_config(page_title="🌳 보람T 어휘 훈련소", page_icon="🌳", layout="centered")

# --- 🖼️ 다크모드 강제 방지 및 가독성 강화 CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700&family=Inter:wght@400;600&display=swap');

    /* 1. 전체 배경색과 기본 텍스트 색상을 라이트 모드로 고정 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }

    /* 2. 모든 텍스트 요소의 색상을 검정으로 강제 (다크모드 반전 방지 핵심) */
    h1, h2, h3, p, span, div, label, li {
        color: #1a1a1a !important;
        -webkit-text-fill-color: #1a1a1a !important;
        font-family: 'Inter', sans-serif;
    }

    /* 3. 타이틀 디자인 */
    .studio-title {
        font-family: 'Noto Serif KR', serif;
        color: #1a1a1a !important;
        -webkit-text-fill-color: #1a1a1a !important;
        text-align: center;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 20px;
    }

    /* 4. 단어 카드 디자인 - 모바일 가독성 극대화 */
    .word-canvas {
        font-family: 'Noto Serif KR', serif;
        font-size: clamp(2rem, 10vw, 3.5rem);
        text-align: center;
        padding: 60px 10px;
        background: #f8f9fa !important;
        border: 2px solid #1a1a1a !important;
        border-radius: 15px;
        color: #1a1a1a !important;
        -webkit-text-fill-color: #1a1a1a !important;
        margin-bottom: 30px;
        font-weight: 700;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    /* 5. 버튼 디자인 - 테두리와 글자색 명확히 */
    div.stButton > button {
        border-radius: 8px;
        border: 2px solid #1a1a1a !important;
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        -webkit-text-fill-color: #1a1a1a !important;
        font-weight: 600 !important;
        min-height: 55px;
        transition: all 0.2s ease;
    }
    
    div.stButton > button:hover {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* 6. 입력창(비밀번호 등) 다크모드 대응 */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1px solid #1a1a1a !important;
    }
    
    input {
        color: #1a1a1a !important;
        -webkit-text-fill-color: #1a1a1a !important;
        background-color: #ffffff !important;
    }

    /* 7. 셀렉트박스 다크모드 대응 */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
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
    st.session_state.update({
        'page': 'main', 'score': 0, 'current_q': 0, 
        'incorrect_list': [], 'review_mode': False,
        'test_words': [], 'current_options': []
    })

def start_session(word_list, is_review=False):
    st.session_state.test_words = word_list
    st.session_state.current_q = 0
    st.session_state.review_mode = is_review
    st.session_state.feedback = False
    st.session_state.current_options = []
    if not is_review:
        st.session_state.score = 0
        st.session_state.incorrect_list = []
    st.session_state.page = 'test'

# --- 1. 보안 게이트 ---
if not st.session_state.authenticated:
    st.markdown("<div style='margin-top:50px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>🔒 보람T 어휘 훈련소 입장</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col2:
        pwd = st.text_input("현장 암호를 입력하세요", type="password")
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
            word_keys = list(words.keys())
            random.shuffle(word_keys)
            start_session(word_keys)
            st.rerun()
        else:
            st.warning("훈련을 시작하려면 최소 4개 이상의 단어가 필요합니다.")

# --- 3. 테스트 화면 ---
elif st.session_state.page == 'test':
    words = load_words(SHEET_URLS[st.session_state.selected_grade])
    word = st.session_state.test_words[st.session_state.current_q]
    correct_ans = words[word]
    
    st.markdown(f"<p style='text-align:center; font-weight:bold;'>{st.session_state.current_q+1} / {len(st.session_state.test_words)}</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='word-canvas'>{word}</div>", unsafe_allow_html=True)

    # 선택지 세션 관리 (리렌더링 시 섞임 방지)
    if not st.session_state.get('feedback', False) and not st.session_state.current_options:
        others = [v for k, v in words.items() if v.strip() != correct_ans.strip()]
        opts = random.sample(others, min(len(others), 3)) + [correct_ans]
        random.shuffle(opts)
        st.session_state.current_options = opts

    if st.session_state.get('feedback', False):
        if st.session_state.is_correct: 
            st.success("🎯 정답입니다!")
        else: 
            st.error(f"⚠️ 오답! 정답: {st.session_state.ans_text}")
        
        if st.button("다음 문제 ➡️", use_container_width=True):
            st.session_state.feedback = False
            st.session_state.current_options = []
            st.session_state.current_q += 1
            if st.session_state.current_q >= len(st.session_state.test_words): 
                st.session_state.page = 'result'
            st.rerun()
    else:
        for i, opt in enumerate(st.session_state.current_options):
            if st.button(opt, key=f"btn_{i}", use_container_width=True):
                st.session_state.feedback = True
                st.session_state.ans_text = correct_ans
                if opt.strip() == correct_ans.strip():
                    if not st.session_state.review_mode: st.session_state.score += 1
                    st.session_state.is_correct = True
                else:
                    st.session_state.is_correct = False
                    if word not in st.session_state.incorrect_list: 
                        st.session_state.incorrect_list.append(word)
                st.rerun()

# --- 4. 결과 화면 ---
elif st.session_state.page == 'result':
    st.markdown("<div class='studio-title'>🎊 테스트 완료</div>", unsafe_allow_html=True)
    total_count = len(st.session_state.test_words)
    score_pct = int((st.session_state.score / total_count) * 100)
    
    st.markdown(f"<h1 style='text-align:center;'>{score_pct}점</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>{total_count}문제 중 {st.session_state.score}문제를 맞혔습니다!</p>", unsafe_allow_html=True)
    
    if st.session_state.incorrect_list:
        with st.expander("📝 틀린 단어 복습하기"):
            all_words = load_words(SHEET_URLS[st.session_state.selected_grade])
            for w in st.session_state.incorrect_list:
                st.write(f"❌ **{w}** : {all_words[w]}")

    if st.button("🔄 메인으로 돌아가기", use_container_width=True):
        st.session_state.page = 'main'
        st.rerun()
