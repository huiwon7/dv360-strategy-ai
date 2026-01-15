# DV360 Campaign Strategy AI Generator

## Overview
Google DV360 프로그래매틱 광고 캠페인 전략을 자동으로 생성하는 AI 시스템입니다.

## Architecture (3-Layer)

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: INPUT INTERFACE                                   │
│  - CampaignBrief 구조화                                      │
│  - InputParser (업종/퍼널 정규화)                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: CONTEXT ASSEMBLY ENGINE                           │
│  - KnowledgeBase (3-Tier: Static/Golden/Realtime)           │
│  - ContextAssembler (Gather → Glean, 8K token budget)       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: MULTI-AGENT REASONING                             │
│  - PlannerAgent: 캠페인 전략 생성                             │
│  - CriticAgent: 15-Point 검증 체크리스트                      │
│  - OptimizerAgent: 자동 수정 및 최적화 제안                   │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
dv360-strategy-ai/
├── dv360_strategy_generator.py   # Main orchestrator
├── requirements.txt              # Dependencies
├── test_generator.py             # Test suite
├── knowledge_base/               # Static knowledge (Tier 1)
│   ├── dv360_targeting_options_2026Q1.md
│   └── dv360_bidding_strategies_2026Q1.md
├── templates/                    # Golden Dataset (Tier 2)
│   ├── golden_dataset.json       # 5 industry templates
│   └── validation_checklist.json # 15-point checklist
├── output/                       # Generated strategies
└── logs/                         # Execution logs
```

## Usage

### Interactive Mode
```bash
python dv360_strategy_generator.py --interactive
```

### With Input File
```bash
python dv360_strategy_generator.py --input campaign_brief.json
```

### Programmatic Usage
```python
from dv360_strategy_generator import DV360StrategyGenerator

generator = DV360StrategyGenerator()

result = generator.generate({
    "industry": "서비스_운세상담",
    "product_service": "모두의운세",
    "target_demographic": "20-50세 여성",
    "funnel_stage": "전환(Conversion)",
    "campaign_goal": "Lead Generation",
    "budget": 3000000,
    "duration_days": 30,
    "kpi_type": "ROAS",
    "kpi_target": 300
})

print(result["metadata"]["grade"])  # S, A, B, C, D
```

## Supported Industries

| Industry | Template ID |
|----------|-------------|
| 건강기능식품 | HEALTH_SUPPLEMENT_4060_CONVERSION |
| 교육 | EDUCATION_2540_CONSIDERATION |
| 금융 | FINANCE_3050_CONVERSION |
| 이커머스_패션 | ECOMMERCE_FASHION_2035_CONVERSION |
| 서비스_운세상담 | SERVICE_FORTUNE_2050_CONVERSION |

## Grading System

| Grade | Score | Description |
|-------|-------|-------------|
| S | 95-100% | 완벽한 전략, 즉시 실행 가능 |
| A | 85-94% | 우수한 전략, 소폭 조정 후 실행 |
| B | 70-84% | 양호한 전략, 일부 개선 필요 |
| C | 50-69% | 개선 필요, 재검토 권장 |
| D | 0-49% | 재작성 필요 |

## Validation Checklist (15-Point)

### Budget Validation
- BV001: 전체 IO 예산 합계 확인
- BV002: 일일 예산 vs 목표 CPA 비율
- BV003: Pacing 설정 적절성

### Targeting Validation
- TV001: 오디언스 중복율 (≤30%)
- TV002: 지역 타겟팅 일치
- TV003: 디바이스 비율 벤치마크
- TV004: Frequency Cap 적절성

### Bidding Validation
- BD001: 목표 CPA 벤치마크 대비 적절성
- BD002: ROAS 목표 달성 가능성
- BD003: 입찰 전략별 데이터 요구사항

### Structure Validation
- SV001: 캠페인 계층 구조
- SV002: 네이밍 규칙 준수
- SV003: Line Item 수 적정성

### Tracking Validation
- TK001: Floodlight 설정 완료
- TK002: 전환 창 설정 적절성

## Version
2026Q1
