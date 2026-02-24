import streamlit as st
from openai import OpenAI
import json

# 1. 예외 단어 리스트 (AI 판단을 거치지 않고 즉시 반환)
# 여기에 문제가 되는 단어를 추가하면 AI 환각이 발생하지 않습니다.
FIXED_DATABASE = {
    "피떡갈비": {"부정점수": 85, "카테고리": "문화 이슈", "배경": "5.18 민주화운동 희생자를 음식에 빗대어 조롱하는 극히 잔혹한 고인 모독형 혐오 표현."},
    "통매음": {"부정점수": 20, "카테고리": "사회적 이슈", "배경": "통신매체이용음란죄의 약칭으로, 특정 비속어가 아닌 법률상 죄명임."},
    "오조오억": {"부정점수": 80, "카테고리": "문화 이슈", "배경": "단순 숫자 표현에서 젠더 갈등 맥락의 비하 밈으로 변질되어 사용됨."},
    "보빨": {"부정점수": 95, "카테고리": "선정적", "배경": "여성의 특정 신체 부위를 비하하고 성적 행위를 저속하게 표현한 비속어."},
    "마약": {"부정점수": 75, "카테고리": "사회적 이슈", "배경": "불법 약물 자체를 의미하며 범죄와 직결된 사회적 금기어임."}
}

st.set_page_config(page_title="Global Vibe Guard Pro", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    word_input = st.text_input("분석할 단어:", placeholder="").strip()

    if st.button("분석"):
        with st.spinner('분석 중입니다.'):
            # [Step 1] 고정 데이터베이스에서 먼저 확인 (가장 확실한 방법)
            if word_input in FIXED_DATABASE:
                data = FIXED_DATABASE[word_input]
                st.divider()
                st.metric("리스크 점수", f"{data['부정점수']}점")
                st.subheader(f"🏷️ {data['카테고리']}")
                st.write(f"🌐 **감지된 언어:** 한국어(고정)")
                st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {data['배경']}")
                st.info(f"⚖️ **정책 판단 근거:** 해당 단어는 정책상 고정 관리 키워드입니다.")
            
            # [Step 2] 목록에 없는 단어만 AI 분석 수행
            else:
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "너는 정책 결정관이야. 이전 맥락을 완전히 무시하고 오직 현재 단어의 사전적/사회적 유해성만 분석해 JSON으로 답해. 욕설은 90점 이상, 일상어는 10점대로 격리해."},
                            {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.metric("리스크 점수", f"{result['부정점수']}점")
                    st.subheader(f"🏷️ {result['카테고리']}")
                    st.write(f"🌐 **감지된 언어:** {result['언어']}")
                    st.info(f"📖 **의미:** {result['표면적의미']}")
                    st.warning(f"⚠️ **배경:** {result['논란의배경']}")
                except:
                    st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
