from backend.app.core.DbFunctions import DbFunctions
import numpy as np
from bertopic import BERTopic
from database.models.ClusterData import Cluster as ClusterModel
from database.models.ArticleData import Article
from database.db import SessionLocal
from datetime import datetime
from sqlalchemy import text

class Cluster:
    num_of_articles = 1000 
    top_representative_count = 10
    articles = DbFunctions.get_articles_with_embedding(lim=num_of_articles)
    clean_articles = [
        a for a in articles
        if isinstance(a.title, str)
        and isinstance(a.embedding, (list, np.ndarray))
        and len(a.embedding) > 0
    ]
    embeddings = np.array(
        [np.array(a.embedding, dtype=np.float32) for a in clean_articles],
        dtype=np.float32
    )
    docs = np.array([article.title for article in clean_articles])

    topic_model = BERTopic(
        embedding_model=None,
        min_topic_size=10,  # Minimum cluster size
        verbose=True,
        nr_topics="auto"  # Let BERTopic determine optimal number
    )
    if articles is None:
        raise Exception("DB returned None (connection issue likely)")
    if len(articles)==0:
        raise Exception("DB returned empty list")

    @staticmethod
    def cluster():        
        # DATA REPORTING
        print("=== DATA STATISTICS ===")
        print(f"Total articles in database: {len(Cluster.articles)}")
        print(f"Clean articles (with valid title and embedding): {len(Cluster.clean_articles)}")
        print(f"Articles filtered out: {len(Cluster.articles) - len(Cluster.clean_articles)}")
        print(f"Articles used for clustering: {len(Cluster.docs)}")
        print(f"Embeddings shape: {Cluster.embeddings.shape}")
        
        topics, probs = Cluster.topic_model.fit_transform(
            Cluster.docs,
            embeddings=Cluster.embeddings
        )
        
        # CLUSTERING RESULTS
        unique_topics = set(topics)
        outlier_count = list(topics).count(-1)
        clustered_count = len(topics) - outlier_count
        
        print("\n=== CLUSTERING RESULTS ===")
        print(f"Total documents processed: {len(topics)}")
        print(f"Number of clusters formed: {len(unique_topics) - (1 if -1 in unique_topics else 0)}")
        print(f"Documents assigned to clusters: {clustered_count}")
        print(f"Outliers (unassigned): {outlier_count}")
        print(f"Outlier percentage: {(outlier_count/len(topics))*100:.2f}%")
        
        # OUTPUT
        for doc, topic in zip(Cluster.docs, topics):
            print(topic, "->", doc)
        print("\n=== TOPIC SUMMARY ===")
        topic_info = Cluster.topic_model.get_topic_info()
        print(topic_info)
        
        # REPRESENTATIVE DOCS
        print("\n=== REPRESENTATIVE DOCS ===")
        for _, row in topic_info.iterrows():
            topic_id = row["Topic"]
            if topic_id == -1:
                continue
            print(f"\nTopic {topic_id}:")
            for doc in row["Representative_Docs"]:
                print(f"  - {doc}")
        
        # Save to database
        Cluster.save_to_database(topics, probs)
    
    @staticmethod
    def save_to_database(topics, probs):
        db = SessionLocal()
        try:
            # Clear existing clusters
            db.query(ClusterModel).delete()
            
            # Reset all article cluster_ids
            db.query(Article).update({Article.cluster_id: None})
            db.commit()
            
            # Get topic info from BERTopic
            topic_info = Cluster.topic_model.get_topic_info()
            
            # Group articles by cluster
            cluster_articles = {}
            for i, (article, topic_id) in enumerate(zip(Cluster.clean_articles, topics)):
                if topic_id != -1:  # Skip outliers
                    if topic_id not in cluster_articles:
                        cluster_articles[topic_id] = []
                    cluster_articles[topic_id].append(article.id)
            
            # Create clusters with top 10 words as description and article IDs
            cluster_counts = {}
            for _, row in topic_info.iterrows():
                if row['Topic'] != -1:  # Skip outlier topic
                    # Get top 10 words as description
                    top_words = row.get('Representation', [])
                    if isinstance(top_words, list) and len(top_words) > 0:
                        description = ', '.join(top_words[:10])
                    else:
                        description = str(top_words) if top_words else None
                    
                    # Get article IDs for this cluster
                    article_ids = cluster_articles.get(row['Topic'], [])
                    article_ids_str = ','.join(map(str, article_ids)) if article_ids else None
                    
                    # Get top 5 most representative articles by ID for this cluster
                    cluster_article_ids = cluster_articles.get(row['Topic'], [])
                    if cluster_article_ids:
                        # Get corresponding clean articles and their titles
                        cluster_articles_list = [a for a in Cluster.clean_articles if a.id in cluster_article_ids]
                        # Sort by some criteria (here we'll just take first N)
                        top_articles = cluster_articles_list[:Cluster.top_representative_count]
                        rep_docs_str = ','.join([str(a.id) for a in top_articles])  # Store IDs instead
                    else:
                        rep_docs_str = None
                    
                    cluster = ClusterModel(
                        cluster_id=row['Topic'],
                        cluster_description=description,
                        article_count=row['Count'],
                        article_ids=article_ids_str,
                        representative_docs=rep_docs_str
                    )
                    db.add(cluster)
                    cluster_counts[row['Topic']] = row['Count']
            
            db.commit()
            
            # Update articles with cluster assignments
            for i, (article, topic_id) in enumerate(zip(Cluster.clean_articles, topics)):
                if topic_id != -1:  # Skip outliers
                    # Direct SQL UPDATE for each article
                    db.execute(
                        text("UPDATE articles SET cluster_id = :cluster_id WHERE id = :article_id"),
                        {"cluster_id": topic_id, "article_id": article.id}
                    )
            
            db.commit()
            print(f"Saved {len(cluster_counts)} clusters and updated {len([t for t in topics if t != -1])} articles")
            
        except Exception as e:
            db.rollback()
            print(f"Error saving to database: {e}")
            raise
        finally:
            db.close()

if __name__ == '__main__':
    Cluster.cluster()
