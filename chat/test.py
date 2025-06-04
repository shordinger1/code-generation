from openai import OpenAI
from client import generation
from pydantic import BaseModel

client = OpenAI(
    base_url="http://10.112.0.32:5239/v1",
    api_key="sk-MLVRuDAU5EHZUG3U56A015Ef43A54d029e55295d8056FaEe",
)


def chat_gpt(message):
    response = client.chat.completions.create(
        model="qwen2.5-7b-test",  # qwen72 本次支持模型
        stream=False,  # 如果需要流式响应，请设置为 True
        messages=message  # 输入的用户消息
    )

    # 输出模型的非流式响应
    # for chunk in response._iter_events():
    #   content = chunk.data
    #   if content:
    #     print(content, end="\n", flush=True)
    return response


def prompt_code_analysis(code, context=None):
    context_part = f"""CONTEXT (additional information about this code):
        {context}
        """ if context is not None else "No additional context provided."

    return f"""
    ROLE: You are a senior code analyst with deep experience in reverse engineering and code comprehension.

    TASK DESCRIPTION:
    Analyze the provided code segment and explain the purpose/usage of each significant part.
    Pay special attention to any functions matching 'func_xxxx' patterns - make educated guesses
    about their purpose based on naming, parameters, and usage context.

    CODE TO ANALYZE:
    {code}

    {context_part}

    INSTRUCTIONS:
    1. First summarize the overall purpose of this code segment
    2. Then analyze each significant function/method/class:
       - For normal functions: Explain their clear purpose
       - For func_xxxx patterns: State "This appears to be..." and make reasonable guesses
    3. Highlight any unusual patterns or potential issues
    4. Format your response as:
       class m(BaseModel):
            component: list[str]
            description: list[str]
    5. Include confidence levels for func_xxxx guesses (Low/Medium/High)
    6. Never say "I don't know" - always make your best guess

    FINAL OUTPUT:
    """


code = open(
    r"C:\Users\bcjPr\Desktop\gtnh\Twist-Space-Technology-Mod\src\main\java\com\Nxer\TwistSpaceTechnology\system"
    "\DysonSphereProgram\logic\DSP_DataCell.java",
    "r").read()


class m(BaseModel):
    component: list[str]
    description: list[str]


print(generation(prompt_code_analysis(code), m))
component = ['DSP_DataCell', 'getSolarSailToDelete', 'getDSPPowerPointCanUse', 'getDSPPowerPointCanUseBigInteger',
             'tryDecreaseUsedPowerPoint', 'tryUsePowerPoint', 'canUsePowerPoint', 'decreaseUsedPowerPointUnsafely',
             'setUsedPowerPointUnsafely', 'flushMaxDSPPowerPoint', 'turnToBigIntegerMode',
             'flushMaxDSPPowerPointNormal', 'flushMaxDSPPowerPointBigInteger', 'shouldUseBigInteger',
             'getMaxDSPPowerPoint', 'addDSPSolarSail', 'addDSPNode', 'setMaxDSPPowerPoint', 'markDirty', 'cancelDirty',
             'toString', 'getOwnerName', 'setOwnerName', 'getGalaxy', 'setGalaxy', 'getDSPSolarSail', 'setDSPSolarSail',
             'getDSPNode', 'setDSPNode']
description = [
    'The class represents a data structure to manage and manipulate solar sails and nodes in a Dyson Sphere Program, keeping track of various attributes such as power points, ownership, and galaxy association.',
    'Calculates the number of solar sails that can be deleted based on current counts and limits.',
    'Calculates the remaining available power points that can be utilized, considering both standard and big integer calculations if enabled.',
    'Calculates the potential usable power points using Big Integers, likely to avoid overflow when large numbers are involved.',
    'Attempts to decrease the used power points by a specific amount, logs errors when the amount exceeds the currently used points.',
    'Requests to use a specified amount of power points if available, marking the data as dirty if successful.',
    'Checks if a specified amount of power points can be utilized without exceeding limits.',
    'Decreases the used power points unsafely by a specified amount, and marks the object as dirty.',
    'Sets used power points unsafely without bounds checking; may lead to potential errors if misused.',
    'Calculates and flushes the maximum possible power points based on solar sail and node amounts, marking the data as dirty during the process.',
    'This appears to be a method for switching to a big integer mode, likely enhancing the potential for managing larger numbers in calculations.',
    'Calculates the maximum power points using standard calculations.',
    'Calculates the maximum power points using big integer calculations for more substantial values.',
    'This appears to be a method to determine whether Big Integer calculation mode should be used, based on current resource counts.',
    'Returns the maximum power points available. Flushes the value if the data is marked dirty, also considering big integer scenarios.',
    'Increments the count of solar sails and nests power point maximum calculations, marking the data as dirty.',
    'Increments the count of DSP nodes and nests power point maximum calculations, marking the data as dirty.',
    'Sets the maximum DSP power point, marking it as dirty in the process.',
    'Marks the current object as dirty, incrementing a synchronization flag to track changes that need to be synchronized with other systems.',
    'Resets the dirty flag, indicating that the current state is now synchronized or up-to-date.',
    'Creates a string representation summary of the current state of the data cell.', "Gets the current owner's name.",
    "Sets the owner's name and marks the data as dirty.", 'Gets the associated galaxy object.',
    'Sets the associated galaxy object and marks the data as dirty.', 'Gets the current number of solar sails.',
    'Sets the number of solar sails and updates the power point calculation, marking as dirty.',
    'Gets the current number of DSP nodes.',
    'Sets the number of DSP nodes and updates the power point calculation, marking as dirty.']
