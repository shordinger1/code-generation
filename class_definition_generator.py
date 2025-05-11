import os
import json
from utils import *
import yaml
import json


def post_process(response):
    result = []
    models = response.replace("\n", "").split("###")[1:]
    # print(models)
    for model in models:
        sequence = model.split("**")
        title = sequence[0]
        for i in range(1, len(sequence), 2):
            function = sequence[i]
            content = sequence[i + 1]
            result.append({"title": title, "function": function[:-1], "content": content})
            # print(f"title: {title}\n function:{function}\n content:{content}\n")
    return result


def definition_prompts_generation(contents):
    prompts = []
    public_list = "###Module and function definition###\n"
    for content in contents:
        public_list += f"module:{content['title']}. function:{content['function']}.\n"
    for content in contents:
        prompt = function_head + tech_head + public_list + \
                 "The following function is what you need to analysis:\n" \
                 f"module:{content['title']}. function:{content['function']}.\n" \
                 f"This is the function you need to implement: {content['content']}" \
                 + function_foot + '\n'
        # print(prompt)
        prompts.append(prompt)

    return prompts


def code_prompts_generation(contents, history):
    prompt = code_head + \
             str(contents) + \
             f"exist elements that you can use and no need to implement again:\n{str(history)}" + \
             tech_head + \
             code_foot + \
             ""
    return prompt


def write_to_file(root, content):
    path = content["path"]
    code = content["code"]

    # 确保目录存在
    full_path = os.path.join(root, path)
    directory = os.path.dirname(full_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 将代码写入文件
    with open(full_path, "w") as file:
        file.write(code)


def concat_exist_tags(exist_tags: dict, prompt: str):
    return prompt + f"exist elements that you can use and no need to implement again:\n{str(exist_tags)}"


# 第一步：根据需求文档生成functions_list
def parse_yaml(yaml_file_path):
    """
    根据需求文档生成functions_list
    Args:
        yaml_file_path
    Returns:
    返回entity_mapping和functions_list, 每个function有以下信息:
        1. name
        2. description
        3. belongs_to, 其中belongs_to不止有entity的名字,我希望将整个entity(entity_description,attributes(required),attributes(optional)全部作为输入信息输进去
        4. 两个Test_cases_for_normal_scenarios,注意只取2个
        5. 两个Test_cases_for_error_scenarios
    """
    with open(yaml_file_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    # Extract entities and functions
    entities = data.get("Entities", {})
    functions = data.get("Functions", [])

    # Map entities for quick lookup
    entity_mapping = {
        entity_name: {
            "entity_name": entity_name,
            "entity_description": entity_details.get("description", ""),
            "attributes": {
                "required": entity_details.get("attributes", {}).get("required", []),
                "optional": entity_details.get("attributes", {}).get("optional", []),
            },
        }
        for entity_name, entity_details in entities.items()
    }

    # Create the functions list
    functions_list = []
    for function in functions:
        function_entry = {
            "name": function.get("name", ""),
            "description": function.get("description", ""),
            "belongs_to": entity_mapping.get(function.get("belongs_to"), {}),
            "Test_cases_for_normal_scenarios": function.get("Test_cases_for_normal_scenarios", [])[:2],
            "Test_cases_for_error_scenarios": function.get("Test_cases_for_error_scenarios", [])[:2],
        }
        functions_list.append(function_entry)
    return entity_mapping, functions_list


# 第二步，构建prompt
# 在发送给ChatGPT的时候，我需要按照以下格式发送
# 1. 头部：function_head + tech_head 
# 2. public_list: 所有function的module（也就是原版的belongs_to）和name，例如
'''module: Teacher. function1. Query the Status of All Books.
module: Teacher. function2. Add Books to the Library.
module: Student. function3. Log in to the System.
module: Administrator. function4. Enter and Register Student Information.
module: Administrator. function5. Enter and Register Teacher Information.
'''


# 3. "The following function is what you need to analysis:\n"
# 4. 当前function的完整信息，包括上文提到的
# 4.1 name
# 4.2 description
# 4.3 belongs_to， 其中belongs_to不止有entity的名字，我希望将整个entity（entity_description，attributes（required），attributes（optional）全部作为输入信息输进去
# 4.4 两个Test_cases_for_normal_scenarios，注意只取2个
# 4.5 两个Test_cases_for_error_scenarios
# 5. 尾部：function_foot
# 6. "exist elements that you can use and no need to implement again:"
# 7. exist_class_list，里面存着已定义的class

def generate_prompt(functions, function_index):
    """
    构造2,3,4
    """
    public_list = "\n".join([
        f"module: {func['belongs_to'].get('entity_name', 'Unknown')}. function{index + 1}. {func['name']}."
        for index, func in enumerate(functions)
    ])
    current_function = functions[function_index]
    belongs_to_info = current_function['belongs_to']
    detailed_function_info = f'''
This is the function you need to implement:
Name: {current_function['name']}
Description: {current_function['description']}
Belongs to:
  Entity Name: {belongs_to_info.get('entity_name', '')}
  Entity Description: {belongs_to_info.get('entity_description', '')}
  Required Attributes: {", ".join(belongs_to_info.get('attributes', {}).get('required', []))}
  Optional Attributes: {", ".join(belongs_to_info.get('attributes', {}).get('optional', []))}
Test Cases for Normal Scenarios:
  1. Input: {current_function['Test_cases_for_normal_scenarios'][0]['input']}
     Expected Result: {current_function['Test_cases_for_normal_scenarios'][0]['expected_result']}
  2. Input: {current_function['Test_cases_for_normal_scenarios'][1]['input']}
     Expected Result: {current_function['Test_cases_for_normal_scenarios'][1]['expected_result']}
Test Cases for Error Scenarios:
  1. Input: {current_function['Test_cases_for_error_scenarios'][0]['input']}
     Expected Result: {current_function['Test_cases_for_error_scenarios'][0]['expected_result']}
  2. Input: {current_function['Test_cases_for_error_scenarios'][1]['input']}
     Expected Result: {current_function['Test_cases_for_error_scenarios'][1]['expected_result']}
'''
    prompt = f"{public_list}\n{detailed_function_info}"
    return prompt


def generate_class_definition(temp_file_path="tmp_class_definition.json",
                              requirements_document_path="example_requirements.yaml"):
    entity_mapping, functions_list = parse_yaml(requirements_document_path)
    result = []
    exist_classes_name = []
    # 将现有的entity添加到class_definition_result里
    for entity_name, entity_details in entity_mapping.items():
        from utils import single_class
        single_class_instance = single_class(
            class_name=entity_details["entity_name"],
            class_description=entity_details["entity_description"],
            properties=[
                param(param_name=attr, param_type="str")  # entity的属性类型总是str
                for attr in entity_details["attributes"]["required"] + entity_details["attributes"]["optional"]
            ],
            methods=[],  # entity没有方法
            class_type=classType.model  # entity的类型总是"model"
        )
        result.append(single_class_instance.model_dump())
    for i in entity_mapping:
        exist_classes_name.append(i)

    for i in range(len(functions_list)):
        prompt = generate_prompt(functions_list, i)
        prompt = function_head + tech_head + "\n###Module and function definition###\n" + prompt + function_foot
        if (len(exist_classes_name) != 0):
            prompt += "exist elements that you should NOT implement again:" + str(exist_classes_name)
        # 第三步，发送给ChatGPT，生成classes_definition
        definition_results = generation(prompt, classes_definition_generation)

        for single_class in definition_results.classes_to_implement_this_function:
            # 如果重名，就不添加了
            if single_class.class_name not in exist_classes_name:
                result.append(single_class.model_dump())
                exist_classes_name.append(single_class.class_name)

    with open(temp_file_path, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
