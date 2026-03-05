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
    
    # [5단계 점수 체계] 시스템 프롬프트
    SYSTEM_PROMPT = (
        "너는 글로벌 정책 결정관이자 온라인 커뮤니티 언어 전문가야. 아래 수칙에 따라 단어를 정밀 분석해.\n\n"
        "### [5단계 리스크 판정 가이드]\n"
        "1. Level 5 (90-100점): 원색적 욕설 원형, 반인륜적 모독, 중대 범죄 사실.\n"
        "2. Level 4 (80-89점): 명확한 비하/조롱 의도가 담긴 혐오 밈.\n"
        "3. Level 3 (60-79점): 강한 비속어 및 그 변형(염병 등), 공격적인 유행어.\n"
        "4. Level 2 (40-59점): 머저리 등 경미한 비하 표현.\n"
        "5. Level 1 (0-39점): 단순 인터넷 밈, 일상어 변형 (오조오억 등 포함)."
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
            
            # 고위험군 보정 로직
            score = res.get('부정점수', 0)
            bg = res.get('논란의배경', '')
            if any(k in bg for k in ["원색적 욕설", "직설적 욕설"]): score = max(score, 95)
            if any(k in bg for k in ["성범죄", "범죄 사실", "연루"]): score = max(score, 92)
            res['부정점수'] = score
            return res
        except: return None

    def display_result(word, res):
        """사용자 맞춤 카드 UI"""
        score = res.get('부정점수', 0)
        st.divider()
        st.success(f"'{word}' 분석 완료")
        
        c1, c2 = st.columns([1, 2])
        with c1: st.metric("리스크 점수", f"{score}점")
        with c2: st.subheader(f"🏷️ {res.get('카테고리', '미분류')}")
        
        st.progress(score/100)
        st.info(f"📖 **표면적 의미:** \n\n {res.get('표면적의미', '')}")
        
        if score >= 85:
            st.error(f"🚨 **상세 맥락 및 배경:** \n\n {res.get('논란의배경', '')}")
        elif score >= 60:
            st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {res.get('논란의배경', '')}")
        else:
            st.success(f"✅ **상세 맥락 및 배경:** \n\n {res.get('논란의배경', '')}")
            
        st.info(f"⚖️ **정책 판단 근거:** \n\n {res.get('판단근거', '')}")

    # 탭 메뉴 구성
    tab1, tab2, tab3 = st.tabs(["🔍 단일 검토", "📂 CSV 일괄 검토", "🖼️ 이미지 분석"])

    # --- Tab 1: 단일 검토 ---
    with tab1:
        word_input = st.text_input("분석할 단어 입력:", key="single")
        if st.button("분석 실행", key="btn_single"):
            with st.spinner('분석 중...'):
                res = analyze_word(word_input)
                if res: display_result(word_input, res)

    # --- Tab 2: CSV 일괄 검토 ---
    with tab2:
        uploaded_csv = st.file_uploader("CSV 파일 업로드", type="csv")
        if uploaded_csv:
            df = pd.read_csv(uploaded_csv)
            col = st.selectbox("분석할 열 선택", df.columns)
            if st.button("일괄 분석 시작"):
                results = []
                bar = st.progress(0)
                for i, row in df.iterrows():
                    word = str(row[col])
                    res = analyze_word(word)
                    if res:
                        res['입력 단어'] = word
                        results.append(res)
                    bar.progress((i+1)/len(df))
                st.dataframe(pd.DataFrame(results))
                st.download_button("결과 CSV 다운로드", pd.DataFrame(results).to_csv(index=False), "result.csv")

    # --- Tab 3: 이미지 분석 (OCR 오인식 수정 및 추출 텍스트 그대로 분석) ---
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
                    # 1단계: Vision AI가 이미지 속 텍스트 리스트 추출 (판독 정밀도 강화)
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "user", "content": [
                                {"type": "text", "text": "이미지 내 텍스트를 정확히 추출해줘. 특히 '염병'을 '엠병'으로 혼동하지 말고 있는 그대로 읽어줘. 추출된 단어를 JSON 'words' 배열로 줘. 예: {'words': ['염병', '단어']}"},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                            ]}
                        ],
                        response_format={ "type": "json_object" }
                    )
                    try:
                        extracted_content = response.choices[0].message.content
                        extracted_list = json.loads(extracted_content).get('words', [])
                        
                        # 2단계: 추출된 단어별로 정밀 분석 엔진(`analyze_word`)을 실행하여 UI 출력 (추출된 그대로 분석)
                        if not extracted_list:
                            st.warning("추출된 텍스트가 없습니다.")
                        else:
                            for word in extracted_list:
                                res = analyze_word(word) # 이미지에서 추출된 단어 그대로 분석 엔진에 전달
                                if res: display_result(word, res)
                    except Exception as e:
                        st.error(f"데이터 처리 중 오류 발생: {e}")
else:
    st.info("API 키를 입력해주세요.")
