import io
import shutil
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

from class_definition_generator import generate_class_definition
from javaFileWriter import javaFileWriter
from java_grammar.java_test import analysis_single_file
from utils import *


class code_generator:
    def __init__(self, root="./test/generation", requirement_file_path="example_requirements.yaml"):
        self.class_definitions = None
        self.code_storage = None
        self.max_level = None
        self.dependency_levels = None
        self.dependency_dict = None
        self.root = root
        if os.path.exists(root):
            shutil.rmtree(root)
        self.java_root = './test/generation/src/main/java'
        self.max_reflection = 10
        self.requirement_file = requirement_file_path
        self.rag = get_rag()
        # self.logger = open(os.path.join(root, 'log.txt'), 'w')
        self.logger = get_logger()
        self.dependency_result = None
        self.finished = False
        self.result_pointer = int(0)

    def generate(self):
        self.finished = False
        try:
            self.logger.write("analysing requirement:\n")
            generate_class_definition(requirements_document_path=self.requirement_file)
            prompt = "Give me the dependency relationship of all following classes. For example, the class \"BookRepository\" " \
                     "depends on the class \"Book\", and the class \"Book\" doesn't depend on any other classes.\nClass data:" + \
                     get_definition_results(temp_file_path='tmp_class_definition.json')
            self.logger.write("asking for dependency result:\n")
            self.dependency_result = generation(prompt, all_dependency_relationships)
            self.dependency_dict, self.dependency_levels = determine_level(
                self.dependency_result.dict()['list_of_dependency_relationships'])
            self.max_level = max(level for _, level in self.dependency_levels)
            self.code_storage = {}
            self.class_definitions = json.loads(get_definition_results())
            self.logger.write("formatted class definition from LLM:\n")
            self.logger.write(self.class_definitions)
            self.logger.write("init AST-RAG for java library:\n")
            self.logger.write(self.rag.get_all_embedding())
            self.logger.write("start generating:\n")
            init_lib()
            for current_level in range(1, self.max_level + 1):
                for class_name, level in self.dependency_levels:
                    if current_level != level:
                        continue
                    try:
                        ret, message = self.first_generate(current_level, class_name)
                        if ret:
                            rag.batch_add_data(message.items())
                        else:
                            self.reflection_generation(current_level, class_name, message)
                    except Exception as e:
                        self.logger.write(f'Error while generating:{class_name}\n')
                        self.logger.write("please debug or write code by yourself\n")
        except Exception as e:
            self.logger.write('Error while generating\n')
        compress_directory(self.root, './test/zip/generation.zip')
        self.finished = True
        self.logger.write('end generating\n')

    def first_generate(self, current_level, class_name):
        self.logger.write(
            f"generating class: {class_name}, dependency:  {self.dependency_dict[class_name]}, level:{current_level}\n")
        prompt = class_generation_prompt(class_name, self.dependency_dict[class_name], self.code_storage)
        return self.post_process(prompt, class_name)

    def reflection_generation(self, current_level, class_name, message):
        for i in self.class_definitions:
            if i['class_name'] == class_name:
                current_class_type = i['class_type']
        directories = "com.test.generation".split('.')
        path = os.path.join(self.java_root, *directories, current_class_type, f"{class_name}.java")
        Path(path).unlink()
        flag = False
        for i in range(self.max_reflection):
            self.logger.write(
                f"reflection class: {class_name}, dependency:  {self.dependency_dict[class_name]}, level:{current_level}\n")
            prompt = class_reflection_prompt(class_name, self.code_storage[class_name], message,
                                             current_class_type)
            ret, message = self.post_process(prompt, class_name)
            if ret:
                rag.batch_add_data(message.items())
                flag = True
                break
        if flag:
            self.logger.write(f"You should fix the {class_name} by yourself")

    def post_process(self, prompt, class_name):
        self.code_storage[class_name] = generation(prompt, code_generation)

        # import dependencies
        for i in self.dependency_dict[class_name]:
            for j in self.class_definitions:
                if j['class_name'] == i:
                    current_class_type = j['class_type']
            self.code_storage[
                class_name].imports += "\nimport com.test.generation." + current_class_type + "." + i + ";"
        current_class_type = ""
        for i in self.class_definitions:
            if i['class_name'] == class_name:
                current_class_type = i['class_type']
        if current_class_type == classType.model or current_class_type == "model":
            # solve getter/setter
            self.code_storage[class_name].imports += "\nimport lombok.Data;"
            self.code_storage[class_name].contents = "\n@Data\n" + self.code_storage[class_name].contents.lstrip()

        # monkey patch
        if "package" in self.code_storage[class_name].contents.lstrip():
            if self.code_storage[class_name].contents[:7] == "\n@Data\n": self.code_storage[class_name].contents = \
                self.code_storage[
                    class_name].contents[
                7:]
            javaFileWriter(self.java_root, class_name, self.code_storage[class_name], current_class_type,
                           overwrite=True,
                           ignore_package_imports=True)
        else:
            javaFileWriter(self.java_root, class_name, self.code_storage[class_name], current_class_type,
                           overwrite=True)

        directories = "com.test.generation".split('.')
        path = os.path.join(self.java_root, *directories, current_class_type, f"{class_name}.java")
        ret, message = analysis_single_file(path)
        if ret:
            self.logger.write(f"success generating class:{class_name}\n")
        else:
            self.logger.write(f"Error generating class:{class_name}\n with message:\n")
            for msg in message:
                self.logger.write(msg + '\n')
        return ret, message

    def get_cached_result(self):
        max_len = len(self.logger.cache)
        prev = self.result_pointer
        self.result_pointer = int(min(max_len, prev + 20))
        if self.result_pointer > prev:
            return self.logger.cache[prev: self.result_pointer]
        else:
            return "\n"


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


def compress_directory(source_dir, zip_path):
    """
    压缩指定目录中的所有文件并保存为 zip 文件。

    参数:
        source_dir (str): 要压缩的目录路径。
        zip_path (str): 压缩文件保存的完整路径（包括 .zip 文件名）。
    """
    # 确保目标目录存在
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)

    # 创建 zip 文件并写入
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(source_dir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)

    print(f"压缩完成，文件保存在：{zip_path}")


app = Flask(__name__)
CORS(app)  # 开放所有跨域请求
UPLOAD_FOLDER = './uploads'
RESULT_FOLDER = './results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
current_file = "example_requirements.yaml"


@app.route('/submit-requirement-files', methods=['POST'])
def submit_requirement_files():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    global current_file
    current_file = filepath
    file.save(filepath)
    return jsonify({"message": f"File {file.filename} uploaded successfully"}), 200


@app.route('/download-result', methods=['GET'])
def download_result():
    result_zip_path = './test/zip/generation.zip'

    if os.path.exists(result_zip_path):
        return send_file(result_zip_path, as_attachment=True)
    else:
        # 返回一个空 zip 文件
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zipf:
            pass
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name='empty.zip', mimetype='application/zip')


# @app.route('/view-result', methods=['GET'])
# def view_result():
#     def generate():
#         executor = ThreadPoolExecutor(max_workers=5)
#         generator = code_generator()
#         executor.submit(code_generator.generate, generator)
#         while not generator.finished:
#             yield generator.get_cached_result().encode('utf-8')
#         return download_result
#
#
#     return Response(generate(), mimetype='text/event-stream')
from flask import Response

# @app.route('/view-result', methods=['GET'])
# def view_result():
#     def generate():
#         if current_file is None:
#             yield "data: [DONE]\n\n"
#         generator = code_generator(requirement_file_path=current_file)
#         generator.generate()  # 同步生成
#
#         for chunk in generator.get_cached_result_stream():
#             print('[SSE CHUNK]', chunk)  # ✅后端调试日志
#             yield f"{chunk}\n\n"
#
#         zip_path = os.path.join(RESULT_FOLDER, 'result.zip')
#         if os.path.exists(zip_path):
#             zip_url = 'http://localhost:9876/download-result'
#             yield f"data: [ZIP]{zip_url}\n\n"
#
#         yield "data: [DONE]\n\n"
#
#     return Response(generate(), mimetype='text/event-stream')  # ✅正确类型
# from flask import Response
import time


@app.route('/view-result', methods=['GET'])
def view_result():
    def generate():
        executor = ThreadPoolExecutor(max_workers=5)
        generator = code_generator()
        executor.submit(code_generator.generate, generator)
        while not generator.finished:
            text = generator.get_cached_result()
            while text == '\n':
                text = generator.get_cached_result()
                time.sleep(1)
            yield f"data: {text.encode('utf-8')}\n\n"
        # 设置伪数据块
        # chunks = code_generator(requirement_file_path=current_file)
        # chunks = ['流式内容1...', '流式内容2...', '流式内容3...']
        # for chunk in chunks:
        #     yield f"data: {chunk}\n\n"
        #     time.sleep(1)
        #
        # 推送 ZIP 下载链接和结束标志
        zip_url = 'http://localhost:9876/download-result'
        yield f"data: [ZIP]{zip_url}\n\n"
        yield "data: [DONE]\n\n"

    return Response(generate(), mimetype='text/event-stream')


@app.route('/re-generate-single-file-with-comment', methods=['POST'])
def regenerate_file():
    data = request.get_json()
    filename = data.get('filename')
    prompt = data.get('prompt')

    if not filename or not prompt:
        return jsonify({"error": "Missing filename or prompt"}), 400

    # 模拟文件生成逻辑（这里只是写入一段字符串）
    filepath = os.path.join(RESULT_FOLDER, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Regenerated based on prompt:\n# {prompt}\n\n# Your updated code goes here...\n")

    return jsonify({"message": f"File {filename} regenerated successfully"}), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9876)
