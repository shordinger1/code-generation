from utils import code_generation
from log import get_logger
import os

LOG = get_logger()


def javaFileWriter(root, class_name, code_result: code_generation, class_type, overwrite=False,
                   ignore_package_imports=False):
    # directories=code_result.package.split('.')
    directories = "com.test.generation".split('.')
    path = os.path.join(root, *directories, class_type, f"{class_name}.java")
    LOG.write(f"java file write to {path}\n")
    if not overwrite:
        if os.path.exists(path):
            LOG.write(f"File already exists at {path}, Skipped\n")
            return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as file:
        if not ignore_package_imports:
            # monkey patch
            LOG.write("package com.test.generation." + str(class_type) + ";\n")
            LOG.write(code_result.imports.replace("\\n", "\n"))
            LOG.write('\n\n')
            file.write("package com.test.generation." + str(class_type) + ";\n")
            file.write(code_result.imports.replace("\\n", "\n"))
            file.write('\n\n')
        LOG.write(code_result.contents.replace("\\n", "\n"))
        file.write(code_result.contents.replace("\\n", "\n"))
    return True
