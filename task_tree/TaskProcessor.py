from openai import OpenAI

class TaskProcessor:

    def __init__(self):
        pass

    def process(self, **kwargs):
        raise NotImplementedError()

class openaiProcessor:

    def __init__(self):
        api_key = 'sk-BGsbjdC7lXQGHgJyh61xf04bBeR1P6uFForzHoXU4jsmWsrx'
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.chatanywhere.tech/v1"
        )

    def process(self, prompt, generation_structure, model_type="gpt-4o-mini"):
        completion = self.client.beta.chat.completions.parse(
            model=model_type,
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format=generation_structure
        )
        return completion.choices[0].message.parsed
