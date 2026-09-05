import unittest
import pandas as pd
from backend.ml.nlp_similarity import NLPSimilarityEngine, haversine_distance_km

class TestNLPSimilarity(unittest.TestCase):
    def test_haversine_distance(self):
        # Distance between two points in Varanasi approx ~5 km
        dist = haversine_distance_km(25.3176, 82.9739, 25.3500, 82.9900)
        self.assertGreater(dist, 3.0)
        self.assertLess(dist, 8.0)

    def test_nlp_similarity_detects_duplicates(self):
        df = pd.DataFrame([
            {
                "project_id": "MPLAD-101",
                "project_name": "Construction of CC road from Rampur Main Chowk to Panchayat Bhavan",
                "project_description": "CC road paving and drainage in Rampur village for village connectivity.",
                "state": "Uttar Pradesh",
                "district": "Varanasi",
                "latitude": 25.3176,
                "longitude": 82.9739
            },
            {
                "project_id": "MPLAD-102",
                "project_name": "Construction of CC road from Rampur Main Chowk to Panchayat Bhavan Ward 4",
                "project_description": "CC road paving and drainage in Rampur village for village connectivity and welfare.",
                "state": "Uttar Pradesh",
                "district": "Varanasi",
                "latitude": 25.3180,
                "longitude": 82.9745
            },
            {
                "project_id": "MPLAD-103",
                "project_name": "Installation of High-Mast Solar LED Street Lighting",
                "project_description": "Erection of solar power illumination in community area.",
                "state": "Uttar Pradesh",
                "district": "Varanasi",
                "latitude": 25.4000,
                "longitude": 83.0500
            }
        ])
        engine = NLPSimilarityEngine(similarity_threshold=0.75)
        res_df, meta = engine.detect_similar_projects(df)
        
        self.assertEqual(res_df.loc[0, "similar_project_id"], "MPLAD-102")
        self.assertGreaterEqual(res_df.loc[0, "similarity_score"], 75.0)
        self.assertIsNone(res_df.loc[2, "similar_project_id"])

if __name__ == "__main__":
    unittest.main()
