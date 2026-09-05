import datetime
import pandas as pd
import numpy as np
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

class FeatureEngineeringService:
    """
    Computes statistical and domain-specific features required for:
    - Isolation Forest unsupervised anomaly model
    - Statistical cost deviation
    - Delay risk scoring
    - Implementation efficiency gap
    - Contractor concentration index
    """

    @staticmethod
    def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        now = pd.Timestamp.now()

        # 1. Financial features
        sanc = pd.to_numeric(df["sanctioned_amount"], errors="coerce").fillna(100000.0)
        sanc = sanc.clip(lower=1.0) # Avoid div zero
        util = pd.to_numeric(df["utilized_amount"], errors="coerce").fillna(0.0)
        benef = pd.to_numeric(df.get("beneficiary_count", 500), errors="coerce").fillna(500).clip(lower=1)
        
        df["cost_per_beneficiary"] = (sanc / benef).round(2)
        df["utilization_percentage"] = ((util / sanc) * 100.0).round(2)
        
        # Financial Progress
        if "financial_progress" not in df.columns or df["financial_progress"].isnull().all():
            df["financial_progress"] = df["utilization_percentage"]
        else:
            df["financial_progress"] = pd.to_numeric(df["financial_progress"], errors="coerce").fillna(0.0).round(2)

        # Physical Progress
        df["physical_progress"] = pd.to_numeric(df.get("physical_progress", 0.0), errors="coerce").fillna(0.0).round(2)
        
        # Efficiency Gap = Financial Progress - Physical Progress
        # High positive gap means funds spent but physical work lags significantly
        df["efficiency_gap"] = (df["financial_progress"] - df["physical_progress"]).round(2)

        # 2. Timeline and Delay Features
        start_dates = pd.to_datetime(df["start_date"], errors="coerce")
        exp_comp_dates = pd.to_datetime(df["expected_completion_date"], errors="coerce")
        act_comp_dates = pd.to_datetime(df.get("actual_completion_date", None), errors="coerce")

        # Project Duration (Expected or Actual)
        df["duration_days"] = ((exp_comp_dates - start_dates).dt.days).fillna(180).astype(int).clip(lower=1)

        # Delay Days
        # If completed: actual_completion - expected_completion
        # If in progress / delayed / stalled: max(0, now - expected_completion)
        delay_list = []
        for idx, row in df.iterrows():
            act = act_comp_dates.iloc[idx]
            exp = exp_comp_dates.iloc[idx]
            st = start_dates.iloc[idx]
            status = str(row.get("status", "In Progress"))
            
            if pd.notnull(act) and pd.notnull(exp):
                diff = (act - exp).days
                delay_list.append(max(0, diff))
            elif pd.notnull(exp) and (status in ["In Progress", "Delayed", "Stalled"]):
                if exp < now:
                    diff = (now - exp).days
                    delay_list.append(max(0, diff))
                else:
                    delay_list.append(0)
            else:
                delay_list.append(0)
                
        df["delay_days"] = delay_list
        df["delay_percentage"] = ((df["delay_days"] / df["duration_days"]) * 100.0).round(2)

        # 3. Contractor Aggregated Features
        if "contractor_id" in df.columns:
            contractor_counts = df.groupby("contractor_id")["project_id"].transform("count")
            contractor_values = df.groupby("contractor_id")["sanctioned_amount"].transform("sum")
            df["contractor_project_count"] = contractor_counts.fillna(1)
            df["contractor_total_value"] = contractor_values.fillna(sanc)
        else:
            df["contractor_project_count"] = 1
            df["contractor_total_value"] = sanc

        # 4. Constituency Density Features
        if "constituency" in df.columns:
            const_counts = df.groupby("constituency")["project_id"].transform("count")
            df["constituency_project_count"] = const_counts.fillna(1)
        else:
            df["constituency_project_count"] = 1

        # 5. Project Type Frequency
        if "project_type" in df.columns:
            type_counts = df.groupby("project_type")["project_id"].transform("count")
            df["project_type_frequency"] = type_counts.fillna(1)
        else:
            df["project_type_frequency"] = 1

        return df
