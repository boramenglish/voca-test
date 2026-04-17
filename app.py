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

# --- CSS 디자인 ---
st.markdown("""
<style>
.big-word { font-size: clamp(2rem, 7vw, 4rem) !important; text-align: center; padding: 30px; border: 2px solid #E2E8F0; border-radius: 15px; background-color: #F8FAFC; margin-bottom: 25px; color: #1e293b; font-weight: bold; }
div.stButton > button { min-height: 65px; border-radius: 12px; font-weight: 600; width: 100%; }
div.stButton > button p { word-break: keep-all !important; white-space: normal !important; font-size: 1.1rem !important; }
/* 오답 서랍 스타일 */
.stExpander { border: 1px solid #fee2e2 !important; background-color: #fff1f2 !important; border-radius: 12px !important; }
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
    st.markdown("<h2 style='text-align:center;'>🔒 보람T 출구시험 입장</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
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
    st.markdown("<h1 style='text-align:center; color:#007AFF;'>어휘 무한 훈련소</h1>", unsafe_allow_html=True)
    st.write("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        grade = st.selectbox("📚 학년을 선택하세요", ["1학년", "2학년", "3학년"])
        st.session_state.selected_grade = grade
        words = load_words(SHEET_URLS[grade])
        st.info(f"🍃 등록된 어휘: {len(words)}개")
        if st.button("🚀 훈련 시작하기", use_container_width=True):
            if len(words) >= 8:
                word_keys = random.sample(list(words.keys()), len(words))
                start_session(word_keys)
                st.rerun()
            else: st.error("어휘를 8개 이상 등록해 주세요!")

# --- 3. 테스트 화면 ---
elif st.session_state.page == 'test':
    words = load_words(SHEET_URLS[st.session_state.selected_grade])
    word = st.session_state.test_words[st.session_state.current_q]
    
    if st.session_state.review_mode:
        st.markdown("<div style='text-align:center; color:#e11d48; font-weight:bold;'>🔥 오답 정복 모드 진행 중 🔥</div>", unsafe_allow_html=True)
    
    st.write(f"📊 {st.session_state.current_q+1} / {len(st.session_state.test_words)}")
    st.markdown(f"<div class='big-word'>{word}</div>", unsafe_allow_html=True)

    if st.session_state.get('feedback', False):
        if st.session_state.is_correct: st.success("🎯 정답입니다!")
        else: st.error(f"⚠️ 오답! 정답은: **{st.session_state.ans}**")
        
        if st.button("다음 문제 ➡️", use_container_width=True):
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

    # --- [NEW] 실시간 오답 서랍 ---
    if st.session_state.incorrect_list:
        st.write("---")
        with st.expander("📝 현재까지 틀린 단어 확인하기"):
            error_data = []
            for w in st.session_state.incorrect_list:
                error_data.append({"단어": w, "뜻": words.get(w, "")})
            st.table(error_data)

# --- 4. 결과 화면 ---
elif st.session_state.page == 'result':
    words = load_words(SHEET_URLS[st.session_state.selected_grade])
    st.balloons()
    st.markdown("<h2 style='text-align:center;'>🎊 테스트 완료 🎊</h2>", unsafe_allow_html=True)
    
    if not st.session_state.review_mode:
        st.markdown(f"<h3 style='text-align:center;'>점수: {st.session_state.score} / {len(st.session_state.test_words)}</h3>", unsafe_allow_html=True)
    
    st.write("---")
    
    if st.session_state.incorrect_list:
        st.subheader("📝 최종 오답 리스트")
        error_data = []
        for w in st.session_state.incorrect_list:
            error_data.append({"단어": w, "뜻": words.get(w, "")})
        st.table(error_data)
        
        if st.button("🔥 틀린 단어만 다시 풀기", use_container_width=True):
            review_words = random.sample(st.session_state.incorrect_list, len(st.session_state.incorrect_list))
            st.session_state.incorrect_list = []
            start_session(review_words, is_review=True)
            st.rerun()
    else:
        st.success("✨ 모든 어휘를 마스터했습니다!")

    if st.button("🔄 메인 메뉴로 돌아가기", use_container_width=True):
        st.session_state.page = 'main'
        st.session_state.review_mode = False
        st.rerun()
