import streamlit as st
import pandas as pd
import random

# [설정] 현장 암호 및 시트 링크 (기존 유지)
SECRET_PASSWORD = "0000"
SHEET_URLS = {
    "1학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=0&single=true&output=csv",
    "2학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=840773385&single=true&output=csv",
    "3학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=893402083&single=true&output=csv"
}

st.set_page_config(page_title="Palette of Words", page_icon="🎨", layout="centered")

# --- 🌸 예술적인 화사함: CSS 디자인 ---
st.markdown("""
<style>
    /* 배경: 화사한 수채화 느낌의 이미지와 그라데이션 조합 */
    .stApp {
        background-image: linear-gradient(rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.7)), 
                          url('https://images.unsplash.com/photo-1513364776144-60967b0f800f?q=80&w=2071&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 메인 타이틀: 감성적인 세리프체 느낌 */
    .main-title {
        font-family: 'Georgia', serif;
        color: #ff7eb9;
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }

    /* 단어 카드: 종이 질감의 캔버스 */
    .big-word {
        font-size: clamp(2.5rem, 10vw, 5rem) !important;
        text-align: center;
        padding: 60px 20px;
        background: rgba(255, 255, 255, 0.85);
        border-radius: 50px 10px 50px 10px; /* 비정형적인 예술적 느낌 */
        border-left: 10px solid #ffbc00;
        box-shadow: 15px 15px 0px rgba(255, 126, 185, 0.2);
        color: #444;
        font-weight: 800;
        margin-bottom: 40px;
    }

    /* 버튼: 팔레트의 물감 컬러 */
    div.stButton > button {
        border-radius: 25px;
        border: none;
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: white;
        font-size: 1.2rem !important;
        font-weight: 600;
        min-height: 70px;
        box-shadow: 0 5px 15px rgba(255, 154, 158, 0.4);
        transition: all 0.3s ease;
    }

    div.stButton > button:hover {
        transform: scale(1.05) rotate(1deg);
        background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
        box-shadow: 0 8px 20px rgba(161, 196, 253, 0.5);
        color: white !important;
    }

    /* 입력창 및 셀렉트박스 스타일 */
    .stSelectbox, .stTextInput {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 로드 함수 (기존 유지)
@st.cache_data(ttl=60)
def load_words(url):
    try:
        df = pd.read_csv(url)
        df = df.dropna(how='all')
        if len(df) < 1: return {}
        return dict(zip(df.iloc[:, 0].astype(str).str.strip(), df.iloc[:, 1].astype(str).str.strip()))
    except: return {}

# 세션 관리 (기존 유지)
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

# --- 1. 보안 게이트 (화사한 입장) ---
if not st.session_state.authenticated:
    st.markdown("<h1 class='main-title'>Welcome to<br>Boram's Atelier</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("🔑 입장 암호를 입력하세요", type="password")
        if st.button("🚪 아뜰리에 입장"):
            if pwd == SECRET_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("🌸 암호가 올바르지 않아요!")
    st.stop()

# --- 2. 메인 메뉴 ---
if st.session_state.page == 'main':
    st.markdown("<h1 class='main-title'>Palette of Words</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align:center; color:#666;'>단어에 색을 입히는 시간입니다.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        grade = st.selectbox("🎨 오늘의 캔버스 (학년)", ["1학년", "2학년", "3학년"])
        st.session_state.selected_grade = grade
        words = load_words(SHEET_URLS[grade])
        
        st.success(f"준비된 영감(단어): {len(words)}개")
        
        if st.button("🖌️ 스케치 시작 (훈련)", use_container_width=True):
            if len(words) >= 4:
                word_keys = random.sample(list(words.keys()), len(words))
                start_session(word_keys)
                st.rerun()
            else: st.error("어휘를 조금 더 채워주세요!")

# --- 3. 테스트 화면 ---
elif st.session_state.page == 'test':
    words = load_words(SHEET_URLS[st.session_state.selected_grade])
    word = st.session_state.test_words[st.session_state.current_q]
    
    st.write(f"🎨 **Progress:** {st.session_state.current_q+1} / {len(st.session_state.test_words)}")
    st.markdown(f"<div class='big-word'>{word}</div>", unsafe_allow_html=True)

    if st.session_state.get('feedback', False):
        if st.session_state.is_correct: 
            st.markdown("<h3 style='text-align:center; color:#4CAF50;'>✨ 환상적인 터치예요!</h3>", unsafe_allow_html=True)
        else: 
            st.markdown(f"<h3 style='text-align:center; color:#e91e63;'>🎨 정답이라는 색은 <b>{st.session_state.ans}</b></h3>", unsafe_allow_html=True)
        
        if st.button("다음 캔버스로 ➡️", use_container_width=True):
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
    st.markdown("<h1 class='main-title'>Masterpiece!</h1>", unsafe_allow_html=True)
    
    score_pct = int((st.session_state.score / len(st.session_state.test_words)) * 100) if not st.session_state.review_mode else 100
    
    st.markdown(f"""
        <div style='text-align:center; padding: 30px; background: rgba(255,255,255,0.7); border-radius: 20px; margin-bottom: 20px;'>
            <h2 style='color:#ff7eb9;'>완성도: {score_pct}%</h2>
            <p>오늘의 어휘 작품이 훌륭하게 완성되었습니다.</p>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.incorrect_list:
        with st.expander("📝 덧칠이 필요한 단어들 (오답)"):
            words_dict = load_words(SHEET_URLS[st.session_state.selected_grade])
            error_data = [{"단어": w, "뜻": words_dict.get(w, "")} for w in st.session_state.incorrect_list]
            st.table(error_data)
        
        if st.button("🔥 오답 리터칭 시작", use_container_width=True):
            review_words = list(st.session_state.incorrect_list)
            st.session_state.incorrect_list = []
            start_session(review_words, is_review=True)
            st.rerun()

    if st.button("🔄 아뜰리에 메인으로", use_container_width=True):
        st.session_state.page = 'main'
        st.session_state.review_mode = False
        st.rerun()
