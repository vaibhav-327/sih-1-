import random
import datetime
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List
from backend.data_sources.base import DataSource

INDIAN_STATES_DATA = {
    "Uttar Pradesh": {
        "districts": ["Varanasi", "Lucknow", "Gorakhpur", "Prayagraj", "Kanpur Nagar", "Agra", "Meerut", "Ayodhya", "Jhansi", "Bareilly"],
        "constituencies": ["Varanasi", "Lucknow", "Gorakhpur", "Allahabad", "Kanpur", "Agra", "Meerut", "Faizabad", "Jhansi", "Bareilly"],
        "lat_range": (25.0, 28.5),
        "lng_range": (78.0, 84.0)
    },
    "Maharashtra": {
        "districts": ["Mumbai Suburban", "Pune", "Nagpur", "Nashik", "Thane", "Aurangabad", "Solapur", "Kolhapur", "Amravati", "Nanded"],
        "constituencies": ["Mumbai South", "Pune", "Nagpur", "Nashik", "Thane", "Aurangabad", "Solapur", "Kolhapur", "Amravati", "Nanded"],
        "lat_range": (16.0, 21.0),
        "lng_range": (73.0, 79.5)
    },
    "Bihar": {
        "districts": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga", "Purnia", "Rohtas", "Samastipur", "Saran", "Begusarai"],
        "constituencies": ["Patna Sahib", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga", "Purnia", "Karakat", "Samastipur", "Saran", "Begusarai"],
        "lat_range": (24.5, 27.5),
        "lng_range": (83.5, 88.0)
    },
    "Karnataka": {
        "districts": ["Bengaluru Urban", "Mysuru", "Dharwad", "Belagavi", "Dakshina Kannada", "Ballari", "Kalaburagi", "Shivamogga", "Tumakuru", "Udupi"],
        "constituencies": ["Bengaluru South", "Mysore", "Dharwad", "Belgaum", "Dakshina Kannada", "Bellary", "Gulbarga", "Shimoga", "Tumkur", "Udupi Chikmagalur"],
        "lat_range": (12.0, 17.5),
        "lng_range": (74.0, 78.5)
    },
    "Tamil Nadu": {
        "districts": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", "Erode", "Vellore", "Thanjavur", "Dindigul"],
        "constituencies": ["Chennai Central", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", "Erode", "Vellore", "Thanjavur", "Dindigul"],
        "lat_range": (8.5, 13.5),
        "lng_range": (76.5, 80.3)
    },
    "Rajasthan": {
        "districts": ["Jaipur", "Jodhpur", "Kota", "Bikaner", "Ajmer", "Udaipur", "Alwar", "Bhilwara", "Sikar", "Pali"],
        "constituencies": ["Jaipur", "Jodhpur", "Kota", "Bikaner", "Ajmer", "Udaipur", "Alwar", "Bhilwara", "Sikar", "Pali"],
        "lat_range": (24.0, 29.5),
        "lng_range": (70.0, 77.0)
    },
    "Madhya Pradesh": {
        "districts": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar", "Rewa", "Satna", "Ratlam", "Chhindwara"],
        "constituencies": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar", "Rewa", "Satna", "Ratlam", "Chhindwara"],
        "lat_range": (21.5, 26.5),
        "lng_range": (74.5, 82.5)
    },
    "West Bengal": {
        "districts": ["Kolkata", "North 24 Parganas", "South 24 Parganas", "Howrah", "Hooghly", "Murshidabad", "Nadia", "Paschim Bardhaman", "Purba Medinipur", "Darjeeling"],
        "constituencies": ["Kolkata North", "Dum Dum", "Diamond Harbour", "Howrah", "Hooghly", "Baharampur", "Krishnanagar", "Asansol", "Tamluk", "Darjeeling"],
        "lat_range": (21.5, 27.0),
        "lng_range": (86.0, 89.5)
    },
    "Gujarat": {
        "districts": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Junagadh", "Gandhinagar", "Anand", "Kutch"],
        "constituencies": ["Ahmedabad East", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Junagadh", "Gandhinagar", "Anand", "Kachchh"],
        "lat_range": (20.5, 24.5),
        "lng_range": (69.0, 74.0)
    },
    "Odisha": {
        "districts": ["Khordha", "Cuttack", "Ganjam", "Sundargarh", "Balasore", "Mayurbhanj", "Puri", "Sambalpur", "Bhadrak", "Bolangir"],
        "constituencies": ["Bhubaneswar", "Cuttack", "Aska", "Sundargarh", "Balasore", "Mayurbhanj", "Puri", "Sambalpur", "Bhadrak", "Bolangir"],
        "lat_range": (18.0, 22.5),
        "lng_range": (81.5, 87.5)
    },
    "Assam": {
        "districts": ["Kamrup Metropolitan", "Dibrugarh", "Cachar", "Nagaon", "Sonitpur", "Jorhat", "Tinsukia", "Barpeta", "Dhubri", "Golaghat"],
        "constituencies": ["Gauhati", "Dibrugarh", "Silchar", "Nowgong", "Tezpur", "Jorhat", "Autonomous District", "Barpeta", "Dhubri", "Kaliabor"],
        "lat_range": (24.0, 28.0),
        "lng_range": (89.5, 96.0)
    },
    "Telangana": {
        "districts": ["Hyderabad", "Ranga Reddy", "Medchal-Malkajgiri", "Warangal Urban", "Nizamabad", "Karimnagar", "Khammam", "Mahabubnagar", "Nalgonda", "Adilabad"],
        "constituencies": ["Hyderabad", "Chevella", "Malkajgiri", "Warangal", "Nizamabad", "Karimnagar", "Khammam", "Mahabubnagar", "Nalgonda", "Adilabad"],
        "lat_range": (15.8, 19.8),
        "lng_range": (77.2, 81.3)
    },
    "Kerala": {
        "districts": ["Thiruvananthapuram", "Ernakulam", "Kozhikode", "Thrissur", "Kollam", "Palakkad", "Malappuram", "Kannur", "Alappuzha", "Kottayam"],
        "constituencies": ["Thiruvananthapuram", "Ernakulam", "Kozhikode", "Thrissur", "Kollam", "Palakkad", "Malappuram", "Kannur", "Alappuzha", "Kottayam"],
        "lat_range": (8.3, 12.8),
        "lng_range": (75.0, 77.4)
    },
    "Punjab": {
        "districts": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Hoshiarpur", "SAS Nagar", "Gurdaspur", "Sangrur", "Firozpur"],
        "constituencies": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Hoshiarpur", "Anandpur Sahib", "Gurdaspur", "Sangrur", "Firozpur"],
        "lat_range": (29.5, 32.5),
        "lng_range": (74.0, 76.9)
    },
    "Delhi": {
        "districts": ["New Delhi", "Central Delhi", "South Delhi", "North Delhi", "East Delhi", "West Delhi", "North East Delhi", "North West Delhi", "South West Delhi", "Shahdara"],
        "constituencies": ["New Delhi", "Chandni Chowk", "South Delhi", "East Delhi", "West Delhi", "North East Delhi", "North West Delhi"],
        "lat_range": (28.4, 28.9),
        "lng_range": (76.8, 77.4)
    }
}

PROJECT_TEMPLATES = [
    {
        "type": "Roads & Connectivity",
        "templates": [
            "Construction of CC road from {village} Main Chowk to Panchayat Bhavan",
            "Interlocking paver road and RCC drainage network in {village} Ward No {ward}",
            "Upgradation and widening of rural link road connecting {village} to State Highway",
            "Construction of bituminous road with stone pitching in {village}"
        ],
        "base_cost_range": (1500000, 4500000), # 15L to 45L
        "base_duration_days": 180,
        "beneficiaries": (800, 3500)
    },
    {
        "type": "Community & Social Infrastructure",
        "templates": [
            "Construction of Multi-Purpose Community Hall and Cultural Kendra at {village}",
            "Construction of Open Gym, Children Park and Boundary Wall in {village}",
            "Construction of Modern Crematorium Shed with Solar lighting at {village}",
            "Establishment of Public Library and Digital Study Center at {village} Gram Kendra"
        ],
        "base_cost_range": (1200000, 3500000), # 12L to 35L
        "base_duration_days": 150,
        "beneficiaries": (1200, 5000)
    },
    {
        "type": "Drinking Water & Sanitation",
        "templates": [
            "Installation of Solar-Powered Mini Deep Tube Well and RO Water Plant in {village}",
            "Construction of Community Sanitary Complex with Running Water Facility at {village} Market",
            "Laying of Drinking Water Pipeline Network and Overhead Tank at {village}",
            "Installation of 20 Nos Deep Borewell Handpumps in SC/ST Habitations of {village}"
        ],
        "base_cost_range": (800000, 2800000), # 8L to 28L
        "base_duration_days": 120,
        "beneficiaries": (600, 4000)
    },
    {
        "type": "Education & Skill Facilities",
        "templates": [
            "Construction of 2 Additional Classrooms and Smart Lab at Govt High School {village}",
            "Construction of Science Laboratory and Girl Students Common Room at {village} College",
            "Construction of Anganwadi Center Model Building with Child Friendly Amenities in {village}",
            "Provision of Solar Rooftop Power System and Furniture at Govt Composite School {village}"
        ],
        "base_cost_range": (1000000, 3200000), # 10L to 32L
        "base_duration_days": 140,
        "beneficiaries": (400, 1800)
    },
    {
        "type": "Healthcare & Wellness",
        "templates": [
            "Upgradation of Primary Health Sub-Centre with Maternity Ward and Equipment at {village}",
            "Procurement and deployment of Advance Life Support Mobile Medical Ambulance for {village} Block",
            "Construction of Ayush Health and Wellness Kendra with boundary wall at {village}",
            "Installation of Oxygen Generator Plant & Emergency Care Unit at CHC {village}"
        ],
        "base_cost_range": (1800000, 5500000), # 18L to 55L
        "base_duration_days": 200,
        "beneficiaries": (2500, 10000)
    },
    {
        "type": "Renewable Energy & Public Safety",
        "templates": [
            "Installation of 100 Nos High-Mast Solar LED Street Lights across public junctions in {village}",
            "Solar Electrification of Panchayat Bhavan, PHC and High School in {village}",
            "Installation of CCTV Surveillance Network for public safety in {village} market area",
            "Solar Powered Agricultural Pumping and Micro-Irrigation Unit for farmers in {village}"
        ],
        "base_cost_range": (600000, 2200000), # 6L to 22L
        "base_duration_days": 90,
        "beneficiaries": (1000, 6000)
    },
    {
        "type": "Irrigation & Water Conservation",
        "templates": [
            "Rejuvenation of Traditional Village Pond (Amrit Sarovar) with embankment and walking track in {village}",
            "Construction of Check Dam and Rainwater Harvesting Structure on local rivulet at {village}",
            "Laying of Minor Irrigation Canal Linings and Sluice Gates in {village} agricultural belt",
            "Construction of Percolation Tank and Recharge Shafts in water-stressed pockets of {village}"
        ],
        "base_cost_range": (1400000, 4000000), # 14L to 40L
        "base_duration_days": 160,
        "beneficiaries": (1500, 4500)
    }
]

CONTRACTORS_LIST = [
    {"id": "CONT-001", "name": "Apex Bharat Infraworks Ltd", "reg": "REG/DL/2018/4891"},
    {"id": "CONT-002", "name": "Pragati Urban Builders & Developers", "reg": "REG/MH/2019/3120"},
    {"id": "CONT-003", "name": "Kavya Geo Engineering Pvt Ltd", "reg": "REG/UP/2017/7821"},
    {"id": "CONT-004", "name": "Shri Ganesh Construction Consortium", "reg": "REG/KA/2020/9012"},
    {"id": "CONT-005", "name": "Nilgiri Public Works Enterprise", "reg": "REG/TN/2016/5421"},
    {"id": "CONT-006", "name": "Marwar Infrastructure & Logistics", "reg": "REG/RJ/2018/1129"},
    {"id": "CONT-007", "name": "Vindhya Civil Solutions LLP", "reg": "REG/MP/2021/6632"},
    {"id": "CONT-008", "name": "Bengal Delta Projects & Infra", "reg": "REG/WB/2019/8841"},
    {"id": "CONT-009", "name": "Girnar Construction Services", "reg": "REG/GJ/2017/4590"},
    {"id": "CONT-010", "name": "Kalinga Heavy Engineering Works", "reg": "REG/OR/2020/3312"},
    {"id": "CONT-011", "name": "Brahmaputra Civil Contractors", "reg": "REG/AS/2018/7723"},
    {"id": "CONT-012", "name": "Deccan Synergy Buildtech", "reg": "REG/TS/2021/5501"},
    {"id": "CONT-013", "name": "Malabar Coastal Infra Ltd", "reg": "REG/KL/2019/2234"},
    {"id": "CONT-014", "name": "Satluj Power & Infrastructure", "reg": "REG/PB/2017/9981"},
    {"id": "CONT-015", "name": "Capital Civic Builders Pvt Ltd", "reg": "REG/DL/2020/6641"},
    {"id": "CONT-016", "name": "National Rural Builders Syndicate", "reg": "REG/UP/2019/1209"},
    {"id": "CONT-017", "name": "Samruddhi Infrastructure Works", "reg": "REG/MH/2018/4398"},
    {"id": "CONT-018", "name": "Navodaya Civil Tech Enterprise", "reg": "REG/KA/2021/8876"},
    {"id": "CONT-019", "name": "Chola Heritage Construction", "reg": "REG/TN/2017/3392"},
    {"id": "CONT-020", "name": "Aravalli Project Engineers", "reg": "REG/RJ/2020/5543"},
    {"id": "CONT-021", "name": "Narmada Rural Tech Builders", "reg": "REG/MP/2019/7711"},
    {"id": "CONT-022", "name": "Howrah Bridge Infra Solutions", "reg": "REG/WB/2016/9934"},
    {"id": "CONT-023", "name": "Sardar Patel Civil Associates", "reg": "REG/GJ/2018/2219"},
    {"id": "CONT-024", "name": "Mahanadi Structural Engineers", "reg": "REG/OR/2021/4402"},
    {"id": "CONT-025", "name": "Kaziranga Public Works Group", "reg": "REG/AS/2019/6618"}
]

AGENCIES_LIST = [
    "District Rural Development Agency (DRDA)",
    "Public Works Department (PWD)",
    "Rural Engineering Services (RES)",
    "Panchayati Raj Engineering Division",
    "Municipal Corporation / Urban Local Body",
    "State Jal Nigam / Water Supply Board",
    "Irrigation & Flood Control Department",
    "State Renewable Energy Development Agency"
]

VILLAGE_NAMES = [
    "Rampur", "Mohanpur", "Shivpur", "Kalyanpur", "Sundarpur", "Govindpur",
    "Haripur", "Ganeshpur", "Chandanpur", "Sitapur", "Devipur", "Anandpur",
    "Fatehpur", "Balarampur", "Madhupur", "Krishnapur", "Shantipurgarh", "Gopalpur",
    "Bishnupur", "Jagannathpur", "Sultanpur", "Lalpur", "Narayanpur", "Chandpur"
]

class SyntheticDataSource(DataSource):
    """
    Generates realistic, statistically sound synthetic data for 5,000+ MPLAD projects
    with realistic distributions and controlled anomaly scenarios.
    """

    def __init__(self, count: int = 5000, seed: int = 42):
        self.count = count
        self.seed = seed
        self.source_name = "SYNTHETIC DEMO"

    def get_source_name(self) -> str:
        return self.source_name

    def get_connection_status(self) -> Dict[str, Any]:
        return {
            "source_name": "SYNTHETIC DEMO",
            "connection_status": "Active (Demo Mode)",
            "is_connected": True,
            "mode": "synthetic",
            "record_count": self.count,
            "last_sync": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_quality_score": 98.4,
            "note": "SYNTHETIC DATA FOR DEMONSTRATION PURPOSES ONLY"
        }

    def fetch_data(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        random.seed(self.seed)
        np.random.seed(self.seed)
        
        base_date = datetime.date(2023, 1, 1)
        today = datetime.date(2026, 8, 30)
        
        records = []
        states = list(INDIAN_STATES_DATA.keys())
        
        # Inject controlled anomalies (~8% total across categories)
        # 1. Cost inflation
        # 2. High financial progress + low physical progress
        # 3. Extreme delay
        # 4. Contractor concentration
        # 5. Duplicate descriptions
        # 6. Normal projects
        
        # Pre-generate duplicate pairs
        duplicate_pairs_count = 60
        duplicate_seeds = []
        for d in range(duplicate_pairs_count):
            st = random.choice(states)
            d_dist_idx = random.randint(0, len(INDIAN_STATES_DATA[st]["districts"]) - 1)
            d_const_idx = d_dist_idx % len(INDIAN_STATES_DATA[st]["constituencies"])
            dist = INDIAN_STATES_DATA[st]["districts"][d_dist_idx]
            const = INDIAN_STATES_DATA[st]["constituencies"][d_const_idx]
            ptype = random.choice(PROJECT_TEMPLATES)
            vname = random.choice(VILLAGE_NAMES)
            t_str = random.choice(ptype["templates"]).format(village=vname, ward=random.randint(1, 15))
            duplicate_seeds.append({
                "state": st,
                "district": dist,
                "constituency": const,
                "project_type": ptype["type"],
                "desc": t_str,
                "cost": random.randint(ptype["base_cost_range"][0], ptype["base_cost_range"][1]),
                "lat": random.uniform(INDIAN_STATES_DATA[st]["lat_range"][0], INDIAN_STATES_DATA[st]["lat_range"][1]),
                "lng": random.uniform(INDIAN_STATES_DATA[st]["lng_range"][0], INDIAN_STATES_DATA[st]["lng_range"][1]),
            })

        for i in range(1, self.count + 1):
            p_id = f"MPLAD-{i:05d}"
            
            # Select State & Location
            state = random.choices(
                states,
                weights=[18, 12, 10, 8, 8, 7, 7, 6, 6, 4, 3, 3, 3, 3, 2],
                k=1
            )[0]
            
            dist_idx = random.randint(0, len(INDIAN_STATES_DATA[state]["districts"]) - 1)
            const_idx = dist_idx % len(INDIAN_STATES_DATA[state]["constituencies"])
            district = INDIAN_STATES_DATA[state]["districts"][dist_idx]
            constituency = INDIAN_STATES_DATA[state]["constituencies"][const_idx]
            
            lat = round(random.uniform(INDIAN_STATES_DATA[state]["lat_range"][0], INDIAN_STATES_DATA[state]["lat_range"][1]), 6)
            lng = round(random.uniform(INDIAN_STATES_DATA[state]["lng_range"][0], INDIAN_STATES_DATA[state]["lng_range"][1]), 6)
            
            ptype_obj = random.choice(PROJECT_TEMPLATES)
            ptype = ptype_obj["type"]
            vname = random.choice(VILLAGE_NAMES)
            ward_num = random.randint(1, 18)
            template_str = random.choice(ptype_obj["templates"])
            project_name = template_str.format(village=vname, ward=ward_num)
            project_desc = f"{project_name}. Sanctioned under MPLADS development initiative for public welfare and village infrastructure enhancement."
            
            # Base cost and duration
            base_min_cost, base_max_cost = ptype_obj["base_cost_range"]
            sanctioned_amount = float(random.randint(base_min_cost, base_max_cost))
            base_duration = ptype_obj["base_duration_days"] + random.randint(-20, 40)
            beneficiaries = random.randint(ptype_obj["beneficiaries"][0], ptype_obj["beneficiaries"][1])
            
            # Contractor
            # Contractor 3, 7, 16 get concentrated anomalies
            if i % 15 == 0:
                contractor = CONTRACTORS_LIST[2] # CONT-003
            elif i % 18 == 0:
                contractor = CONTRACTORS_LIST[6] # CONT-007
            else:
                contractor = random.choice(CONTRACTORS_LIST)
                
            agency = random.choice(AGENCIES_LIST)
            
            # Timeline dates
            start_offset_days = random.randint(60, 1100)
            start_date = base_date + datetime.timedelta(days=start_offset_days)
            sanction_date = start_date - datetime.timedelta(days=random.randint(15, 60))
            expected_completion = start_date + datetime.timedelta(days=base_duration)
            
            # Determine Anomaly Type for injection
            anomaly_type = "NORMAL"
            
            # Injected Scenarios
            if i in range(1, 75): # Cost Inflation Anomaly (~75 records)
                anomaly_type = "COST_INFLATION"
                sanctioned_amount = sanctioned_amount * random.uniform(2.1, 3.8)
                released_amount = round(sanctioned_amount * random.uniform(0.7, 0.95), -3)
                utilized_amount = round(released_amount * random.uniform(0.8, 1.0), -3)
                physical_progress = round(random.uniform(30.0, 60.0), 1)
                financial_progress = round((utilized_amount / sanctioned_amount) * 100, 1)
                status = "In Progress"
                actual_completion = None
                
            elif i in range(75, 175): # High Financial vs Physical Progress Gap (~100 records)
                anomaly_type = "EFFICIENCY_GAP"
                released_amount = round(sanctioned_amount * random.uniform(0.85, 1.0), -3)
                utilized_amount = round(released_amount * random.uniform(0.9, 1.0), -3)
                physical_progress = round(random.uniform(15.0, 42.0), 1) # Low physical progress
                financial_progress = round((utilized_amount / sanctioned_amount) * 100, 1) # High financial (85%+)
                status = "Stalled" if physical_progress < 25 else "In Progress"
                actual_completion = None
                
            elif i in range(175, 275): # Extreme Delay (~100 records)
                anomaly_type = "EXTREME_DELAY"
                expected_completion = start_date + datetime.timedelta(days=int(base_duration * 0.8)) # Early target
                released_amount = round(sanctioned_amount * random.uniform(0.5, 0.8), -3)
                utilized_amount = round(released_amount * random.uniform(0.4, 0.7), -3)
                physical_progress = round(random.uniform(20.0, 50.0), 1)
                financial_progress = round((utilized_amount / sanctioned_amount) * 100, 1)
                status = "Delayed"
                actual_completion = None
                
            elif i in range(275, 275 + duplicate_pairs_count): # Injected Duplicates
                anomaly_type = "DUPLICATE_SUSPECT"
                d_idx = i - 275
                d_seed = duplicate_seeds[d_idx]
                state = d_seed["state"]
                district = d_seed["district"]
                constituency = d_seed["constituency"]
                ptype = d_seed["project_type"]
                project_name = d_seed["desc"]
                project_desc = f"{project_name} for rural development and civic convenience."
                sanctioned_amount = d_seed["cost"]
                lat = round(d_seed["lat"] + random.uniform(-0.005, 0.005), 6) # Within ~0.5 km
                lng = round(d_seed["lng"] + random.uniform(-0.005, 0.005), 6)
                released_amount = round(sanctioned_amount * 0.9, -3)
                utilized_amount = round(released_amount * 0.85, -3)
                physical_progress = 75.0
                financial_progress = 85.0
                status = "In Progress"
                actual_completion = None
                
            else: # Normal realistic project distribution
                # Normal progress curve based on elapsed time
                elapsed_days = (today - start_date).days
                if elapsed_days < 0:
                    status = "Sanctioned"
                    released_amount = 0.0
                    utilized_amount = 0.0
                    physical_progress = 0.0
                    financial_progress = 0.0
                    actual_completion = None
                elif elapsed_days >= base_duration + 60:
                    # Likely completed
                    if random.random() < 0.82:
                        status = "Completed"
                        released_amount = sanctioned_amount
                        utilized_amount = round(sanctioned_amount * random.uniform(0.92, 1.0), -3)
                        physical_progress = 100.0
                        financial_progress = round((utilized_amount / sanctioned_amount) * 100, 1)
                        actual_completion = expected_completion + datetime.timedelta(days=random.randint(-15, 30))
                    else:
                        status = "Delayed"
                        released_amount = round(sanctioned_amount * random.uniform(0.7, 0.9), -3)
                        utilized_amount = round(released_amount * random.uniform(0.7, 0.9), -3)
                        physical_progress = round(random.uniform(60.0, 88.0), 1)
                        financial_progress = round((utilized_amount / sanctioned_amount) * 100, 1)
                        actual_completion = None
                else:
                    # In progress
                    fraction = min(1.0, max(0.05, elapsed_days / base_duration))
                    physical_progress = round(min(98.0, fraction * 100 + random.uniform(-8, 8)), 1)
                    rel_fraction = min(1.0, fraction + random.uniform(0.05, 0.2))
                    released_amount = round(sanctioned_amount * rel_fraction, -3)
                    util_fraction = min(rel_fraction, physical_progress / 100.0 + random.uniform(-0.05, 0.08))
                    utilized_amount = round(sanctioned_amount * max(0.05, util_fraction), -3)
                    financial_progress = round((utilized_amount / sanctioned_amount) * 100, 1)
                    status = "In Progress"
                    actual_completion = None

            # Enforce non-negative bounds
            sanctioned_amount = max(100000.0, float(sanctioned_amount))
            released_amount = min(sanctioned_amount, max(0.0, float(released_amount)))
            utilized_amount = min(released_amount, max(0.0, float(utilized_amount)))
            physical_progress = min(100.0, max(0.0, float(physical_progress)))
            financial_progress = min(100.0, max(0.0, float(financial_progress)))
            
            records.append({
                "project_id": p_id,
                "project_name": project_name,
                "project_description": project_desc,
                "state": state,
                "district": district,
                "constituency": constituency,
                "latitude": lat,
                "longitude": lng,
                "project_type": ptype,
                "beneficiary_count": beneficiaries,
                "sanctioned_amount": sanctioned_amount,
                "released_amount": released_amount,
                "utilized_amount": utilized_amount,
                "physical_progress": physical_progress,
                "financial_progress": financial_progress,
                "status": status,
                "start_date": start_date.isoformat(),
                "sanction_date": sanction_date.isoformat(),
                "expected_completion_date": expected_completion.isoformat(),
                "actual_completion_date": actual_completion.isoformat() if actual_completion else None,
                "contractor_id": contractor["id"],
                "contractor_name": contractor["name"],
                "implementing_agency": agency,
                "source": "SYNTHETIC DEMO",
                "source_file": "synthetic_mplads_5000.csv",
                "source_record_id": p_id,
                "import_timestamp": datetime.datetime.now().isoformat(),
                "data_version": "v1.0"
            })

        df = pd.DataFrame(records)
        metadata = {
            "source": "SYNTHETIC DEMO",
            "total_records": len(df),
            "generated_at": datetime.datetime.now().isoformat(),
            "note": "SYNTHETIC DATA FOR DEMONSTRATION PURPOSES ONLY"
        }
        return df, metadata
