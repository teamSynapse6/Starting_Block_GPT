import requests
import os
from openai import OpenAI
import json
from prompts import instructions

# prompts.py에서 정의된 지시문을 사용
from prompts import instructions as assistant_instructions

# 환경 변수에서 OpenAI API 키 로드
OPENAI_API_KEY = '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'

#assistant 초기화
client = OpenAI(api_key=OPENAI_API_KEY)


# PDF서버로부터 id의 데이터를 호출하는 메소드
def information_from_pdf_server(announcement_id):
    print(f'서버 검색 요청, id:{announcement_id}')
    pdf_url = f"https://pdf.startingblock.co.kr/announcement?id={announcement_id}"
    response = requests.get(pdf_url)
    
    if response.status_code == 200:
        text_data = response.content.decode('utf-8')
        print('서버 데이터 호출을 완료했습니다')
        return text_data
    elif response.status_code == 404:
        print(f"ID: {announcement_id}에 해당하는 정보를 찾을 수 없습니다.")
        return "요청하신 정보를 찾을 수 없습니다."
    else:
        print(f"Error getting information: {response.status_code}")
        return "서버에서 정보를 검색하는 동안 오류가 발생했습니다."

def create_assistant(client):
    assistant_file_path = 'assistant.json'

    #만약 assistant.json이 이미 있다면 로드.
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    
    else:
        #만약 assistant.json이 없다면, 아래의 메소드를 사용하는 새 파일을 생성.
        assistant = client.beta.assistants.create(
            instructions=assistant_instructions,
            name = "Starting_Block_GPT_PDF_Assistant",
            model="gpt-3.5-turbo-1106",
             tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "information_from_pdf_server",
                        "description": "Retrieve text information from a PDF server using the announcement ID.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "announcement_id": {
                                    "type": "integer",
                                    "description": "The ID of the announcement to retrieve information for."
                                }
                            },
                            "required": ["announcement_id"]
                        }
                    }
                }
            ]
        )

        # 생성된 보조자 ID를 assistant.json 파일에 저장합니다.
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
            print("Created a new assistant and saved the ID.")
        assistant_id = assistant.id

    return assistant_id