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
    
    # [5단계 점수 체계 및 상세 정보 가이드]
    SYSTEM_PROMPT = (
        "너는 글로벌 정책 결정관이자 언어 전문가야. 아래 수칙을 절대 준수해.\n\n"
        "1. Level 5 (90-100점): '좆까', '씨발' 등 원색적 욕설 및 중대 범죄 사실.\n"
        "2. Level 4 (80-89점): 강한 비하/조롱 의도가 담긴 혐오 밈.\n"
        "3. Level 3 (60-79점): 비속어 변형(염병 등) 및 공격적 유행어.\n"
        "4. Level 2 (40-59점): 경미한 비하 표현.\n"
        "5. Level 1 (0-39점): 일상적 유머 및 단순 수치 과장 (오조오억 등)."
    )

    def analyze_word(word):
        try:
            # [물리적 보정] 앱스타인 고정
            if "앱스타인" in word.replace(" ", ""):
                return {"언어": "한국어", "카테고리": "범죄 이슈", "부정점수": 92, "표면적의미": "성범죄 연루자", "논란의배경": "중대 범죄 사실", "판단근거": "정책적 관리 필요"}

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"'{word}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                ],
                response_format={ "type": "json_object" },
                temperature=0
            )
            return json.loads(response.choices[0].message.content)
        except: return None

    def display_result(word, res):
        score = res.get('부정점수', 0)
        st.divider()
        st.success(f"'{word}' 분석 완료")
        c1, c2 = st.columns([1, 2])
        with c1: st.metric("리스크 점수", f"{score}점")
        with c2: st.subheader(f"🏷️ {res.get('카테고리', '미분류')}")
        st.progress(score/100)
        st.info(f"📖 **표면적 의미:** \n\n {res.get('표면적의미', '')}")
        if score >= 90: st.error(f"🚨 **상세 맥락:** \n\n {res.get('논란의배경', '')}")
        else: st.warning(f"⚠️ **상세 맥락:** \n\n {res.get('논란의배경', '')}")
        st.info(f"⚖️ **판단 근거:** \n\n {res.get('판단근거', '')}")

    tab1, tab2, tab3 = st.tabs(["🔍 단일 검토", "📂 CSV 일괄 검토", "🖼️ 이미지 분석"])

    # --- Tab 3: 이미지 분석 (OCR 정밀도 및 단어 직통 분석) ---
    with tab3:
        uploaded_img = st.file_uploader("이미지 업로드", type=["jpg", "png", "jpeg"], key="img_tab")
        if uploaded_img:
            img = Image.open(uploaded_img)
            st.image(img, width=400)
            if st.button("이미지 텍스트 분석"):
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                with st.spinner('분석 중...'):
                    # Vision AI에게 글자 판독 정밀도 극대화 지시
                    vision_res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "user", "content": [
                                {"type": "text", "text": "이미지 속 글자를 정확히 읽어줘. 특히 '좆'의 'ㅗ'와 '죳'의 'ㅛ'를 엄격히 구분해. 이미지에 적힌 그대로 JSON {'words': []} 배열로 추출해."},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                            ]}
                        ],
                        response_format={ "type": "json_object" }
                    )
                    try:
                        extracted_list = json.loads(vision_res.choices[0].message.content).get('words', [])
                        for word in extracted_list:
                            res = analyze_word(word) # 추출된 그대로 분석 엔진에 전달
                            if res: display_result(word, res)
                    except: st.error("이미지 처리 중 오류 발생")

    # (단일/CSV 탭 로직은 이전과 동일하게 유지)
