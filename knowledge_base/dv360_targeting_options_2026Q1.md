# DV360 Targeting Options Guide (2026 Q1)

## 1. Affinity Audiences (관심분야 오디언스)

**정의**: 장기적 관심사를 기반으로 한 타겟팅
**사용 시기**: 인지(Awareness) 단계, 광범위한 도달 필요 시

### 주요 카테고리

| 카테고리 | 세부 항목 | 예상 CPM (KR) |
|----------|----------|---------------|
| Health & Fitness Buffs | Yoga, Runners, Weight Training | $3-6 |
| Sports & Fitness | Golf, Tennis, Hiking & Camping | $4-7 |
| Lifestyles & Hobbies | Home & Garden, Arts & Crafts | $3-5 |
| Media & Entertainment | Movie Lovers, Gamers | $4-8 |
| Shoppers | Bargain Hunters, Luxury Shoppers | $5-10 |
| Beauty & Wellness | Spa & Beauty Service, Skincare | $5-9 |

**도달 규모**: 대형 (100만+ 사용자)
**전환율**: 낮음 (0.5-1.5%)
**추천 퍼널**: TOFU (인지)

---

## 2. In-Market Audiences (구매 의도 오디언스)

**정의**: 구매 행동 신호를 보이는 사용자
**사용 시기**: 고려(Consideration) 및 전환(Conversion) 단계

### 주요 카테고리

| 카테고리 | 세부 항목 | 예상 CPM (KR) |
|----------|----------|---------------|
| Health & Medical | Vitamins & Supplements, Pain Relief | $8-15 |
| Financial Services | Insurance, Investment Services | $12-25 |
| Education | Continuing Education, Tutoring | $8-18 |
| Real Estate | Residential Properties | $10-20 |
| Travel | Hotels & Accommodations, Flights | $6-12 |
| Apparel & Accessories | Activewear, Luxury Goods | $7-14 |

**도달 규모**: 중형 (10만-50만 사용자)
**전환율**: 높음 (2-5%)
**추천 퍼널**: MOFU/BOFU (고려/전환)

---

## 3. Custom Audiences (맞춤 오디언스)

**정의**: 광고주가 직접 정의한 키워드/URL 기반 타겟팅

### 구축 방법

1. **키워드 기반**
   - 검색어, 관심사 키워드 입력
   - 예: "관절 건강", "등산 용품", "골프 레슨"

2. **URL 기반**
   - 경쟁사 웹사이트
   - 관련 콘텐츠 사이트
   - 리뷰 사이트

3. **앱 기반**
   - 관련 앱 사용자 타겟팅

### 권장 키워드 수
- 최소: 50개
- 권장: 100-200개
- 최대: 500개

**도달 규모**: 조절 가능
**전환율**: 중상 (1.5-4%)
**추천 퍼널**: 전체

---

## 4. Similar Audiences (유사 오디언스)

**정의**: 기존 전환자와 유사한 행동 패턴을 가진 사용자

### 소스 데이터 요구사항
- 최소 1,000명 이상의 시드 오디언스
- 최근 30일 이내 활성 데이터
- 전환자 또는 고가치 사용자 권장

### 유사도 레벨
| 레벨 | 유사도 | 도달 규모 | 전환율 |
|------|--------|----------|--------|
| Narrow | 높음 | 소형 | 높음 |
| Balanced | 중간 | 중형 | 중간 |
| Broad | 낮음 | 대형 | 낮음 |

**추천 퍼널**: MOFU (고려)

---

## 5. 1st Party Audiences (자사 데이터)

### 유형

1. **웹사이트 방문자**
   - 전체 방문자
   - 특정 페이지 방문자 (장바구니, 결제 페이지)
   - 전환 미완료자

2. **CRM 데이터**
   - 기존 고객 (업셀/크로스셀)
   - 휴면 고객 (재활성화)
   - VIP 고객 (Lookalike 소스)

3. **앱 사용자**
   - 앱 설치자
   - 특정 액션 완료자
   - 비활성 사용자

### Floodlight 태그 설정 필수
- Global Site Tag (gtag.js)
- Event Snippet (전환 이벤트별)

---

## 6. Demographics (데모그래픽)

### 설정 옵션

| 항목 | 옵션 |
|------|------|
| 성별 | 남성, 여성, 알 수 없음 |
| 연령 | 18-24, 25-34, 35-44, 45-54, 55-64, 65+ |
| 가구 소득 | 상위 10%, 11-20%, 21-30%, ... |
| 부모 여부 | 부모, 부모 아님 |

### 주의사항
- "알 수 없음" 제외 시 도달 규모 30-40% 감소
- 가구 소득 타겟팅은 미국/영국 등 일부 국가만 지원

---

## 7. Geography (지역 타겟팅)

### 설정 레벨
1. 국가
2. 시/도 (광역시, 도)
3. 도시/구/군
4. 반경 타겟팅 (위치 기반)

### 한국 주요 지역 코드
| 지역 | 타겟팅 ID |
|------|----------|
| 서울특별시 | 21187 |
| 경기도 | 21188 |
| 부산광역시 | 21189 |
| 인천광역시 | 21190 |

---

## 8. Device Targeting (디바이스 타겟팅)

### 옵션

| 디바이스 | 권장 상황 |
|----------|----------|
| Mobile | 전화 상담, 앱 설치, 즉시 전환 |
| Desktop | 고관여 제품, 긴 폼 작성 |
| Tablet | 콘텐츠 소비, 미디어 시청 |
| Connected TV | 브랜드 인지도, 영상 광고 |

### 운영체제별 세분화
- Android (Mobile/Tablet)
- iOS (iPhone/iPad)
- Windows
- macOS

---

## 9. Time of Day (시간대 타겟팅)

### 권장 설정 (한국 기준)

| 시간대 | 특성 | 입찰 조정 |
|--------|------|----------|
| 07:00-09:00 | 출근 시간 (모바일) | +10% |
| 12:00-14:00 | 점심 시간 (검색/구매) | +15% |
| 18:00-22:00 | 황금 시간대 (최대 활동) | +20% |
| 22:00-24:00 | 야간 (충동 구매) | +10% |
| 00:00-06:00 | 심야 (낮은 전환) | -30% |

---

## 10. 타겟팅 조합 전략

### 인지 캠페인 (Awareness)
```
Affinity Audiences (넓은 관심사)
+ Demographics (핵심 연령/성별)
+ Geography (서비스 가능 지역)
```

### 고려 캠페인 (Consideration)
```
In-Market Audiences (구매 의도)
+ Custom Audiences (경쟁사 키워드)
+ Device (주력 디바이스)
```

### 전환 캠페인 (Conversion)
```
1st Party (사이트 방문자)
+ Similar Audiences (전환자 유사)
+ Time of Day (고전환 시간대)
```
