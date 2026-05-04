# Document Retrieval Benchmark

작성일: 2026-05-05

## 목적

구조화된 문서 구성과 평탄화된 문서 구성이 agent의 문서 검색 효율에 어떤 차이를 만드는지 비교했다.

비교 대상:

- `test/docs`: 디렉터리 구조와 YAML frontmatter가 있는 구조화 문서 세트
- `test2`: 모든 Markdown 파일이 한 폴더에 있는 평탄화 문서 세트

## 벤치마크 도구

벤치마크 스크립트:

[tools/doc_search_benchmark.py](/Users/kris/code/ai/proj/totalvulscaner/tools/doc_search_benchmark.py)

문서에는 코드 내용을 포함하지 않는다.

## 측정 방식

측정 항목:

- 검색 속도
- context 소모량
- 추정 token 소모량
- 접근 성공 여부
- 정확한 파일 도달 여부
- 정확한 섹션 도달 여부

테스트 구성:

- 비교용 generated 문서: 각 구조당 66개
- 검색 시나리오: 18개
- 반복 횟수: 각 구조당 1,800회

구조화 문서 검색 방식:

- `PROJECT-CONTEXT.md`를 시작점으로 사용
- YAML frontmatter의 `type`, `status`, `topics`, `summary`를 후보 선별에 사용
- 상위 후보 문서만 읽음

평탄화 문서 검색 방식:

- 단일 폴더의 Markdown 파일을 대상으로 검색
- 파일명과 문서 앞부분을 읽어 후보를 선별
- 디렉터리 구조와 frontmatter 힌트는 사용하지 않음

## 결과

| metric | structured `test` | flat `test2` |
| --- | ---: | ---: |
| runs | 1800 | 1800 |
| access success | 100% | 100% |
| exact file hit | 100% | 100% |
| exact section hit | 100% | 100% |
| avg context chars | 20,223 | 27,032.56 |
| estimated avg tokens | 5,055.75 | 6,758.14 |
| avg elapsed ms | 1.3950 | 1.0031 |

## 해석

두 구조 모두 목표 파일과 목표 섹션 도달률은 100%였다.

다만 구조화된 `test/docs`는 평탄화된 `test2`보다 평균 context 사용량이 낮았다.

```text
structured context chars: 20,223
flat context chars:       27,032.56
reduction:                about 25.2%
```

추정 token 기준으로도 구조화된 문서 세트가 약 25.2% 적게 사용했다.

로컬 파일 검색 시간은 `test2`가 더 낮게 나왔다. 하지만 실제 AI agent 비용 관점에서는 파일 IO 시간보다 LLM에 들어가는 context/token 양이 더 중요하다. 따라서 이 벤치마크에서는 구조화 문서의 이점이 검색 속도보다 **문맥 비용 절감**으로 나타났다.

## 결론

문서 수가 늘어날수록 디렉터리 구조, frontmatter metadata, `PROJECT-CONTEXT.md` 기반 라우팅은 context 소모를 줄이는 데 유리하다.

이번 테스트에서는 정확도는 동일했고, 구조화 문서 세트가 같은 검색 성공률을 유지하면서 약 25% 적은 문맥으로 목표 문서와 섹션에 도달했다.

즉 구조화 문서 체계의 실질적 장점은 다음이다.

- agent가 전체 문서를 덜 읽어도 됨
- token/context 소모가 줄어듦
- 문서 수가 증가해도 검색 범위를 좁히기 쉬움
- 세션 변경 후에도 문서 라우팅이 안정적임

## 한계

이 벤치마크는 deterministic 검색 시뮬레이션이다.

실제 LLM agent는 다음 요인에 따라 결과가 달라질 수 있다.

- 문서 내용의 모호성
- 파일명 품질
- frontmatter 품질
- 검색 query 품질
- agent의 문서 선택 전략
- 문서 수 증가에 따른 후보 충돌

따라서 이 결과는 “구조화 문서가 항상 더 빠르다”는 결론이 아니라, **구조화 문서가 동일 정확도에서 context 비용을 줄일 가능성이 높다**는 근거로 해석해야 한다.
