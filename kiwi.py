from fastmcp import FastMCP
import kiwipiepy
from collections import Counter

# 1. 서버 인스턴스 생성
mcp = FastMCP("kiwi-mcp-http")

# 2. @mcp.tool 데코레이터로 함수를 '도구'로 등록
@mcp.tool

def extract_keywords(query: str, top_n: int = 2) -> list[str]:
    """
    한국어 질의에서 중요 키워드를 추출합니다.
    
    Args:
        query: 한국어 자연어 질의문
        top_n: 추출할 키워드 수 (기본값: 2)
    
    Returns:
        상위 키워드 리스트
    """
    kiwi = kiwipiepy.Kiwi()
    
    # 불필요한 단어 (불용어) 목록
    stopwords = {
        "것", "수", "등", "때", "곳", "말", "그", "이", "저", "거",
        "좀", "제", "정도", "내용", "방법", "경우", "부분", "중", "위"
    }
    
    # 형태소 분석 후 명사(NNG: 일반명사, NNP: 고유명사) 추출
    result = kiwi.tokenize(query)
    nouns = [
        token.form
        for token in result
        if token.tag in ("NNG", "NNP")       # 명사만 선택
        and len(token.form) > 1               # 한 글자 제외
        and token.form not in stopwords       # 불용어 제외
    ]
    
    # 빈도 기준 상위 키워드 반환
    counter = Counter(nouns)
    keywords = [word for word, _ in counter.most_common(top_n)]
    
    # 빈도가 같으면 원문 등장 순서 우선
    if len(keywords) < top_n:
        # 부족하면 동사/형용사 어근도 포함
        extras = [
            token.form
            for token in result
            if token.tag.startswith("V") and len(token.form) > 1
            and token.form not in stopwords and token.form not in keywords
        ]
        keywords += extras[:top_n - len(keywords)]
    
    return keywords


# 3. 서버 실행 (스크립트가 직접 실행될 때만)
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000 )