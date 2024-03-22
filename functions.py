import requests
import os
import openai
import json

# prompts.py에서 정의된 지시문을 사용
from prompts import instructions as assistant_instructions

# 환경 변수에서 OpenAI API 키 로드
OPENAI_API_KEY = os.getenv('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')

def create_assistant(client):
    assistant_file_path = 'assistant.json'

    # OpenAI 클라이언트 초기화
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # assistant.json 파일이 이미 존재하는지 확인
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
            return assistant_id
    else:
        # 새 보조자 생성
        assistant = openai.Assistant.create(
            description="Assistant for Starting_block_GPT, specialized in responding to queries about startup support programs in South Korea.",
           
                "model": "gpt-3.5-turbo-1106",
         
        )

        # 생성된 보조자 ID를 assistant.json 파일에 저장
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant["id"]}, file)
            print("Created a new assistant and saved the ID.")

        return assistant["id"]


def information_from_pdf_server(announcement_id):
    # 공고의 txt 정보를 받아오는 엔드포인트 URL
    url = f"https://pdf.startingblock.co.kr/announcement?id={announcement_id}"
    
    # 서버로부터 정보를 GET 방식으로 요청
    response = requests.get(url)
    
    # 응답 상태 코드가 200(성공)인 경우
    if response.status_code == 200:
        # UTF-8로 인코딩된 텍스트 데이터를 처리
        text_data = response.content.decode('utf-8')
        
        return text_data
    
    # 응답 상태 코드가 200이 아닌 경우(실패)
    else:
        print(f"Error getting information: {response.text}")
        return None