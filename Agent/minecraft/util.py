from task_tree.TaskTree import TaskTree, TaskNode
from Agent.minecraft.mod import minecraft_mod


def mod_generate(mod_name, path, author, requirement):
    generation_task = TaskTree("root")
    mod = minecraft_mod(mod_name, path, author)
    generation_task.create_task(f"{mod_name}", mod, requirement)
    generation_task.execute()


