import json
from flask import Flask, request, jsonify
import os
import openai
from openai import OpenAI
import functions
import time


# 환경 변수에서 OpenAI API 키 로드
OPENAI_API_KEY = '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'


app = Flask(__name__)


# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

# 보조자(Assistant) 생성 또는 로드
assistant_id = functions.create_assistant(client)  # 이 기능은 funcionts.py에서 사용


# 대화 만들기
@app.route('/start', methods=['GET'])
def start_conversation():
      print("새로운 대화 시작 중")
      thread = client.beta.threads.create()
      print(f"새로운 대화가 쓰레드 {thread.id}에서 시작되었습니다")
      return jsonify({"thread_id": thread.id})

    
# 채팅 시작하기
@app.route('/chat', methods=['POST'])
def chat(): # 먼저 post에서 받아오는 데이터 정의
    data = request.json
    thread_id = data.get('thread_id')
    announcement_id = data.get('announcement_id')
    message = data.get('message')


    # 쓰레드 ID가 없을 경우
    if not thread_id:
        print("Error: thread_id가 없습니다")
        return jsonify({"error": "thread_id가 없습니다"}), 400

    print(f"Received message: {message} for thread ID: {thread_id}")

    #유저의 메시지를 쓰레드에 추가
    client.beta.threads.messages.create(thread_id=thread_id,
                                        role="user",
                                        content= message)
    
    #어시스턴트 실행
    run = client.beta.threads.runs.create(thread_id=thread_id,
                                            assistant_id=assistant_id)
    
    #만약 functions.py에서 처리해야하는 내용일 경우 실행
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                       run_id=run.id)
        #Run status의 출력에 따라 처리
        if run_status.status == "completed":
            print('1차 프로세스가 완료')
            break
        elif run_status.status == "requires_action":
            print('2차 프로세스 시작')
            for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
                if tool_call.function.name == "information_from_pdf_server":
                    #PDF 서버에서 정보 찾기
                    arguments = json.loads(tool_call.function.arguments)
                    output = functions.information_from_pdf_server(arguments["announcement_id"])
                    client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id,
                                                                 run_id=run.id,
                                                                 tool_outputs=[{
                                                                     "tool_call_id": tool_call.id,
                                                                     "output": json.dumps(output)
                                                                 }])
            time.sleep(1) #완료 후 1초간 대기
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[0].content[0].text.value

    print(f"Assistant response: {response}")
    return jsonify({"response": response})

# 대화 종료 후 쓰레드 삭제하기
@app.route('/end', methods=['DELETE'])
def delete_thread():
    # 쿼리 파라미터에서 thread_id 추출
    thread_id = request.args.get('thread_id')
    
    # thread_id의 유효성 검사
    if not thread_id:
        print("Error: thread_id가 제공되지 않았습니다.")
        return jsonify({"error": "thread_id 파라미터가 필요합니다."}), 400
    
    # OpenAI API를 사용하여 스레드 삭제
    try:
        response = client.beta.threads.delete(thread_id)
        print(f"스레드 {thread_id}가 삭제되었습니다.")
        return jsonify({"id": thread_id, "object": "thread.deleted", "deleted": True}), 200
    except Exception as e:
        print(f"스레드 삭제 중 오류 발생: {e}")
        return jsonify({"error": "스레드를 삭제하는 동안 오류가 발생했습니다."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
