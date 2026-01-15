"""
Test Suite for DV360 Strategy Generator
========================================
"""

import pytest
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dv360_strategy_generator import (
    DV360StrategyGenerator,
    InputParser,
    CampaignBrief,
    FunnelStage,
    CampaignGoal,
    KnowledgeBase,
    ContextAssembler
)


class TestInputParser:
    """Test input parsing functionality"""

    def test_parse_basic_input(self):
        """Test basic input parsing"""
        raw_input = {
            "industry": "운세",
            "product_service": "모두의운세",
            "target_demographic": "20-50세",
            "funnel_stage": "전환",
            "campaign_goal": "Lead Generation",
            "budget": 3000000,
            "duration_days": 30,
            "kpi_type": "ROAS",
            "kpi_target": 300
        }

        brief = InputParser.parse_brief(raw_input)

        assert brief.industry == "서비스_운세상담"
        assert brief.funnel_stage == FunnelStage.CONVERSION
        assert brief.campaign_goal == CampaignGoal.LEAD_GENERATION
        assert brief.budget == 3000000

    def test_industry_normalization(self):
        """Test industry name normalization"""
        test_cases = [
            ("건강", "건강기능식품"),
            ("health", "건강기능식품"),
            ("교육", "교육"),
            ("금융", "금융"),
            ("패션", "이커머스_패션"),
            ("운세", "서비스_운세상담"),
        ]

        for input_industry, expected in test_cases:
            result = InputParser._normalize_industry(input_industry)
            assert result == expected, f"Failed for {input_industry}"

    def test_funnel_stage_parsing(self):
        """Test funnel stage parsing"""
        test_cases = [
            ("인지", FunnelStage.AWARENESS),
            ("awareness", FunnelStage.AWARENESS),
            ("고려", FunnelStage.CONSIDERATION),
            ("consideration", FunnelStage.CONSIDERATION),
            ("전환", FunnelStage.CONVERSION),
            ("conversion", FunnelStage.CONVERSION),
        ]

        for input_stage, expected in test_cases:
            result = InputParser._parse_funnel_stage(input_stage)
            assert result == expected, f"Failed for {input_stage}"


class TestKnowledgeBase:
    """Test knowledge base functionality"""

    @pytest.fixture
    def kb(self):
        """Create knowledge base fixture"""
        return KnowledgeBase(str(Path(__file__).parent))

    def test_load_golden_dataset(self, kb):
        """Test golden dataset loading"""
        assert len(kb.golden_dataset) > 0
        assert kb.golden_dataset[0].get("template_id") is not None

    def test_load_validation_checklist(self, kb):
        """Test validation checklist loading"""
        assert "validation_categories" in kb.validation_checklist
        assert len(kb.validation_checklist["validation_categories"]) > 0

    def test_find_similar_template(self, kb):
        """Test template matching"""
        brief = CampaignBrief(
            industry="서비스_운세상담",
            product_service="테스트",
            target_demographic="20-50세",
            funnel_stage=FunnelStage.CONVERSION,
            campaign_goal=CampaignGoal.LEAD_GENERATION,
            budget=3000000,
            duration_days=30,
            kpi_type="ROAS",
            kpi_target=300
        )

        template = kb.find_similar_template(brief)
        assert template is not None
        assert template.get("template_id") == "SERVICE_FORTUNE_2050_CONVERSION"


class TestContextAssembler:
    """Test context assembly functionality"""

    @pytest.fixture
    def assembler(self):
        """Create context assembler fixture"""
        kb = KnowledgeBase(str(Path(__file__).parent))
        return ContextAssembler(kb)

    def test_assemble_context(self, assembler):
        """Test context assembly"""
        brief = CampaignBrief(
            industry="서비스_운세상담",
            product_service="모두의운세",
            target_demographic="20-50세",
            funnel_stage=FunnelStage.CONVERSION,
            campaign_goal=CampaignGoal.LEAD_GENERATION,
            budget=3000000,
            duration_days=30,
            kpi_type="ROAS",
            kpi_target=300
        )

        context = assembler.assemble_context(brief)

        assert "brief" in context
        assert "similar_template" in context
        assert "benchmarks" in context
        assert "seasonality" in context


class TestDV360StrategyGenerator:
    """Test main generator functionality"""

    @pytest.fixture
    def generator(self):
        """Create generator fixture"""
        return DV360StrategyGenerator(str(Path(__file__).parent))

    def test_generate_fortune_strategy(self, generator):
        """Test strategy generation for fortune service"""
        raw_input = {
            "industry": "서비스_운세상담",
            "product_service": "모두의운세 - 전화 운세 상담 플랫폼",
            "target_demographic": "20-50세 여성",
            "funnel_stage": "전환(Conversion)",
            "campaign_goal": "Lead Generation",
            "budget": 3000000,
            "duration_days": 30,
            "kpi_type": "ROAS",
            "kpi_target": 300,
            "geo_targets": ["대한민국 전역"]
        }

        result = generator.generate(raw_input)

        # Check metadata
        assert "metadata" in result
        assert result["metadata"]["grade"] in ["S", "A", "B", "C", "D"]

        # Check campaign structure
        assert "campaign" in result
        assert result["campaign"]["budget"] == 3000000

        # Check insertion orders
        assert "insertion_orders" in result
        assert len(result["insertion_orders"]) > 0

        # Check targeting
        assert "targeting" in result

        # Check bidding
        assert "bidding" in result

    def test_generate_health_strategy(self, generator):
        """Test strategy generation for health supplement"""
        raw_input = {
            "industry": "건강기능식품",
            "product_service": "관절 건강 보조제",
            "target_demographic": "40-60세",
            "funnel_stage": "전환(Conversion)",
            "campaign_goal": "Lead Generation",
            "budget": 30000000,
            "duration_days": 30,
            "kpi_type": "CPA",
            "kpi_target": 15000
        }

        result = generator.generate(raw_input)

        assert result["metadata"]["grade"] in ["S", "A", "B", "C", "D"]
        assert len(result["insertion_orders"]) > 0

    def test_generate_education_strategy(self, generator):
        """Test strategy generation for education"""
        raw_input = {
            "industry": "교육",
            "product_service": "온라인 영어 교육",
            "target_demographic": "25-40세",
            "funnel_stage": "고려(Consideration)",
            "campaign_goal": "Lead Generation",
            "budget": 50000000,
            "duration_days": 30,
            "kpi_type": "CPA",
            "kpi_target": 30000
        }

        result = generator.generate(raw_input)

        assert result["metadata"]["grade"] in ["S", "A", "B", "C", "D"]
        assert "benchmarks" in result


class TestValidation:
    """Test validation functionality"""

    @pytest.fixture
    def generator(self):
        """Create generator fixture"""
        return DV360StrategyGenerator(str(Path(__file__).parent))

    def test_budget_validation(self, generator):
        """Test budget validation"""
        raw_input = {
            "industry": "운세",
            "product_service": "테스트",
            "target_demographic": "20-50세",
            "funnel_stage": "전환",
            "campaign_goal": "Lead Generation",
            "budget": 3000000,
            "duration_days": 30,
            "kpi_type": "CPA",
            "kpi_target": 10000
        }

        result = generator.generate(raw_input)

        # Check validation results
        assert "validation" in result
        validation = result["validation"]
        assert "passed" in validation
        assert "warnings" in validation
        assert "critical_failures" in validation

    def test_grade_calculation(self, generator):
        """Test grade calculation"""
        raw_input = {
            "industry": "서비스_운세상담",
            "product_service": "모두의운세",
            "target_demographic": "20-50세",
            "funnel_stage": "전환",
            "campaign_goal": "Lead Generation",
            "budget": 3000000,
            "duration_days": 30,
            "kpi_type": "CPA",
            "kpi_target": 10000
        }

        result = generator.generate(raw_input)

        # Grade should be assigned
        assert result["metadata"]["grade"] in ["S", "A", "B", "C", "D"]


def test_end_to_end():
    """End-to-end integration test"""
    generator = DV360StrategyGenerator(str(Path(__file__).parent))

    # Test with 모두의운세 example
    raw_input = {
        "industry": "서비스_운세상담",
        "product_service": "모두의운세 (모운) - 전화 운세 상담 플랫폼",
        "target_demographic": "20-50세 여성",
        "funnel_stage": "전환(Conversion)",
        "campaign_goal": "Lead Generation (가입/상담 연결)",
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

    result = generator.generate(raw_input)

    # Comprehensive checks
    assert result is not None
    assert result["campaign"]["name"].startswith("DV360_")
    assert len(result["insertion_orders"]) >= 2
    assert result["metadata"]["grade"] in ["S", "A", "B"]

    print(f"\n✅ End-to-end test passed!")
    print(f"   Campaign: {result['campaign']['name']}")
    print(f"   Grade: {result['metadata']['grade']}")
    print(f"   IOs: {len(result['insertion_orders'])}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
