from pydantic import BaseModel
from enum import Enum
from openai import OpenAI
from pydantic import BaseModel
import json
from openai import OpenAI
from ast_rag import DynamicRAG
import zipfile
import os

# please use your own api-key instead of using ours
api_key = 'sk-BGsbjdC7lXQGHgJyh61xf04bBeR1P6uFForzHoXU4jsmWsrx'
client = OpenAI(
    api_key=api_key,
    base_url="https://api.chatanywhere.tech/v1"
)
spring_lib = r"./spring-lib/generation.zip"
rag = DynamicRAG()


def get_rag():
    return rag


def init_lib():
    zip_path = spring_lib
    save_path = './test'
    file = zipfile.ZipFile(zip_path)
    file.extractall(save_path)
    file.close()


class param(BaseModel):
    param_name: str
    param_type: str


class method(BaseModel):
    method_name: str
    method_inputs: list[param]
    method_return_type: str


class classType(str, Enum):
    controller = "controller"
    model = "model"
    repository = "repository"
    service = "service"
    dto = "dto"
    other = "other"


class single_class(BaseModel):
    class_name: str
    class_description: str
    properties: list[param]
    methods: list[method]
    class_type: classType


class classes_definition_generation(BaseModel):
    classes_to_implement_this_function: list[single_class]


class code_generation(BaseModel):
    package: str
    imports: str
    contents: str


class dependency(BaseModel):
    dependency_class_name: str


class dependency_relationship(BaseModel):
    class_name: str
    list_of_dependencies: list[dependency]


class all_dependency_relationships(BaseModel):
    list_of_dependency_relationships: list[dependency_relationship]


def generation(content, generation_structure, model_type="gpt-4o-mini"):
    completion = client.beta.chat.completions.parse(
        model=model_type,
        messages=[
            {"role": "user", "content": content}
        ],
        response_format=generation_structure
    )
    return completion.choices[0].message.parsed


def get_definition_results():
    with open("tmp_class_definition.json", "r") as f:
        definition_results = f.read()
        return definition_results


def class_generation_prompt(current_class_name, dependencies, code_storage):
    a = json.loads(get_definition_results())

    s = """Now you are given the definition about one single class. You need to implement it by Java.
        Here is the class you need to implement:
        \n"""
    for i in a:
        if (i["class_name"] == current_class_name):
            s += str(i)
            # now_class_definition=deepcopy(i)
            # del now_class_definition["related_function_no"]
            # now_class_definition["related_functions"]=[]
            # for j in i["related_function_no"]:
            #     now_class_definition["related_functions"].append(functions_list[j])
            # s+=str(now_class_definition)
    s += "\nExist elements that you can use and no need to implement again:"
    for i in range(len(dependencies)):
        s += "\n\nDependency " + str(i + 1) + ":\n"
        for j in a:
            rag_result = rag.query(j["class_name"])
            print(rag_result)
            for k in rag_result:
                pair = k.split('&&&&&')
                key, val = pair[0], pair[1]
                if key == dependencies[i]:
                    s += f'{key}:{val}\n'
    s += """\n\nOther tips:
        Assert the package root as com.test.generation, you should concat package definition after that.
        Give the code only, do not give any summary or conclusion in the begin or end of the answer.
        Only generate the single class and its functions I give to you."""

    return s


def class_reflection_prompt(current_class_name, code_storage, reflection, current_class_type):
    a = json.loads(get_definition_results())

    s = """Now you are given a code with syntax error You need to fix it by Java.
        Here is the class you need to implement:
        \n"""
    for i in a:
        if i["class_name"] == current_class_name:
            s += str(i)
    s += "\nHere is the preview code:"
    s += str("package com.test.generation." + str(current_class_type) + ";\n")
    s += str(code_storage.imports.replace("\\n", "\n"))
    s += str('\n\n')
    s += str(code_storage.contents.replace("\\n", "\n"))
    s += "\nHere is the Error you get:"
    for err in reflection:
        s += err

    s += """\n\nOther tips:
        Assert the package root as com.test.generation, you should concat package definition after that.
        Give the code only, do not give any summary or conclusion in the begin or end of the answer.
        Only generate the single class and its functions I give to you."""

    return s


requirement_head = "You are now a professional program architect. Your job is to read a requirement document and " \
                   "provide a reasonable project structure based on this document.\n" \
                   "The following are the points for your analysis:\n" \
                   "1. This project uses Java as the development language and Spring-boot as the development framework.\n" \
                   "2. You do not need to provide the corresponding code.\n"
step1 = "Analyze each function in the requirements document, and then write the process required to implement each " \
        "function. This process should be unrelated to code or computer system, but based on real-world logic.\n"

function_head = """
You are now a program developer. Now you have obtained a design plan and you need to complete the code design of one of the functions.
"""

tech_head = """
1. This project uses Java as the development language and Spring-boot as the development framework.\n
2. You do not need to provide the corresponding code.\n
3. The first step of your analysis should be to provide a specific framework and the functions of 
each module in the framework. I will give some module definitions:Controller (controller layer): 
responsible for processing HTTP requests and responses, usually annotated with @RestController. 
Service (service layer): contains business logic, usually annotated with @Service. Repository (
data access layer): interacts with the database, usually annotated with @Repository, 
combined with JPA/Hibernate for data persistence operations. Model (model layer): defines data 
structure and database mapping, usually annotated with @Entity.\n
4. The second step of your analysis should be to give the definition of specific classes in each 
module. For example: suppose our project needs a class to operate on students, then we should 
give a Student class, and give all the required attributes in the student class and the methods 
for student operations mentioned in the requirement document. If necessary, you can add the code 
related to adding/deleting/changing/querying students.\n
5. If there is any possible sensitive information, please use \"//confidential\" as a comment in 
the corresponding position, for example: password//sensitive.\n
6. All given class attributes should include names, and all given methods should include input, 
output and name.\n
7. There is no need to provide getter/setter methods, but these methods should be assumed to 
exist during design."\n
8. Java version is 17, so do not use javax, use jakarta instead.
"""

code_head = """
Now you are given a list of definition about classes and functions. you need to implement all of them.
here is the list:
"""

function_foot = """
You only need to give the classes and information of each class (eg: name, description, all properties in this class with their name and type, all methods in this class with their input name, input type, and type of their return) you need, and you don't need to give specific code.
Do not give any summary or conclusion in the begin or end of the answer.
"""

code_foot = """
assert the package root as com.test.generation, you should concat package definition after that.
give the code only, do not give any summary or conclusion in the begin or end of the answer.
only generate the single class and its functions I give to you.
"""
