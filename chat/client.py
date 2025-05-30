from openai import OpenAI
from util import get_logger

LOG = get_logger()
api_key = 'sk-BGsbjdC7lXQGHgJyh61xf04bBeR1P6uFForzHoXU4jsmWsrx'
client = OpenAI(
    api_key=api_key,
    base_url="https://api.chatanywhere.tech/v1"
)


def generation(content, generation_structure, model_type="gpt-4o-mini", logger=LOG):
    logger.write('--------------asking gpt for--------------\n')
    logger.write(content + '\n')
    completion = client.beta.chat.completions.parse(
        model=model_type,
        messages=[
            {"role": "user", "content": content}
        ],
        response_format=generation_structure
    )
    logger.write('--------------got response--------------\n')
    logger.write(str(completion.choices[0].message.parsed) + '\n')
    return completion.choices[0].message.parsed
