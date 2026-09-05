import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import SessionLocal
from backend.models.project import Project
from backend.services.validation_service import DataValidationService

def main():
    print("🔍 Running Data Validation Checks on Active Database...")
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        if not projects:
            print("No records found in database.")
            return

        data_list = []
        for p in projects:
            data_list.append({
                "project_id": p.id,
                "project_name": p.project_name,
                "state": p.state,
                "district": p.district,
                "constituency": p.constituency,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "project_type": p.project_type,
                "sanctioned_amount": p.sanctioned_amount,
                "released_amount": p.released_amount,
                "utilized_amount": p.utilized_amount,
                "physical_progress": p.physical_progress,
                "financial_progress": p.financial_progress,
                "start_date": p.start_date.isoformat() if p.start_date else None,
                "expected_completion_date": p.expected_completion_date.isoformat() if p.expected_completion_date else None,
                "contractor_name": p.contractor_name
            })

        df = pd.DataFrame(data_list)
        _, report = DataValidationService.validate_dataframe(df)

        print(f"\n========================================================")
        print(f"   DATA QUALITY REPORT: {report['data_quality_score']}/100")
        print(f"========================================================")
        print(f"• Total Records: {report['total_records']:,}")
        print(f"• Valid Records: {report['valid_records']:,}")
        print(f"• Duplicates: {report['duplicates_count']}")
        print(f"• Issues Found: {len(report['issues'])}")
        print("\nPassed Compliance Checks:")
        for chk in report["passed_checks"]:
            print(f"  ✓ {chk}")
        print("\nFlagged Issues:")
        for iss in report["issues"]:
            print(f"  ⚠ [{iss['severity']}] {iss['rule']}: {iss['description']}")
        print("========================================================\n")

    finally:
        db.close()

if __name__ == "__main__":
    main()
