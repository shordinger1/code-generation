import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from antlr4.error.ErrorListener import ErrorListener
from language_provider.python.Python3Lexer import Python3Lexer
from language_provider.python.Python3Parser import Python3Parser
from language_provider.python.Python3ParserListener import Python3ParserListener


def analysis_python_file(file_path):
    analyzer = PythonAnalyzer(str(file_path))
    is_valid = analyzer.analyze_syntax()
    if not is_valid:
        msg = []
        for error in analyzer.errors:
            msg.append(f"Line {error['line']}:{error['column']} - {error['type']} - {error['message']}")
        return False, msg
    else:
        module_info = analyzer.extract_module_info()
        return True, module_info


def analysis_python_files(root_dir):
    root_dir = Path(root_dir)
    modules = []
    py_files = list(root_dir.glob('**/*.py'))
    rt = str(root_dir).split(os.sep)[-1]
    os.makedirs(f"temp/{rt}", exist_ok=True)

    def process_file(file_path):
        name = str(file_path).split(rt)[-1][1:-3].replace(os.sep, "-")
        tempfile = f"temp/{rt}/{name}.json"
        if os.path.exists(tempfile):
            return PythonModule.read(tempfile)

        try:
            analyzer = PythonAnalyzer(str(file_path))
            if analyzer.analyze_syntax():
                module = analyzer.extract_module_info()
                module.write(tempfile)
                return module
            print(f"语法错误: {file_path}")
            return PythonModule(file_path)
        except Exception as e:
            print(f"处理失败 {file_path}: {str(e)}")
            return PythonModule(file_path)
        except UnicodeDecodeError:
            print(f"编码错误: {file_path}")
            return PythonModule(file_path)

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(process_file, f): f for f in py_files}

        for future in as_completed(futures):
            file_path = futures[future]
            try:
                result = future.result()
                modules.append(result)
            except Exception as e:
                print(f"结果合并异常 {file_path}: {str(e)}")

    return modules


class PythonModule:
    def __init__(self, file_name, functions=None, classes=None, imports=None, temp_file=""):
        self.file_name = file_name
        self.functions = functions if functions is not None else []
        self.classes = classes if classes is not None else []
        self.imports = imports if imports is not None else []
        self.temp_file = temp_file

    def get(self):
        return {
            "file": str(self.file_name),
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports
        }

    @classmethod
    def read(cls, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(
            data["file"],
            data.get("functions", []),
            data.get("classes", []),
            data.get("imports", []),
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
        self.errors.append({
            "line": line,
            "column": column,
            "type": "SyntaxError",
            "message": msg
        })


class PythonAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.errors = []
        self.functions = []
        self.classes = []
        self.imports = []

        self.input_stream = FileStream(file_path, encoding='utf-8')
        self.lexer = Python3Lexer(self.input_stream)
        self.token_stream = CommonTokenStream(self.lexer)
        self.parser = Python3Parser(self.token_stream)

        self.error_listener = SyntaxErrorListener()
        self.parser.removeErrorListeners()
        self.parser.addErrorListener(self.error_listener)

    def analyze_syntax(self):
        try:
            self.tree = self.parser.file_input()
            self.errors = self.error_listener.errors
            return len(self.errors) == 0
        except Exception as e:
            self.errors.append({
                "line": 0,
                "column": 0,
                "type": "CriticalError",
                "message": str(e)
            })
            return False

    def extract_module_info(self):
        class ModuleInfoExtractor(Python3ParserListener):
            def __init__(self, token_stream):
                self.token_stream = token_stream
                self.functions = []
                self.classes = []
                self.imports = []
                self.current_class = None
                self.current_function = None
                self.in_class = False
                self.in_function = False

            def enterImport_stmt(self, ctx: Python3Parser.Import_stmtContext):
                import_text = self.token_stream.getText(ctx)
                self.imports.append(import_text)

            def enterFuncdef(self, ctx: Python3Parser.FuncdefContext):
                func_name = ctx.name().getText()
                self.current_function = {
                    "name": func_name,
                    "parameters": [],
                    "decorators": [],
                    "return_type": None,
                    "code": ""
                }
                self.in_function = True

                # 获取装饰器
                if ctx.decorators():
                    decorators = ctx.decorators().getText().split('@')[1:]
                    self.current_function["decorators"] = [d.strip() for d in decorators]

                # 获取参数
                if ctx.typedargslist():
                    params = ctx.typedargslist().getText().split(',')
                    for param in params:
                        if '=' in param:
                            name, default = param.split('=', 1)
                            self.current_function["parameters"].append({
                                "name": name.strip(),
                                "default": default.strip()
                            })
                        else:
                            self.current_function["parameters"].append({
                                "name": param.strip()
                            })

                # 获取返回类型注解
                if ctx.test():
                    self.current_function["return_type"] = ctx.test().getText()

            def exitFuncdef(self, ctx: Python3Parser.FuncdefContext):
                start = ctx.start.tokenIndex
                stop = ctx.stop.tokenIndex
                self.current_function["code"] = self.token_stream.getText(start, stop)

                if self.in_class:
                    # 如果是类中的方法
                    for cls in self.classes:
                        if cls["name"] == self.current_class:
                            cls["methods"].append(self.current_function)
                            break
                else:
                    # 模块级函数
                    self.functions.append(self.current_function)

                self.in_function = False
                self.current_function = None

            def enterClassdef(self, ctx: Python3Parser.ClassdefContext):
                class_name = ctx.name().getText()
                new_class = {
                    "name": class_name,
                    "bases": [],
                    "attributes": [],
                    "methods": [],
                    "code": ""
                }

                # 获取基类
                if ctx.arglist():
                    bases = ctx.arglist().getText().split(',')
                    new_class["bases"] = [base.strip() for base in bases]

                self.classes.append(new_class)
                self.current_class = class_name
                self.in_class = True

            def exitClassdef(self, ctx: Python3Parser.ClassdefContext):
                start = ctx.start.tokenIndex
                stop = ctx.stop.tokenIndex
                self.classes[-1]["code"] = self.token_stream.getText(start, stop)
                self.in_class = False
                self.current_class = None

            def enterExpr_stmt(self, ctx: Python3Parser.Expr_stmtContext):
                if self.in_class and not self.in_function:
                    # 类属性定义
                    if ctx.testlist_star_expr() and ctx.assign_part():
                        var_name = ctx.testlist_star_expr().getText()
                        value = ctx.assign_part().getText()
                        self.classes[-1]["attributes"].append({
                            "name": var_name,
                            "value": value
                        })

        extractor = ModuleInfoExtractor(self.token_stream)
        walker = ParseTreeWalker()
        walker.walk(extractor, self.tree)

        self.functions = extractor.functions
        self.classes = extractor.classes
        self.imports = extractor.imports

        return PythonModule(
            self.file_path,
            functions=self.functions,
            classes=self.classes,
            imports=self.imports
        )