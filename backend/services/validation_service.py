import datetime
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple

class DataValidationService:
    """
    Validates MPLAD records against compliance and integrity rules.
    Calculates Data Quality Score (0-100) and pinpointed validation issues.
    """

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        total_records = len(df)
        if total_records == 0:
            return df, {
                "data_quality_score": 0.0,
                "total_records": 0,
                "valid_records": 0,
                "invalid_records": 0,
                "duplicates_count": 0,
                "missing_fields_count": 0,
                "issues": [],
                "passed_checks": [],
                "timestamp": datetime.datetime.now().isoformat()
            }

        issues = []
        deductions = 0.0
        passed_checks = []

        # 1. Check Duplicate Project IDs
        if "project_id" in df.columns:
            dup_mask = df.duplicated(subset=["project_id"], keep=False)
            dup_count = int(dup_mask.sum())
            if dup_count > 0:
                dup_ids = df.loc[dup_mask, "project_id"].astype(str).tolist()[:10]
                issues.append({
                    "rule": "Duplicate Project IDs",
                    "severity": "CRITICAL",
                    "count": dup_count,
                    "description": f"Found {dup_count} records with non-unique project IDs.",
                    "affected_ids": dup_ids
                })
                deductions += min(15.0, dup_count * 1.5)
            else:
                passed_checks.append("All Project IDs are unique")
        else:
            issues.append({
                "rule": "Missing Project ID Column",
                "severity": "CRITICAL",
                "count": total_records,
                "description": "Dataset missing primary project_id identifier column.",
                "affected_ids": []
            })
            deductions += 25.0

        # 2. Check Negative Sanctioned / Released / Utilized
        for col, col_name in [
            ("sanctioned_amount", "Sanctioned Amount"),
            ("released_amount", "Released Amount"),
            ("utilized_amount", "Utilized Amount")
        ]:
            if col in df.columns:
                neg_mask = df[col] < 0
                neg_count = int(neg_mask.sum())
                if neg_count > 0:
                    aff_ids = df.loc[neg_mask, "project_id"].astype(str).tolist()[:5] if "project_id" in df.columns else []
                    issues.append({
                        "rule": f"Negative {col_name}",
                        "severity": "ERROR",
                        "count": neg_count,
                        "description": f"{neg_count} records have negative {col_name} values.",
                        "affected_ids": aff_ids
                    })
                    deductions += min(10.0, neg_count * 2.0)
                else:
                    passed_checks.append(f"No negative {col_name} values")

        # 3. Released > Sanctioned Check
        if "released_amount" in df.columns and "sanctioned_amount" in df.columns:
            rel_gt_sanc = df["released_amount"] > (df["sanctioned_amount"] * 1.001) # Allow minor rounding
            rel_gt_count = int(rel_gt_sanc.sum())
            if rel_gt_count > 0:
                aff_ids = df.loc[rel_gt_sanc, "project_id"].astype(str).tolist()[:5] if "project_id" in df.columns else []
                issues.append({
                    "rule": "Released Amount Exceeds Sanctioned",
                    "severity": "ERROR",
                    "count": rel_gt_count,
                    "description": f"{rel_gt_count} projects have released funds exceeding sanctioned allocation.",
                    "affected_ids": aff_ids
                })
                deductions += min(10.0, rel_gt_count * 1.5)
            else:
                passed_checks.append("Released funds within sanctioned limits")

        # 4. Utilized > Released Check
        if "utilized_amount" in df.columns and "released_amount" in df.columns:
            util_gt_rel = df["utilized_amount"] > (df["released_amount"] * 1.001)
            util_gt_count = int(util_gt_rel.sum())
            if util_gt_count > 0:
                aff_ids = df.loc[util_gt_rel, "project_id"].astype(str).tolist()[:5] if "project_id" in df.columns else []
                issues.append({
                    "rule": "Utilized Amount Exceeds Released",
                    "severity": "ERROR",
                    "count": util_gt_count,
                    "description": f"{util_gt_count} projects report expenditure greater than released funds.",
                    "affected_ids": aff_ids
                })
                deductions += min(10.0, util_gt_count * 1.5)
            else:
                passed_checks.append("Reported expenditure within released funds")

        # 5. Physical Progress Range Check (> 100 or < 0)
        if "physical_progress" in df.columns:
            phys_invalid = (df["physical_progress"] > 100.0) | (df["physical_progress"] < 0.0)
            phys_inv_count = int(phys_invalid.sum())
            if phys_inv_count > 0:
                aff_ids = df.loc[phys_invalid, "project_id"].astype(str).tolist()[:5] if "project_id" in df.columns else []
                issues.append({
                    "rule": "Invalid Physical Progress Percentage",
                    "severity": "WARNING",
                    "count": phys_inv_count,
                    "description": f"{phys_inv_count} projects have physical progress outside 0-100% boundary.",
                    "affected_ids": aff_ids
                })
                deductions += min(8.0, phys_inv_count * 1.0)
            else:
                passed_checks.append("Physical progress values within 0-100% range")

        # 6. Date Consistency (Expected completion before start)
        if "start_date" in df.columns and "expected_completion_date" in df.columns:
            try:
                start_dt = pd.to_datetime(df["start_date"], errors="coerce")
                comp_dt = pd.to_datetime(df["expected_completion_date"], errors="coerce")
                inv_date_mask = (start_dt.notnull()) & (comp_dt.notnull()) & (comp_dt < start_dt)
                inv_date_count = int(inv_date_mask.sum())
                if inv_date_count > 0:
                    aff_ids = df.loc[inv_date_mask, "project_id"].astype(str).tolist()[:5] if "project_id" in df.columns else []
                    issues.append({
                        "rule": "Expected Completion Precedes Start Date",
                        "severity": "WARNING",
                        "count": inv_date_count,
                        "description": f"{inv_date_count} projects have expected completion earlier than project start.",
                        "affected_ids": aff_ids
                    })
                    deductions += min(8.0, inv_date_count * 1.0)
                else:
                    passed_checks.append("Project timeline dates are logically sequential")
            except Exception:
                pass

        # 7. Missing Critical Fields (State, Constituency, Contractor)
        missing_crit_count = 0
        for crit_col in ["state", "constituency", "contractor_name"]:
            if crit_col in df.columns:
                m_count = int(df[crit_col].isnull().sum() + (df[crit_col] == "").sum())
                if m_count > 0:
                    missing_crit_count += m_count
                    issues.append({
                        "rule": f"Missing {crit_col.replace('_', ' ').title()}",
                        "severity": "WARNING",
                        "count": m_count,
                        "description": f"{m_count} records have blank {crit_col.replace('_', ' ')}.",
                        "affected_ids": []
                    })
                    deductions += min(6.0, m_count * 0.5)

        # 8. Coordinate Validation (India bounding box roughly Lat 6-38, Lng 68-98)
        if "latitude" in df.columns and "longitude" in df.columns:
            invalid_coords = (
                (df["latitude"].notnull()) & ((df["latitude"] < 6.0) | (df["latitude"] > 38.0)) |
                (df["longitude"].notnull()) & ((df["longitude"] < 68.0) | (df["longitude"] > 98.0))
            )
            inv_coord_count = int(invalid_coords.sum())
            if inv_coord_count > 0:
                issues.append({
                    "rule": "Coordinates Outside India Geographic Bounds",
                    "severity": "WARNING",
                    "count": inv_coord_count,
                    "description": f"{inv_coord_count} records contain latitude/longitude outside geographic India.",
                    "affected_ids": []
                })
                deductions += min(5.0, inv_coord_count * 0.5)
            else:
                passed_checks.append("Geographic coordinates validated within Indian territory")

        # Compute Quality Score (100 minus weighted penalties)
        # Cap max penalty per category
        dup_penalty = min(25.0, (dup_count / total_records) * 50.0) if "project_id" in df.columns and dup_count > 0 else 0.0
        neg_penalty = min(20.0, (neg_count / total_records) * 40.0) if "sanctioned_amount" in df.columns and neg_count > 0 else 0.0
        rel_gt_penalty = min(20.0, (rel_gt_count / total_records) * 40.0) if "released_amount" in df.columns and rel_gt_count > 0 else 0.0
        util_gt_penalty = min(20.0, (util_gt_count / total_records) * 40.0) if "utilized_amount" in df.columns and util_gt_count > 0 else 0.0
        phys_penalty = min(15.0, (phys_inv_count / total_records) * 30.0) if "physical_progress" in df.columns and phys_inv_count > 0 else 0.0
        date_penalty = min(15.0, (inv_date_count / total_records) * 30.0) if inv_date_count > 0 else 0.0

        total_deductions = dup_penalty + neg_penalty + rel_gt_penalty + util_gt_penalty + phys_penalty + date_penalty
        quality_score = max(5.0, round(100.0 - total_deductions, 1))
        invalid_records = sum(iss["count"] for iss in issues if iss["severity"] in ("CRITICAL", "ERROR"))

        report = {
            "data_quality_score": quality_score,
            "total_records": total_records,
            "valid_records": max(0, total_records - invalid_records),
            "invalid_records": min(total_records, invalid_records),
            "duplicates_count": dup_count if "project_id" in df.columns else 0,
            "missing_fields_count": missing_crit_count,
            "issues": issues,
            "passed_checks": passed_checks,
            "timestamp": datetime.datetime.now().isoformat()
        }

        return df, report
