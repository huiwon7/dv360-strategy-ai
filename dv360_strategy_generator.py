"""
DV360 Campaign Strategy AI Generator
=====================================
3-Layer Architecture: Input Interface → Context Assembly → Multi-Agent Reasoning

Version: 2026Q1
Author: VIVIDAD
"""

import json
import os
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/strategy_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# LAYER 1: INPUT INTERFACE
# ============================================================================

class FunnelStage(Enum):
    AWARENESS = "인지(Awareness)"
    CONSIDERATION = "고려(Consideration)"
    CONVERSION = "전환(Conversion)"


class CampaignGoal(Enum):
    BRAND_AWARENESS = "Brand Awareness"
    LEAD_GENERATION = "Lead Generation"
    PURCHASE = "Purchase"
    APP_INSTALL = "App Install"


@dataclass
class CampaignBrief:
    """Structured input for campaign brief"""
    industry: str
    product_service: str
    target_demographic: str
    funnel_stage: FunnelStage
    campaign_goal: CampaignGoal
    budget: int  # Monthly budget in KRW
    duration_days: int
    kpi_type: str  # "CPA" or "ROAS"
    kpi_target: float
    geo_targets: List[str] = field(default_factory=list)
    first_party_data: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "industry": self.industry,
            "product_service": self.product_service,
            "target_demographic": self.target_demographic,
            "funnel_stage": self.funnel_stage.value,
            "campaign_goal": self.campaign_goal.value,
            "budget": self.budget,
            "duration_days": self.duration_days,
            "kpi_type": self.kpi_type,
            "kpi_target": self.kpi_target,
            "geo_targets": self.geo_targets,
            "first_party_data": self.first_party_data,
            "constraints": self.constraints
        }


class InputParser:
    """Parse and validate user input"""

    INDUSTRY_MAPPING = {
        "건강": "건강기능식품",
        "health": "건강기능식품",
        "supplement": "건강기능식품",
        "교육": "교육",
        "education": "교육",
        "금융": "금융",
        "finance": "금융",
        "패션": "이커머스_패션",
        "fashion": "이커머스_패션",
        "운세": "서비스_운세상담",
        "fortune": "서비스_운세상담",
    }

    @classmethod
    def parse_brief(cls, raw_input: Dict) -> CampaignBrief:
        """Parse raw input into structured CampaignBrief"""
        industry = cls._normalize_industry(raw_input.get("industry", ""))

        funnel_stage = cls._parse_funnel_stage(raw_input.get("funnel_stage", ""))
        campaign_goal = cls._parse_campaign_goal(raw_input.get("campaign_goal", ""))

        return CampaignBrief(
            industry=industry,
            product_service=raw_input.get("product_service", ""),
            target_demographic=raw_input.get("target_demographic", ""),
            funnel_stage=funnel_stage,
            campaign_goal=campaign_goal,
            budget=int(raw_input.get("budget", 0)),
            duration_days=int(raw_input.get("duration_days", 30)),
            kpi_type=raw_input.get("kpi_type", "CPA"),
            kpi_target=float(raw_input.get("kpi_target", 0)),
            geo_targets=raw_input.get("geo_targets", ["대한민국 전역"]),
            first_party_data=raw_input.get("first_party_data", {}),
            constraints=raw_input.get("constraints", [])
        )

    @classmethod
    def _normalize_industry(cls, industry: str) -> str:
        industry_lower = industry.lower()
        for key, value in cls.INDUSTRY_MAPPING.items():
            if key in industry_lower:
                return value
        return industry

    @classmethod
    def _parse_funnel_stage(cls, stage: str) -> FunnelStage:
        stage_lower = stage.lower()
        if "인지" in stage_lower or "awareness" in stage_lower:
            return FunnelStage.AWARENESS
        elif "고려" in stage_lower or "consideration" in stage_lower:
            return FunnelStage.CONSIDERATION
        else:
            return FunnelStage.CONVERSION

    @classmethod
    def _parse_campaign_goal(cls, goal: str) -> CampaignGoal:
        goal_lower = goal.lower()
        if "brand" in goal_lower or "인지" in goal_lower:
            return CampaignGoal.BRAND_AWARENESS
        elif "lead" in goal_lower or "리드" in goal_lower:
            return CampaignGoal.LEAD_GENERATION
        elif "purchase" in goal_lower or "구매" in goal_lower:
            return CampaignGoal.PURCHASE
        elif "app" in goal_lower or "앱" in goal_lower:
            return CampaignGoal.APP_INSTALL
        else:
            return CampaignGoal.LEAD_GENERATION


# ============================================================================
# LAYER 2: CONTEXT ASSEMBLY ENGINE
# ============================================================================

class KnowledgeBase:
    """3-Tier Hybrid Knowledge Base (without Vector DB)"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.static_knowledge = {}
        self.golden_dataset = []
        self.validation_checklist = {}
        self._load_knowledge()

    def _load_knowledge(self):
        """Load all knowledge base files"""
        # Load static knowledge (markdown files)
        kb_path = self.base_path / "knowledge_base"
        if kb_path.exists():
            for md_file in kb_path.glob("*.md"):
                with open(md_file, 'r', encoding='utf-8') as f:
                    self.static_knowledge[md_file.stem] = f.read()
                logger.info(f"Loaded static knowledge: {md_file.stem}")

        # Load golden dataset
        golden_path = self.base_path / "templates" / "golden_dataset.json"
        if golden_path.exists():
            with open(golden_path, 'r', encoding='utf-8') as f:
                self.golden_dataset = json.load(f)
            logger.info(f"Loaded {len(self.golden_dataset)} golden templates")

        # Load validation checklist
        checklist_path = self.base_path / "templates" / "validation_checklist.json"
        if checklist_path.exists():
            with open(checklist_path, 'r', encoding='utf-8') as f:
                self.validation_checklist = json.load(f)
            logger.info("Loaded validation checklist")

    def find_similar_template(self, brief: CampaignBrief) -> Optional[Dict]:
        """Find most similar template from golden dataset"""
        best_match = None
        best_score = 0

        for template in self.golden_dataset:
            score = self._calculate_similarity(brief, template)
            if score > best_score:
                best_score = score
                best_match = template

        logger.info(f"Best template match: {best_match.get('template_id') if best_match else 'None'} (score: {best_score})")
        return best_match

    def _calculate_similarity(self, brief: CampaignBrief, template: Dict) -> float:
        """Calculate similarity score between brief and template"""
        score = 0.0

        # Industry match (40% weight)
        if brief.industry == template.get("industry"):
            score += 0.4
        elif brief.industry in template.get("industry", ""):
            score += 0.2

        # Funnel stage match (30% weight)
        if brief.funnel_stage.value == template.get("funnel_stage"):
            score += 0.3

        # Budget range match (20% weight)
        budget_range = template.get("budget_range", "")
        if self._budget_in_range(brief.budget, budget_range):
            score += 0.2

        # Target demographic overlap (10% weight)
        template_demo = template.get("target_demographic", "")
        if any(age in template_demo for age in brief.target_demographic.split("-")):
            score += 0.1

        return score

    def _budget_in_range(self, budget: int, range_str: str) -> bool:
        """Check if budget falls within range string"""
        try:
            # Parse range like "월 300만-1,000만원"
            range_str = range_str.replace("월", "").replace("원", "").replace(",", "").replace(" ", "")
            parts = range_str.split("-")
            if len(parts) == 2:
                min_val = int(parts[0].replace("만", "0000"))
                max_val = int(parts[1].replace("만", "0000"))
                return min_val <= budget <= max_val
        except:
            pass
        return False

    def get_bidding_guide(self, strategy: str) -> str:
        """Get bidding strategy guide from static knowledge"""
        bidding_kb = self.static_knowledge.get("dv360_bidding_strategies_2026Q1", "")
        # Extract relevant section
        if strategy.lower() in bidding_kb.lower():
            return bidding_kb
        return ""

    def get_targeting_guide(self, audience_type: str) -> str:
        """Get targeting guide from static knowledge"""
        targeting_kb = self.static_knowledge.get("dv360_targeting_options_2026Q1", "")
        return targeting_kb


class ContextAssembler:
    """Gather → Glean pipeline for context assembly"""

    TOKEN_BUDGET = 8000  # Max tokens for context

    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base

    def assemble_context(self, brief: CampaignBrief) -> Dict:
        """Assemble relevant context for strategy generation"""
        context = {
            "brief": brief.to_dict(),
            "similar_template": None,
            "bidding_guide": "",
            "targeting_guide": "",
            "seasonality": {},
            "benchmarks": {}
        }

        # Gather phase: Collect all potentially relevant information
        gathered = self._gather(brief)

        # Glean phase: Filter and prioritize
        context = self._glean(gathered, brief)

        return context

    def _gather(self, brief: CampaignBrief) -> Dict:
        """Gather all potentially relevant information"""
        return {
            "template": self.kb.find_similar_template(brief),
            "bidding": self.kb.get_bidding_guide(brief.kpi_type),
            "targeting": self.kb.get_targeting_guide("all"),
            "checklist": self.kb.validation_checklist
        }

    def _glean(self, gathered: Dict, brief: CampaignBrief) -> Dict:
        """Filter and prioritize gathered information"""
        template = gathered.get("template", {})

        # Extract relevant benchmarks from template
        benchmarks = {}
        if template:
            success_metrics = template.get("success_metrics", {})
            benchmarks = {
                "industry": template.get("industry"),
                "achieved_cpa": success_metrics.get("achieved_cpa"),
                "target_cpa": success_metrics.get("target_cpa"),
                "conversion_rate": success_metrics.get("conversion_rate"),
                "roas": success_metrics.get("roas"),
                "key_learnings": template.get("key_learnings", [])
            }

        # Calculate seasonality factors
        seasonality = self._calculate_seasonality(brief)

        return {
            "brief": brief.to_dict(),
            "similar_template": template,
            "benchmarks": benchmarks,
            "seasonality": seasonality,
            "validation_rules": gathered.get("checklist", {}).get("validation_categories", [])
        }

    def _calculate_seasonality(self, brief: CampaignBrief) -> Dict:
        """Calculate seasonality adjustments"""
        now = datetime.now()
        month = now.month

        seasonality = {
            "current_month": month,
            "is_peak_season": False,
            "cpm_adjustment": 1.0,
            "notes": []
        }

        # Industry-specific seasonality
        if brief.industry == "서비스_운세상담":
            if month in [1, 12]:  # New Year season
                seasonality["is_peak_season"] = True
                seasonality["cpm_adjustment"] = 1.2
                seasonality["notes"].append("신년 시즌: CPA 20% 감소 예상")
        elif brief.industry == "교육":
            if month in [2, 3, 8, 9]:  # School season
                seasonality["is_peak_season"] = True
                seasonality["cpm_adjustment"] = 0.8
                seasonality["notes"].append("신학기 시즌: CPA 40% 감소 예상")
        elif brief.industry == "이커머스_패션":
            if month in [5, 11]:  # Sale seasons
                seasonality["is_peak_season"] = True
                seasonality["cpm_adjustment"] = 1.3
                seasonality["notes"].append("세일 시즌: 리타겟팅 빈도 확대 권장")

        return seasonality


# ============================================================================
# LAYER 3: MULTI-AGENT REASONING SYSTEM
# ============================================================================

@dataclass
class CampaignStrategy:
    """Generated campaign strategy structure"""
    campaign_name: str
    campaign_goal: str
    total_budget: int
    duration_days: int
    insertion_orders: List[Dict]
    targeting_summary: Dict
    bidding_summary: Dict
    optimization_roadmap: List[Dict]
    floodlight_setup: Dict
    validation_results: Dict = field(default_factory=dict)
    grade: str = ""


class PlannerAgent:
    """Generate initial campaign strategy"""

    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base

    def generate_strategy(self, context: Dict) -> CampaignStrategy:
        """Generate campaign strategy based on context"""
        brief = context["brief"]
        template = context.get("similar_template", {})
        benchmarks = context.get("benchmarks", {})
        seasonality = context.get("seasonality", {})

        logger.info(f"Generating strategy for {brief['industry']} campaign")

        # Calculate budget allocation
        budget_allocation = self._calculate_budget_allocation(brief, template)

        # Generate insertion orders
        ios = self._generate_insertion_orders(brief, template, budget_allocation)

        # Generate targeting summary
        targeting = self._generate_targeting_summary(brief, template)

        # Generate bidding summary
        bidding = self._generate_bidding_summary(brief, benchmarks, seasonality)

        # Generate optimization roadmap
        roadmap = self._generate_optimization_roadmap(brief)

        # Generate Floodlight setup
        floodlight = self._generate_floodlight_setup(brief)

        strategy = CampaignStrategy(
            campaign_name=f"DV360_{brief['industry']}_{datetime.now().strftime('%Y%m')}",
            campaign_goal=brief["campaign_goal"],
            total_budget=brief["budget"],
            duration_days=brief["duration_days"],
            insertion_orders=ios,
            targeting_summary=targeting,
            bidding_summary=bidding,
            optimization_roadmap=roadmap,
            floodlight_setup=floodlight
        )

        return strategy

    def _calculate_budget_allocation(self, brief: Dict, template: Dict) -> Dict:
        """Calculate budget allocation based on funnel stage"""
        funnel = brief.get("funnel_stage", "")

        if "전환" in funnel or "Conversion" in funnel:
            return {
                "remarketing": 0.5,
                "prospecting_inmarket": 0.3,
                "prospecting_similar": 0.2
            }
        elif "고려" in funnel or "Consideration" in funnel:
            return {
                "remarketing": 0.35,
                "prospecting_inmarket": 0.40,
                "prospecting_custom": 0.25
            }
        else:  # Awareness
            return {
                "prospecting_affinity": 0.50,
                "prospecting_inmarket": 0.30,
                "remarketing": 0.20
            }

    def _generate_insertion_orders(self, brief: Dict, template: Dict, allocation: Dict) -> List[Dict]:
        """Generate insertion orders structure"""
        ios = []
        budget = brief["budget"]

        # Use template structure if available, otherwise generate default
        if template and "campaign_structure" in template:
            template_ios = template["campaign_structure"].get("insertion_orders", [])
            for tpl_io in template_ios:
                io = {
                    "io_name": tpl_io.get("io_name", "IO_Default"),
                    "budget": int(budget * float(tpl_io.get("budget_allocation", "30%").replace("%", "")) / 100),
                    "pacing": tpl_io.get("pacing", "Even"),
                    "line_items": []
                }

                for tpl_li in tpl_io.get("line_items", []):
                    li = {
                        "li_name": tpl_li.get("li_name", "LI_Default"),
                        "targeting": tpl_li.get("targeting", {}),
                        "bidding": tpl_li.get("bidding", {}),
                        "frequency_cap": tpl_li.get("frequency_cap", "3회/일, 15회/주"),
                        "creative": tpl_li.get("creative", {})
                    }
                    io["line_items"].append(li)

                ios.append(io)
        else:
            # Generate default structure
            ios = self._generate_default_ios(brief, allocation)

        return ios

    def _generate_default_ios(self, brief: Dict, allocation: Dict) -> List[Dict]:
        """Generate default IO structure"""
        budget = brief["budget"]
        ios = []

        for io_type, ratio in allocation.items():
            io = {
                "io_name": f"IO_{io_type.replace('_', ' ').title().replace(' ', '_')}",
                "budget": int(budget * ratio),
                "pacing": "ASAP" if "remarketing" in io_type else "Even",
                "line_items": [{
                    "li_name": f"LI_{io_type}_Main",
                    "targeting": {"audience": io_type, "geo": brief.get("geo_targets", ["대한민국 전역"])},
                    "bidding": {"strategy": brief.get("kpi_type", "CPA"), "target": brief.get("kpi_target", 0)},
                    "frequency_cap": "3회/일, 15회/주"
                }]
            }
            ios.append(io)

        return ios

    def _generate_targeting_summary(self, brief: Dict, template: Dict) -> Dict:
        """Generate targeting summary"""
        return {
            "primary_audience": template.get("target_demographic", brief.get("target_demographic", "")),
            "geo_targets": brief.get("geo_targets", ["대한민국 전역"]),
            "device_split": "Mobile 80% / Desktop 20%",
            "time_targeting": "전 시간대 (저녁 7-11시 입찰 상향)",
            "exclusions": ["기존 전환 고객", "경쟁사 직원"]
        }

    def _generate_bidding_summary(self, brief: Dict, benchmarks: Dict, seasonality: Dict) -> Dict:
        """Generate bidding summary"""
        kpi_type = brief.get("kpi_type", "CPA")
        kpi_target = brief.get("kpi_target", 0)

        # Adjust target based on benchmarks
        if benchmarks.get("achieved_cpa"):
            benchmark_cpa = int(benchmarks["achieved_cpa"].replace("원", "").replace(",", ""))
            if kpi_target > benchmark_cpa * 1.5:
                recommendation = "목표 CPA가 벤치마크 대비 높음, 달성 가능성 높음"
            elif kpi_target < benchmark_cpa * 0.7:
                recommendation = "목표 CPA가 벤치마크 대비 낮음, 상향 조정 권장"
            else:
                recommendation = "목표 CPA가 벤치마크와 유사, 적절한 목표"
        else:
            recommendation = "벤치마크 데이터 없음, 2주 학습 후 조정 권장"

        return {
            "primary_strategy": f"Target {kpi_type}",
            "target_value": f"{kpi_target:,}원" if kpi_type == "CPA" else f"{kpi_target}%",
            "phase_1": "Maximize Conversions (1-2주)",
            "phase_2": f"Target {kpi_type} (2-4주)",
            "seasonality_adjustment": seasonality.get("cpm_adjustment", 1.0),
            "recommendation": recommendation
        }

    def _generate_optimization_roadmap(self, brief: Dict) -> List[Dict]:
        """Generate optimization roadmap"""
        return [
            {
                "phase": "Phase 1: 학습 (Week 1-2)",
                "actions": [
                    "Maximize Conversions 전략으로 시작",
                    "전체 예산의 70% 활용",
                    "A/B 테스트 셋업 (메시지/크리에이티브)"
                ],
                "kpis": ["전환 수", "CPM", "CTR"]
            },
            {
                "phase": "Phase 2: 최적화 (Week 3-4)",
                "actions": [
                    f"Target {brief.get('kpi_type', 'CPA')} 전환",
                    "저성과 Line Item 예산 재배분",
                    "고성과 오디언스 확장"
                ],
                "kpis": [brief.get("kpi_type", "CPA"), "전환율", "ROAS"]
            }
        ]

    def _generate_floodlight_setup(self, brief: Dict) -> Dict:
        """Generate Floodlight setup guide"""
        return {
            "global_site_tag": "gtag.js 설치 필요",
            "activities": [
                {
                    "name": "Purchase/Lead",
                    "type": "Counter",
                    "counting_method": "Standard",
                    "attribution_window": {
                        "click": "30일",
                        "view": "1일"
                    }
                },
                {
                    "name": "PageView",
                    "type": "Counter",
                    "counting_method": "Per Session"
                }
            ],
            "audience_lists": [
                "All Visitors (30일)",
                "Product Viewers (14일)",
                "Cart Abandoners (7일)",
                "Converters (90일) - Exclusion용"
            ]
        }


class CriticAgent:
    """Validate strategy against 15-point checklist"""

    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.checklist = knowledge_base.validation_checklist

    def validate(self, strategy: CampaignStrategy, context: Dict) -> Dict:
        """Run 15-point validation"""
        results = {
            "passed": [],
            "warnings": [],
            "critical_failures": [],
            "score": 0,
            "grade": ""
        }

        categories = self.checklist.get("validation_categories", [])
        total_checks = 0
        passed_checks = 0

        for category in categories:
            for item in category.get("items", []):
                total_checks += 1
                check_result = self._run_check(item, strategy, context)

                if check_result["passed"]:
                    passed_checks += 1
                    results["passed"].append(check_result)
                elif check_result["severity"] == "critical":
                    results["critical_failures"].append(check_result)
                else:
                    results["warnings"].append(check_result)

        # Calculate score and grade
        results["score"] = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        results["grade"] = self._calculate_grade(results)

        logger.info(f"Validation complete: {results['grade']} ({results['score']:.1f}%)")

        return results

    def _run_check(self, item: Dict, strategy: CampaignStrategy, context: Dict) -> Dict:
        """Run individual validation check"""
        check_id = item.get("id", "")
        check_result = {
            "id": check_id,
            "description": item.get("description", ""),
            "severity": item.get("severity", "info"),
            "passed": True,
            "message": ""
        }

        # Budget validation checks
        if check_id == "BV001":
            io_total = sum(io.get("budget", 0) for io in strategy.insertion_orders)
            if io_total != strategy.total_budget:
                check_result["passed"] = False
                check_result["message"] = f"예산 불일치: IO 합계({io_total:,}) ≠ 총예산({strategy.total_budget:,})"

        elif check_id == "BV002":
            daily_budget = strategy.total_budget / strategy.duration_days
            target_cpa = context["brief"].get("kpi_target", 0)
            if target_cpa > 0 and daily_budget < target_cpa * 10:
                check_result["passed"] = False
                check_result["message"] = f"일일 예산({daily_budget:,.0f})이 목표 CPA({target_cpa:,})의 10배 미만"

        # Targeting validation checks
        elif check_id == "TV004":
            for io in strategy.insertion_orders:
                for li in io.get("line_items", []):
                    freq_cap = li.get("frequency_cap", "")
                    # Simple frequency cap check
                    if "무제한" in freq_cap:
                        check_result["passed"] = False
                        check_result["message"] = "무제한 Frequency Cap 발견, 조정 권장"
                        break

        # Structure validation checks
        elif check_id == "SV001":
            if not strategy.insertion_orders:
                check_result["passed"] = False
                check_result["message"] = "Insertion Order가 없음"
            else:
                for io in strategy.insertion_orders:
                    if not io.get("line_items"):
                        check_result["passed"] = False
                        check_result["message"] = f"{io.get('io_name', 'IO')}에 Line Item이 없음"
                        break

        return check_result

    def _calculate_grade(self, results: Dict) -> str:
        """Calculate grade based on validation results"""
        score = results["score"]
        critical_count = len(results["critical_failures"])
        warning_count = len(results["warnings"])

        grading = self.checklist.get("grading_system", {})

        if critical_count == 0 and score >= 95 and warning_count <= 1:
            return "S"
        elif critical_count == 0 and score >= 85 and warning_count <= 3:
            return "A"
        elif critical_count == 0 and score >= 70 and warning_count <= 5:
            return "B"
        elif critical_count <= 2 and score >= 50:
            return "C"
        else:
            return "D"


class OptimizerAgent:
    """Suggest optimizations and auto-fixes"""

    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base

    def optimize(self, strategy: CampaignStrategy, validation: Dict, context: Dict) -> CampaignStrategy:
        """Apply optimizations based on validation results"""

        # Auto-fix critical issues
        for failure in validation.get("critical_failures", []):
            strategy = self._apply_auto_fix(strategy, failure, context)

        # Apply optimization suggestions
        for warning in validation.get("warnings", []):
            suggestion = self._generate_suggestion(warning, context)
            if suggestion:
                logger.info(f"Optimization suggestion: {suggestion}")

        return strategy

    def _apply_auto_fix(self, strategy: CampaignStrategy, failure: Dict, context: Dict) -> CampaignStrategy:
        """Apply automatic fixes for critical issues"""
        check_id = failure.get("id", "")

        if check_id == "BV001":
            # Auto-redistribute budget proportionally
            io_total = sum(io.get("budget", 0) for io in strategy.insertion_orders)
            if io_total > 0:
                ratio = strategy.total_budget / io_total
                for io in strategy.insertion_orders:
                    io["budget"] = int(io["budget"] * ratio)
                logger.info("Auto-fix applied: Budget redistributed proportionally")

        return strategy

    def _generate_suggestion(self, warning: Dict, context: Dict) -> str:
        """Generate optimization suggestion for warnings"""
        check_id = warning.get("id", "")

        suggestions = {
            "BV002": "일일 예산을 목표 CPA의 10배 이상으로 증액하거나, Line Item 수를 줄이세요.",
            "TV001": "오디언스 중복을 줄이기 위해 Negative Targeting을 추가하세요.",
            "TV004": "Frequency Cap을 일 7회, 주 35회 이하로 조정하세요.",
            "BD001": "목표 CPA를 업종 벤치마크 기준으로 재설정하세요."
        }

        return suggestions.get(check_id, "")


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class DV360StrategyGenerator:
    """Main orchestrator for DV360 campaign strategy generation"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.kb = KnowledgeBase(base_path)
        self.context_assembler = ContextAssembler(self.kb)
        self.planner = PlannerAgent(self.kb)
        self.critic = CriticAgent(self.kb)
        self.optimizer = OptimizerAgent(self.kb)

        logger.info("DV360 Strategy Generator initialized")

    def generate(self, raw_input: Dict) -> Dict:
        """Main entry point for strategy generation"""
        logger.info("=" * 50)
        logger.info("Starting strategy generation pipeline")
        logger.info("=" * 50)

        # Step 1: Parse input
        brief = InputParser.parse_brief(raw_input)
        logger.info(f"Input parsed: {brief.industry} / {brief.funnel_stage.value}")

        # Step 2: Assemble context
        context = self.context_assembler.assemble_context(brief)
        logger.info("Context assembled")

        # Step 3: Generate strategy (Planner Agent)
        strategy = self.planner.generate_strategy(context)
        logger.info("Initial strategy generated")

        # Step 4: Validate strategy (Critic Agent)
        validation = self.critic.validate(strategy, context)
        strategy.validation_results = validation
        strategy.grade = validation["grade"]
        logger.info(f"Validation complete: Grade {strategy.grade}")

        # Step 5: Optimize strategy (Optimizer Agent)
        if validation["grade"] in ["C", "D"]:
            strategy = self.optimizer.optimize(strategy, validation, context)
            # Re-validate after optimization
            validation = self.critic.validate(strategy, context)
            strategy.validation_results = validation
            strategy.grade = validation["grade"]
            logger.info(f"Re-validation after optimization: Grade {strategy.grade}")

        # Step 6: Generate output
        output = self._format_output(strategy, context)

        # Save output
        self._save_output(output)

        logger.info("Strategy generation complete")
        return output

    def _format_output(self, strategy: CampaignStrategy, context: Dict) -> Dict:
        """Format strategy for output"""
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator_version": "2026Q1",
                "grade": strategy.grade
            },
            "campaign": {
                "name": strategy.campaign_name,
                "goal": strategy.campaign_goal,
                "budget": strategy.total_budget,
                "duration_days": strategy.duration_days
            },
            "insertion_orders": strategy.insertion_orders,
            "targeting": strategy.targeting_summary,
            "bidding": strategy.bidding_summary,
            "optimization_roadmap": strategy.optimization_roadmap,
            "floodlight": strategy.floodlight_setup,
            "validation": strategy.validation_results,
            "benchmarks": context.get("benchmarks", {}),
            "seasonality": context.get("seasonality", {})
        }

    def _save_output(self, output: Dict):
        """Save output to file"""
        output_dir = self.base_path / "output"
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"strategy_{timestamp}.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        logger.info(f"Output saved to {output_path}")


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(description="DV360 Campaign Strategy Generator")
    parser.add_argument("--input", "-i", type=str, help="Path to input JSON file")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")

    args = parser.parse_args()

    generator = DV360StrategyGenerator()

    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            raw_input = json.load(f)
        result = generator.generate(raw_input)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.interactive:
        print("DV360 Campaign Strategy Generator - Interactive Mode")
        print("=" * 50)

        raw_input = {
            "industry": input("업종 (예: 건강기능식품, 교육, 금융, 패션, 운세): "),
            "product_service": input("제품/서비스명: "),
            "target_demographic": input("타겟 연령대 (예: 20-50세): "),
            "funnel_stage": input("퍼널 단계 (인지/고려/전환): "),
            "campaign_goal": input("캠페인 목표 (Lead Generation/Purchase): "),
            "budget": input("월 예산 (원): "),
            "duration_days": input("캠페인 기간 (일): "),
            "kpi_type": input("KPI 유형 (CPA/ROAS): "),
            "kpi_target": input("KPI 목표값: ")
        }

        result = generator.generate(raw_input)
        print("\n" + "=" * 50)
        print("Generated Strategy:")
        print("=" * 50)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        # Example usage
        example_input = {
            "industry": "서비스_운세상담",
            "product_service": "모두의운세 - 전화 운세 상담 플랫폼",
            "target_demographic": "20-50세 여성",
            "funnel_stage": "전환(Conversion)",
            "campaign_goal": "Lead Generation",
            "budget": 3000000,
            "duration_days": 30,
            "kpi_type": "ROAS",
            "kpi_target": 300,
            "geo_targets": ["대한민국 전역"],
            "first_party_data": {
                "site_visitors": True,
                "signup_abandoners": True
            }
        }

        print("Running with example input...")
        result = generator.generate(example_input)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
