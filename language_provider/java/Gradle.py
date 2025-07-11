import os
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

from language_provider.java.JavaAnalyzer import analysis_java_files

project_dir = r"C:\Users\bcjPr\Desktop\gtnh\Twist-Space-Technology-Mod"


class DependencyAnalyzer:
    def __init__(self):
        self.temp_dirs = []
        self.gradle_cache = Path(
            os.environ.get('GRADLE_HOME', r'C:\Users\bcjPr\.gradle')) / 'caches/modules-2/files-2.1'
        print('project gradle cached lib in ', self.gradle_cache)

    def analyze_dependencies(self):
        """解析项目依赖并进行分析"""
        # 生成依赖树
        _generate_dependency_tree()

        # 解析依赖坐标
        dependencies = _parse_dependencies()

        # 分析每个依赖
        dependency_methods = []
        for dep in dependencies:
            dep_methods = self._process_dependency(dep)
            dependency_methods.extend(dep_methods)

        return dependency_methods

    def _process_dependency(self, dependency):
        """处理单个依赖"""
        source_jar = self._find_source_jar(dependency)
        if source_jar:
            print(f"source jar path:{source_jar}")
            return self._analyze_jar(source_jar, is_source=True)

        binary_jar = self._find_binary_jar(dependency)
        if binary_jar:
            print(f"binary jar path:{binary_jar}")
            return self._analyze_jar(binary_jar, is_source=False)

        print(f"⚠️ Dependency not found: {dependency}")
        return {}

    def _find_source_jar(self, dependency):
        """查找源码JAR"""
        parts = dependency.split(':')
        group, artifact, version = parts[:3]
        search_path = self.gradle_cache / group / artifact / version

        return next(search_path.glob(f'**/{artifact}-{version}-sources.jar'), None)

    def _find_binary_jar(self, dependency):
        parts = dependency.split(':')
        group, artifact, version = parts[:3]
        #         group_path = group.replace('.', '/')

        search_path = self.gradle_cache / group / artifact / version
        # 匹配主JAR和带分类器的JAR
        for jar in search_path.glob(f"**/{artifact}-{version}*.jar"):
            if not any(s in jar.name.lower() for s in ['-sources', '-javadoc']):
                return jar
        return None

    def _analyze_jar(self, jar_path, is_source=True):
        """分析JAR文件（修复方法调用）"""
        temp_dir = Path(f"syntax_db/temp_{jar_path.stem}")
        self.temp_dirs.append(temp_dir)
        if not os.path.exists(temp_dir):
            temp_dir.mkdir(parents=True, exist_ok=True)
            # print(is_source)
            if is_source:
                try:
                    with zipfile.ZipFile(jar_path) as zip_ref:
                        zip_ref.extractall(temp_dir)
                except zipfile.BadZipFile:
                    print(f"无效的ZIP文件: {jar_path}")
                    return {}
            else:
                print(f"反编译jar文件:{jar_path}")
                _decompile_jar(jar_path, temp_dir)

        # 调用统一的分析函数
        return analysis_java_files(temp_dir)

    def cleanup(self):
        return
        """清理临时文件"""
        for d in self.temp_dirs:
            shutil.rmtree(d, ignore_errors=True)


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


def _decompile_jar(jar_path, output_dir):
    # if os.path.exists(output_dir):
    #     return
    """使用JD-CLI反编译"""
    jd_cli_path = Path('jd-cli-1.2.0.jar')
    if not jd_cli_path.exists():
        raise FileNotFoundError("JD-CLI not found, download from https://github.com/intoolswetrust/jd-cli")

    subprocess.run([
        'java', '-jar', str(jd_cli_path),
        str(jar_path),
        '--outputDir', str(output_dir),
    ], check=True, timeout=120)


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
