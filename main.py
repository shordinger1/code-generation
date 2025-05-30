import os
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from Agent.minecraft.mod import minecraft_mod
from java_grammar.JavaAnalyzer import analysis_java_files

project_dir = r"C:\Users\bcjPr\Desktop\gtnh\Twist-Space-Technology-Mod"


def _decompile_jar(jar_path, output_dir):
    if os.path.exists(output_dir):
        return
    """使用JD-CLI反编译"""
    jd_cli_path = Path('jd-cli.jar')
    if not jd_cli_path.exists():
        raise FileNotFoundError("JD-CLI not found, download from https://github.com/intoolswetrust/jd-cli")

    subprocess.run([
        'java', '-jar', str(jd_cli_path),
        '--outputDir', str(output_dir),
        '--srcFile', str(jar_path)
    ], check=True)


def _generate_dependency_tree():
    """生成Gradle依赖树"""
    print()
    subprocess.run(
        [f'{project_dir}/gradlew.bat',
         'dependencies', '--configuration', 'compileClasspath'],
        cwd=project_dir,
        check=True,
        stdout=subprocess.DEVNULL
    )


def _parse_dependencies():
    """解析依赖树文件"""
    dependencies = set()
    dep_tree_path = Path(project_dir) / 'dependencies.txt'

    with open(dep_tree_path, 'r') as f:
        pattern = r'([\w\.-]+:[\w\.-]+:[\w\.-]+)'
        for line in f:
            matches = re.findall(pattern, line)
            for match in matches:
                if ' -> ' in match:
                    actual = match.split(' -> ')[1]
                    dependencies.add(actual)
                else:
                    dependencies.add(match)
    return sorted(dependencies)


class DependencyAnalyzer:
    def __init__(self):
        self.temp_dirs = []
        self.gradle_cache = Path(
            os.environ.get('GRADLE_HOME', r'C:\Users\bcjPr\.gradle')) / 'caches/modules-2/files-2.1'
        print(self.gradle_cache)

    def analyze_dependencies(self):
        """解析项目依赖并进行分析"""
        # 生成依赖树
        _generate_dependency_tree()

        # 解析依赖坐标
        dependencies = _parse_dependencies()

        # 分析每个依赖
        dependency_methods = {}
        for dep in dependencies:
            dep_methods = self._process_dependency(dep)
            dependency_methods.update(dep_methods)

        return dependency_methods

    def _process_dependency(self, dependency):
        """处理单个依赖"""
        source_jar = self._find_source_jar(dependency)
        if source_jar:
            return self._analyze_jar(dependency, source_jar, is_source=True)

        binary_jar = self._find_binary_jar(dependency)
        if binary_jar:
            return self._analyze_jar(dependency, binary_jar, is_source=False)

        print(f"⚠️ Dependency not found: {dependency}")
        return {}

    def _find_source_jar(self, dependency):
        """查找源码JAR"""
        parts = dependency.split(':')
        group, artifact, version = parts[:3]
        search_path = self.gradle_cache / group / artifact / version
        print(f"source jar path:{search_path}")
        return next(search_path.glob(f'**/{artifact}-{version}-sources.jar'), None)

    def _find_binary_jar(self, dependency):
        parts = dependency.split(':')
        group, artifact, version = parts[:3]
        #         group_path = group.replace('.', '/')

        search_path = self.gradle_cache / group / artifact / version
        print(f"binary jar path:{search_path}")
        # 匹配主JAR和带分类器的JAR
        for jar in search_path.glob(f"**/{artifact}-{version}*.jar"):
            if not any(s in jar.name.lower() for s in ['-sources', '-javadoc']):
                return jar
        return None

    def _analyze_jar(self, dependency, jar_path, is_source=True):
        """分析JAR文件（修复方法调用）"""
        parts = dependency.split(':')
        group, artifact, version = parts[:3]
        temp_dir = Path(f"syntax_db/temp_{jar_path.stem}")
        self.temp_dirs.append(temp_dir)
        if not os.path.exists(temp_dir):
            temp_dir.mkdir(parents=True, exist_ok=True)

            # 解压JAR文件
            try:
                with zipfile.ZipFile(jar_path) as zip_ref:
                    zip_ref.extractall(temp_dir)
            except zipfile.BadZipFile:
                print(f"无效的ZIP文件: {jar_path}")
                return {}
        # 调用统一的分析函数
        return analysis_java_files(temp_dir)

    def _decompile_and_analyze(self, jar_path):
        """反编译并分析二进制JAR"""
        temp_dir = Path(f"syntax_db/temp_decompiled_{jar_path.stem}")
        self.temp_dirs.append(temp_dir)

        try:
            # 使用JD-CLI反编译
            subprocess.run(
                ['java', '-jar', 'jd-cli.jar',
                 '--outputDir', str(temp_dir),
                 '--srcFile', str(jar_path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            print(f"反编译失败: {e.stderr.decode('utf-8', errors='replace')}")
            return {}

            # 调用统一分析函数
            # return self._analyze_java_files(temp_dir)

    def cleanup(self):
        return
        """清理临时文件"""
        for d in self.temp_dirs:
            shutil.rmtree(d, ignore_errors=True)


# 可扩展的标签配置（不区分大小写）
TAG_CONFIG = {
    'item': ['item', '物品', '道具'],
    'block': ['block', '方块', '地块'],
    'entity': ['entity', '实体'],
    'world': ['world', '世界', '维度'],
    'network': ['network', 'net', '网络']
}


class MethodClassifier:
    def __init__(self, output_root="classified_methods"):
        self.output_root = Path(output_root)
        self._prepare_dirs()

    def _prepare_dirs(self):
        """创建分类目录结构"""
        # 清空并重建根目录
        if self.output_root.exists():
            shutil.rmtree(self.output_root)
        self.output_root.mkdir()

        # 为每个标签创建目录
        for tag in TAG_CONFIG.keys():
            (self.output_root / tag).mkdir(parents=True)

        # 创建未分类目录
        (self.output_root / "_uncategorized").mkdir()

    def _detect_tags(self, class_name, method_code):
        """检测方法和类的标签"""
        detected_tags = set()

        # 检测类名标签（不区分大小写）
        lower_class = class_name.lower()
        for tag, keywords in TAG_CONFIG.items():
            if any(kw in lower_class for kw in [k.lower() for k in keywords]):
                detected_tags.add(tag)

        # 检测方法注释标签（支持多行注释）
        comment_pattern = r'/\*.*?@tag:\s*([\w\s,]+).*?\*/|//\s*@tag:\s*([\w\s,]+)'
        matches = re.findall(comment_pattern, method_code, re.DOTALL)
        for match in matches:
            tags = [t.strip().lower() for t in (match[0] or match[1]).split(',')]
            for t in tags:
                if t in TAG_CONFIG:
                    detected_tags.add(t)

        return list(detected_tags) if detected_tags else ['_uncategorized']

    def classify_methods(self, all_methods):
        """分类存储方法"""
        class_files = {}  # 记录类文件路径

        for method_signature, method_code in all_methods.items():
            # 解析类名和方法名
            class_name = '.'.join(method_signature.split('.')[:-1])
            method_name = method_signature.split('.')[-1]

            # 检测标签
            tags = self._detect_tags(class_name, method_code)

            # 写入对应目录
            for tag in tags:
                tag_dir = self.output_root / tag

                # 按类聚合到文件
                class_file = tag_dir / f"{class_name}.java"
                if class_file not in class_files:
                    class_files[class_file] = open(class_file, 'w', encoding='utf-8')

                # 写入方法代码
                header = f"// === Method: {method_name} ===\n"
                class_files[class_file].write(header + method_code + '\n\n')

        # 关闭所有文件
        for f in class_files.values():
            f.close()


def rag_init():
    project_methods = analysis_java_files(project_dir)
    project_methods = {}
    # 分析依赖库
    dep_analyzer = DependencyAnalyzer()
    try:
        dependency_methods = dep_analyzer.analyze_dependencies()
    finally:
        dep_analyzer.cleanup()

    # 合并结果
    all_methods = {**project_methods, **dependency_methods}
    classifier = MethodClassifier()
    classifier.classify_methods(all_methods)
    # 写入文件
    with open("rag.txt", "w", encoding="utf-8") as f:
        for k, v in all_methods.items():
            f.write(f"{k}\n:{v}\n\n")


def main():
    mod = minecraft_mod("AutoGeneratedMod", r"C:\Users\bcjPr\Desktop\gtnh\ExampleMod1.7.10", "shordinger")
    mod.generate_main_mod_file()
    mod.add_items('test item1', 'test item2', 'test item 3')
    mod.add_blocks('test block1','test block2','test block3')
    mod.write_items()
    mod.write_blocks()
    mod.write_lang_all()
    # mod.build()
    # mod.spotless()


# 分析项目代码


if __name__ == "__main__":
    main()
