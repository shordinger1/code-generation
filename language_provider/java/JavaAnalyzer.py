import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from antlr4.error.ErrorListener import ErrorListener
from language_provider.java.JavaLexer import JavaLexer
from language_provider.java.JavaParser import JavaParser
from language_provider.java.JavaParserListener import JavaParserListener


def analysis_java_file(file_path):
    analyzer = JavaAnalyzer(str(file_path))
    is_valid = analyzer.analyze_syntax()
    if not is_valid:
        msg = []
        for error in analyzer.errors:
            msg.append(f"Line {error['line']}:{error['column']} - {error['type']} - {error['message']}")
        return False, msg
    else:
        method = analyzer.extract_methods()
        return True, method


def analysis_java_files(root_dir):
    root_dir = Path(root_dir)
    methods = []
    java_files = list(root_dir.glob('**/*.java'))
    rt = str(root_dir).split("\\")[-1]
    os.makedirs(f"temp/{rt}", exist_ok=True)

    def process_file(file_path):
        name = str(file_path).split(rt)[-1][1:-5].replace("\\", "-")
        tempfile = f"temp/{rt}/{name}.json"
        if os.path.exists(tempfile):
            # print(f"获取缓存文件：{file_path}")
            return JavaMethods.read(tempfile)
        """处理单个Java文件的线程任务"""
        try:
            analyzer = JavaAnalyzer(str(file_path))
            if analyzer.analyze_syntax():
                # print(f"成功分析: {file_path}")
                method = analyzer.extract_methods()
                method.write(tempfile)
                return method
            print(f"语法错误: {file_path}")
            return {}
        except Exception as e:
            print(f"处理失败 {file_path}: {str(e)}")
            return {}
        except UnicodeDecodeError:
            print(f"编码错误: {file_path}")
            return {}

    # 创建线程池 (建议根据CPU核心数调整max_workers)
    with ThreadPoolExecutor(max_workers=16) as executor:
        # 提交所有任务
        futures = {executor.submit(process_file, f): f for f in java_files}

        # 按完成顺序处理结果
        for future in as_completed(futures):
            file_path = futures[future]
            try:
                result = future.result()
                methods.append(result)
            except Exception as e:
                print(f"结果合并异常 {file_path}: {str(e)}")

    return methods


class JavaMethods:
    def __init__(self, file_name, methods, temp_file=""):
        self.file_name = file_name
        self.methods = methods
        self.temp_file = temp_file

    def get(self):
        return {
            "file": self.file_name,
            "class_methods": self.methods,
            # "temp_file": self.temp_file
        }

    @classmethod
    def read(cls, file_path):
        """从JSON文件读取数据并创建JavaMethods对象"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(data["file"], data["class_methods"], file_path)

    def write(self, file_path):
        """将JavaMethods对象写入JSON文件，使用类中的file_name作为路径"""
        self.temp_file = file_path
        data = self.get()

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)


class JavaAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.errors = []
        self.methods = {}

        # 初始化解析器
        self.input_stream = FileStream(file_path, encoding='utf-8')
        self.lexer = JavaLexer(self.input_stream)
        self.token_stream = CommonTokenStream(self.lexer)
        self.parser = JavaParser(self.token_stream)

        # 自定义错误监听器
        self.error_listener = SyntaxErrorListener()
        self.parser.removeErrorListeners()
        self.parser.addErrorListener(self.error_listener)

    def analyze_syntax(self):
        """执行语法分析"""
        try:
            self.tree = self.parser.compilationUnit()
            self.errors = self.error_listener.errors
            return len(self.errors) == 0
        except Exception as e:
            self.errors.append(f"Critical error: {str(e)}")
            return False

    def extract_methods(self):
        """提取类方法信息"""

        class MethodExtractor(JavaParserListener):
            def __init__(self, token_stream):
                self.token_stream = token_stream
                self.methods = {}
                self.current_class = ""

            def enterClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
                self.current_class = ctx.identifier().getText()

            def enterMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
                method_name = ctx.identifier().getText()

                # 获取完整方法代码
                start = ctx.start.tokenIndex
                stop = ctx.stop.tokenIndex
                method_code = self.token_stream.getText(start, stop)

                full_name = f"{self.current_class}.{method_name}"
                self.methods[full_name] = method_code

        extractor = MethodExtractor(self.token_stream)
        walker = ParseTreeWalker()
        walker.walk(extractor, self.tree)

        self.methods = extractor.methods
        return JavaMethods(self.file_path, self.methods)


class SyntaxErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_type = "Syntax Error"
        if "missing" in msg:
            error_type = "Missing Token"
        elif "extraneous" in msg:
            error_type = "Extraneous Token"

        self.errors.append({
            "line": line,
            "column": column,
            "message": msg,
            "type": error_type
        })
