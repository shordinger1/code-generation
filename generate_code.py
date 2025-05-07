from collections import defaultdict
from javaFileWriter import javaFileWriter
from utils import *
from java_grammar.java_test import analysis_single_file
import shutil
from pathlib import Path

if os.path.exists("./test/generation"):
    shutil.rmtree("./test/generation")

java_root = "./test/generation/src/main/java"
max_reflection = 10
prompt = "Give me the dependency relationship of all following classes. For example, the class \"BookRepository\" " \
         "depends on the class \"Book\", and the class \"Book\" doesn't depend on any other classes.\nClass data:" + \
         get_definition_results()

dependency_result = generation(prompt, all_dependency_relationships)


def determine_level(data):
    dependencies = defaultdict(list)
    dependents = defaultdict(list)

    for item in data:
        class_name = item["class_name"]
        dependencies[class_name] = [dep["dependency_class_name"] for dep in item["list_of_dependencies"]]
        for dep in dependencies[class_name]:
            dependents[dep].append(class_name)

    levels = {}

    def determine_level_recursive(class_name):
        if class_name in levels:
            return levels[class_name]
        if not dependencies[class_name]:
            levels[class_name] = 1
            return 1
        level = 1 + max(determine_level_recursive(dep) for dep in dependencies[class_name])
        levels[class_name] = level
        return level

    classes = list(dependencies.keys())
    for class_name in classes:
        determine_level_recursive(class_name)
    return dependencies, list(levels.items())


dependency_dict, dependency_levels = determine_level(dependency_result.dict()['list_of_dependency_relationships'])
max_level = max(level for _, level in dependency_levels)

code_storage = {}
# rag = get_rag()
# java_lib = analysis_java_files('./spring-lib')
# rag.batch_add_data(java_lib.items())
init_lib()
# outputs = rag.query('decode json files', 10)
# print(outputs)
for current_level in range(1, max_level + 1):
    for class_name, level in dependency_levels:
        if current_level != level: continue
        print("generating class: ", class_name, ", dependency: ", dependency_dict[class_name], ", level: ",
              current_level, sep="")
        prompt = class_generation_prompt(class_name, dependency_dict[class_name], code_storage)
        code_storage[class_name] = generation(prompt, code_generation)

        class_definitions = json.loads(get_definition_results())
        # import dependencies
        for i in dependency_dict[class_name]:
            for j in class_definitions:
                if j['class_name'] == i:
                    current_class_type = j['class_type']
            code_storage[class_name].imports += "\nimport com.test.generation." + current_class_type + "." + i + ";"
        current_class_type = ""
        for i in class_definitions:
            if i['class_name'] == class_name:
                current_class_type = i['class_type']
        if current_class_type == classType.model or current_class_type == "model":
            # solve getter/setter
            code_storage[class_name].imports += "\nimport lombok.Data;"
            code_storage[class_name].contents = "\n@Data\n" + code_storage[class_name].contents.lstrip()

        # monkey patch
        if ("package" in code_storage[class_name].contents.lstrip()):
            if (code_storage[class_name].contents[:7] == "\n@Data\n"): code_storage[class_name].contents = code_storage[
                                                                                                               class_name].contents[
                                                                                                           7:]
            javaFileWriter(java_root, class_name, code_storage[class_name], current_class_type, overwrite=True,
                           ignore_package_imports=True)
        else:
            javaFileWriter(java_root, class_name, code_storage[class_name], current_class_type, overwrite=True)

        directories = "com.test.generation".split('.')
        path = os.path.join(java_root, *directories, current_class_type, f"{class_name}.java")
        ret, message = analysis_single_file(path)
        if ret:
            rag.batch_add_data(message.items())
        else:
            Path(path).unlink()
            print(message)
            flag = False
            for i in range(max_reflection):
                prompt = class_reflection_prompt(class_name, code_storage[class_name], message, current_class_type)
                code_storage[class_name] = generation(prompt, code_generation)

                class_definitions = json.loads(get_definition_results())
                # import dependencies
                for i in dependency_dict[class_name]:
                    for j in class_definitions:
                        if j['class_name'] == i:
                            current_class_type = j['class_type']
                    code_storage[
                        class_name].imports += "\nimport com.test.generation." + current_class_type + "." + i + ";"
                current_class_type = ""
                for i in class_definitions:
                    if i['class_name'] == class_name:
                        current_class_type = i['class_type']
                if current_class_type == classType.model or current_class_type == "model":
                    # solve getter/setter
                    code_storage[class_name].imports += "\nimport lombok.Data;"
                    code_storage[class_name].contents = "\n@Data\n" + code_storage[class_name].contents.lstrip()

                # monkey patch
                if "package" in code_storage[class_name].contents.lstrip():
                    if code_storage[class_name].contents[:7] == "\n@Data\n":
                        code_storage[class_name].contents = \
                            code_storage[class_name].contents[7:]
                    javaFileWriter(java_root, class_name, code_storage[class_name], current_class_type, overwrite=True,
                                   ignore_package_imports=True)
                else:
                    javaFileWriter(java_root, class_name, code_storage[class_name], current_class_type, overwrite=True)

                directories = "com.test.generation".split('.')
                path = os.path.join(java_root, *directories, current_class_type, f"{class_name}.java")
                ret, message = analysis_single_file(path)
                if ret:
                    rag.batch_add_data(message.items())
                    flag = True
                    break
            if flag:
                print(f"You should fix the {class_name} by yourself")
