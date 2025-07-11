from openai import OpenAI
import datetime
import json


class TaskProcessor:

    def __init__(self, processor_name):
        self.processing_log = []
        self.processor_name = processor_name
        self.description = None

    def to_json(self, file_path):
        """
        将当前对象序列化为JSON并写入文件
        :param file_path: 要写入的JSON文件路径
        """
        data = {
            'processor_name': self.processor_name,
            'description': self.description,
            'processing_log': self.processing_log
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def from_json(cls, file_path):
        """
        从JSON文件读取并反序列化为TaskProcessor对象
        :param file_path: 要读取的JSON文件路径
        :return: TaskProcessor实例
        """
        with open(file_path, 'r') as f:
            data = json.load(f)

        processor = cls(data['processor_name'])
        processor.description = data['description']
        processor.processing_log = data['processing_log']

        return processor

    def process(self, description, **kwargs):
        self.description = description
        self.log(description)
        # raise NotImplementedError()

    def analyze(self, **kwargs):
        raise NotImplementedError()

    def log(self, content):
        log = f"[{datetime.now().strftime('%y:%m:%d:%H:%M:%S')}] {self.processor_name}: {content}"
        self.processing_log.append(log)
        print(log)

    def print_log(self):
        return "\n".join(self.processing_log)


class openaiProcessor(TaskProcessor):

    def __init__(self):
        super().__init__("openAI")
        api_key = 'sk-BGsbjdC7lXQGHgJyh61xf04bBeR1P6uFForzHoXU4jsmWsrx'
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.chatanywhere.tech/v1"
        )

    def process(self, description, **kwargs):
        """
        :param description: ACTUALLY MEANS PROMPT
        :param kwargs: should give generation_structure and model_type here. FOR STRUCTURE
        GENERATION, YOUR PROMPT SHOULD CONTAIN THE DEFINITION OF GENERATION STRUCTRURE
        :return: chatGPT generated chat result
        """
        try:
            generation_structure = kwargs.get('generation_structure')
        except Exception as e:
            raise  ValueError("value generation_structure not given")
        model_type = kwargs.get('model_type', default="gpt-4o-mini")
        completion = self.client.beta.chat.completions.parse(
            model=model_type,
            messages=[
                {"role": "user", "content": description}
            ],
            response_format=generation_structure
        )
        return completion.choices[0].message.parsed
