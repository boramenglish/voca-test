import streamlit as st
import pandas as pd
import random

# [설정] 기존 데이터 유지
SECRET_PASSWORD = "0501"
SHEET_URLS = {
    "1학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=0&single=true&output=csv",
    "2학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=840773385&single=true&output=csv",
    "3학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=893402083&single=true&output=csv"
}

st.set_page_config(page_title="🌳 보람T 어휘 훈련소", page_icon="🌳", layout="centered")

# --- CSS 디자인 (동일) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@200;400;700&family=Inter:wght@300;400;600&display=swap');
    .stApp { background-color: #ffffff; font-family: 'Inter', sans-serif; }
    .studio-title { font-family: 'Noto Serif KR', serif; color: #1a1a1a; text-align: center; font-size: 2.2rem; font-weight: 700; letter-spacing: -0.05em; margin-bottom: 10px; }
    .word-canvas { font-family: 'Noto Serif KR', serif; font-size: clamp(2.5rem, 8vw, 4rem); text-align: center; padding: 80px 20px; background: #f9f9f9; border: 1px solid #eeeeee; color: #1a1a1a; margin-bottom: 50px; font-weight: 400; }
    div.stButton > button { border-radius: 0px; border: 1px solid #1a1a1a; background-color: #ffffff; color: #1a1a1a; font-size: 1rem !important; min-height: 55px; transition: all 0.3s ease; }
    div.stButton > button:hover { background-color: #1a1a1a !important; color: #ffffff !important; }
    .stExpander { border: 1px solid #eeeeee !important; border-radius: 0px !important; }
    hr { border-top: 1px solid #1a1a1a; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_words(url):
    try:
        df = pd.read_csv(url)
        df = df.dropna(how='all')
        return dict(zip(df.iloc[:, 0].astype(str).str.strip(), df.iloc[:, 1].astype(str).str.strip()))
    except: return {}

# 세션 초기화
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'page' not in st.session_state:
    st.session_state.update({
        'page': 'main', 'score': 0, 'current_q': 0, 
        'incorrect_list': [], 'review_mode': False, 'feedback': False
    })

def start_session(word_list, is_review=False):
    st.session_state.update({
        'test_words': word_list, 'current_q': 0, 'review_mode': is_review,
        'feedback': False, 'page': 'test'
    })
    if not is_review:
        st.session_state.update({'score': 0, 'incorrect_list': []})
    if 'current_options' in st.session_state:
        del st.session_state.current_options

# --- 1. 보안 게이트 ---
if not st.session_state.authenticated:
    st.markdown("<div style='margin-top:100px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-family:\"Noto Serif KR\";'>🔒 보람T 어휘 훈련소 입장</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        pwd = st.text_input("현장 암호를 입력하세요", type="password")
        if st.button("🚪 입장하기") or (pwd == SECRET_PASSWORD):
            if pwd == SECRET_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            elif pwd: st.error("❌ 암호가 틀렸습니다!")
    st.stop()

# --- 2. 메인 메뉴 ---
if st.session_state.page == 'main':
    st.markdown("<div style='margin-top:50px;'></div><div class='studio-title'>어휘 무한 훈련소</div><hr>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        grade = st.selectbox("📚 학년을 선택하세요", ["1학년", "2학년", "3학년"])
        st.session_state.selected_grade = grade
        words_dict = load_words(SHEET_URLS[grade])
        st.markdown(f"<p style='text-align:center; color:#666;'>🍃 등록된 어휘: {len(words_dict)}개</p>", unsafe_allow_html=True)
        if st.button("🚀 훈련 시작하기", use_container_width=True):
            if len(words_dict) >= 4:
                word_keys = random.sample(list(words_dict.keys()), len(words_dict))
                start_session(word_keys)
                st.rerun()

# --- 3. 테스트 화면 ---
elif st.session_state.page == 'test':
    words_dict = load_words(SHEET_URLS[st.session_state.selected_grade])
    current_word = st.session_state.test_words[st.session_state.current_q]
    
    # [핵심] 보기 생성 및 세션 고정
    if 'current_options' not in st.session_state:
        correct_ans = words_dict[current_word]
        others = [v for k, v in words_dict.items() if v != correct_ans]
        opts = random.sample(others, min(len(others), 5)) + [correct_ans]
        random.shuffle(opts)
        st.session_state.current_options = opts
        st.session_state.current_answer = correct_ans

    if st.session_state.review_mode:
        st.markdown("<div style='text-align:center; color:#e63946; font-size:0.8rem; font-weight:bold; margin-bottom:10px;'>🔥 오답 정복 모드 진행 중 🔥</div>", unsafe_allow_html=True)
    
    st.markdown(f"<p style='text-align:center; color:#888;'>{st.session_state.current_q+1} / {len(st.session_state.test_words)}</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='word-canvas'>{current_word}</div>", unsafe_allow_html=True)

    if st.session_state.feedback:
        if st.session_state.is_correct:
            st.markdown("<p style='text-align:center; color:#1a1a1a; font-weight:600;'>🎯 정답입니다!</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='text-align:center; color:#e63946;'>⚠️ 오답! 정답은: <b>{st.session_state.current_answer}</b></p>", unsafe_allow_html=True)
        
        if st.button("다음 문제 ➡️", use_container_width=True):
            st.session_state.feedback = False
            st.session_state.current_q += 1
            if 'current_options' in st.session_state: del st.session_state.current_options
            if st.session_state.current_q >= len(st.session_state.test_words): st.session_state.page = 'result'
            st.rerun()
    else:
        cols = st.columns(2)
        for i, opt in enumerate(st.session_state.current_options):
            if cols[i%2].button(opt, key=f"btn_{st.session_state.current_q}_{i}", use_container_width=True):
                st.session_state.feedback = True
                # 세션에 저장된 정답과 클릭한 옵션을 직접 비교
                if opt == st.session_state.current_answer:
                    if not st.session_state.review_mode: st.session_state.score += 1
                    st.session_state.is_correct = True
                else:
                    st.session_state.is_correct = False
                    if current_word not in st.session_state.incorrect_list:
                        st.session_state.incorrect_list.append(current_word)
                st.rerun()

# --- 4. 결과 화면 ---
elif st.session_state.page == 'result':
    st.markdown("<div style='margin-top:50px;'></div><div class='studio-title'>🎊 테스트 완료 🎊</div>", unsafe_allow_html=True)
    if not st.session_state.review_mode:
        score_pct = int((st.session_state.score / len(st.session_state.test_words)) * 100)
        st.markdown(f"<h3 style='text-align:center; font-size:3rem;'>{score_pct}%</h3>", unsafe_allow_html=True)
    
    st.write("---")
    if st.session_state.incorrect_list:
        st.subheader("📝 최종 오답 리스트")
        words_dict = load_words(SHEET_URLS[st.session_state.selected_grade])
        st.table([{"단어": w, "뜻": words_dict.get(w, "")} for w in st.session_state.incorrect_list])
        if st.button("🔥 틀린 단어만 다시 풀기", use_container_width=True):
            review_words = list(st.session_state.incorrect_list)
            st.session_state.incorrect_list = []
            start_session(review_words, is_review=True)
            st.rerun()
    else: st.success("✨ 모든 어휘를 마스터했습니다!")

    if st.button("🔄 메인 메뉴로 돌아가기", use_container_width=True):
        st.session_state.page = 'main'
        st.rerun()
