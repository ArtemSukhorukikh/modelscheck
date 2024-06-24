import ollama

def getCompanyDataJson(description):
    response = ollama.chat(model='mistral', messages=[
    {
        'role': 'user',
        'content': f'''Попытайся создать JSON формата [{{"label":"название характеристики", "value":"полученная характеристика"}}] из
          представленного далее текста описания предприятия. Если нет описания или характеристик, то верни пустой JSON
          {description}
          Отвечай только на русском языке. Никаких личных расмышлений только ответ в формате JSON с характеристиками предприятия''',
    },
    ])
    return response['message']['content']
