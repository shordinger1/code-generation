import os
import shutil

from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener

from java_grammar.JavaLexer import JavaLexer
from java_grammar.JavaParser import JavaParser
from java_grammar.JavaParserListener import JavaParserListener

from log import get_logger

LOG = get_logger()


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
        return self.methods


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


def analysis_java_files(root_dir):
    methods = dict()
    # 确保输出目录存在
    for foldername, subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            try:
                if filename.endswith('.java'):
                    src_path = os.path.join(foldername, filename)
                    analyzer = JavaAnalyzer(src_path)
                    is_valid = analyzer.analyze_syntax()
                    if not is_valid:
                        LOG.write(f"syntax error detected：{src_path}\n")
                        for error in analyzer.errors:
                            LOG.write(f"Line {error['line']}:{error['column']} - {error['type']} - {error['message']}")
                    mtd = analyzer.extract_methods()
                    methods.update(mtd)
                    LOG.write(f"extracted abstract syntax tree from {filename}\n")
                    # for m in mtd:
                    #     LOG.write(analyzer.extract_methods())
            except UnicodeEncodeError:
                LOG.write("Error occurred while decode characters\n")
                continue
                # methods.update()
    return methods


def analysis_single_file(file_path):
    analyzer = JavaAnalyzer(file_path)
    is_valid = analyzer.analyze_syntax()

    if not is_valid:
        message = []
        for error in analyzer.errors:
            message.append(f"Line {error['line']}:{error['column']} - {error['type']} - {error['message']}")
        return False, message
    else:
        return True, analyzer.extract_methods()


if __name__ == "__main__":
    analysis_java_files("../spring-lib")
