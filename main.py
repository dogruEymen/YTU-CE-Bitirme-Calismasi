from ai_engine.embeddings.model import model

vec1 = model.vectorize("Hello")
vec2 = model.vectorize("car")

res = model.cosine_sim(vec1, vec2)
print(res)
