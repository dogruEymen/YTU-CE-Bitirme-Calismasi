from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class model:
    embedding_model = SentenceTransformer("intfloat/multilingual-e5-base")

    @staticmethod
    def vectorize(string):
        emb = model.embedding_model.encode(string, normalize_embeddings=True)
        return emb
    @staticmethod
    def cosine_sim(vec1, vec2):
        return cosine_similarity([vec1], [vec2])
