import datetime
import pandas as pd
from typing import Dict, Any

class DataProvenanceService:
    """
    Ensures every ingested record tracks its origin:
    source, source_file, source_record_id, import_timestamp, data_version.
    Prevents silent mutation or mixing of sources.
    """

    @staticmethod
    def attach_provenance(df: pd.DataFrame, source: str, source_file: str = "direct_sync", version: str = "v1.0") -> pd.DataFrame:
        df = df.copy()
        if "source" not in df.columns or df["source"].isnull().any():
            df["source"] = source
        if "source_file" not in df.columns or df["source_file"].isnull().any():
            df["source_file"] = source_file
        if "source_record_id" not in df.columns or df["source_record_id"].isnull().any():
            if "project_id" in df.columns:
                df["source_record_id"] = df["project_id"].astype(str)
            else:
                df["source_record_id"] = [f"REC-{i+1}" for i in range(len(df))]
        if "import_timestamp" not in df.columns or df["import_timestamp"].isnull().any():
            df["import_timestamp"] = datetime.datetime.now().isoformat()
        if "data_version" not in df.columns or df["data_version"].isnull().any():
            df["data_version"] = version
        return df
