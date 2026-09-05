import os
import json
import io
import datetime
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from backend.data_sources.base import DataSource

MAPPING_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "esakshi_mapping.json")

class ESakshiFileDataSource(DataSource):
    """
    Ingests e-Sakshi exported files (CSV, XLSX, JSON).
    Applies configurable column mapping to produce the normalized schema.
    """

    def __init__(self, file_path_or_bytes, filename: str, mapping_config: Optional[Dict[str, Any]] = None):
        self.file_path_or_bytes = file_path_or_bytes
        self.filename = filename
        self.source_name = "e-SAKSHI (File Export)"
        self.mapping_config = mapping_config or self._load_mapping_config()

    def _load_mapping_config(self) -> Dict[str, Any]:
        if os.path.exists(MAPPING_CONFIG_PATH):
            try:
                with open(MAPPING_CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"mappings": {}, "default_values": {}}

    def get_source_name(self) -> str:
        return "e-SAKSHI"

    def get_connection_status(self) -> Dict[str, Any]:
        return {
            "source_name": "e-SAKSHI",
            "connection_status": f"Loaded from file: {self.filename}",
            "is_connected": True,
            "mode": "esakshi_file",
            "last_sync": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def fetch_data(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        # Read raw dataframe based on extension
        ext = os.path.splitext(self.filename)[1].lower()
        
        if isinstance(self.file_path_or_bytes, (bytes, bytearray)):
            buffer = io.BytesIO(self.file_path_or_bytes)
            if ext in [".xlsx", ".xls"]:
                raw_df = pd.read_excel(buffer)
            elif ext == ".json":
                raw_df = pd.read_json(buffer)
            else:
                raw_df = pd.read_csv(buffer)
        else:
            if ext in [".xlsx", ".xls"]:
                raw_df = pd.read_excel(self.file_path_or_bytes)
            elif ext == ".json":
                raw_df = pd.read_json(self.file_path_or_bytes)
            else:
                raw_df = pd.read_csv(self.file_path_or_bytes)

        # Apply configurable column mappings
        mappings = self.mapping_config.get("mappings", {})
        default_values = self.mapping_config.get("default_values", {})
        
        normalized_df = pd.DataFrame()
        
        # Rename matched columns
        col_rename_dict = {}
        for col in raw_df.columns:
            cleaned_col = str(col).strip()
            if cleaned_col in mappings:
                col_rename_dict[col] = mappings[cleaned_col]
            else:
                # Case-insensitive search
                for map_key, target_col in mappings.items():
                    if map_key.lower() == cleaned_col.lower():
                        col_rename_dict[col] = target_col
                        break

        renamed_df = raw_df.rename(columns=col_rename_dict)
        
        # Ensure critical columns exist with fallbacks
        required_cols = [
            "project_id", "project_name", "project_description", "state", "district",
            "constituency", "latitude", "longitude", "project_type", "beneficiary_count",
            "sanctioned_amount", "released_amount", "utilized_amount",
            "physical_progress", "financial_progress", "status",
            "start_date", "sanction_date", "expected_completion_date", "actual_completion_date",
            "contractor_id", "contractor_name", "implementing_agency"
        ]

        for col in required_cols:
            if col in renamed_df.columns:
                normalized_df[col] = renamed_df[col]
            else:
                normalized_df[col] = default_values.get(col, None)

        # Fallback IDs and names if missing
        if "project_id" not in normalized_df.columns or normalized_df["project_id"].isnull().all():
            normalized_df["project_id"] = [f"ESK-IMP-{i+1:05d}" for i in range(len(normalized_df))]
        
        # Sanitize numeric fields
        for num_col in ["sanctioned_amount", "released_amount", "utilized_amount", "physical_progress", "financial_progress"]:
            if num_col in normalized_df.columns:
                normalized_df[num_col] = pd.to_numeric(normalized_df[num_col], errors="coerce").fillna(0.0)

        # Fill provenance
        normalized_df["source"] = "e-Sakshi"
        normalized_df["source_file"] = self.filename
        normalized_df["source_record_id"] = normalized_df["project_id"].astype(str)
        normalized_df["import_timestamp"] = datetime.datetime.now().isoformat()
        normalized_df["data_version"] = "v1.0"

        metadata = {
            "source": "e-Sakshi",
            "file_name": self.filename,
            "total_records": len(normalized_df),
            "columns_mapped": len(col_rename_dict),
            "timestamp": datetime.datetime.now().isoformat()
        }
        return normalized_df, metadata
