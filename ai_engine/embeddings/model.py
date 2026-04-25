from sentence_transformers import SentenceTransformer

class model:
    embedding_model = SentenceTransformer("intfloat/multilingual-e5-base")

    @staticmethod
    def vectorize(string):
        emb = model.embedding_model.encode(string)
        return emb
