import streamlit as st
import pandas as pd
from openai import OpenAI
import json
import base64
from io import BytesIO
from PIL import Image

# 1. 페이지 설정 및 스타일
st.set_page_config(page_title="Global Vibe Guard Pro Max", page_icon="🌍", layout="wide")
st.title("🌍 글로벌 금칙어 정책 분석기 (Pro Max)")

# 2. API 키 설정
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key 설정", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    
    # 공통 시스템 프롬프트 (기존 5단계 로직 유지)
    SYSTEM_PROMPT = (
        "너는 글로벌 정책 결정관이자 언어학 전문가야. 아래 5단계 리스크 가이드를 엄격히 적용해.\n\n"
        "1. Level 5 (90~100점): 원색적 욕설 원형, 반인륜적 고인 모독, 극도의 혐오 표현.\n"
        "2. Level 4 (80~89점): 특정 집단/성별에 대한 강한 혐오 및 비하 밈.\n"
        "3. Level 3 (60~79점): 욕설의 변형어(순화어) 및 타인을 강하게 공격하는 비속어.\n"
        "4. Level 4 (40~59점): '머저리', '등신' 등 지능이나 행동을 낮잡아 보는 경미한 비하 표현.\n"
        "5. Level 5 (0~39점): '비아냥', '메롱', '가즈아' 등 일상적 유머, 태도 묘사, 단순 감탄사.\n\n"
        "분석 시 '실제 타격감'과 '모욕의 강도'를 최우선으로 하고, 한자 풀이 등 사전적 정의에 매몰되지 마."
    )

    def analyze_word(word):
        """단일 단어 분석 함수 (보정 로직 포함)"""
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
            result = json.loads(response.choices[0].message.content)
            # 동적 보정 레이어
            if any(k in result['논란의배경'] for k in ["원색적", "직설적"]): result['부정점수'] = max(result['부정점수'], 95)
            if any(k in result['논란의배경'] for k in ["낮잡아", "경미한"]): result['부정점수'] = 50
            if any(k in result['논란의배경'] for k in ["태도", "비꼬는", "유머"]): result['부정점수'] = min(result['부정점수'], 30)
            return result
        except: return None

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["🔍 단일 검토", "📂 CSV 일괄 검토", "🖼️ 이미지 분석"])

    # --- Tab 1: 단일 검토 (기존 기능) ---
    with tab1:
        word_input = st.text_input("분석할 단어 입력:", placeholder="예: 머저리")
        if st.button("분석 실행", key="single"):
            with st.spinner('분석 중...'):
                res = analyze_word(word_input)
                if res:
                    st.metric("리스크 점수", f"{res['부정점수']}점")
                    st.json(res)

    # --- Tab 2: CSV 일괄 검토 (추가 기능) ---
    with tab2:
        st.info("검토할 단어들이 들어있는 CSV 파일을 업로드하세요. (첫 번째 열을 단어로 인식합니다)")
        uploaded_csv = st.file_uploader("CSV 파일 선택", type="csv")
        if uploaded_csv:
            df = pd.read_csv(uploaded_csv)
            col_name = st.selectbox("분석할 컬럼 선택:", df.columns)
            if st.button("일괄 검토 시작"):
                results = []
                progress = st.progress(0)
                for i, row in df.iterrows():
                    word = str(row[col_name])
                    res = analyze_word(word)
                    if res:
                        res['단어'] = word
                        results.append(res)
                    progress.progress((i + 1) / len(df))
                
                res_df = pd.DataFrame(results)
                st.dataframe(res_df)
                st.download_button("결과 다운로드", res_df.to_csv(index=False), "analysis_result.csv")

    # --- Tab 3: 이미지 분석 (추가 기능) ---
    with tab3:
        st.info("텍스트가 포함된 이미지를 업로드하면 Vision AI가 텍스트를 추출하여 정책을 검토합니다.")
        uploaded_img = st.file_uploader("이미지 파일 선택", type=["png", "jpg", "jpeg"])
        if uploaded_img:
            img = Image.open(uploaded_img)
            st.image(img, caption="업로드된 이미지", width=400)
            
            if st.button("이미지 내 텍스트 분석"):
                with st.spinner('이미지 분석 및 정책 검토 중...'):
                    # 이미지 인코딩
                    buffered = BytesIO()
                    img.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Vision API 호출
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT + "\n이미지 속 텍스트를 모두 추출하고, 그 중 정책 위반 소지가 있는 단어들을 리스트업하여 분석해줘."},
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "이 이미지 내의 모든 텍스트를 분석하여 JSON 배열 형태로 반환해줘. 각 객체는 단어, 부정점수, 카테고리, 판단근거를 포함해야 해."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                                ]
                            }
                        ],
                        response_format={ "type": "json_object" }
                    )
                    img_res = json.loads(response.choices[0].message.content)
                    st.write("### 📸 이미지 분석 결과")
                    st.json(img_res)
else:
    st.info("API 키를 입력해주세요.")
