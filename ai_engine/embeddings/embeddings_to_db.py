
from model import EmbeddingModel
from backend.app.core.DbFunctions import DbFunctions 

total_articles = 50000
batch_size = 1000
processed = 0

while processed < total_articles:
    # Batch boyutunu kalan makale sayısına göre ayarla
    current_batch = min(batch_size, total_articles - processed)
    
    li_articles = DbFunctions.get_articles_for_embedding(current_batch)
    
    if not li_articles:
        print("İşlenecek makale kalmadı")
        break
        
    print(f"{len(li_articles)} makale işleniyor... ({processed + len(li_articles)}/{total_articles})")
    
    li_abtracts = [f"{article.title} {article.abstract_text}" for article in li_articles]
    li_embeddings = EmbeddingModel.vectorize(li_abtracts)
    
    for i, embedding in enumerate(li_embeddings):
        articleid = li_articles[i].id
        emb = embedding
        DbFunctions.update_embedding(articleid, emb)
            
    processed += len(li_articles)
    print(f"Toplam işlenen: {processed}")
