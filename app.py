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
    
    # [최종 확정] 5단계 점수 체계 및 상세 정보 조회 가이드
    SYSTEM_PROMPT = (
        "너는 글로벌 정책 결정관이자 온라인 커뮤니티 언어 전문가야. 아래 수칙에 따라 단어를 정밀 분석해.\n\n"
        "### [1. 상세 정보 조회 가이드]\n"
        "- 단어의 사전적 의미보다 '실제 온라인 커뮤니티(디시, 더쿠, 에펨 등)의 사용 맥락'을 상세히 분석해라.\n"
        "- 범죄 사실(앱스타인 등)이나 혐오 유래(흉자 등)는 인터넷 밈이라는 표현 뒤에 숨지 말고 구체적인 팩트를 서술해라.\n\n"
        "### [2. 5단계 리스크 판정 가이드]\n"
        "1. Level 5 (90-100점): 원색적 욕설 원형('씨발', '좆까' 등), 반인륜적 모독, 중대 범죄 사실.\n"
        "2. Level 4 (80-89점): 명확한 비하/조롱 의도가 담긴 혐오 밈.\n"
        "3. Level 3 (60-79점): 강한 비속어 및 그 변형('염병', '니미럴' 등), 공격적인 유행어.\n"
        "4. Level 2 (40-59점): 머저리 등 경미한 비하 표현.\n"
        "5. Level 1 (0-39점): 단순 인터넷 밈('오조오억' 등), 일상어 변형."
    )

    def analyze_word(word):
        """단어 정밀 분석 통합 엔진"""
        try:
            # [물리적 보정] 앱스타인 고득점 및 범죄 맥락 고정
            if "앱스타인" in word.replace(" ", ""):
                return {
                    "언어": "한국어", "카테고리": "고위험 사회적 이슈/범죄", "부정점수": 92,
                    "표면적의미": "실제 아동 성범죄 및 인신매매 사건 연루자 제프리 앱스타인.",
                    "논란의배경": "대규모 성착취 네트워크를 운영한 중대 범죄자이며, 이를 희화화하는 것은 매우 위험함.",
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
            
            # 고위험군 욕설 보정
            score = res.get('부정점수', 0)
            bg = res.get('논란의배경', '')
            if any(k in word for k in ["씨발", "좆까", "느금마"]): score = max(score, 95)
            res['부정점수'] = score
            return res
        except: return None

    def display_result(word, res):
        """복원된 카드 UI 출력 스타일"""
        score = res.get('부정점수', 0)
        st.divider()
        st.success(f"'{word}' 분석 완료")
        
        c1, c2 = st.columns([1, 2])
        with c1: st.metric("리스크 점수", f"{score}점")
        with c2: st.subheader(f"🏷️ {res.get('카테고리', '미분류')}")
        
        st.progress(score/100)
        st.info(f"📖 **표면적 의미:** \n\n {res.get('표면적의미', '')}")
        
        if score >= 90:
            st.error(f"🚨 **상세 맥락 및 배경:** \n\n {res.get('논란의배경', '')}")
        else:
            st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {res.get('논란의배경', '')}")
            
        st.info(f"⚖️ **정책 판단 근거:** \n\n {res.get('판단근거', '')}")

    # 탭 메뉴 구성 (모든 기능 통합)
    tab1, tab2, tab3 = st.tabs(["🔍 단일 검토", "📂 CSV 일괄 검토", "🖼️ 이미지 분석"])

    # --- Tab 1: 단일 검토 (입력창 복구) ---
    with tab1:
        word_input = st.text_input("분석할 단어 입력:", key="single_input")
        if st.button("분석 실행", key="btn_single"):
            if word_input:
                with st.spinner('분석 중...'):
                    res = analyze_word(word_input)
                    if res: display_result(word_input, res)
            else:
                st.warning("단어를 입력해주세요.")

    # --- Tab 2: CSV 일괄 검토 (업로드 기능 복구) ---
    with tab2:
        st.info("CSV 파일을 업로드하여 대량의 단어를 일괄 분석하세요.")
        uploaded_csv = st.file_uploader("CSV 파일 선택", type="csv", key="csv_upload")
        if uploaded_csv:
            df = pd.read_csv(uploaded_csv)
            col = st.selectbox("분석할 컬럼(열) 선택:", df.columns)
            if st.button("일괄 분석 시작", key="btn_csv"):
                results = []
                bar = st.progress(0)
                for i, row in df.iterrows():
                    word = str(row[col])
                    res = analyze_word(word)
                    if res:
                        res['입력 단어'] = word
                        results.append(res)
                    bar.progress((i+1)/len(df))
                
                res_df = pd.DataFrame(results)
                st.dataframe(res_df)
                st.download_button("결과 CSV 다운로드", res_df.to_csv(index=False), "vibe_guard_results.csv")

    # --- Tab 3: 이미지 분석 (OCR 정밀도 지침 강화) ---
    with tab3:
        st.info("이미지 속 텍스트를 추출하여 정책을 검토합니다.")
        uploaded_img = st.file_uploader("이미지 업로드", type=["jpg", "png", "jpeg"], key="img_upload")
        if uploaded_img:
            img = Image.open(uploaded_img)
            st.image(img, width=400)
            if st.button("이미지 텍스트 분석", key="btn_img"):
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                with st.spinner('분석 중...'):
                    # Vision AI에게 획 단위 정밀 판독 지시 (염병/좆까 오인식 방지)
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "user", "content": [
                                {"type": "text", "text": "이미지 속 글자를 왜곡 없이 아주 정밀하게 읽어줘. 특히 '염'과 '엠', '좆'과 '죳'의 획 차이를 엄격히 구분해서 적힌 그대로 추출해. 추출된 단어들을 JSON {'words': []} 배열로 줘."},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                            ]}
                        ],
                        response_format={ "type": "json_object" }
                    )
                    try:
                        extracted_list = json.loads(response.choices[0].message.content).get('words', [])
                        if not extracted_list:
                            st.warning("추출된 텍스트가 없습니다.")
                        else:
                            for word in extracted_list:
                                res = analyze_word(word)
                                if res: display_result(word, res)
                    except:
                        st.error("이미지 분석 중 오류가 발생했습니다.")
else:
    st.info("API 키를 입력해주세요.")
