import os
import json
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

MAX_TOKEN = 512  # 最大token限制
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'  # 小型高效embedding模型


class DynamicRAG:
    def __init__(self):
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        self.client = chromadb.Client(Settings())
        self.collection = self.client.get_or_create_collection(
            name="rag_data",
            metadata={"hnsw:space": "cosine"}
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=MAX_TOKEN,
            chunk_overlap=50,
            length_function=len
        )
        self.metadata_store = {}

    def _chunk_text(self, text: str) -> list:
        if len(text) <= MAX_TOKEN:
            return [text]
        return self.text_splitter.split_text(text)

    def add_data(self, key: str, value: dict):
        """
        添加键值对数据
        value格式: {
            "file_path": "path/to/file.json",
            "content": {
                "file": "my/java/file.java",
                "class_methods": [
                    {"name": "method1", "code": "public void method1(){}"}
                ]
            }
        }
        """
        file_path = value["file_path"]
        content = value["content"]

        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 写入JSON文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

        # 生成唯一ID (使用文件路径确保相同文件重复添加可去重)
        entry_id = str(hash(f"{key}_{file_path}"))
        self.metadata_store[entry_id] = {
            "original_key": key,
            "file_path": file_path  # 只存储文件路径
        }

        # 处理文本分块
        chunks = self._chunk_text(key)
        embeddings = self.embedder.encode(chunks).tolist()

        # 存储到向量数据库
        self.collection.add(
            ids=[f"{entry_id}_{i}" for i in range(len(chunks))],
            embeddings=embeddings,
            metadatas=[{"source": entry_id} for _ in chunks]
        )

    def query(self, query_text: str, top_k: int = 3) -> list:
        """检索查询并返回解析后的JSON对象"""
        query_embedding = self.embedder.encode(query_text).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        seen_files = set()
        final_results = []

        for i, result_id in enumerate(results['ids'][0]):
            source_id = results['metadatas'][0][i]['source']
            metadata = self.metadata_store.get(source_id)

            if not metadata:
                continue

            file_path = metadata["file_path"]

            # 文件去重
            if file_path in seen_files:
                continue
            seen_files.add(file_path)

            try:
                # 读取并解析JSON文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                final_results.append(content)
            except Exception as e:
                print(f"Error reading {file_path}: {str(e)}")

        return final_results[:top_k]  # 确保不超过top_k

    def batch_add_data(self, items: list):
        """批量添加数据 (优化: 同文件只写入一次)"""
        file_write_map = {}
        all_ids = []
        all_embeddings = []
        all_metadatas = []

        for key, value in items:
            file_path = value["file_path"]
            content = value["content"]

            # 记录需要写入的文件
            file_write_map[file_path] = content

            entry_id = str(hash(f"{key}_{file_path}"))
            self.metadata_store[entry_id] = {
                "original_key": key,
                "file_path": file_path
            }

            chunks = self._chunk_text(key)
            embeddings = self.embedder.encode(chunks).tolist()

            all_ids.extend([f"{entry_id}_{i}" for i in range(len(chunks))])
            all_embeddings.extend(embeddings)
            all_metadatas.extend([{"source": entry_id} for _ in chunks])

        # 批量写入文件
        for path, content in file_write_map.items():
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)

        if all_ids:
            self.collection.add(
                ids=all_ids,
                embeddings=all_embeddings,
                metadatas=all_metadatas
            )

    def delete_data(self, key: str, value: dict):
        """删除数据 (仅删除元数据，不删除物理文件)"""
        file_path = value["file_path"]
        entry_id = str(hash(f"{key}_{file_path}"))

        if entry_id in self.metadata_store:
            # 删除向量数据库记录
            self.collection.delete(ids=[f"{entry_id}_{i}" for i in range(100)])  # 预估最大分块数

            # 删除元数据
            del self.metadata_store[entry_id]
            return True
        return False

    # 其他辅助方法保持不变
    def get_all_embedding(self):
        return self.collection.get()


def enhanced_query(self, query_text: str, top_k: int = 3) -> list:
    """带相似度得分的增强检索"""
    query_embedding = self.embedder.encode(query_text).tolist()
    results = self.collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k * 3  # 扩大召回数量
    )

    score_map = {}
    for i, result_id in enumerate(results['ids'][0]):
        source_id = results['metadatas'][0][i]['source']
        distance = results['distances'][0][i]
        if source_id not in score_map or distance < score_map[source_id]:
            score_map[source_id] = distance

    # 按相似度排序并返回top_k
    sorted_results = sorted(
        [(k, v) for k, v in score_map.items()],
        key=lambda x: x[1]
    )[:top_k]

    return [
        (self.metadata_store[res[0]]['value'], 1 - res[1])
        for res in sorted_results
    ]


# 使用示例


rag = DynamicRAG()


# 添加数据
# rag.add_data(key="UserController",
#              value={
#                  "file_path": "data/user_controller.json",
#                  "content": {
#                      "file": "com/example/UserController.java",
#                      "class_methods": [
#                          {"name": "createUser", "code": "public User createUser() {...}"},
#                          {"name": "deleteUser", "code": "public void deleteUser() {...}"}
#                      ]
#                  }
#              })
#
# # 查询
# results = rag.query("How to create user?", top_k=2)
# 返回: [{"file": "...", "class_methods": [...]}, ...]
