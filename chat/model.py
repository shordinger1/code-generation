from enum import Enum
from pydantic import BaseModel


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


def prompt_code_generation(description, code=None, template_code=None, rag_code=None):
    exist_code_part = f"""EXISTING CODE (base to improve, and your code should based on this part): 
    {code}
    """ if code is not None else "No existing code provided ,you should generate your self."
    template_code_part = f"""TEMPLATE CODE (structural reference):
    {template_code}
    """ if template_code is not None else ""
    rag_code_part = f"""RAG RETRIEVED CODE (best practices reference):
    {rag_code}
    """ if rag_code is not None else ""
    return f"""
    ROLE: You are a senior software engineer. Improve the given code using all provided resources.
    TASK DESCRIPTION:
    {description}
    {exist_code_part}
    {template_code_part}
    {rag_code_part}
    INSTRUCTIONS:
    1. Generate complete runnable code by synthesizing all inputs
    2. Preserve existing code's core functionality and interface
    3. Incorporate relevant patterns from template and RAG code
    4. Maintain original naming conventions
    5. Add essential comments (<20% of total lines)
    6. OUTPUT ONLY RAW PYTHON CODE - NO EXPLANATIONS
    7. If any part we mentioned above not provided, feel free to design your own code
    8. code output should be formatted as follow:
    class code_generation(BaseModel):
        package: str
        imports: str
        contents: str
    FINAL OUTPUT:
    """


def prompt_code_reflection(description, error_message, code=None, template_code=None, rag_code=None):
    exist_code_part = f"""EXISTING CODE (base to improve, and your code should based on this part): 
        {code}
        """ if code is not None else "No existing code provided ,you should generate your self."
    template_code_part = f"""TEMPLATE CODE (structural reference):
        {template_code}
        """ if template_code is not None else ""
    rag_code_part = f"""RAG RETRIEVED CODE (best practices reference):
        {rag_code}
        """ if rag_code is not None else ""
    return f"""
    ROLE: You are a senior software engineer debugging code. Fix the errors using all provided resources.

    TASK DESCRIPTION:
    {description}
    ERROR MESSAGE (debugging reference):
    {error_message}
    {exist_code_part}
    {template_code_part}
    {rag_code_part}

    INSTRUCTIONS:
    1. Diagnose and fix bugs based on the error message
    2. Maintain original functionality while correcting errors
    3. Preserve existing variable names and interface contracts
    4. Incorporate relevant patterns from template and RAG code
    5. Add essential comments only where necessary (<15% of total lines)
    6. OUTPUT ONLY CORRECTED PYTHON CODE - NO EXPLANATIONS OR DIAGNOSIS
    7. If any part we mentioned above not provided, feel free to design your own code
    8. code output should be formatted as follow:
    class code_generation(BaseModel):
        package: str
        imports: str
        contents: str
    
    FINAL OUTPUT:
    """
