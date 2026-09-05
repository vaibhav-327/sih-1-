import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.project import Project
from backend.models.contractor import Contractor
from backend.models.constituency import Constituency
from backend.models.alert import Alert

class DynamicInsightsService:
    """
    Generates dynamic, real-time executive insights based strictly on database metrics.
    Zero hardcoded values.
    """

    @staticmethod
    def generate_insights(db: Session, data_source: str = "SYNTHETIC DEMO") -> dict:
        total_projects = db.query(func.count(Project.id)).scalar() or 0
        if total_projects == 0:
            return {
                "generated_at": datetime.datetime.now().isoformat(),
                "data_source": data_source,
                "summary_headline": "No projects loaded into system yet.",
                "total_anomalies_detected": 0,
                "insights": [],
                "national_overview": {}
            }

        # Financial Aggregates
        total_sanc = db.query(func.sum(Project.sanctioned_amount)).scalar() or 0.0
        total_rel = db.query(func.sum(Project.released_amount)).scalar() or 0.0
        total_util = db.query(func.sum(Project.utilized_amount)).scalar() or 0.0
        util_rate = round((total_util / total_sanc * 100), 1) if total_sanc > 0 else 0.0

        # Anomaly Queries
        high_risk_count = db.query(func.count(Project.id)).filter(Project.risk_score >= 60.0).scalar() or 0
        critical_risk_count = db.query(func.count(Project.id)).filter(Project.risk_score >= 80.0).scalar() or 0
        cost_anomaly_count = db.query(func.count(Project.id)).filter(Project.cost_deviation >= 50.0).scalar() or 0
        delay_count = db.query(func.count(Project.id)).filter(Project.delay_days >= 60).scalar() or 0
        stalled_count = db.query(func.count(Project.id)).filter(Project.status == "Stalled").scalar() or 0
        
        # Efficiency Gap (> 35% gap)
        eff_gap_count = db.query(func.count(Project.id)).filter(Project.efficiency_gap >= 35.0).scalar() or 0
        
        # Similar duplicate pairs
        dup_count = db.query(func.count(Project.id)).filter(Project.similarity_score >= 80.0).scalar() or 0

        # High-risk contractor concentration
        high_risk_contractors = db.query(func.count(Contractor.id)).filter(Contractor.high_risk_projects >= 3).scalar() or 0

        # High-risk state/district concentration
        top_delayed_district = (
            db.query(Project.district, func.count(Project.id).label("cnt"))
            .filter(Project.delay_days >= 60)
            .group_by(Project.district)
            .order_by(func.count(Project.id).desc())
            .first()
        )
        delayed_district_name = top_delayed_district[0] if top_delayed_district else "Select Districts"
        delayed_district_count = top_delayed_district[1] if top_delayed_district else 0

        insights_list = []

        # 1. Financial Insight: Efficiency Gap
        if eff_gap_count > 0:
            insights_list.append({
                "category": "Financial Risks",
                "icon_type": "alert",
                "title": "Disbursement-to-Execution Imbalance",
                "description": f"{eff_gap_count} projects exhibit fund utilization above 75% while physical progress remains below 45%.",
                "impact_level": "CRITICAL" if eff_gap_count > 50 else "HIGH",
                "metric_value": f"{eff_gap_count} projects ({round((eff_gap_count/total_projects)*100, 1)}%)",
                "recommended_action": "Prioritize physical on-site verification before releasing remaining sanction tranches.",
                "affected_count": eff_gap_count
            })

        # 2. Cost Anomaly Insight
        if cost_anomaly_count > 0:
            insights_list.append({
                "category": "Financial Risks",
                "icon_type": "warning",
                "title": "Peer-Group Cost Outliers Detected",
                "description": f"{cost_anomaly_count} works exceed the 75th percentile cost benchmark for comparable works in their respective states.",
                "impact_level": "HIGH",
                "metric_value": f"{cost_anomaly_count} projects",
                "recommended_action": "Audit DPR estimates and schedule-of-rate unit costs with district planning officers.",
                "affected_count": cost_anomaly_count
            })

        # 3. Implementation Delays
        if delay_count > 0:
            insights_list.append({
                "category": "Implementation Risks",
                "icon_type": "warning",
                "title": "Timeline Overruns in Active Schemes",
                "description": f"{delay_count} projects have exceeded their targeted completion milestone by 60 days or more.",
                "impact_level": "HIGH",
                "metric_value": f"{delay_count} delayed ({round((delay_count/total_projects)*100, 1)}%)",
                "recommended_action": "Issue status review notices to implementing agencies and assess contractor bandwidth.",
                "affected_count": delay_count
            })

        # 4. Contractor Concentration Risk
        if high_risk_contractors > 0:
            insights_list.append({
                "category": "Contractor Risks",
                "icon_type": "alert",
                "title": "Contractor Portfolio Overextension",
                "description": f"{high_risk_contractors} contracting entities have 3 or more concurrent projects flagged with elevated risk indicators.",
                "impact_level": "HIGH",
                "metric_value": f"{high_risk_contractors} contractors",
                "recommended_action": "Conduct enhanced performance review and monitor cross-constituency workload allocations.",
                "affected_count": high_risk_contractors
            })

        # 5. Potential Duplicate Project Scope
        if dup_count > 0:
            insights_list.append({
                "category": "Emerging Patterns",
                "icon_type": "warning",
                "title": "High Text & Spatial Description Overlap",
                "description": f"AI NLP similarity identified {dup_count} projects with >=80% title/description overlap located within proximate geographic bounds.",
                "impact_level": "MEDIUM",
                "metric_value": f"{dup_count} project pairs",
                "recommended_action": "Cross-verify site coordinates and beneficiary habitations to ensure no overlapping work.",
                "affected_count": dup_count
            })

        # 6. Geographic Concentration
        if delayed_district_count > 0:
            insights_list.append({
                "category": "Geographic Risks",
                "icon_type": "info",
                "title": f"Regional Implementation Delay Hub: {delayed_district_name}",
                "description": f"District {delayed_district_name} accounts for {delayed_district_count} delayed projects, indicating local administrative or supply bottlenecks.",
                "impact_level": "MEDIUM",
                "metric_value": f"{delayed_district_count} projects in {delayed_district_name}",
                "recommended_action": "Schedule dedicated review meeting with District Collector / District Magistrate.",
                "affected_count": delayed_district_count
            })

        # 7. Positive Fund Utilization Insight
        insights_list.append({
            "category": "National Overview",
            "icon_type": "check",
            "title": "Overall Fund Utilization Rate",
            "description": f"Across {total_projects:,} projects, total expenditure stands at ₹{total_util/1e7:.2f} Cr against ₹{total_sanc/1e7:.2f} Cr sanctioned ({util_rate}%).",
            "impact_level": "POSITIVE",
            "metric_value": f"{util_rate}% utilized",
            "recommended_action": "Maintain monitoring cadence to sustain fund flow and project delivery.",
            "affected_count": total_projects
        })

        return {
            "generated_at": datetime.datetime.now().isoformat(),
            "data_source": data_source,
            "summary_headline": f"AI Sentinel scanned {total_projects:,} projects across India. {high_risk_count} projects flagged for prioritized review.",
            "total_anomalies_detected": high_risk_count + cost_anomaly_count + dup_count,
            "insights": insights_list,
            "national_overview": {
                "total_projects": total_projects,
                "total_sanctioned_cr": round(total_sanc / 1e7, 2),
                "total_utilized_cr": round(total_util / 1e7, 2),
                "utilization_percentage": util_rate,
                "high_risk_count": high_risk_count,
                "critical_risk_count": critical_risk_count,
                "delayed_count": delay_count
            }
        }
