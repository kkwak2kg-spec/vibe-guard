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
    
    # [사용자 피드백 반영] 고위험군 및 5단계 판정 수칙
    SYSTEM_PROMPT = (
        "너는 글로벌 정책 결정관이자 언어학 전문가야. 아래 수칙을 절대 준수해.\n\n"
        "### [1. 고위험군 사실 관계 복원]\n"
        "- '앱스타인': 성범죄 관련 중대 범죄자임. 구체적 사건 맥락과 함께 Level 5(92점 이상) 부여.\n"
        "- '씨발': 원형 욕설은 반드시 95점 이상 부여.\n"
        "- '염병', '니미럴': 타인을 비하하거나 저주하는 강한 비속어이므로 Level 3~4(75~80점) 부여.\n\n"
        "### [2. 5단계 리스크 판정 가이드]\n"
        "1. Level 5 (90-100점): 직설적 욕설, 중대 범죄 사건, 반인륜적 모독.\n"
        "2. Level 4 (80-89점): 강한 비하/조롱 의도가 담긴 혐오 밈.\n"
        "3. Level 3 (60-79점): 비속어 변형 및 공격적 유행어.\n"
        "4. Level 2 (40-59점): 머저리 등 경미한 비하 표현.\n"
        "5. Level 1 (0-39점): 일상적 유머 및 단순 수치 과장 (오조오억 등)."
    )

    def analyze_word(word):
        """단어 정밀 분석 통합 엔진"""
        try:
            # [물리적 보정] 앱스타인 점수 하락 원천 봉쇄
            if "앱스타인" in word.replace(" ", ""):
                return {
                    "언어": "한국어", "카테고리": "고위험 사회적 이슈/범죄", "부정점수": 92,
                    "표면적의미": "실제 아동 성범죄 및 인신매매 사건 연루자 제프리 앱스타인.",
                    "논란의배경": "대규모 성착취 네트워크를 운영한 혐의로 기소된 중대 범죄자이며, 이를 희화화하는 맥락은 매우 위험함.",
                    "판단근거": "반인륜적 범죄 사실과 연관된 고유 명사로 고위험 금칙어 관리 필요."
                }

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
            # 욕설 보정
            if any(k in res.get('논란의배경', '') for k in ["원색적 욕설", "직설적 욕설"]):
                res['부정점수'] = max(res.get('부정점수', 0), 95)
            return res
        except: return None

    def display_result(word, res):
        """사용자 맞춤형 카드 UI"""
        score = res.get('부정점수', 0)
        st.divider()
        st.success(f"'{word}' 분석 완료")
        c1, c2 = st.columns([1, 2])
        with c1: st.metric("리스크 점수", f"{score}점")
        with c2: st.subheader(f"🏷️ {res.get('카테고리', '미분류')}")
        st.progress(score/100)
        st.info(f"📖 **표면적 의미:** \n\n {res.get('표면적의미', '')}")
        if score >= 90: st.error(f"🚨 **상세 맥락 및 배경:** \n\n {res.get('논란의배경', '')}")
        else: st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {res.get('논란의배경', '')}")
        st.info(f"⚖️ **정책 판단 근거:** \n\n {res.get('판단근거', '')}")

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["🔍 단일 검토", "📂 CSV 일괄 검토", "🖼️ 이미지 분석"])

    # --- Tab 1: 단일 검토 ---
    with tab1:
        word_input = st.text_input("분석할 단어 입력:", key="single")
        if st.button("분석 실행", key="btn_single"):
            with st.spinner('분석 중...'):
                res = analyze_word(word_input)
                if res: display_result(word_input, res)

    # --- Tab 2: CSV 일괄 검토 (복구 완료) ---
    with tab2:
        st.info("CSV 파일을 업로드하여 대량의 단어를 한 번에 분석하세요.")
        uploaded_csv = st.file_uploader("CSV 파일 업로드", type="csv", key="csv_upload")
        if uploaded_csv:
            df = pd.read_csv(uploaded_csv)
            col = st.selectbox("분석할 열 선택", df.columns)
            if st.button("일괄 분석 시작", key="btn_csv"):
                results = []
                bar = st.progress(0)
                for i, word in enumerate(df[col]):
                    res = analyze_word(str(word))
                    if res:
                        res['입력 단어'] = word
                        results.append(res)
                    bar.progress((i+1)/len(df))
                
                res_df = pd.DataFrame(results)
                st.dataframe(res_df)
                st.download_button("결과 CSV 다운로드", res_df.to_csv(index=False), "analysis_results.csv")

    # --- Tab 3: 이미지 분석 ---
    with tab3:
        uploaded_img = st.file_uploader("이미지 업로드", type=["jpg", "png", "jpeg"], key="img_upload")
        if uploaded_img:
            img = Image.open(uploaded_img)
            st.image(img, width=400)
            if st.button("이미지 텍스트 분석", key="btn_img"):
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                with st.spinner('분석 중...'):
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "user", "content": [
                                {"type": "text", "text": "이미지 속 글자를 정밀 판독해줘. '염병' 등을 혼동하지 말고 정확히 JSON {'words': []} 리스트로 추출해."},
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
