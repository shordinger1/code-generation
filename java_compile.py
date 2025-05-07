import subprocess
import os
from pathlib import Path

# 配置参数
project_path = Path("./test/generation")  # 替换为你的项目路径
error_log_path = Path("error.log")  # 错误日志保存路径


def main():
    # 检查项目路径是否存在
    if not project_path.is_dir():
        print(f"错误：项目目录不存在 {project_path}")
        return

    # 根据操作系统选择 gradlew 命令
    gradle_cmd = "gradlew.bat" if os.name == "nt" else "./gradlew"

    try:
        # 执行编译命令，合并标准输出和错误输出
        result = subprocess.run(
            [gradle_cmd, "runBoot"],
            cwd=project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # 合并错误到标准输出
            text=True,
            check=True  # 如果命令返回非零退出码则抛出异常
        )
    except subprocess.CalledProcessError as e:
        # 编译失败时写入日志
        with open(error_log_path, "w") as f:
            f.write(e.stdout)
        print(f"编译失败，错误已保存至 {error_log_path}")
    except Exception as e:
        # 其他异常（如命令不存在）
        with open(error_log_path, "w") as f:
            f.write(f"执行命令时发生错误：{str(e)}")
        print(f"运行时错误：{str(e)}")
    else:
        # 编译成功时也保存输出（可能包含警告）
        with open(error_log_path, "w") as f:
            f.write(result.stdout)
        print("编译成功，输出已保存至 error.log")


if __name__ == "__main__":
    main()