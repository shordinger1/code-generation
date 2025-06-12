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
        method = analyzer.extract_class_info()
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
            return JavaClass.read(tempfile)
        """处理单个Java文件的线程任务"""
        try:
            analyzer = JavaAnalyzer(str(file_path))
            if analyzer.analyze_syntax():
                # print(f"成功分析: {file_path}")
                method = analyzer.extract_class_info()
                method.write(tempfile)
                return method
            print(f"语法错误: {file_path}")
            return JavaClass(file_path)
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


class JavaClass:
    def __init__(self, file_name, methods=None, abstract_methods=None, parameters=None, temp_file=""):
        self.file_name = file_name
        self.methods = methods if methods is not None else []
        self.abstract_methods = abstract_methods if abstract_methods is not None else []
        self.parameters = parameters if parameters is not None else []
        self.temp_file = temp_file

    def get(self):
        return {
            "file": str(self.file_name),
            "methods": [*self.methods, *self.abstract_methods],
            # "abstract_methods": self.abstract_methods,
            "parameters": self.parameters,
        }

    @classmethod
    def read(cls, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(
            data["file"],
            data.get("methods", []),
            data.get("abstract_methods", []),
            data.get("parameters", []),
            file_path
        )

    def write(self, file_path):
        self.temp_file = file_path
        data = self.get()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)


class SyntaxErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"Line {line}:{column} {msg}")


class JavaAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.errors = []
        self.methods = []
        self.abstract_methods = []
        self.parameters = []

        self.input_stream = FileStream(file_path, encoding='utf-8')
        self.lexer = JavaLexer(self.input_stream)
        self.token_stream = CommonTokenStream(self.lexer)
        self.parser = JavaParser(self.token_stream)

        self.error_listener = SyntaxErrorListener()
        self.parser.removeErrorListeners()
        self.parser.addErrorListener(self.error_listener)

    def analyze_syntax(self):
        try:
            self.tree = self.parser.compilationUnit()
            self.errors = self.error_listener.errors
            return len(self.errors) == 0
        except Exception as e:
            self.errors.append(f"Critical error: {str(e)}")
            return False

    def extract_class_info(self):
        class ClassInfoExtractor(JavaParserListener):
            def __init__(self, token_stream):
                self.token_stream = token_stream
                self.methods = []
                self.abstract_methods = []
                self.parameters = []
                self.current_class = ""
                self.in_interface = False

            def enterClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
                self.current_class = ctx.identifier().getText()
                self.in_interface = False

            def enterInterfaceDeclaration(self, ctx: JavaParser.InterfaceDeclarationContext):
                self.current_class = ctx.identifier().getText()
                self.in_interface = True

            def enterFieldDeclaration(self, ctx: JavaParser.FieldDeclarationContext):
                """提取类属性"""
                field_type = ctx.typeType().getText()

                for var in ctx.variableDeclarators().variableDeclarator():
                    field_name = var.variableDeclaratorId().getText()

                    modifiers = []
                    if ctx.parentCtx and isinstance(ctx.parentCtx, JavaParser.ClassBodyDeclarationContext):
                        modifier_list = ctx.parentCtx.modifier()
                        for mod in modifier_list:
                            modifiers.append(mod.getText())

                    self.parameters.append({
                        "name": field_name,
                        "type": field_type,
                        "modifiers": modifiers
                    })

            @staticmethod
            def camel_to_words(s):
                if not s:
                    return ""
                words = []
                start = 0  # 当前单词的起始位置
                n = len(s)

                for i in range(1, n):
                    if s[i].isupper():
                        # 当前字符是大写字母，且满足以下条件之一则拆分：
                        # 1. 下一个字符是小写字母（如：HTTPRequest的P后）
                        # 2. 前一个字符是小写字母（如：myClass的y后）
                        if (i + 1 < n and s[i + 1].islower()) or s[i - 1].islower():
                            words.append(s[start:i].lower())
                            start = i
                words.append(s[start:].lower())  # 添加最后一个单词
                return " ".join(words)

            # 测试
            # print(camel_to_words("MyClassFunction"))  # 输出: "my class function"
            # print(camel_to_words("HTTPRequest"))  # 输出: "http request"
            # print(camel_to_words("SimpleHTTPServer"))  # 输出: "simple http server"
            # print(camel_to_words("getHTTPResponse"))  # 输出: "get http response"

            def enterMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
                """处理类中的方法"""
                method_name = f"{self.current_class} {ctx.identifier().getText()}"
                method_name = ClassInfoExtractor.camel_to_words(method_name)
                return_type_ctx = ctx.typeTypeOrVoid()
                return_type = return_type_ctx.getText() if return_type_ctx else 'void'

                parameters = []
                params_ctx = ctx.formalParameters()
                if params_ctx.formalParameterList():
                    for param in params_ctx.formalParameterList().formalParameter():
                        param_type = param.typeType().getText()
                        param_name = param.variableDeclaratorId().getText()
                        parameters.append({
                            "type": param_type,
                            "name": param_name
                        })

                modifiers = []
                if ctx.parentCtx and isinstance(ctx.parentCtx, JavaParser.ClassBodyDeclarationContext):
                    modifier_list = ctx.parentCtx.modifier()
                    for mod in modifier_list:
                        modifiers.append(mod.getText())

                # 判断是否为抽象方法
                is_abstract = 'abstract' in modifiers

                # 获取完整方法代码
                start = ctx.start.tokenIndex
                stop = ctx.stop.tokenIndex
                method_code = self.token_stream.getText(start, stop)

                method_info = {
                    "name": method_name,
                    "return_type": return_type,
                    "parameters": parameters,
                    "modifiers": modifiers,
                    "code": method_code,
                    "is_abstract": is_abstract
                }

                if is_abstract:
                    self.abstract_methods.append(method_info)
                else:
                    self.methods.append(method_info)

            def enterInterfaceMethodDeclaration(self, ctx: JavaParser.InterfaceMethodDeclarationContext):
                """处理接口中的方法 - 修正后的版本"""
                # 直接访问接口方法声明的组成部分
                body_ctx = ctx.interfaceCommonBodyDeclaration()
                if not body_ctx:
                    return

                method_name = f"{self.current_class} {body_ctx.identifier().getText()}"
                method_name = ClassInfoExtractor.camel_to_words(method_name)
                return_type_ctx = body_ctx.typeTypeOrVoid()
                return_type = return_type_ctx.getText() if return_type_ctx else 'void'

                parameters = []
                if body_ctx.formalParameters().formalParameterList():
                    for param in body_ctx.formalParameters().formalParameterList().formalParameter():
                        param_type = param.typeType().getText()
                        param_name = param.variableDeclaratorId().getText()
                        parameters.append({
                            "type": param_type,
                            "name": param_name
                        })

                # 接口方法没有显式的修饰符节点，但可能有注解
                modifiers = []

                # 检查方法是否有默认实现
                is_abstract = 'abstract' in modifiers or self.in_interface

                # 获取完整方法代码
                start = ctx.start.tokenIndex
                stop = ctx.stop.tokenIndex
                method_code = self.token_stream.getText(start, stop)

                method_info = {
                    "name": method_name,
                    "return_type": return_type,
                    "parameters": parameters,
                    "modifiers": modifiers,
                    "code": method_code,
                    "is_abstract": is_abstract
                }

                if is_abstract:
                    self.abstract_methods.append(method_info)
                else:
                    self.methods.append(method_info)

        extractor = ClassInfoExtractor(self.token_stream)
        walker = ParseTreeWalker()
        walker.walk(extractor, self.tree)

        self.methods = extractor.methods
        self.abstract_methods = extractor.abstract_methods
        self.parameters = extractor.parameters

        return JavaClass(
            self.file_path,
            methods=self.methods,
            abstract_methods=self.abstract_methods,
            parameters=self.parameters
        )
