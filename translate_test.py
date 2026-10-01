import ollama

response = ollama.chat(
    model="qwen2.5",
    messages=[
        {
            "role": "user",
            "content": "Translate the following Chinese text to English. Only output the translation, nothing else:\n\n行进中国"
        }
    ]
)

print(response["message"]["content"])