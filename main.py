from ai_engine.embeddings.model import model

vec = model.vectorize("Merhaba")
print(vec.shape)
