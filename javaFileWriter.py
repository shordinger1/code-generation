from utils import code_generation
import os


def javaFileWriter(root, class_name, code_result: code_generation, class_type, overwrite=False, ignore_package_imports=False):
    # directories=code_result.package.split('.')
    directories = "com.test.generation".split('.')
    path = os.path.join(root, *directories, class_type, f"{class_name}.java")
    print(f"java file write to {path}")
    if not overwrite:
        if os.path.exists(path):
            print(f"File already exists at {path}, Skipped")
            return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as file:
        if not ignore_package_imports:
            # monkey patch
            file.write("package com.test.generation." + str(class_type) + ";\n")
            file.write(code_result.imports.replace("\\n", "\n"))
            file.write('\n\n')
        file.write(code_result.contents.replace("\\n", "\n"))
    return True
