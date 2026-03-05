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
    
    # 공통 분석 로직 (5단계 리스크 세분화 적용)
    SYSTEM_PROMPT = (
        "너는 글로벌 정책 결정관이자 언어학 전문가야. 아래 5단계 리스크 가이드를 엄격히 적용해.\n\n"
        "1. Level 5 (90~100점): 원색적 욕설 원형, 반인륜적 고인 모독, 극도의 혐오 표현.\n"
        "2. Level 4 (80~89점): 특정 집단/성별에 대한 강한 혐오 및 비하 밈.\n"
        "3. Level 3 (60~79점): 욕설의 변형어(순화어) 및 타인을 강하게 공격하는 비속어.\n"
        "4. Level 2 (40~59점): '머저리' 등 지능이나 행동을 낮잡아 보는 경미한 비하 표현.\n"
        "5. Level 1 (0~39점): '비아냥', '가즈아' 등 일상적 유머, 태도 묘사, 단순 감탄사.\n\n"
        "분석 시 '실제 타격감'과 '모욕의 강도'를 최우선으로 하고, 한자 풀이 등 사전적 정의에 매몰되지 마."
    )

    def analyze_word(word):
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
            # 동적 보정 로직
            score = res.get('부정점수', 0)
            bg = res.get('논란의배경', '')
            if any(k in bg for k in ["원색적", "직설적"]) and score < 95: score = 95
            if any(k in bg for k in ["낮잡아", "경미한"]) and score > 60: score = 50
            if any(k in bg for k in ["태도", "비꼬는", "유머"]) and score > 40: score = 25
            res['부정점수'] = score
            return res
        except: return None

    def display_result(word, res):
        """기존 UI 스타일로 결과 출력"""
        score = res.get('부정점수', 0)
        st.divider()
        st.success(f"'{word}' 분석 완료")
        
        c1, c2 = st.columns([1, 2])
        with c1: st.metric("리스크 점수", f"{score}점")
        with c2: st.subheader(f"🏷️ {res.get('카테고리', '미분류')}")
        
        st.progress(score/100)
        
        st.info(f"📖 **표면적 의미:** \n\n {res.get('표면적의미', '')}")
        if score >= 80:
            st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {res.get('논란의배경', '')}")
        else:
            st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {res.get('논란의배경', '')}")
        st.info(f"⚖️ **정책 판단 근거:** \n\n {res.get('판단근거', '')}")

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["🔍 단일 검토", "📂 CSV 일괄 검토", "🖼️ 이미지 분석"])

    # --- Tab 1: 단일 검토 (이전 UI 복원) ---
    with tab1:
        word_input = st.text_input("분석할 단어 입력:", key="single_input")
        if st.button("분석 실행", key="single_btn"):
            with st.spinner('심층 분석 중...'):
                res = analyze_word(word_input)
                if res: display_result(word_input, res)

    # --- Tab 2: CSV 일괄 검토 ---
    with tab2:
        uploaded_csv = st.file_uploader("CSV 파일 업로드", type="csv")
        if uploaded_csv:
            df = pd.read_csv(uploaded_csv)
            col = st.selectbox("분석할 열 선택", df.columns)
            if st.button("일괄 분석 시작"):
                all_results = []
                bar = st.progress(0)
                for i, row in df.iterrows():
                    word = str(row[col])
                    res = analyze_word(word)
                    if res:
                        res['입력 단어'] = word
                        all_results.append(res)
                    bar.progress((i+1)/len(df))
                
                final_df = pd.DataFrame(all_results)
                st.dataframe(final_df)
                st.download_button("결과 CSV 다운로드", final_df.to_csv(index=False), "result.csv")

    # --- Tab 3: 이미지 분석 ---
    with tab3:
        uploaded_img = st.file_uploader("이미지 업로드", type=["jpg", "png", "jpeg"])
        if uploaded_img:
            img = Image.open(uploaded_img)
            st.image(img, width=400)
            if st.button("이미지 텍스트 분석"):
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                with st.spinner('이미지 내 텍스트 추출 및 분석 중...'):
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": [
                                {"type": "text", "text": "이미지 속 텍스트를 추출하고, 위반 소지가 있는 단어들을 분석하여 JSON 리스트로 줘."},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                            ]}
                        ],
                        response_format={ "type": "json_object" }
                    )
                    img_data = json.loads(response.choices[0].message.content)
                    # 리스트 형태의 결과물을 기존 UI로 반복 출력
                    for item in img_data.get('분석결과', []):
                        display_result(item.get('단어'), item)

else:
    st.info("API 키를 입력해주세요.")
