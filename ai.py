import os
import openai

client = openai.OpenAI(api_key=os.getenv("PERSONAL_OAI_API_KEY"))

def generate_guidance(systolic: int, diastolic: int, heart_rate: int, symptoms: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates guidance for blood pressure readings."},
            {"role": "user", "content": f"Systolic: {systolic}, Diastolic: {diastolic}, Heart Rate: {heart_rate}, Symptoms: {symptoms}"}
        ]
    )
    return response.choices[0].message.content
