import streamlit as st
import pandas as pd
import random
import time
import re
import math
import requests
from datetime import datetime, timezone, timedelta

# =====================================================================
# [설정] ← 여기만 고치면 됩니다
# =====================================================================
SECRET_PASSWORD = "1111"        # 학생 입장 암호
ADMIN_PASSWORD = "0502"         # 관리자(합격자 명단) 암호 ← 선생님만 아는 번호로 바꾸세요

# 구글 Apps Script 배포 후 받은 '웹 앱 URL'을 따옴표 안에 붙여넣으세요
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwoSPC2NhxiPPobsSljSQIVx1iiPZsLtikIeFHyWqY9Vw-ckyNsQjVL52Ixu6QDfFQF/exec"
APPS_SCRIPT_TOKEN = "boramT-vocab-2026"   # Apps Script 코드의 TOKEN과 똑같아야 함

GRADES = ["예비1학년", "1학년", "2학년"]
SHEET_URLS = {
    "예비1학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=893402083&single=true&output=csv",
    "1학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=0&single=true&output=csv",
    "2학년": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTRKKWnPkBvYx6PWMzyyrQSl3GX-eyS96nIJgWx2_S1I-YYBEs4z2ufB3HRghy4L3hzJqnwmWj4BHOa/pub?gid=840773385&single=true&output=csv",
}

# 시험 규칙
EXAM_TOTAL = 50        # 출제 문항 수
EXAM_PASS = 40         # 합격 기준 (정답 수)
EXAM_MAX_WRONG = 10    # 허용 오답 수 (11개째 틀리면 즉시 탈락)
TIME_LIMIT = 4         # 화면에 보이는 제한시간(초)
TIME_GRACE = 0.5       # 인터넷 지연 대비 숨은 여유시간(초) → 실제 판정 4.5초
PRACTICE_OPTS = 6      # 연습 보기 개수
EXAM_OPTS = 8          # 시험 보기 개수

KST = timezone(timedelta(hours=9))

st.set_page_config(page_title="🌳 보람T 어휘 훈련소", page_icon="🌳", layout="centered")

# --- 🖼️ 현대미술관(MoMA) 스타일 CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght=200;400;700&family=Inter:wght=300;400;600&display=swap');
    .stApp { background-color: #ffffff; font-family: 'Inter', sans-serif; }
    .studio-title {
        font-family: 'Noto Serif KR', serif; color: #1a1a1a; text-align: center;
        font-size: 2.2rem; font-weight: 700; letter-spacing: -0.05em; margin-bottom: 10px;
    }
    .word-canvas {
        font-family: 'Noto Serif KR', serif; font-size: clamp(2.5rem, 8vw, 4rem);
        text-align: center; padding: 80px 20px; background: #f9f9f9;
        border: 1px solid #eeeeee; color: #1a1a1a; margin-bottom: 50px; font-weight: 400;
    }
    .word-canvas-exam {
        font-family: 'Noto Serif KR', serif; font-size: clamp(2.2rem, 7vw, 3.5rem);
        text-align: center; padding: 40px 20px; background: #f9f9f9;
        border: 1px solid #eeeeee; color: #1a1a1a; margin-bottom: 25px; font-weight: 400;
    }
    .exam-bar { display: flex; justify-content: space-between; gap: 8px; margin-bottom: 8px; }
    .exam-box {
        flex: 1; text-align: center; border: 1px solid #1a1a1a; padding: 8px 4px;
        font-size: 0.8rem; color: #666;
    }
    .exam-box b { display: block; font-size: 1.4rem; color: #1a1a1a; font-family: 'Inter', sans-serif; }
    .exam-box.danger b { color: #e63946; }
    .rule-box {
        border: 1px solid #eeeeee; background: #f9f9f9; padding: 14px 18px;
        font-size: 0.85rem; color: #444; line-height: 1.7; margin-top: 10px;
    }
    div.stButton > button {
        border-radius: 0px; border: 1px solid #1a1a1a; background-color: #ffffff;
        color: #1a1a1a; font-size: 1rem !important; min-height: 55px; transition: all 0.3s ease;
    }
    div.stButton > button:hover { background-color: #1a1a1a !important; color: #ffffff !important; }
    .stExpander { border: 1px solid #eeeeee !important; border-radius: 0px !important; }
    hr { border-top: 1px solid #1a1a1a; }
    [data-testid="stStatusWidget"] { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

ss = st.session_state


@st.cache_data(ttl=60)
def load_words(url):
    try:
        df = pd.read_csv(url)
        df = df.dropna(how='all')
        return dict(zip(df.iloc[:, 0].astype(str).str.strip(), df.iloc[:, 1].astype(str).str.strip()))
    except Exception:
        return {}


def make_options(words, ans, n):
    """정답 1개 + 오답 (n-1)개 보기 생성"""
    others = list(set(v for v in words.values() if v != ans))
    opts = random.sample(others, min(len(others), n - 1)) + [ans]
    random.shuffle(opts)
    return opts


def now_kst_str():
    return datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")


def save_passer(grade, name, score, when):
    """구글 시트(Apps Script)로 합격자 기록 전송"""
    try:
        r = requests.post(APPS_SCRIPT_URL, json={
            "token": APPS_SCRIPT_TOKEN, "grade": grade,
            "name": name, "score": score, "time": when,
        }, timeout=20)
        data = r.json()
        return data.get("ok", False), data.get("error", "")
    except Exception as e:
        return False, str(e)


def load_passers():
    """관리자용: 합격자 명단 불러오기"""
    try:
        r = requests.get(APPS_SCRIPT_URL, params={"token": APPS_SCRIPT_TOKEN}, timeout=20)
        data = r.json()
        if data.get("ok"):
            return data.get("data", {}), ""
        return None, data.get("error", "알 수 없는 오류")
    except Exception as e:
        return None, str(e)


# ---------------- 세션 초기화 ----------------
if 'authenticated' not in ss: ss.authenticated = False
if 'page' not in ss:
    ss.page = 'main'
    ss.score = 0
    ss.current_q = 0
    ss.incorrect_list = []
    ss.review_mode = False
if 'selected_grade' not in ss: ss.selected_grade = GRADES[0]


def start_session(word_list, is_review=False):
    """연습 모드 시작 (기존 그대로)"""
    ss.test_words = word_list
    ss.current_q = 0
    ss.review_mode = is_review
    ss.feedback = False
    if 'current_opts' in ss: del ss.current_opts
    if not is_review:
        ss.score = 0
        ss.incorrect_list = []
    ss.page = 'test'


def start_exam(grade, words):
    """실전 시험 시작"""
    ss.exam_grade = grade
    ss.exam_words = random.sample(list(words.keys()), EXAM_TOTAL)
    ss.exam_q = 0
    ss.exam_correct = 0
    ss.exam_wrong = 0
    ss.exam_wrong_list = []
    ss.exam_opts = None
    ss.exam_opts_q = -1
    ss.exam_q_start = None
    ss.exam_saved = False
    ss.exam_pass_time = None
    ss.exam_balloons = False
    ss.page = 'exam'


def exam_record(correct, word):
    """한 문제 결과 기록 → 다음 문제로 / 종료 판정"""
    if correct:
        ss.exam_correct += 1
    else:
        ss.exam_wrong += 1
        ss.exam_wrong_list.append(word)
    ss.exam_q += 1
    ss.exam_opts = None

    if ss.exam_wrong > EXAM_MAX_WRONG:          # 11개째 오답 → 즉시 탈락
        ss.page = 'exam_fail'
        ss.show_fail_dialog = True
    elif ss.exam_q >= len(ss.exam_words):       # 50문제 끝
        if ss.exam_correct >= EXAM_PASS:
            ss.page = 'exam_pass'
            ss.exam_pass_time = now_kst_str()
        else:
            ss.page = 'exam_fail'
            ss.show_fail_dialog = True


# =====================================================================
# 1. 보안 게이트
# =====================================================================
if not ss.authenticated:
    st.markdown("<div style='margin-top:100px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-family:\"Noto Serif KR\";'>🔒 보람T 어휘 훈련소 입장</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        pwd = st.text_input("현장 암호를 입력하세요", type="password")
        if st.button("🚪 입장하기") or (pwd == SECRET_PASSWORD):
            if pwd == SECRET_PASSWORD:
                ss.authenticated = True
                st.rerun()
            elif pwd:
                st.error("❌ 암호가 틀렸습니다!")
    st.stop()


# =====================================================================
# 2. 메인 메뉴 (학년 선택 → 연습 / 시험)
# =====================================================================
if ss.page == 'main':
    st.markdown("<div style='margin-top:50px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='studio-title'>어휘 무한 훈련소</div>", unsafe_allow_html=True)
    st.write("---")
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        default_idx = GRADES.index(ss.selected_grade) if ss.selected_grade in GRADES else 0
        grade = st.selectbox("📚 학년을 선택하세요", GRADES, index=default_idx)
        ss.selected_grade = grade
        words = load_words(SHEET_URLS[grade])
        st.markdown(f"<p style='text-align:center; color:#666; margin-top:15px;'>🍃 등록된 어휘: {len(words)}개</p>", unsafe_allow_html=True)

        if st.button("📖 연습하기", use_container_width=True):
            if len(words) >= 4:
                word_keys = random.sample(list(words.keys()), len(words))
                start_session(word_keys)
                st.rerun()
            else:
                st.error("단어를 불러오지 못했습니다. 잠시 후 다시 시도하세요.")

        if st.button("📝 실전 시험 보기", use_container_width=True):
            if len(words) >= EXAM_TOTAL and len(set(words.values())) >= EXAM_OPTS:
                start_exam(grade, words)
                st.rerun()
            else:
                st.error(f"시험을 보려면 단어가 {EXAM_TOTAL}개 이상 필요합니다.")

    st.markdown(f"""
    <div class='rule-box'>
    <b>📝 실전 시험 규칙</b><br>
    · 단어 {EXAM_TOTAL}개 랜덤 출제, 보기 {EXAM_OPTS}개<br>
    · 문제당 제한시간 {TIME_LIMIT}초 (시간 초과 = 오답)<br>
    · {EXAM_PASS}개 이상 맞히면 <b>합격</b><br>
    · 오답 {EXAM_MAX_WRONG + 1}개가 되는 순간 <b>즉시 탈락</b><br>
    · 몇 번이든 다시 도전할 수 있습니다
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:60px;'></div>", unsafe_allow_html=True)
    with st.expander("🔐 관리자"):
        apw = st.text_input("관리자 암호", type="password", key="admin_pw")
        if st.button("명단 보기"):
            if apw == ADMIN_PASSWORD:
                ss.page = 'admin'
                st.rerun()
            else:
                st.error("❌ 암호가 틀렸습니다!")


# =====================================================================
# 3. 연습 화면 (기존 그대로, 보기 6개)
# =====================================================================
elif ss.page == 'test':
    words = load_words(SHEET_URLS[ss.selected_grade])
    word = ss.test_words[ss.current_q]
    ans = words.get(word, "")

    if 'current_opts' not in ss or ss.get('last_q_idx') != ss.current_q:
        ss.current_opts = make_options(words, ans, PRACTICE_OPTS)
        ss.last_q_idx = ss.current_q

    if ss.review_mode:
        st.markdown("<div style='text-align:center; color:#e63946; font-size:0.8rem; font-weight:bold; margin-bottom:10px;'>🔥 오답 정복 모드 진행 중 🔥</div>", unsafe_allow_html=True)

    st.markdown(f"<p style='text-align:center; color:#888; font-size:0.9rem;'>[{ss.selected_grade} 연습] {ss.current_q+1} / {len(ss.test_words)}</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='word-canvas'>{word}</div>", unsafe_allow_html=True)

    if ss.get('feedback', False):
        if ss.is_correct:
            st.markdown("<p style='text-align:center; color:#1a1a1a; font-weight:600;'>🎯 정답입니다!</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='text-align:center; color:#e63946;'>⚠️ 오답! 정답은: <b>{ss.ans}</b></p>", unsafe_allow_html=True)

        if st.button("다음 문제 ➡️", use_container_width=True):
            ss.feedback = False
            ss.current_q += 1
            if ss.current_q >= len(ss.test_words): ss.page = 'result'
            st.rerun()
    else:
        opts = ss.current_opts
        cols = st.columns(2)
        for i, opt in enumerate(opts):
            if cols[i % 2].button(opt, key=f"btn_{i}", use_container_width=True):
                ss.feedback = True
                ss.ans = ans
                if opt == ans:
                    if not ss.review_mode: ss.score += 1
                    ss.is_correct = True
                else:
                    ss.is_correct = False
                    if word not in ss.incorrect_list: ss.incorrect_list.append(word)
                st.rerun()

    # 하단 오답 서랍 및 재시험 버튼
    if ss.incorrect_list:
        st.write("---")
        with st.expander(f"📝 현재까지 틀린 단어 ({len(ss.incorrect_list)}개) 확인하기"):
            if st.button("🔥 지금 바로 틀린 단어만 재시험 보기", use_container_width=True):
                review_words = list(ss.incorrect_list)
                ss.incorrect_list = []
                start_session(review_words, is_review=True)
                st.rerun()
            error_data = [{"단어": w, "뜻": words.get(w, "")} for w in ss.incorrect_list]
            st.table(error_data)

    st.write("")
    if st.button("🏠 메인으로", key="practice_home"):
        ss.page = 'main'
        ss.review_mode = False
        st.rerun()


# =====================================================================
# 4. 연습 결과 화면 (기존 그대로)
# =====================================================================
elif ss.page == 'result':
    st.markdown("<div style='margin-top:50px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='studio-title'>🎊 연습 완료 🎊</div>", unsafe_allow_html=True)
    score_pct = int((ss.score / len(ss.test_words)) * 100) if not ss.review_mode else 100
    if not ss.review_mode:
        st.markdown(f"<h3 style='text-align:center; font-family:\"Noto Serif KR\"; font-size:3rem;'>{score_pct}%</h3>", unsafe_allow_html=True)
    st.write("---")
    if ss.incorrect_list:
        st.subheader("📝 최종 오답 리스트")
        words_dict = load_words(SHEET_URLS[ss.selected_grade])
        error_data = [{"단어": w, "뜻": words_dict.get(w, "")} for w in ss.incorrect_list]
        st.table(error_data)
        if st.button("🔥 틀린 단어만 다시 풀기", use_container_width=True):
            review_words = list(ss.incorrect_list)
            ss.incorrect_list = []
            start_session(review_words, is_review=True)
            st.rerun()
    else:
        st.success("✨ 모든 어휘를 마스터했습니다!")
    if st.button("🔄 메인 메뉴로 돌아가기", use_container_width=True):
        ss.page = 'main'
        ss.review_mode = False
        st.rerun()


# =====================================================================
# 5. 실전 시험 화면 (0.5초마다 타이머 갱신)
# =====================================================================
elif ss.page == 'exam':

    @st.fragment(run_every=0.5)
    def exam_screen():
        if ss.page != 'exam':
            return
        words = load_words(SHEET_URLS[ss.exam_grade])
        q = ss.exam_q
        word = ss.exam_words[q]
        ans = words.get(word, "")

        # 새 문제면 보기 8개 생성 + 시작 시각 기록
        if ss.exam_opts is None or ss.exam_opts_q != q:
            ss.exam_opts = make_options(words, ans, EXAM_OPTS)
            ss.exam_opts_q = q
            ss.exam_q_start = time.time()

        elapsed = time.time() - ss.exam_q_start

        # 시간 초과 → 오답 처리 후 다음 문제
        if elapsed > TIME_LIMIT + TIME_GRACE:
            exam_record(False, word)
            st.rerun()

        remain = max(0, math.ceil(TIME_LIMIT - elapsed))
        wrong_cls = "exam-box danger" if ss.exam_wrong >= EXAM_MAX_WRONG - 2 else "exam-box"
        time_cls = "exam-box danger" if remain <= 1 else "exam-box"

        st.markdown(f"<p style='text-align:center; color:#e63946; font-size:0.8rem; font-weight:bold; margin-bottom:6px;'>📝 {ss.exam_grade} 실전 시험</p>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='exam-bar'>
            <div class='exam-box'>진행<b>{q + 1} / {len(ss.exam_words)}</b></div>
            <div class='{time_cls}'>남은 시간<b>{remain}초</b></div>
            <div class='{wrong_cls}'>오답<b>{ss.exam_wrong} / {EXAM_MAX_WRONG}</b></div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(max(0.0, min(1.0, 1 - elapsed / TIME_LIMIT)))
        st.markdown(f"<div class='word-canvas-exam'>{word}</div>", unsafe_allow_html=True)

        cols = st.columns(2)
        for i, opt in enumerate(ss.exam_opts):
            if cols[i % 2].button(opt, key=f"ex_{q}_{i}", use_container_width=True):
                exam_record(opt == ans, word)
                st.rerun()

    exam_screen()


# =====================================================================
# 6. 시험 탈락
# =====================================================================
elif ss.page == 'exam_fail':

    @st.dialog("❌ 탈락")
    def fail_dialog():
        st.markdown(f"### 오답이 {EXAM_MAX_WRONG + 1}개가 되어 시험이 종료되었습니다.")
        st.write(f"맞힌 개수: **{ss.exam_correct}개** / 푼 문제: {ss.exam_q}개")
        st.write("연습으로 실력을 다지고 다시 도전하세요! 💪")
        if st.button("확인", use_container_width=True):
            st.rerun()

    if ss.pop('show_fail_dialog', False):
        fail_dialog()

    st.markdown("<div style='margin-top:50px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='studio-title'>❌ 탈락</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#666;'>{ss.exam_grade} 실전 시험 · 맞힌 개수 {ss.exam_correct}개 · 오답 {ss.exam_wrong}개</p>", unsafe_allow_html=True)
    st.write("---")

    if ss.exam_wrong_list:
        st.subheader("📝 이번 시험 오답")
        words_dict = load_words(SHEET_URLS[ss.exam_grade])
        st.table([{"단어": w, "뜻": words_dict.get(w, "")} for w in ss.exam_wrong_list])

    c1, c2 = st.columns(2)
    if c1.button("🔁 다시 도전", use_container_width=True):
        words = load_words(SHEET_URLS[ss.exam_grade])
        start_exam(ss.exam_grade, words)
        st.rerun()
    if c2.button("📖 연습하러 가기", use_container_width=True):
        ss.selected_grade = ss.exam_grade
        words = load_words(SHEET_URLS[ss.exam_grade])
        start_session(random.sample(list(words.keys()), len(words)))
        st.rerun()
    if st.button("🏠 메인으로", use_container_width=True):
        ss.page = 'main'
        st.rerun()


# =====================================================================
# 7. 시험 합격 → 이름 등록
# =====================================================================
elif ss.page == 'exam_pass':
    if not ss.get('exam_balloons'):
        st.balloons()
        ss.exam_balloons = True

    st.markdown("<div style='margin-top:50px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='studio-title'>🎉 합격을 축하합니다! 🎉</div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center; font-family:\"Noto Serif KR\"; font-size:2.5rem;'>{ss.exam_correct} / {EXAM_TOTAL}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:#666;'>{ss.exam_grade} 실전 시험 · 합격 시각 {ss.exam_pass_time}</p>", unsafe_allow_html=True)
    st.write("---")

    if not ss.exam_saved:
        st.markdown("**✍️ 합격자 명단에 이름을 등록하세요 (한글)**")
        name = st.text_input("이름", placeholder="예: 홍길동", max_chars=10)
        if st.button("✅ 명단에 등록하기", use_container_width=True):
            name = name.strip()
            if not re.fullmatch(r"[가-힣]{2,10}", name):
                st.error("이름은 한글 2~10자로, 띄어쓰기 없이 입력하세요.")
            else:
                with st.spinner("등록 중..."):
                    ok, err = save_passer(ss.exam_grade, name,
                                          f"{ss.exam_correct}/{EXAM_TOTAL}", ss.exam_pass_time)
                if ok:
                    ss.exam_saved = True
                    ss.exam_saved_name = name
                    st.rerun()
                else:
                    st.error("등록에 실패했습니다. 다시 한 번 눌러주세요. 계속 안 되면 선생님께 알려주세요.")
    else:
        st.success(f"✨ {ss.exam_saved_name} 님, 합격자 명단에 등록되었습니다!")

    if ss.exam_wrong_list:
        with st.expander(f"📝 이번 시험 오답 ({len(ss.exam_wrong_list)}개)"):
            words_dict = load_words(SHEET_URLS[ss.exam_grade])
            st.table([{"단어": w, "뜻": words_dict.get(w, "")} for w in ss.exam_wrong_list])

    if st.button("🏠 메인으로", use_container_width=True):
        ss.page = 'main'
        st.rerun()


# =====================================================================
# 8. 관리자: 합격자 명단
# =====================================================================
elif ss.page == 'admin':
    st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='studio-title'>🔐 합격자 명단</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    refresh = c1.button("🔄 새로고침", use_container_width=True)
    if c2.button("🏠 메인으로", use_container_width=True):
        ss.page = 'main'
        st.rerun()

    with st.spinner("명단 불러오는 중..."):
        data, err = load_passers()

    if data is None:
        st.error(f"명단을 불러오지 못했습니다: {err}")
    else:
        tabs = st.tabs([f"{g} ({len(data.get(g, []))}명)" for g in GRADES])
        for tab, g in zip(tabs, GRADES):
            with tab:
                rows = data.get(g, [])
                if not rows:
                    st.info("아직 합격자가 없습니다.")
                    continue
                df = pd.DataFrame([r[:3] for r in rows], columns=["이름", "합격 일시(한국시간)", "점수"])
                df = df.sort_values(["이름", "합격 일시(한국시간)"]).reset_index(drop=True)
                df.index = df.index + 1
                st.dataframe(df, use_container_width=True)
