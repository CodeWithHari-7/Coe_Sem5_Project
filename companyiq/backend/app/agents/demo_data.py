"""
Demo data for Tata Motors — clearly labeled as synthetic/demo data.
Used when DEMO_MODE=true or no real LLM API key is configured.
All data is illustrative — not real-world facts verified at runtime.
"""

DEMO_COMPANY_INTELLIGENCE = {
    "data_label": "DEMO_DATA",
    "disclaimer": "This is synthetic demo data for illustrative purposes only. Not verified real-world information.",
    "company_profile": {
        "name": "Tata Motors",
        "industry": "Automotive / Electric Vehicles",
        "description": "Tata Motors is one of India's largest automobile manufacturers and a subsidiary of the Tata Group. The company produces passenger vehicles, commercial vehicles, and has made significant strides in the electric vehicle segment.",
        "business_model": "Design, manufacture, and sale of vehicles across passenger and commercial segments. Revenue from vehicle sales, spare parts, financing, and fleet management services.",
        "products_services": [
            "Passenger Vehicles (Tata Nexon, Tata Punch, Tata Safari)",
            "Electric Vehicles (Tata Nexon EV, Tata Tiago EV, Tata Tigor EV)",
            "Commercial Vehicles (Trucks, Buses, Vans)",
            "Defense Vehicles",
            "Vehicle Financing (Tata Motors Finance)",
            "Fleet Management Services"
        ],
        "market_position": "Market leader in Indian EV segment with ~70% market share (demo estimate). Global operations through Jaguar Land Rover (JLR) subsidiary.",
        "technologies": [
            "Battery Electric Vehicle (BEV) platform",
            "Zinc-Air battery research",
            "ADAS (Advanced Driver Assistance Systems)",
            "Connected car technology",
            "OTA software updates",
            "Battery Management Systems (BMS)"
        ],
        "strategic_priorities": [
            "Accelerate EV portfolio expansion (10+ EV models by 2026 — demo projection)",
            "Develop domestic battery manufacturing capability",
            "Expand charging infrastructure partnerships",
            "Grow Jaguar Land Rover EV lineup",
            "Reduce carbon footprint across manufacturing"
        ],
        "recent_developments": [
            "[DEMO] Tata Motors announced investment in battery cell manufacturing JV",
            "[DEMO] Launched Tata Punch EV with extended range battery",
            "[DEMO] Partnership with Tata Power for EV charging network expansion",
            "[DEMO] Secured fleet EV orders from government agencies",
            "[DEMO] JLR announced all-electric Range Rover timeline"
        ],
        "potential_challenges": [
            "Battery raw material supply chain dependency",
            "Charging infrastructure gaps in Tier-2/3 cities",
            "Increasing competition from Chinese EV manufacturers",
            "High upfront EV cost vs. ICE alternatives",
            "Semiconductor supply chain volatility"
        ],
        "business_signals": [
            "Strong EV sales growth trajectory",
            "Active government FAME-II subsidy beneficiary",
            "Battery technology R&D investment signals",
            "Fleet electrification deals pipeline"
        ],
        "competitive_landscape": [
            "MG Motor India (EV segment competitor)",
            "Hyundai Motor India (Kona EV, Ioniq 5)",
            "BYD India (growing presence)",
            "Mahindra Electric (domestic competitor)",
            "Ola Electric (two-wheeler EV adjacent market)"
        ],
        "decision_maker_roles": [
            "Chief Technology Officer (CTO) — EV platform decisions",
            "VP of EV Business Unit — commercial EV strategy",
            "Head of Battery Technology — battery R&D partnerships",
            "VP of Supply Chain — battery cell sourcing",
            "Chief Digital Officer — connected vehicle / data platforms"
        ],
        "confidence": {
            "value": 0.72,
            "label": "MEDIUM",
            "basis": "demo_data",
            "evidence_count": 8
        },
        "insufficient_evidence": False
    },
    "opportunities": [
        {
            "title": "Battery Predictive Analytics Platform",
            "description": "Tata Motors' aggressive EV expansion creates strong demand for battery health monitoring, predictive maintenance, and remaining useful life (RUL) estimation systems.",
            "opportunity_type": "product_fit",
            "what": "Deploy an AI-powered battery analytics platform that monitors cell-level health metrics, predicts failures, and optimizes charging cycles across the EV fleet.",
            "why": "Tata Motors is scaling EV production rapidly while managing battery warranty costs. Predictive analytics can reduce warranty claims by 15-25% and improve customer satisfaction.",
            "evidence": [
                {
                    "source_type": "demo",
                    "title": "[DEMO] Tata Motors EV Expansion Announcement",
                    "url": None,
                    "snippet": "Tata Motors plans to invest significantly in battery technology and EV manufacturing scale-up.",
                    "relevance_score": 0.91,
                    "publication_date": "2024-Q3",
                    "retrieved_at": "2024-12-01"
                },
                {
                    "source_type": "demo",
                    "title": "[DEMO] EV Battery Warranty Cost Analysis",
                    "url": None,
                    "snippet": "Battery-related warranty claims represent 30-40% of total EV warranty costs industry-wide.",
                    "relevance_score": 0.85,
                    "publication_date": "2024-Q2",
                    "retrieved_at": "2024-12-01"
                }
            ],
            "confidence": {"value": 0.87, "label": "HIGH", "basis": "evidence_coverage", "evidence_count": 2},
            "limitations": "Actual battery warranty cost data for Tata Motors is not publicly available. Opportunity sizing requires internal data access.",
            "score_breakdown": {
                "business_relevance": 92.0,
                "recent_activity": 85.0,
                "product_fit": 90.0,
                "historical_similarity": 72.0,
                "evidence_confidence": 88.0,
                "overall": 87.0,
                "level": "HIGH"
            },
            "insufficient_evidence": False
        },
        {
            "title": "Fleet EV Data Intelligence Platform",
            "description": "Government and corporate fleet electrification creates demand for fleet-level analytics, route optimization, and energy cost management.",
            "opportunity_type": "product_fit",
            "what": "Provide a SaaS fleet intelligence platform covering real-time EV health, route optimization, charging scheduling, and total cost of ownership dashboards.",
            "why": "Tata Motors is actively securing fleet EV contracts. Fleet operators need analytics to justify EV adoption ROI.",
            "evidence": [
                {
                    "source_type": "demo",
                    "title": "[DEMO] Government Fleet Electrification Policy",
                    "url": None,
                    "snippet": "Indian government mandated electrification of government vehicle fleet under EV30@30 initiative.",
                    "relevance_score": 0.80,
                    "publication_date": "2024-Q1",
                    "retrieved_at": "2024-12-01"
                }
            ],
            "confidence": {"value": 0.74, "label": "HIGH", "basis": "evidence_coverage", "evidence_count": 1},
            "limitations": "Fleet contract pipeline size not publicly confirmed. Competition from established fleet management players.",
            "score_breakdown": {
                "business_relevance": 80.0,
                "recent_activity": 78.0,
                "product_fit": 75.0,
                "historical_similarity": 65.0,
                "evidence_confidence": 70.0,
                "overall": 74.6,
                "level": "HIGH"
            },
            "insufficient_evidence": False
        },
        {
            "title": "Connected Vehicle Data Platform",
            "description": "OTA software updates and connected vehicle features create opportunity for data platform, API marketplace, and developer ecosystem services.",
            "opportunity_type": "product_fit",
            "what": "Build or integrate a connected vehicle data platform that ingests telemetry data, enables third-party app integrations, and provides a monetizable data marketplace.",
            "why": "Tata Motors is investing in connected car technology and OTA updates, indicating data platform infrastructure readiness.",
            "evidence": [
                {
                    "source_type": "demo",
                    "title": "[DEMO] Tata Motors Connected Vehicle Initiative",
                    "url": None,
                    "snippet": "Tata Motors expanding connected features across its EV lineup with OTA update capability.",
                    "relevance_score": 0.77,
                    "publication_date": "2024-Q2",
                    "retrieved_at": "2024-12-01"
                }
            ],
            "confidence": {"value": 0.62, "label": "MEDIUM", "basis": "evidence_coverage", "evidence_count": 1},
            "limitations": "Tata Motors' data monetization strategy not publicly confirmed. Regulatory constraints on vehicle data in India.",
            "score_breakdown": {
                "business_relevance": 70.0,
                "recent_activity": 65.0,
                "product_fit": 68.0,
                "historical_similarity": 55.0,
                "evidence_confidence": 62.0,
                "overall": 65.2,
                "level": "MEDIUM"
            },
            "insufficient_evidence": False
        }
    ],
    "account_plan": {
        "title": "Tata Motors — Account Plan Q4 2024",
        "company_name": "Tata Motors",
        "ai_confidence": 0.76,
        "data_label": "DEMO_DATA",
        "sections": [
            {
                "id": "s1",
                "title": "Company Overview",
                "section_type": "overview",
                "status": "AI_GENERATED",
                "priority": "high",
                "order": 1,
                "content": "Tata Motors is India's largest automobile manufacturer and a global automotive player through its Jaguar Land Rover (JLR) subsidiary. The company has established itself as the dominant player in the Indian EV market with approximately 70% market share (demo estimate). With aggressive plans to expand its EV portfolio to 10+ models by 2026 and significant investments in battery technology, Tata Motors presents a strong opportunity for AI-powered analytics and platform partnerships.",
                "confidence": 0.76,
                "evidence": [],
                "human_note": None,
                "recommendations": []
            },
            {
                "id": "s2",
                "title": "Business Goals",
                "section_type": "goals",
                "status": "AI_GENERATED",
                "priority": "high",
                "order": 2,
                "content": "1. Become the leading EV manufacturer in India by 2026\n2. Develop domestic battery manufacturing capability to reduce import dependency\n3. Expand JLR's all-electric lineup globally\n4. Grow fleet EV business through government and corporate contracts\n5. Achieve carbon neutrality across manufacturing by 2035",
                "confidence": 0.71,
                "evidence": [],
                "human_note": None,
                "recommendations": []
            },
            {
                "id": "s3",
                "title": "Current Challenges",
                "section_type": "challenges",
                "status": "AI_GENERATED",
                "priority": "high",
                "order": 3,
                "content": "1. Battery raw material supply chain — heavy reliance on imported lithium-ion cells\n2. Charging infrastructure gaps in Tier-2/3 Indian cities limiting EV adoption\n3. Rising competition from BYD and other Chinese EV manufacturers entering India\n4. High upfront EV cost compared to ICE alternatives creating adoption friction\n5. Battery warranty cost management as EV fleet ages",
                "confidence": 0.73,
                "evidence": [],
                "human_note": None,
                "recommendations": []
            },
            {
                "id": "s4",
                "title": "Business Opportunities",
                "section_type": "opportunities",
                "status": "AI_GENERATED",
                "priority": "high",
                "order": 4,
                "content": "Three high-priority opportunities identified:\n\n1. Battery Predictive Analytics (Score: 87/100 — HIGH)\nAI-powered battery health monitoring and predictive maintenance.\n\n2. Fleet EV Data Intelligence (Score: 74/100 — HIGH)\nFleet analytics and route optimization for B2B EV customers.\n\n3. Connected Vehicle Data Platform (Score: 65/100 — MEDIUM)\nVehicle telemetry data platform and developer ecosystem.",
                "confidence": 0.80,
                "evidence": [],
                "human_note": None,
                "recommendations": []
            },
            {
                "id": "s5",
                "title": "Key Stakeholder Roles",
                "section_type": "stakeholders",
                "status": "AI_GENERATED",
                "priority": "medium",
                "order": 5,
                "content": "Primary Decision Makers (hypothesis — verify through outreach):\n\n1. CTO — Technology strategy and EV platform decisions\n2. VP EV Business Unit — Commercial EV product roadmap\n3. Head of Battery Technology — Battery R&D and vendor partnerships\n4. VP Supply Chain — Battery cell sourcing and supply decisions\n5. Chief Digital Officer — Connected vehicle and data platform strategy\n\n⚠️ [AI HYPOTHESIS] These roles are inferred from industry norms. Verify actual decision makers before outreach.",
                "confidence": 0.55,
                "evidence": [],
                "human_note": None,
                "recommendations": []
            },
            {
                "id": "s6",
                "title": "Recommended Next Actions",
                "section_type": "actions",
                "status": "AI_GENERATED",
                "priority": "high",
                "order": 6,
                "content": "1. Schedule discovery call with Tata Motors EV Business Unit leadership\n2. Prepare battery analytics ROI analysis (warranty cost reduction model)\n3. Identify Tata Motors fleet EV contracts pipeline via public announcements\n4. Develop Tata-specific product demo for battery predictive analytics\n5. Research JLR digital strategy for potential parallel opportunity in European market",
                "confidence": 0.70,
                "evidence": [],
                "human_note": None,
                "recommendations": []
            },
            {
                "id": "s7",
                "title": "Risks",
                "section_type": "risks",
                "status": "AI_GENERATED",
                "priority": "medium",
                "order": 7,
                "content": "1. Tata Motors may develop battery analytics capability in-house through Tata Consultancy Services (TCS) — related group company\n2. Long enterprise sales cycle in automotive sector (12-18 months typical)\n3. Budget freeze risk if EV sales growth slows\n4. Regulatory data sovereignty concerns for vehicle telemetry",
                "confidence": 0.65,
                "evidence": [],
                "human_note": None,
                "recommendations": []
            },
            {
                "id": "s8",
                "title": "Research Timeline",
                "section_type": "timeline",
                "status": "AI_GENERATED",
                "priority": "low",
                "order": 8,
                "content": "Initial Research: December 2024 [DEMO]\nNext Refresh: January 2025 [DEMO]\nTarget First Contact: Q1 2025 [DEMO]\nPilot Proposal: Q2 2025 [DEMO]",
                "confidence": 0.60,
                "evidence": [],
                "human_note": None,
                "recommendations": []
            }
        ]
    },
    "evaluation": {
        "baseline": {
            "system_type": "baseline",
            "precision": 0.52,
            "recall": 0.48,
            "f1_score": 0.50,
            "acceptance_rate": 0.41,
            "avg_response_time_ms": 320.0,
            "evidence_coverage": 0.35,
            "false_positive_rate": 0.28,
            "false_negative_rate": 0.31,
            "failure_rate": 0.12,
            "is_synthetic": True
        },
        "ai_rag": {
            "system_type": "ai_rag",
            "precision": 0.76,
            "recall": 0.71,
            "f1_score": 0.735,
            "acceptance_rate": 0.68,
            "avg_response_time_ms": 1850.0,
            "evidence_coverage": 0.82,
            "false_positive_rate": 0.14,
            "false_negative_rate": 0.18,
            "failure_rate": 0.04,
            "is_synthetic": True
        },
        "improvement": {
            "precision": 46.2,
            "recall": 47.9,
            "f1_score": 47.0,
            "acceptance_rate": 65.9,
            "evidence_coverage": 134.3,
            "failure_rate": -66.7
        },
        "notes": "⚠️ SYNTHETIC EVALUATION — These metrics are illustrative demo values, not from real user studies. Real evaluation requires actual user feedback data.",
        "generated_at": "2024-12-01T00:00:00Z"
    }
}

DEMO_COMPANIES = [
    {"name": "Tata Motors", "industry": "Automotive / EV", "size": "Enterprise", "country": "India", "is_demo": True},
    {"name": "Infosys", "industry": "IT Services / SaaS", "size": "Enterprise", "country": "India", "is_demo": True},
    {"name": "Apollo Hospitals", "industry": "Healthcare", "size": "Enterprise", "country": "India", "is_demo": True},
    {"name": "Reliance Retail", "industry": "Retail", "size": "Enterprise", "country": "India", "is_demo": True},
    {"name": "HDFC Bank", "industry": "Banking / Financial Services", "size": "Enterprise", "country": "India", "is_demo": True},
    {"name": "Mahindra Logistics", "industry": "Logistics / Supply Chain", "size": "Enterprise", "country": "India", "is_demo": True},
    {"name": "Adani Green Energy", "industry": "Renewable Energy", "size": "Enterprise", "country": "India", "is_demo": True},
    {"name": "Delhivery", "industry": "Logistics / E-commerce", "size": "Mid-Market", "country": "India", "is_demo": True},
    {"name": "Razorpay", "industry": "Fintech / SaaS", "size": "Mid-Market", "country": "India", "is_demo": True},
    {"name": "Ola Electric", "industry": "EV / Two-Wheeler", "size": "Mid-Market", "country": "India", "is_demo": True},
]
