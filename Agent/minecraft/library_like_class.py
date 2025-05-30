import os.path
from code_template.java_template_class import java_template_class


class library_like_class(java_template_class):

    def __init__(self, project_root: str, class_name: str, package: str):
        super().__init__(project_root, class_name, package)
        # 用于存储静态字段定义的列表
        self.static_contents = []

    def add_static_field(self, field_definition: str):
        """添加静态字段定义到静态内容列表"""
        self.static_contents.append(field_definition)
        return self

    def clear_static_fields(self):
        """清空静态内容列表"""
        self.static_contents = []
        return self

    def insert_static_into_code(self):
        if self.static_contents:
            # 在类体中插入静态字段
            static_block = "\n".join(["    " + field for field in self.static_contents])
            container = f"""
                    public enum Container {{
            // 枚举常量（自动为 public static final）
            {static_block};
            private final Object value;

            Container(Object value) {{
                this.value = value;
            }}

            public Object getValue() {{
                return value;
            }}

            // 获取所有枚举常量及其值
            public static ArrayList<Object> get_all() {{
                ArrayList<Object> result = new ArrayList<Object>;
                for (Container item : Container.values()) {{
                    result.add(item.getValue());
                }}
                return result;
            }}
        }}
                    """
            # 查找类体开始位置
            class_start = self.code.find('{')
            if class_start != -1:
                # 在开括号后插入静态字段块
                self.code = (
                        self.code[:class_start + 1] +
                        "\n" + container + "\n" +
                        self.code[class_start + 1:]
                )
            else:
                # 如果没有找到{，直接追加到代码末尾
                self.code += "\n" + static_block + "\n"
