# 컨텍스트 효율적인 프로젝트 문서화 템플릿

AI 에이전트가 장기 프로젝트에서 문서를 더 적게 읽고도 정확한 맥락에 도달하도록 돕는 문서 템플릿 세트입니다.

이 템플릿의 전제는 단순합니다.

> AI 에이전트에게 필요한 것은 많은 문서가 아니라, 찾기 쉽고 읽기 저렴하며 프로젝트 연속성을 보존하는 문서입니다.

## 초록

AI 기반 장기 프로젝트에서는 세션이 바뀌면서 맥락이 흐려지고, 같은 문서를 반복 탐색하며, 결정 사항이나 작업 이력이 누락되는 문제가 생깁니다. 이 템플릿 세트는 다음 요소를 통해 그 문제를 줄이는 것을 목표로 합니다.

- 프로젝트 컨텍스트 라우터
- 메타데이터 기반 문서 탐색
- 예측 가능한 파일명 규칙
- 작업/시나리오/모듈 단위 진행 기록
- 의사결정 및 아카이브 기록
- 소스 파일이 손실되어도 프로젝트 의도를 복구할 수 있는 기록 방식

또한 구조화된 문서 구성과 평탄화된 문서 구성을 비교하는 작은 deterministic 벤치마크를 수행했습니다. 실험 결과, 구조화된 문서 구성은 동일한 목표 파일/섹션 도달률을 유지하면서 약 **25% 적은 추정 컨텍스트 토큰**을 사용했습니다.

## 목적

이 템플릿 세트는 AI 코딩 에이전트를 여러 세션에 걸쳐 사용하는 내부 프로젝트 문서화를 위한 것입니다.

목표는 다음과 같습니다.

- 필요한 문서를 더 빠르게 찾기
- 관련 없는 과거 기록을 덜 읽기
- 결정 사항과 작업 상태를 보존하기
- 중단된 작업을 다음 세션에서 이어가기
- 중요한 맥락이 조용히 삭제되는 것을 방지하기
- 소스 파일이 사라져도 프로젝트 방향과 구현 의도를 복구하기

이 템플릿 세트는 명령 실행 정책이 아니라 문서 구조와 기록 관리에 초점을 둡니다.

## 템플릿 세트 구성

```text
DocsTempletv2/
  documentation-guide.md
  templates/
    PROJECT-CONTEXT.template.md
    meeting-log.template.md
    product.template.md
    architecture.template.md
    spec.template.md
    ADR.template.md
    task.template.md
    scenario.template.md
    module-work.template.md
    archive.template.md
```

## 권장 프로젝트 문서 구조

프로젝트에 적용할 때 권장되는 구조는 다음과 같습니다.

```text
docs/
  PROJECT-CONTEXT.md

  meetings/
    <year>/
      YYYY-MM-DD_NNN_short-topic.md

  product/
    overview.md
    goals-and-non-goals.md
    user-workflows.md

  architecture/
    overview.md
    module-map.md
    data-flow.md
    runtime-boundaries.md

  specs/
    <module-name>.md
    <module-name>/
      overview.md
      <specific-capability>.md

  decisions/
    ADR-NNNN_short-decision-title.md

  tasks/
    backlog.md
    active.md
    completed.md
    scenarios/
      scenario-NNN_short-topic.md
    modules/
      <module-name>-<work-topic>.md

  archive/
    <year>/
      YYYY-MM_short-topic.md
```

## 핵심 아이디어

### 1. `PROJECT-CONTEXT.md`는 라우터다

`PROJECT-CONTEXT.md`는 모든 세부 정보를 담는 문서가 아닙니다. 프로젝트의 현재 상태와 다음에 읽어야 할 문서를 알려주는 진입점입니다.

미래의 agent 세션은 이 파일을 통해 다음을 파악할 수 있어야 합니다.

- 프로젝트가 무엇인지
- 현재 무엇이 진행 중인지
- 어떤 문서가 현재 작업과 관련 있는지
- 활성 작업과 주요 결정이 어디에 있는지
- 어떤 문서가 아카이브되었거나 대체되었는지

### 2. 메타데이터 우선 탐색

각 durable Markdown 문서는 YAML frontmatter를 가집니다.

```text
id
type
status
topics
summary
last_updated
```

선택 필드는 다음과 같습니다.

```text
related
supersedes
superseded_by
source_meeting
owner
```

이 메타데이터를 통해 agent는 전체 문서를 읽기 전에 후보 문서를 좁힐 수 있습니다.

### 3. 예측 가능한 파일명

파일명은 English kebab-case와 예측 가능한 패턴을 사용합니다.

예시:

```text
meetings/2026/2026-05-05_001_project-start.md
decisions/ADR-0001_use-agent-execution-policy.md
specs/agent-runtime/tool-execution-policy.md
tasks/scenarios/scenario-001_initial-project-setup.md
tasks/modules/agent-runtime-context-recovery.md
archive/2026/2026-05_completed-planning-history.md
```

파일을 열기 전에 문서의 목적을 어느 정도 알 수 있게 하는 것이 목표입니다.

### 4. 작업 연속성

작업 문서는 다음 정보를 보존합니다.

- 목표
- 범위
- 관련 문서
- 관련 파일
- 완료 조건
- 구현 메모
- 검증 계획과 결과
- 열린 리스크
- 인수인계 메모
- 변경 이력

이를 통해 다음 세션의 agent가 전체 대화를 다시 읽지 않고도 작업을 이어갈 수 있습니다.

### 5. 복구 가능한 기록

중요한 기능, 모듈, 결정은 소스 파일이 사라져도 프로젝트 의도를 복구할 수 있을 정도로 기록되어야 합니다.

중요 작업에는 다음을 남깁니다.

- 목표와 사용자 관점의 동작
- 모듈 경계
- 핵심 인터페이스
- 데이터 구조
- 런타임 흐름
- 중요한 알고리즘이나 규칙
- 설정과 환경 가정
- 검증 명령과 기대 결과
- 알려진 리스크와 한계

### 6. 조용한 이력 삭제 방지

agent는 문서를 “정리”하면서 유용한 맥락을 지워버릴 수 있습니다.

이 템플릿은 다음을 요구합니다.

- 의미 있는 이력은 보존
- 완료되었거나 오래된 내용은 삭제하지 않고 아카이브
- 내용이 이동되면 원문에 포인터 남김
- 대체된 문서는 조용히 덮어쓰지 않고 superseded 상태로 표시

## 벤치마크

구조화된 문서 구성과 평탄화된 문서 구성을 비교하는 deterministic 문서 검색 벤치마크를 수행했습니다.

이 벤치마크의 실험 변수는 문서 구조, 디렉터리 배치, YAML frontmatter 유무, 그리고 문서 라우팅 가능성입니다.

비교 대상:

- `test/docs`: 디렉터리 구조와 YAML frontmatter가 있는 구조화 문서 세트
- `test2`: 모든 Markdown 파일이 한 폴더에 있고 frontmatter가 없는 평탄화 문서 세트

벤치마크 스크립트:

[tools/doc_search_benchmark.py](/tools/doc_search_benchmark.py)

상세 벤치마크 문서:

[docs/document-retrieval-benchmark.md](/docs/document-retrieval-benchmark.md)

## 벤치마크 구성

벤치마크는 두 구조에 대해 비교 가능한 synthetic 프로젝트 문서를 생성했습니다.

구성:

- generated 문서: 각 구조당 66개
- 검색 시나리오: 18개
- 반복 실행: 각 구조당 1,800회
- 목표: 정확한 파일과 섹션 찾기
- 측정 항목:
  - 접근 성공률
  - 정확한 파일 도달률
  - 정확한 섹션 도달률
  - context 문자 수
  - 추정 context token 수
  - 실행 시간

## 벤치마크 결과

| Metric | Structured `test/docs` | Flat `test2` |
| --- | ---: | ---: |
| runs | 1800 | 1800 |
| access success | 100% | 100% |
| exact file hit | 100% | 100% |
| exact section hit | 100% | 100% |
| average context chars | 20,223 | 27,032.56 |
| estimated average tokens | 5,055.75 | 6,758.14 |
| average elapsed ms | 1.3950 | 1.0031 |

## 결과 해석

두 구조 모두 모든 시나리오에서 정확한 파일과 섹션에 도달했습니다.

다만 구조화된 구성은 더 적은 context를 사용했습니다.

```text
structured context chars: 20,223
flat context chars:       27,032.56
reduction:                about 25.2%
```

추정 토큰 기준에서도 같은 감소 경향을 보였습니다.

평탄화된 구조는 로컬 파일 IO 시간 기준으로는 약간 더 빨랐습니다. 하지만 AI agent 워크플로우에서는 로컬 파일 탐색 시간보다 모델 context에 들어가는 양이 더 중요한 경우가 많습니다.

이 실험에서 구조화 문서는 정확도를 높인 것이 아니라, **동일한 정확도에 더 적은 context로 도달**했습니다.

따라서 이 결과는 구조화된 문서 배치와 frontmatter 기반 탐색이 만든 절감 효과로 해석해야 합니다.

## 실험의 한계

이 벤치마크는 완전한 LLM agent 평가가 아닙니다.

한계:

- deterministic 검색 시뮬레이션
- synthetic 문서
- 통제된 검색 시나리오
- 실제 모델 추론 변동성 없음
- 현실적인 장기 프로젝트의 지저분한 이력 없음
- 인간 품질 평가 없음
- 다중 세션 drift 측정 없음

따라서 이 결과는 “구조화 문서가 항상 더 빠르다”는 뜻이 아닙니다.

더 좁은 결론은 다음입니다.

> 이 통제된 검색 테스트에서, 메타데이터와 라우팅이 있는 구조화 문서는 동일한 목표에 도달하면서 약 25% 적은 추정 context를 사용했다.

## 권장 사용처

이 템플릿 세트는 다음 프로젝트에 적합합니다.

- 장기 AI-assisted 개발
- 반복적인 세션 인수인계
- 복구 가능한 프로젝트 기록
- 구조화된 의사결정 기록
- 중단된 작업의 연속성
- 문서 탐색 시 context 소모 절감

## 현재 상태

이 문서 세트는 작은 벤치마크를 포함한 실험적 템플릿입니다. 일반적인 증명은 아닙니다. 다음 단계는 실제 프로젝트와 실제 AI agent 세션에서 검증하는 것입니다.
