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
    
    # [사용자 극찬] 5단계 점수 체계 및 상세 정보 조회 프롬프트
    SYSTEM_PROMPT = (
        "너는 글로벌 정책 결정관이자 온라인 커뮤니티 언어 전문가야.\n\n"
        "### [중요 수칙]\n"
        "- 사전적 풀이보다 '실제 커뮤니티 사용 맥락'을 상세히 분석해라.\n"
        "- 원형 욕설(씨발 등)은 95점 이상, 사회적 혐오 밈은 80점 이상으로 엄격히 판정해라.\n\n"
        "### [5단계 리스크 판정 기준]\n"
        "1. Level 5 (90-100점): 원색적 욕설 원형, 반인륜적 모독, 중대 범죄 사실.\n"
        "2. Level 4 (80-89점): 명확한 비하/조롱 의도가 담긴 혐오 밈.\n"
        "3. Level 3 (60-79점): 강한 비속어 변형, 공격적인 유행어.\n"
        "4. Level 2 (40-59점): 머저리 등 경미한 비하 표현.\n"
        "5. Level 1 (0-39점): 단순 인터넷 밈, 일상어 변형."
    )

    def analyze_word(word):
        """단어 정밀 분석 엔진"""
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
            # 보정 로직 적용
            if any(k in res.get('논란의배경', '') for k in ["원색적 욕설", "직설적 욕설"]):
                res['부정점수'] = max(res.get('부정점수', 0), 95)
            return res
        except: return None

    def display_result(word, res):
        """기존 카드 UI 출력"""
        score = res.get('부정점수', 0)
        st.divider()
        st.success(f"'{word}' 분석 완료")
        c1, c2 = st.columns([1, 2])
        with c1: st.metric("리스크 점수", f"{score}점")
        with c2: st.subheader(f"🏷️ {res.get('카테고리', '미분류')}")
        st.progress(score/100)
        st.info(f"📖 **표면적 의미:** \n\n {res.get('표면적의미', '')}")
        if score >= 80:
            st.error(f"🚨 **상세 맥락 및 배경:** \n\n {res.get('논란의배경', '')}")
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

    with tab2:
        uploaded_csv = st.file_uploader("CSV 파일 업로드", type="csv")
        if uploaded_csv:
            df = pd.read_csv(uploaded_csv)
            col = st.selectbox("분석할 열 선택", df.columns)
            if st.button("일괄 분석 시작"):
                results = []
                bar = st.progress(0)
                for i, word in enumerate(df[col]):
                    res = analyze_word(str(word))
                    if res: res['입력 단어'] = word; results.append(res)
                    bar.progress((i+1)/len(df))
                st.dataframe(pd.DataFrame(results))

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
                    # Vision AI 지침 강화: 텍스트 추출 후 각각 분석 수행 지시
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": [
                                {"type": "text", "text": "이미지 속 텍스트(예: '니미럴')를 정확히 추출하고, 추출된 각 단어에 대해 5단계 리스크 기준에 따른 분석 결과를 JSON 배열 '분석결과'로 작성해줘."},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                            ]}
                        ],
                        response_format={ "type": "json_object" }
                    )
                    img_data = json.loads(response.choices[0].message.content)
                    # 추출된 단어별로 상세 리포트 출력
                    for item in img_data.get('분석결과', []):
                        display_result(item.get('단어', '추출단어'), item)
else:
    st.info("API 키를 입력해주세요.")
