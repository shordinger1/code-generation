from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.config import Settings

MAX_TOKEN = 512  # 最大token限制
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'  # 小型高效embedding模型


class DynamicRAG:
    def __init__(self):
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        self.client = chromadb.Client(Settings())
        self.collection = self.client.get_or_create_collection(name="rag_data", metadata={"hnsw:space": "cosine"})
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=MAX_TOKEN,
            chunk_overlap=50,
            length_function=len
        )
        self.metadata_store = {}
        self.logger = open("log.txt", "a")

    def _chunk_text(self, text: str) -> list:
        """文本分块处理"""
        if len(text) <= MAX_TOKEN:
            return [text]
        return self.text_splitter.split_text(text)

    def add_data(self, key: str, value: str):
        value = f'{key}&&&&&{value}'
        """添加键值对数据"""
        # 生成唯一ID
        entry_id = str(hash(f"{key}_{value}"))

        # 存储原始数据
        self.metadata_store[entry_id] = {
            "original_key": key,
            "value": value
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

    def delete_data(self, key: str, value: str):
        """删除指定键值对"""
        entry_id = str(hash(f"{key}_{value}"))
        if entry_id in self.metadata_store:
            # 验证元数据和实际存储是否一致
            if (self.metadata_store[entry_id]['original_key'] == key and
                    self.metadata_store[entry_id]['value'] == value):
                self.delete_data(key, value)
                return True
        return False

    def query(self, query_text: str, top_k: int = 3) -> list:
        """检索查询"""
        # 生成查询embedding
        query_embedding = self.embedder.encode(query_text).tolist()

        # 执行相似性搜索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # 处理返回结果
        seen = set()
        final_results = []
        for i, result_id in enumerate(results['ids'][0]):
            source_id = results['metadatas'][0][i]['source']
            if source_id not in seen:
                seen.add(source_id)
                metadata = self.metadata_store.get(source_id)
                if metadata:
                    final_results.append(metadata['value'])
        self.logger.write(query_text)
        self.logger.write('\n')
        self.logger.write(str(final_results))
        return final_results

    # 添加批量插入功能
    def batch_add_data(self, items: list):
        """批量添加数据"""
        all_ids = []
        all_embeddings = []
        all_metadatas = []

        for key, value in items:
            value = f'{key}&&&&&{value}'
            entry_id = str(hash(f"{key}_{value}"))
            self.metadata_store[entry_id] = {
                "original_key": key,
                "value": value
            }
            chunks = self._chunk_text(key)
            embeddings = self.embedder.encode(chunks).tolist()

            all_ids.extend([f"{entry_id}_{i}" for i in range(len(chunks))])
            all_embeddings.extend(embeddings)
            all_metadatas.extend([{"source": entry_id} for _ in chunks])

        self.collection.add(
            ids=all_ids,
            embeddings=all_embeddings,
            metadatas=all_metadatas
        )


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
if __name__ == "__main__":
    rag = DynamicRAG()

    # 添加数据
    rag.add_data(
        key="机器学习是一种通过经验自动改进的计算机算法",
        value="machine_learning_definition.txt"
    )

    rag.add_data(
        key="天下最好看的小说",
        value="voc_list.txt"
    )

    # 查询
    print(rag.query("什么是机器学习？"))

    # 删除数据
    rag.delete_data(
        key="机器学习是一种通过经验自动改进的计算机算法",
        value="machine_learning_definition.txt"
    )
