import math
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Tuple, Dict, Any, List, Optional

def haversine_distance_km(lat1, lon1, lat2, lon2) -> float:
    """Calculate the great circle distance in kilometers between two points on the earth."""
    if any(v is None or pd.isnull(v) for v in [lat1, lon1, lat2, lon2]):
        return 999.0
    R = 6371.0 # Earth radius in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

class NLPSimilarityEngine:
    """
    Identifies duplicate or highly similar projects using TF-IDF and Cosine Similarity,
    cross-referenced with geographical proximity.
    """

    def __init__(self, similarity_threshold: float = 0.82, max_features: int = 5000):
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=max_features,
            ngram_range=(1, 2)
        )

    def detect_similar_projects(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        df = df.copy()
        
        # Prepare text corpus (Name + Description)
        text_corpus = (
            df["project_name"].fillna("").astype(str) + " " +
            df["project_description"].fillna("").astype(str)
        ).tolist()

        if len(text_corpus) == 0 or all(t.strip() == "" for t in text_corpus):
            df["similar_project_id"] = None
            df["similarity_score"] = 0.0
            return df, {"similar_pairs_count": 0}

        # Compute TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(text_corpus)
        
        # To scale efficiently for 5000+ items, do batch cosine similarity
        similar_ids = [None] * len(df)
        sim_scores = [0.0] * len(df)
        similar_pairs = []

        # Compare within same constituency or district chunks to optimize computation
        project_ids = df["project_id"].tolist()
        lats = df.get("latitude", [None] * len(df)).tolist()
        lngs = df.get("longitude", [None] * len(df)).tolist()
        states = df.get("state", [""] * len(df)).tolist()
        districts = df.get("district", [""] * len(df)).tolist()

        # Group indices by state to reduce search space
        state_groups = {}
        for idx, st in enumerate(states):
            state_groups.setdefault(st, []).append(idx)

        for st, idx_list in state_groups.items():
            if len(idx_list) < 2:
                continue
            sub_tfidf = tfidf_matrix[idx_list]
            sub_sim = cosine_similarity(sub_tfidf, sub_tfidf)
            np.fill_diagonal(sub_sim, 0.0) # Zero out diagonal
            
            # Find max similarity per row
            max_sim_indices = np.argmax(sub_sim, axis=1)
            max_sim_values = np.max(sub_sim, axis=1)

            for i_local, (match_local, best_score) in enumerate(zip(max_sim_indices, max_sim_values)):
                if best_score >= self.similarity_threshold:
                    i_global = idx_list[i_local]
                    best_global = idx_list[match_local]
                    dist_km = haversine_distance_km(
                        lats[i_global], lngs[i_global],
                        lats[best_global], lngs[best_global]
                    )
                    if districts[i_global] == districts[best_global] or dist_km <= 25.0:
                        similar_ids[i_global] = project_ids[best_global]
                        sim_scores[i_global] = round(float(best_score) * 100.0, 1)
                        if i_global < best_global:
                            similar_pairs.append({
                                "project_1": project_ids[i_global],
                                "project_2": project_ids[best_global],
                                "similarity_percentage": round(float(best_score) * 100.0, 1),
                                "distance_km": dist_km,
                                "district": districts[i_global],
                                "state": st
                            })

        df["similar_project_id"] = similar_ids
        df["similarity_score"] = sim_scores

        metadata = {
            "model_type": "TF-IDF + Cosine Similarity + Geographic Distance",
            "similarity_threshold": self.similarity_threshold,
            "similar_pairs_count": len(similar_pairs),
            "sample_similar_pairs": similar_pairs[:10]
        }

        return df, metadata
