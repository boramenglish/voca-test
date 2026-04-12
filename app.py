import streamlit as st
import pandas as pd
import random
import datetime

# ==========================================
# 🔒 [설정 1] 이번 주 현장 암호 
# ==========================================
SECRET_PASSWORD = "0000"

# ==========================================
# 🔗 [설정 2] 학년별 구글 시트 CSV 링크 (보람T 전용)
# ==========================================
SHEET_URLS = {
    "1학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=0&single=true&output=csv",
    "2학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=840773385&single=true&output=csv",
    "3학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=893402083&single=true&output=csv"
}

# 페이지 기본 설정
st.set_page_config(page_title="🌳 남보람T의 출구시험", page_icon="🌳", layout="centered")

# --- [핵심] 긴 단어 깨짐 방지 디자인 설정 (CSS) ---
st.markdown("""
<style>
/* 1. 메인 문제(영어 단어) 글자 크기 유연하게 조절 */
.big-word {
    font-size: clamp(2.5rem, 8vw, 5rem) !important; /* 스마트폰에서는 작게, PC에서는 크게 자동 조절 */
    word-break: keep-all; /* 단어 중간에 줄바꿈 방지 */
    text-align: center;
    padding: 20px;
    border: 2px solid #CBD5E1;
    border-radius: 15px;
    margin-bottom: 20px;
}

/* 2. 보기 버튼 글자 안 깨지게 조절 */
div.stButton > button {
    height: auto !important; /* 글자가 길면 버튼 세로 길이를 알아서 늘림 */
    min-height: 60px; /* 기본 버튼 두께 확보 */
    padding: 10px !important; 
}
div.stButton > button p {
    word-break: keep-all !important; /* '당연하 / 게' 처럼 이상하게 잘리는 것 방지 */
    white-space: normal !important; /* 글자가 길면 자연스럽게 다음 줄로 넘김 */
    font-size: 1rem !important; /* 보기 글자 크기 최적화 */
    line-height: 1.4 !important; /* 줄간격을 넓혀서 읽기 편하게 */
}
</style>
""", unsafe_allow_html=True)

# --- 데이터 불러오기 ---
@st.cache_data(ttl=60)
def load_words(url):
    try:
        df = pd.read_csv(url)
        df = df.dropna(how='all') 
        if len(df) < 8:
            return {} 
        return dict(zip(df.iloc[:, 0].astype(str).str.strip(), df.iloc[:, 1].astype(str).str.strip()))
    except Exception as e:
        return {}

# --- 세션 상태 관리 ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'page' not in st.session_state:
    st.session_state.page = 'main'
    st.session_state.score = 0
    st.session_state.current_q = 0
    st.session_state.test_words = []
    st.session_state.show_feedback = False
    st.session_state.is_correct = False
    st.session_state.correct_word = ""
    st.session_state.selected_grade = "1학년"

def reset_test():
    st.session_state.page = 'main'
    st.session_state.score = 0
    st.session_state.current_q = 0
    st.session_state.show_feedback = False

# ==========================================
# 🚧 화면 0: 보안 게이트 (암호 입력)
# ==========================================
if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #007AFF; font-size: 4em;'>🔒</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #1E293B;'>남보람T의 출구시험 입장</h2>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center; color: #64748B; margin-bottom: 30px;'>오늘 칠판에 적힌 현장 암호를 입력하세요.</h5>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd_input = st.text_input("비밀번호", type="password", placeholder="여기에 암호 입력", label_visibility="collapsed")
        
        if st.button("🚪 입장하기", use_container_width=True) or pwd_input:
            if pwd_input == SECRET_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            elif pwd_input:
                st.error("❌ 암호가 틀렸습니다. 칠판을 다시 확인하세요!")
    
    st.stop() 

# ==========================================
# 🍃 화면 1: 메인 메뉴 
# ==========================================
if st.session_state.page == 'main':
    st.markdown("<h3 style='text-align: center; color: #64748B;'>남보람T의</h3>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #007AFF; font-size: 4em;'>어휘 무한 훈련소</h1>", unsafe_allow_html=True)
    
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected = st.selectbox("📚 본인의 학년을 선택하세요!", ["1학년", "2학년", "3학년"])
        st.session_state.selected_grade = selected
    
    current_url = SHEET_URLS[st.session_state.selected_grade]
    word_dict = load_words(current_url)
    total_words = len(word_dict)
    
    st.markdown(f"<h4 style='text-align: center; color: #166534; margin-top: 20px;'>🍃 {st.session_state.selected_grade} 등록된 어휘: {total_words}개 🍃</h4>", unsafe_allow_html=True)
    
    with col2:
        st.write("") 
        if st.button("💪 연습 시작하기", use_container_width=True):
            if total_words < 8:
                st.error(f"🚨 {st.session_state.selected_grade} 구글 시트에 어휘를 8개 이상 채워주세요! (현재 {total_words}개)")
            else:
                st.session_state.test_words = random.sample(list(word_dict.keys()), total_words)
                st.session_state.show_feedback = False
                st.session_state.page = 'test'
                st.rerun()

# ==========================================
# 📝 화면 2: 시험 푸는 중
# ==========================================
elif st.session_state.page == 'test':
    current_url = SHEET_URLS[st.session_state.selected_grade]
    word_dict = load_words(current_url)
    
    total_q = len(st.session_state.test_words)
    current_q_display = st.session_state.current_q + 1
    
    st.markdown(f"<h5 style='color: #64748B;'>📖 {st.session_state.selected_grade} 어휘 훈련 중</h5>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #007AFF; text-align: right;'>QUESTION {current_q_display} / {total_q}</h3>", unsafe_allow_html=True)
    
    word = st.session_state.test_words[st.session_state.current_q]
    
    # CSS 클래스를 적용하여 긴 단어도 폰트 사이즈가 유연하게 줄어들도록 변경!
    st.markdown(f"<div class='big-word'>{word}</div>", unsafe_allow_html=True)

    if st.session_state.show_feedback:
        if st.session_state.is_correct:
            st.success("🎉 **정답입니다!** 훌륭해요!")
        else:
            st.error(f"❌ **오답입니다!** \n\n 확실하게 외워두세요! 👉 정답은: **[{st.session_state.correct_word}]**")
        
        if st.button("다음 문제 ➡️", use_container_width=True):
            st.session_state.show_feedback = False
            st.session_state.current_q += 1
            if st.session_state.current_q >= total_q:
                st.session_state.page = 'result'
            st.rerun()
    else:
        correct = word_dict[word]
        others = [v for k, v in word_dict.items() if v != correct]
        
        if 'current_options' not in st.session_state or st.session_state.get('q_idx_for_options') != st.session_state.current_q:
            options = random.sample(others, min(len(others), 7)) + [correct]
            random.shuffle(options)
            st.session_state.current_options = options
            st.session_state.q_idx_for_options = st.session_state.current_q
        else:
            options = st.session_state.current_options
        
        def check_answer(selected):
            st.session_state.show_feedback = True
            st.session_state.correct_word = correct
            if selected == correct:
                st.session_state.score += 1
                st.session_state.is_correct = True
            else:
                st.session_state.is_correct = False
                
        for i in range(0, 8, 4):
            cols = st.columns(4)
            for j in range(4):
                idx = i + j
                if idx < len(options):
                    if cols[j].button(options[idx], key=f"btn_{st.session_state.current_q}_{idx}", use_container_width=True):
                        check_answer(options[idx])
                        st.rerun()

# ==========================================
# 🎉 화면 3: 결과 화면
# ==========================================
elif st.session_state.page == 'result':
    total_q = len(st.session_state.test_words)
    
    st.balloons()
    st.markdown("<h1 style='text-align: center; color: #166534;'>🎉 훈련 완료! 🎉</h1>", unsafe_allow_html=True)
    
    if st.session_state.score == total_q:
        st.success(f"완벽합니다! {total_q}문제 중 {st.session_state.score}개를 맞췄습니다. (백점 💯)")
    else:
        st.warning(f"수고하셨습니다! {total_q}문제 중 {st.session_state.score}개를 맞췄습니다.")
    
    name = st.text_input("연습 기록을 남기려면 이름을 입력하고 엔터를 치세요", placeholder="예: 홍길동")
    if name:
        with open("passers.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] [{st.session_state.selected_grade}] {name} (연습완료: {st.session_state.score}/{total_q})\n")
        st.success("기록 저장 완료! 참 잘했어요 😊")
        
    st.write("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 메인 메뉴로 돌아가기", use_container_width=True):
            reset_test()
            st.rerun()
