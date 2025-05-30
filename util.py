from ast_rag import rag


def read_temp(root):
    dic = {}
    with open(root, "r") as f:
        lines = f.read().split('++++|++++')
        for i in range(1, len(lines), 2):
            dic[lines[i - 1]] = lines[i]
    return dic


def write_temp(root, dic):
    with open(root, "w") as f:
        for k, v in dic.items():
            f.write(f"{k}\n++++|++++\n{v}\n++++|++++\n")


class logger:
    def __init__(self, path='gpt.log'):
        self.logger = open(path, 'w')
        self.cache = ""

    def write(self, content):
        if isinstance(content, dict):
            for k, v in content.items():
                self.cache += str(f"{k}\n{v}\n")
                print(f"{k}\n{v}\n")
                self.logger.write(f"{k}\n{v}\n")
        elif isinstance(content, list):
            for item in content:
                self.cache += str(item)
                print(item)
                self.logger.write(str(item))
        elif content is None:
            return
        else:
            if content[-1] is not '\n':
                content += '\n'
            self.cache += str(content)
            print(content)
            self.logger.write(str(content))


LOG = logger()
RAG = rag


def get_rag():
    return RAG


def get_logger():
    return LOG
