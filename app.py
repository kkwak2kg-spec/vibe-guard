import streamlit as st
import pandas as pd
from openai import OpenAI
import json
import base64
from io import BytesIO
from PIL import Image

# 1. 페이지 설정
st.set_page_config(page_title="Global Vibe Guard Pro", page_icon="🌍", layout="wide")
st.title("🌍 글로벌 금칙어 정책 분석기")

# 2. API 키 설정
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key 설정", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    
    # [사용자님 극찬 기준] 고위험군 범죄 사실 및 욕설 원형 보호 프롬프트
    SYSTEM_PROMPT = (
        "너는 글로벌 정책 결정관이자 사회 문제 전문가야. 아래 수칙을 절대 준수해.\n\n"
        "### [1. 고위험군 사실 관계 복원 - 필수]\n"
        "- '앱스타인'은 단순 밈이나 칭찬이 아님. 실제 아동 성범죄 및 인신매매 사건 연루자임을 명시하고 반드시 Level 5(92점 이상)를 부여해라.\n"
        "- '씨발' 등 원형 욕설은 무조건 95점 이상이다. 70점대는 중대한 오류다.\n\n"
        "### [2. 5단계 리스크 판정 가이드]\n"
        "1. Level 5 (90-100점): 직설적 욕설 원형, 중대 범죄 사건(성범죄 등), 반인륜적 모독.\n"
        "2. Level 4 (80-89점): 강한 비하/조롱 의도가 담긴 혐오 밈 (흉자 등).\n"
        "3. Level 3 (60-79점): 비속어 변형(니미럴, 염병 등) 및 강한 비소어.\n"
        "4. Level 2 (40-59점): 경미한 비하 표현 (머저리 등).\n"
        "5. Level 1 (0-39점): 일상적 유머 및 단순 수치 과장 (오조오억 등)."
    )

    def analyze_word(word):
        """단어 정밀 분석 통합 엔진"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"'{word}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                ],
                response_format={ "type": "json_object" },
                temperature=0
            )
            res = json.loads(response.choices[0].message.content)
            
            # [물리적 보정] 앱스타인 및 원형 욕설 보호
            if "앱스타인" in word:
                res['부정점수'], res['카테고리'] = 92, "중대 사회 범죄 이슈"
            if any(k in res.get('논란의배경', '') for k in ["원색적 욕설", "직설적 욕설"]):
                res['부정점수'] = max(res.get('부정점수', 0), 95)
                
            return res
        except: return None

    def display_result(word, res):
        """사용자님이 만족하신 카드 UI 출력"""
        score = res.get('부정점수', 0)
        st.divider()
        st.success(f"'{word}' 분석 완료")
        c1, c2 = st.columns([1, 2])
        with c1: st.metric("리스크 점수", f"{score}점")
        with c2: st.subheader(f"🏷️ {res.get('카테고리', '미분류')}")
        st.progress(score/100)
        st.info(f"📖 **표면적 의미:** \n\n {res.get('표면적의미', '')}")
        
        # 고위험군은 빨간색 카드로 출력
        if score >= 90:
            st.error(f"🚨 **상세 맥락 및 배경 (구체적 사건 중심):** \n\n {res.get('논란의배경', '')}")
        else:
            st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {res.get('논란의배경', '')}")
        st.info(f"⚖️ **정책 판단 근거:** \n\n {res.get('판단근거', '')}")

    tab1, tab2, tab3 = st.tabs(["🔍 단일 검토", "📂 CSV 일괄 검토", "🖼️ 이미지 분석"])

    with tab1:
        word_input = st.text_input("분석할 단어 입력:", key="single")
        if st.button("분석 실행", key="btn_single"):
            with st.spinner('분석 중...'):
                res = analyze_word(word_input)
                if res: display_result(word_input, res)

    with tab3:
        uploaded_img = st.file_uploader("이미지 업로드", type=["jpg", "png", "jpeg"])
        if uploaded_img:
            img = Image.open(uploaded_img)
            st.image(img, width=400)
            if st.button("이미지 텍스트 분석"):
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                with st.spinner('분석 중...'):
                    # Vision AI에게 글자 하나하나 정밀하게 읽으라고 지시 (환각 방지)
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "user", "content": [
                                {"type": "text", "text": "이미지 속 글자를 왜곡 없이 정확히 읽어줘. 특히 '니미럴' 같은 단어를 다른 단어로 착각하지 마. 추출된 단어를 JSON 'words' 배열로 줘."},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                            ]}
                        ],
                        response_format={ "type": "json_object" }
                    )
                    extracted = json.loads(response.choices[0].message.content).get('words', [])
                    for word in extracted:
                        res = analyze_word(word)
                        if res: display_result(word, res)
else:
    st.info("API 키를 입력해주세요.")
