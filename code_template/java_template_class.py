import os.path
import subprocess
import json
from chat.client import generation
from chat.model import code_generation, prompt_code_generation, prompt_code_reflection
from language_provider.java.JavaAnalyzer import analysis_java_file
from task_tree.TaskProcessor import TaskProcessor
from util import get_logger



class java_template_class(TaskProcessor):

    def __init__(self, project_root: str, class_name: str, package: str):
        super().__init__(class_name)

        class_name = ''.join(words.capitalize() for words in class_name.split(' ')) if ' ' in class_name else class_name
        self.description = None
        self.project_root = project_root
        self.class_name = class_name
        self.package = package
        self.imports = []
        self.code = None
        self.inited = False
        self.class_path = os.path.join(project_root, 'src', 'main', 'java', self.package)
        self.file_path = self.class_path + '/' + self.class_name + '.java'
        # self.read_from_file()
        print(f'java class inited as {class_name} in {self.class_path}')

    def print_info(self):
        print({
            'project_root': self.project_root,
            'class_name': self.class_name,
            'package': self.package,
            'imports': self.imports,
            'code': self.code,
            'inited': self.inited,
            'description': self.description
        })

    def save_to_json(self):
        """
        将类属性保存为JSON文件
        """
        # 创建保存目录
        root = os.path.join(self.project_root, 'generation')
        os.makedirs(root, exist_ok=True)

        # 构建文件路径
        file = os.path.join(root, self.class_name + '.json')

        # 准备要保存的数据
        data = {
            'project_root': self.project_root,
            'class_name': self.class_name,
            'package': self.package,
            'imports': self.imports,
            'code': self.code,
            'inited': self.inited,
            'description': self.description
            # 注意：class_path和file_path是计算属性，不需要保存
        }

        # 写入JSON文件
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        return file

    @classmethod
    def load_from_json(cls, json_file):
        """
        从JSON文件加载并创建新的类对象
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 创建新对象
        new_obj = type(cls.__name__, (), {})()

        # 设置基本属性
        new_obj.project_root = data['project_root']
        new_obj.class_name = data['class_name']
        new_obj.package = data['package']
        new_obj.imports = data['imports']
        new_obj.code = data['code']
        new_obj.inited = data['inited']
        new_obj.description = data['description']

        # 计算派生属性
        new_obj.class_path = os.path.join(
            new_obj.project_root, 'src', 'main', 'java', new_obj.package)
        new_obj.file_path = os.path.join(
            new_obj.class_path, new_obj.class_name + '.java')

        return new_obj

    def write_to_file(self):

        os.makedirs(self.class_path, exist_ok=True)
        with open(self.file_path, "w", encoding='utf-8') as f:
            f.write(self.formatted_code())

    @classmethod
    def create_from_java_file(cls, java_file_path: str, project_root: str, generation):
        """
        从Java文件创建并返回一个新的java_template_class对象

        Args:
            java_file_path: Java文件的完整路径
            project_root: 项目根目录路径
            generation: 用于生成描述的生成函数

        Returns:
            初始化好的java_template_class对象
        """
        # 读取Java文件内容
        with open(java_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析Java文件
        package_line, imports_list, class_code = split_java_file(content)

        # 从文件路径获取类名
        class_name = os.path.basename(java_file_path).replace('.java', '')

        # 从package行提取包名
        package = package_line.replace('package', '').replace(';', '').strip()

        # 创建新对象
        template = java_template_class(
            project_root=project_root,
            class_name=class_name,
            package=package
        )

        # 设置其他属性
        template.imports = imports_list
        template.code = class_code
        template.inited = True

        # 使用生成函数创建描述
        prompt = f"Generate a description for Java class {class_name} with package {package}"
        template.description = generation(prompt)

        return template

    def formatted_code(self):
        if self.code is None:
            return None
        package = self.package.replace('\\', '.').replace('/', '.')
        code = f"package {package};\n"
        for impt in self.imports:
            code += f"{impt}\n"
        code += f"{self.code}\n"
        return code

    def add_import(self, *imports):
        # Should resolve imports from RAG?
        for impt in imports:
            if impt not in self.imports:
                self.imports.append(impt)
        return self

    def init_code(self, code):
        if self.code is not None:
            print(f"code already inited for {self.file_path}/{self.class_name}, want convert?")
            return
        self.code = code

    def syntax_check(self):
        res, msg = analysis_java_file(self.file_path)
        if not res:
            self.log(f"syntax check failed while checking {self.file_path} \n Errors:\n {msg}")
        return res, msg

    def build_project(self):
        error = None
        try:
            result = subprocess.run(
                [f'{self.project_root}/gradlew.bat', 'build'],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,  # 分别捕获 stdout/stderr
                text=True,
                check=True
            )
            error = result.stderr
        except subprocess.CalledProcessError as e:
            error = e.stderr  # 失败时返回已捕获的输出
        return self.error_analysis(error)

    def error_analysis(self, error):
        # TODO
        return True, error

    def get_template(self):
        raise NotImplementedError()

    def analyze(self, **kwargs):
        raise NotImplementedError()

    def process(self, description, **kwargs):
        super().process(description)
        self.log(f"START AUTO PROCESSING FOR {self.file_path}:\n TASK DESCRIPTION:{description}\n processing:\n")

        if self.code is None:
            self.log("No template generated file detected, will generated by LLM\n")
        # rag_prompt = prompt_rag_question_generator(description)
        # rag_list = generation(rag_prompt, rag_problems)
        rag_code = []  # TODO
        # for problem in rag_list:
        #     score, key, value = RAG.enhanced_query(problem)[0]
        #     rag_code.append(value["class_methods"][key])
        template_code = self.get_template()

        if template_code is None:
            self.log("No template code detected, ignored\n")
        if rag_code is None:
            self.log("No RAG code detected, ignored\n")
        prompt = prompt_code_generation(description, self.formatted_code(), template_code, rag_code)
        chat_result = generation(prompt, code_generation)
        self.package = chat_result.package
        self.imports = chat_result.imports
        self.code = chat_result.contents
        self.write_to_file()
        retry = 0
        MAX_RETRY = 3
        res, msg = self.syntax_check()
        while retry < MAX_RETRY and res:
            retry += 1
            self.log(f"syntax Error occurred, retry with reflection module! retry:{retry}")
            prompt = prompt_code_reflection(description, msg, self.formatted_code(), template_code, rag_code)
            chat_result = generation(prompt, code_generation)
            self.package = chat_result.package
            self.imports = chat_result.imports
            self.code = chat_result.contents
            self.write_to_file()
            res, msg = self.syntax_check()
        retry = 0
        res, msg = self.build_project()
        while retry < MAX_RETRY and res:
            retry += 1
            self.log(f"Compile Error occurred, retry with reflection module! retry:{retry}")
            prompt = prompt_code_reflection(description, msg, self.formatted_code(), template_code, rag_code)
            chat_result = generation(prompt, code_generation)
            self.package = chat_result.package
            self.imports = chat_result.imports
            self.code = chat_result.contents
            self.write_to_file()
            res, msg = self.build_project()


# def init_java_from_file(root, path: str):
#     if not path.endswith(".java"):
#         raise ValueError("This is not a java file!")
#     with open(path, "r") as f:
#         p, i, c = split_java_file(f.read())
#         p = p.replace(".", "/")
#         path = path.split("\\")
#         new_obj = java_template_class(root, )


def split_java_file(content: str) -> tuple:
    """
    分割Java源代码文件为package、imports和class三部分

    参数:
    content (str): Java源代码字符串

    返回:
    tuple: (package_line, imports_list, class_code)
      - package_line: 字符串，package行（包括换行符），无则为空字符串
      - imports_list: 字符串列表，所有import行（包括换行符）
      - class_code: 字符串，剩余代码
    """
    lines = content.splitlines(keepends=True)  # 保留行尾换行符
    package_line = ""
    imports_list = []
    class_lines = []
    in_import_section = True  # 标志是否仍在import部分
    line_count = 0
    # 处理package行
    if not lines:
        return None, None, None
    size = len(lines)
    while line_count < size and not lines[line_count].lstrip().startswith('package'):
        line_count += 1
    package_line = lines[line_count][7:-2]
    line_count += 1
    # 处理imports和class部分
    while line_count < size:
        line = lines[line_count]
        stripped = line.lstrip()  # 移除行首空白（保留行尾）

        if not in_import_section:
            # 已离开import部分，直接添加到class
            class_lines.append(line)
            continue

        if stripped.startswith('import'):
            # 找到import行
            imports_list.append(line[0:-1])
        elif stripped == '' or stripped.startswith('//') or stripped.startswith('/*'):
            # 空行或注释行，不打断import部分
            class_lines.append(line)
        else:
            # 遇到非import/空行/注释行，进入class部分
            in_import_section = False
            class_lines.append(line)
        line_count += 1

    class_code = ''.join(class_lines)
    return package_line, imports_list, class_code
