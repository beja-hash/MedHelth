from fastapi import FastAPI
from vectorization_rag import qa_retrieval
from pydantic import BaseModel
import requests
import json


class ShemaForGenerateAnswer(BaseModel):
    prompt: str
    model: str

app = FastAPI()



chat_history = [
        {
            'id': 0,
            'user_prompt': '',
            'assistent_answer': '',
        },
    ]

@app.post('/generate_answer')
async def generate_answer(requestModel: ShemaForGenerateAnswer):
    global chat_history
    

    formatted_chat_history = []

    for item in chat_history:
        user = item.get("user_prompt", "").strip()
        assistant = item.get("assistent_answer", "").strip()
        if user or assistant:
            formatted_chat_history.append((user, assistant))

    payload = {
        'question': requestModel.prompt,
        'chat_history': formatted_chat_history,
    }
    history_dialog = ''
    for item in chat_history:
                if item['user_prompt'].strip() or item['assistent_answer'].strip():
                    history_dialog += f"Пользовователь спрашивает:{item['user_prompt']}\n"
                    history_dialog += f"Ты отвечаешь:{item['assistent_answer']}\n\n"


    result = qa_retrieval.invoke(payload)

    answer = result['answer']
    
    

    promptForModel = """
        Ты — помощник для медицинского чат-бота. Твоя задача — перепроверить и переформулировать ответ, сделанный другим ИИ, чтобы он стал:

        
        - понятным человеку без мед. образования,
        - точным (если информации недостаточно — честно скажи об этом),
        - и при необходимости — дополнен коротким практическим советом.

        Отвечай опираясь на предыдущие ответы:
        '{history_dialog}

        Вот запрос пользователя:
        "{requestModelPrompt}"

        Вот ответ предыдущей модели:
        Отвечай исключительно на русском языке, независимо от языка предыдущих ответов:
            "{answer}"


        Теперь сгенерируй финальный ответ, которым можно делиться с пользователем. Если ответ звучит неуверенно, исправь. Если он неточен — укажи, что нужна консультация специалиста.

    """.format(requestModelPrompt=requestModel.prompt, answer=answer, history_dialog=history_dialog)

    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'prompt':promptForModel, 'model':requestModel.model},
            stream = True
        )

        response.raise_for_status()

        result = ''

        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                result += data.get('response', 'Языковая модель ничего не вернула')
        
        max_id = max(item['id'] for item in chat_history)

        chat_history.append({'id':max_id + 1, 'user_prompt': requestModel.prompt, 'assistent_answer': result})

        

        return {'generated_text': result}

        
    
    except requests.exceptions.HTTPError as h:
        return {'error': str(h), 'status':response.status_code}
    
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)