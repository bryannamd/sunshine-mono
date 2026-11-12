# 재사용 가능한 코딩 리거처 폰트 조사

2026-11-12 확인. 단순 설치가 아니라 Sunshine Mono에 수정·병합·재배포할 수 있는 후보를 비교했다. 전 세계 폰트를 전수 평가한 순위가 아니라 공식 기능 자료와 라이선스를 바탕으로 한 추천이다.

| 후보 | 강점 | Sunshine Mono에서의 판단 | 라이선스 |
|---|---|---|---|
| Fira Code | 풍부한 연산자·확장 가능한 화살표 조합, 스타일 선택, 문장부호 간격 조정 | 리거처 품질을 비교할 첫 기준. 필요한 기능을 선별할 참고·재사용 후보 | OFL 1.1 |
| Iosevka | 언어별 리거처 세트와 조합별 커스텀 빌드 | 현재 영문 기반이므로 실제 확장에 가장 자연스러운 우선안 | OFL 1.1 |
| JetBrains Mono | 다수의 코드 연산자, 불필요한 세부를 줄인 글자 형태 | 절제된 미감과 가독성을 비교할 대안 | OFL 1.1 |
| Cascadia Code | 프로그래밍 리거처, 터미널·편집기용 폰트 | Windows 환경 비교 후보. Cascadia Mono에는 리거처가 없음 | OFL 1.1, Cascadia Code 예약명 명시 |

## 추천

리거처 자체를 우선 비교한다면 Fira Code, 현재 Sunshine Mono를 개선한다면 Iosevka를 우선한다. 기존 검증의 ‘15종’은 검사한 연산자 표본 수이며 Iosevka가 지원하는 전체 리거처 개수가 아니다. 폰트 전체 교체 전, 필요한 연산자 조합과 Iosevka의 기본/선택 기능을 먼저 대조하는 편이 합리적이다.

다른 폰트의 리거처는 그림 한 개를 복사하는 것만으로 끝나지 않는다. 참조 글리프와 문맥 치환 규칙, 굵기, 550-unit 칸 폭, 주변 연산자와의 조합을 함께 맞춰야 한다. 이 판단은 현재 프로젝트의 폰트 구조를 바탕으로 한 구현상 판단이다. 이번 조사에서는 외부 리거처를 도입하지 않았다.

## 활용 조건

OFL은 사용·수정·병합·임베딩·재배포를 허용한다. 배포하는 수정 폰트는 OFL을 유지하고 원저작권 및 라이선스를 동봉해야 한다. 예약 폰트 이름이 있으면 허가 없이 수정판의 이름으로 사용할 수 없다. 폰트 파일이나 그 구성요소 자체만 단독 판매하는 것은 허용되지 않는다. 소프트웨어와 묶어 배포·판매하는 것은 조건을 지키면 가능하며, 이 폰트로 만든 문서·이미지에 OFL을 적용할 의무는 없다.

## 공식 근거

- [Fira Code 기능·리거처](https://github.com/tonsky/FiraCode), [라이선스](https://github.com/tonsky/FiraCode/blob/master/LICENSE)
- [Iosevka 기능·언어별 리거처·커스텀 빌드](https://github.com/be5invis/Iosevka), [라이선스](https://github.com/be5invis/Iosevka/blob/main/LICENSE.md)
- [JetBrains Mono 설계와 리거처 목록](https://www.jetbrains.com/lp/mono/), [현행 OFL](https://github.com/JetBrains/JetBrainsMono/blob/master/OFL.txt)
- [Microsoft의 Cascadia 설명](https://learn.microsoft.com/en-us/windows/terminal/cascadia-code), [라이선스·예약명](https://github.com/microsoft/cascadia-code/blob/main/LICENSE)
- [SIL OFL 1.1 공식 전문](https://openfontlicense.org/open-font-license-official-text/)

GitHub 저장소는 agent-reach 스킬의 GitHub CLI 경로와 공식 웹 자료로 확인했다.
