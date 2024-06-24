import ollama

def getCompanyCombineCondition(companyData, condition):
    response = ollama.chat(model='mistral', messages=[
    {
        'role': 'user',
        'content': f'''В формате JSON представлены характеристики предприятия, твоя задача сказать true, если предприятие соответствует условию участия
        false если нет. Отвечай только true или false. Характеристики предприятия {companyData}. Условие участия {condition}
          Отвечай только на русском языке. Не нужно самому додумывать, только на основании полученных данных''',
    },
    ])
    return response['message']['content']
