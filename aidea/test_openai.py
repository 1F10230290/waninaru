from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # <- これが必要


# クライアント作成
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"),
base_url="https://api.openai.iniad.org/api/v1",
)

question = input('Question:')

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {'role':'user', 'content':question},
    ]
)

print(response.choices[0].message.content)