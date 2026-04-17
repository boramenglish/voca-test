import streamlit as st
import pandas as pd
import random
import time

# [설정] 현장 암호 및 시트 링크 (기존 유지)
SECRET_PASSWORD = "0000"
SHEET_URLS = {
    "1학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=0&single=true&output=csv",
    "2학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=840773385&single=true&output=csv",
    "3학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=893402083&single=true&output=csv"
}

st.set_page_config(page_title="BoramT Voca Atelier", page_icon="🎨", layout="centered")

# --- ✨ 미술적 감각을 더한 CSS 디자인 ---
st.markdown("""
<style>
    /* 전체 배경: 은은한 파스텔 그라데이션 */
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    }

    /* 메인 타이틀 스타일 */
    .main-title {
        font-family: 'serif';
        color: #4a5568;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 300;
        letter-spacing: -1px;
        margin-bottom: 30px;
    }

    /* 단어 카드: 캔버스 느낌의 글래스모피즘 */
    .big-word {
        font-size: clamp(2.2rem, 8vw, 4.5rem) !important;
        text-align: center;
        padding: 50px 20px;
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        color: #2d3748;
        font-weight: 700;
        margin-bottom: 40px;
        transition: transform 0.3s ease;
    }

    /* 버튼 스타일: 감각적인 라운딩과 컬러링 */
    div.stButton > button {
        border-radius: 20px;
        border: none;
        background-color: white;
        color: #4a5568;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        min-height: 60px;
        transition: all 0.2s ease;
        border: 1px solid #edf2f7;
    }

    div.stButton > button:hover {
        background: #6366f1 !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(99, 102, 241, 0.2);
    }

    /* 다음 문제 버튼 (강조) */
    div.stButton > button[kind="secondary"] {
        background: #6366f1;
        color: white;
    }

    /* 오답 리스트 테이블 스타일 */
    .stTable {
        background: white;
        border-radius: 20px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_words(url):
    try:
        df = pd.read_csv(url)
        df = df.dropna(how='all')
        if len(df) < 1: return {}
        return dict(zip(df.iloc[:, 0].astype(str).str.strip(), df.iloc[:, 1].astype(str).str.strip()))
    except: return {}

# 세션 상태 초기화 (기존 로직 유지)
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
    st.session_state.feedback = False
    if not is_review:
        st.session_state.score = 0
        st.session_state.incorrect_list = []
    st.session_state.page = 'test'

# --- 1. 보안 게이트 (미니멀 디자인) ---
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align:center; color:#4a5568; margin-top:100px;'>Enter the Atelier</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("Password", type="password", placeholder="비밀번호를 입력하세요")
        if st.button("🚪 ENTER") or (pwd == SECRET_PASSWORD):
            if pwd == SECRET_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            elif pwd: st.error("❌ 비밀번호가 올바르지 않습니다.")
    st.stop()

# --- 2. 메인 메뉴 ---
if st.session_state.page == 'main':
    st.markdown("<h1 class='main-title'>BoramT Voca Atelier</h1>", unsafe_allow_html=True)
    st.write("<div style='text-align:center; color:#718096; margin-bottom:40px;'>오늘의 어휘 영감을 채워보세요.</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        grade = st.selectbox("🎨 학년 선택", ["1학년", "2학년", "3학년"])
        st.session_state.selected_grade = grade
        words = load_words(SHEET_URLS[grade])
        
        st.markdown(f"""
            <div style='text-align:center; padding: 20px; border-radius: 20px; background: rgba(255,255,255,0.5); margin-bottom: 20px;'>
                <span style='color:#718096;'>준비된 캔버스(단어):</span> 
                <span style='color:#6366f1; font-weight:bold;'>{len(words)}개</span>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 어휘 훈련 시작", use_container_width=True):
            if len(words) >= 4:
                word_keys = random.sample(list(words.keys()), len(words))
                start_session(word_keys)
                st.rerun()
            else: st.error("어휘를 더 등록해 주세요!")

# --- 3. 테스트 화면 ---
elif st.session_state.page == 'test':
    words = load_words(SHEET_URLS[st.session_state.selected_grade])
    word = st.session_state.test_words[st.session_state.current_q]
    
    # 상단 진행바
    progress = (st.session_state.current_q) / len(st.session_state.test_words)
    st.progress(progress)
    st.write(f"<div style='text-align:right; color:#a0aec0; font-size:0.9rem;'>Sketch {st.session_state.current_q+1} of {len(st.session_state.test_words)}</div>", unsafe_allow_html=True)

    if st.session_state.review_mode:
        st.markdown("<div style='text-align:center; color:#f87171; font-size:0.8rem; letter-spacing:2px; margin-bottom:10px;'>RE-TOUCHING MODE</div>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='big-word'>{word}</div>", unsafe_allow_html=True)

    if st.session_state.get('feedback', False):
        if st.session_state.is_correct: 
            st.markdown("<div style='text-align:center; color:#10b981; font-size:1.2rem; margin-bottom:20px;'>✨ 탁월한 선택입니다!</div>", unsafe_allow_html=True)
        else: 
            st.markdown(f"<div style='text-align:center; color:#f87171; font-size:1.2rem; margin-bottom:20px;'>정답은 <b>{st.session_state.ans}</b> 이었습니다.</div>", unsafe_allow_html=True)
        
        if st.button("Next Canvas ➡️", use_container_width=True):
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

# --- 4. 결과 화면 ---
elif st.session_state.page == 'result':
    st.balloons()
    st.markdown("<h2 style='text-align:center; color:#4a5568;'>Finishing Touches</h2>", unsafe_allow_html=True)
    
    score_pct = int((st.session_state.score / len(st.session_state.test_words)) * 100) if not st.session_state.review_mode else 100
    
    st.markdown(f"""
        <div style='text-align:center; padding: 40px; border-radius: 30px; background: white; margin: 30px 0;'>
            <div style='font-size: 1.2rem; color: #a0aec0;'>Mastery Rate</div>
            <div style='font-size: 4rem; font-weight: bold; color: #6366f1;'>{score_pct}%</div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.incorrect_list:
        with st.expander("🎨 다시 그려볼 단어들 (오답 리스트)"):
            words_dict = load_words(SHEET_URLS[st.session_state.selected_grade])
            error_data = [{"단어": w, "의미": words_dict.get(w, "")} for w in st.session_state.incorrect_list]
            st.table(error_data)
        
        if st.button("🔥 오답 리터칭(재시험) 하기", use_container_width=True):
            review_words = list(st.session_state.incorrect_list)
            st.session_state.incorrect_list = []
            start_session(review_words, is_review=True)
            st.rerun()
    else:
        st.success("완벽합니다! 당신의 어휘 캔버스가 완성되었습니다.")

    if st.button("🔄 아틀리에 메인으로", use_container_width=True):
        st.session_state.page = 'main'
        st.session_state.review_mode = False
        st.rerun()
