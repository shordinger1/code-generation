class TaskNode:
    def __init__(self, name, description, processor=None):
        """
        任务节点类
        :param name: 任务名称
        :param processor: 任务处理对象，需包含process()方法，返回布尔值
        """
        self.name = name
        self.description = description
        self.processor = processor
        self.children = []
        self.status = None  # 任务状态: True=成功, False=失败, None=未执行

    def add_child(self, child_node):
        """添加子任务"""
        self.children.append(child_node)
        print(f"[任务树] 添加子任务: '{child_node.name}' -> 父任务 '{self.name}'")

    def analyze(self):
        pass

    def execute(self):
        """执行当前任务及其子任务"""
        print(f"[任务树] 开始执行任务: '{self.name}'")
        print(f"[任务描述] : '{self.description}'")
        # 先执行所有子任务
        if self.children:
            print(f"[任务树] 任务 '{self.name}' 有 {len(self.children)} 个子任务，开始执行子任务...")

            all_children_success = True
            for i, child in enumerate(self.children, 1):
                print(f"[任务树] 正在执行子任务 ({i}/{len(self.children)}): '{child.name}'")
                if not child.execute():
                    all_children_success = False

            # 检查子任务执行结果
            if not all_children_success:
                self.status = False
                print(f"[任务树] 任务 '{self.name}' 的子任务执行失败，终止执行")
                return False

        # 执行当前任务（当没有子任务或所有子任务成功时）
        if self.processor:
            try:
                print(f"[任务树] 开始执行 '{self.name}' 的主任务处理")
                result = self.processor.process()
                self.status = result
                status_str = "成功" if result else "失败"
                print(f"[任务树] 任务 '{self.name}' 执行{status_str}")
                return result
            except Exception as e:
                self.status = False
                print(f"[任务树] 任务 '{self.name}' 执行时发生异常: {str(e)}")
                return False
        else:
            # 没有处理器的中间节点默认成功
            self.status = True
            print(f"[任务树] 任务 '{self.name}' 是汇总节点，无需执行，状态成功")
            return True


class TaskTree:
    def __init__(self, root_name):
        """
        任务树管理类
        :param root_name: 根节点名称
        """
        self.root = TaskNode(root_name)
        print(f"[任务树] 创建任务树，根节点: '{root_name}'")

    def create_task(self, name, processor=None, parent=None):
        """
        创建新任务
        :param name: 任务名称
        :param processor: 任务处理对象
        :param parent: 父任务节点，默认为根节点
        """
        if parent is None:
            parent = self.root

        new_task = TaskNode(name, processor)
        parent.add_child(new_task)
        return new_task

    def execute(self):
        """执行整个任务树"""
        print(f"[任务树] === 开始执行任务树 ===")
        result = self.root.execute()
        print(f"[任务树] === 任务树执行完成 ===")
        return result


# 示例使用
if __name__ == "__main__":
    # 创建任务处理器示例
    class TaskProcessor:
        def __init__(self, name, success=True):
            self.name = name
            self.success = success

        def process(self):
            print(f"[处理器] 执行处理器 '{self.name}'")
            return self.success


    # 创建任务树
    tree = TaskTree("项目总任务")

    # 创建子任务
    design = tree.create_task("设计阶段", TaskProcessor("设计处理器"))
    dev = tree.create_task("开发阶段")
    test = tree.create_task("测试阶段", TaskProcessor("测试处理器"))

    # 为开发阶段添加子任务
    frontend = tree.create_task("前端开发", TaskProcessor("前端处理器"), parent=dev)
    backend = tree.create_task("后端开发", TaskProcessor("后端处理器", success=False), parent=dev)
    deployment = tree.create_task("部署", TaskProcessor("部署处理器"), parent=dev)

    # 执行整个任务树
    final_result = tree.execute()
    print(f"任务树最终执行结果: {'成功' if final_result else '失败'}")
