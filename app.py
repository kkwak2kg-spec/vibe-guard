import streamlit as st
from openai import OpenAI
import json

# 1. 페이지 설정
st.set_page_config(page_title="Global Vibe Guard Pro", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

# 2. API 키 로드
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key 설정", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    word_input = st.text_input("분석할 단어:", placeholder="").strip()

    if st.button("분석"):
        with st.spinner('분석 중입니다.'):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 게임 정책 결정관이자 다국어 분석 전문가야. "
                                "단어의 표면적 발음보다 '본래 의미의 유해성'을 최우선으로 판단해.\n\n"
                                "### [외국어 비하어 판정 가이드]\n"
                                "1. **의미 기반 점수 산정**: 외국어 단어가 '바보', '어리석은' 등 타인을 비하하는 의미를 담고 있다면, "
                                "설령 발음이 한국어 욕설과 비슷하더라도 '건전한 외국어'로 분류하지 마. 최소 **40~60점**의 리스크 점수를 부여해.\n"
                                "2. **상세 배경 의무화**: '상세 맥락 및 배경' 필드를 절대로 비워두지 마. 해당 단어가 실제 그 언어권 커뮤니티에서 어떤 뉘앙스로 쓰이는지 구체적으로 기술해.\n"
                                "3. **발음 유사성 언급 주의**: 한국어 욕설과 발음이 비슷하다는 사실에만 집중하지 말고, 그 단어 자체가 가진 고유의 부정적 영향력을 분석해.\n"
                                "4. **카테고리**: 비하의 의미가 있다면 [욕설/비속어] 또는 [문화 이슈]로 분류해."
                            )
                        },
                        {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0 
                )
                
                result = json.loads(response.choices[0].message.content)
                st.divider()
                st.success("분석 완료")
                
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{result['부정점수']}점")
                with c2: st.subheader(f"🏷️ {result['카테고리']}")
                
                st.write(f"🌐 **감지된 언어:** {result['언어']}")
                st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                
                # 배경 설명이 누락되지 않도록 UI 강제 출력
                bg_info = result.get('논란의배경', '상세 배경 정보가 생성되지 않았습니다. 정책 확인이 필요합니다.')
                if result['부정점수'] >= 40:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {bg_info}")
                else:
                    st.info(f"💡 **상세 맥락 및 배경:** \n\n {bg_info}")
                
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
