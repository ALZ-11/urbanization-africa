# tests/test_transform.py
import unittest
import pandas as pd
from src.transform import parse_wkt_point, transform_roads

class TestTransformations(unittest.TestCase):
    
    def test_parse_wkt_point_valid(self):
        lat, lon = parse_wkt_point("Point(31.25 29.95)")
        self.assertEqual(lat, 29.95)
        self.assertEqual(lon, 31.25)
        
    def test_parse_wkt_point_invalid(self):
        lat, lon = parse_wkt_point("invalid_string")
        self.assertIsNone(lat)
        self.assertIsNone(lon)
        
        lat, lon = parse_wkt_point(None)
        self.assertIsNone(lat)
        self.assertIsNone(lon)

    def test_transform_roads(self):
        mock_data = pd.DataFrame({
            "roadLabel": ["Route 1", "Route 2"],
            "length": ["1200", "500"]
        })
        df_clean = transform_roads(mock_data)
        self.assertEqual(df_clean["length"].iloc[0], 1200.0)
        self.assertEqual(df_clean["length"].iloc[1], 500.0)

if __name__ == "__main__":
    unittest.main()