# 한글 코딩 폰트 후보와 제작 계획

조사일: 2026-11-12. 공식 저장소 README와 라이선스를 확인했다. 미감 평가는 제작 가설이며, 실제 비교 후 확정한다. 바이너리 전수 검증은 제작 단계에 수행한다.

## 방향

목표는 작은 크기에서도 한글과 영문의 획 굵기, 시각적 크기, 기준선, 여백이 자연스럽게 이어지는 코딩 폰트다. 기존 글리프를 조합한 OFL 파생 폰트로 시작하고, 비교에서 드러나는 문제에 한해 윤곽을 수정한다.

D2Coding만 한글을 지원하는 것은 아니다. 아래 기존 폰트를 먼저 비교하면 새로 만들어야 할 부분을 좁힐 수 있다. D2Coding 공식 설명상 한글 바탕은 나눔바른고딕이다.

## 이미 한글을 포함하는 비교 대상

| 폰트 / 공식 출처 | 구성과 용도 | 프로젝트에서의 역할 |
|---|---|---|
| [Jetendard](https://github.com/kuskhan/jetendard) | JetBrains Mono Nerd Font Mono + Pretendard. README상 한글을 영문 두 칸에 맞춤 | 현대적 영문 + 본고딕 계열 한글의 선행 사례 |
| [Sarasa Mono K / Term K](https://github.com/be5invis/Sarasa-Gothic) | Iosevka 계열 + Source Han Sans. K는 한국어 자형. Mono/Term/Fixed의 기호 폭·리거처 정책이 다름 | 좁은 영문과 CJK 조합의 기준. 첫 비교는 Mono K |
| [Monoplex KR](https://github.com/y-kim/monoplex) | IBM Plex Mono + IBM Plex Sans KR. CJK 판도 별도 존재 | 같은 디자인 계열의 한영 조화 기준 |
| [Noto Sans Mono CJK KR](https://github.com/notofonts/noto-cjk/tree/main/Sans/Mono) | 한국어용 Mono Regular/Bold 파일 제공 | 범용 CJK 비교군. 실제 셀 폭은 바이너리로 검증 |
| [나눔고딕코딩](https://github.com/google/fonts/tree/main/ofl/nanumgothiccoding) | 한글 지원 고정폭 폰트 | 기존 네이버 계열 대조군 |
| [D2Coding](https://github.com/naver/d2-coding-font) | 한글·영문 코딩 폰트, OFL | 현재 불만을 구체화할 기준 |

모두 OFL 계열이다. Jetendard의 Nerd Font 아이콘까지 재사용하면 포함된 각 원천의 고지도 별도 확인한다.

## 한글 원천 후보

아래 폰트는 그대로 전체 글꼴을 코딩용 고정폭 폰트로 간주하지 않는다. 한글을 가져와 셀과 영문에 맞추는 작업이 필요하다.

| 후보 / 공식 출처 | 장점 또는 비교 가설 | 제약 |
|---|---|---|
| [IBM Plex Sans KR](https://github.com/IBM/plex) | Plex Mono와 같은 패밀리. 한영 통일감 우선 후보 | Monoplex와의 차별점 필요 |
| [Pretendard](https://github.com/orioncactus/pretendard) | 익숙하고 정돈된 UI 인상 | 본고딕 기반. Jetendard와 단순 조합이 중복됨 |
| [SUIT](https://github.com/sun-typeface/SUIT) | 간결한 UI 인상 비교 | 본고딕 기반. 선택 파일의 현대 한글 전체 수록 여부를 먼저 측정 |
| [Wanted Sans](https://github.com/wanteddev/wanted-sans) | 기하학적 인상 비교 | 본고딕 기반. 라틴을 교체하면 원래 패밀리의 인상이 그대로 유지되지는 않음 |
| [Source Han Sans KR](https://github.com/adobe-fonts/source-han-sans) / [Noto Sans CJK KR](https://github.com/notofonts/noto-cjk) | 소스와 광범위한 CJK 자산 | 서로 독립적인 미감 후보로 중복 계산하지 않음 |
| [고운돋움](https://github.com/yangheeryu/Gowun-Dodum) | 손의 움직임이 남은 휴머니스트 디자인. 본고딕과 다른 방향 | 공식 설명상 Regular만 제공. 작은 크기 선명도와 Bold 제작 부담 확인 |
| [고운바탕](https://github.com/yangheeryu/Gowun-Batang) | 섬세하고 따뜻한 대안. Regular/Bold, 현대 한글 11,172자 명시 | 명조 계열 실험안. 작은 크기 획과 코드 기호의 조화 확인 |

라이선스는 모두 SIL OFL 1.1. Pretendard·SUIT·Wanted Sans의 한글 바탕이 모두 본고딕이라는 점이 중요하다. 이름만 바꿔 비교하면 디자인 다양성을 과대평가할 수 있다.

## 영문 코딩 원천 후보

| 후보 / 공식 출처 | 우선 검토 이유 |
|---|---|
| [IBM Plex Mono](https://github.com/IBM/plex) | Plex Sans KR와 패밀리 통일 |
| [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) | 높은 소문자, 문자 구분, 리거처와 NL 선택 |
| [Iosevka](https://github.com/be5invis/Iosevka) | 폭·자형·리거처를 빌드 설정으로 조절. 한글 중심 설계에 유리 |
| [Geist Mono](https://github.com/vercel/geist-font) | 간결한 현대적 인상의 비교군 |
| [Fira Code](https://github.com/tonsky/FiraCode) | 풍부한 프로그래밍 리거처 |
| [Cascadia Code / Mono](https://github.com/microsoft/cascadia-code) | 터미널 지향, 리거처 유무 선택 |
| [Source Code Pro](https://github.com/adobe-fonts/source-code-pro) | 담백한 코드용 비교군 |

폰트 라이선스는 모두 OFL 1.1로 확인했다. 빌드 도구·소스 코드의 라이선스는 폰트와 별도로 확인한다. 영문 원천만으로 한글 지원이 충족된다고 가정하지 않는다.

## 좁힌 제작 후보

1. **통일감 우선:** IBM Plex Mono + IBM Plex Sans KR. Monoplex KR 실사용 후 불만이 남는 지점만 조정한다.
2. **현대적 가독성 우선:** JetBrains Mono + Pretendard. Jetendard를 기준으로 크기·굵기·여백을 비교한다. 이미 만족스럽다면 신규 제작보다 기존 폰트 사용이 합리적이다.
3. **맞춤 설계 우선:** Iosevka custom + 선택한 한글. Sarasa K와 비교하면서 영문 폭·자형부터 한글에 맞춘다.
4. **우아함 실험:** Iosevka 또는 Plex Mono + 고운돋움. 먼저 Regular 소규모 시안으로 판정한다. 고운바탕은 별도 명조 실험안이다.

## 제작 단계와 완료 기준

| 단계 | 작업 | 완료 기준 |
|---|---|---|
| 1. 기존 폰트 비교 | Jetendard·Sarasa Mono K·Monoplex KR 설치. 동일 코드, 크기, 행간, 테마로 평가 | 선호하는 한글/영문과 불만 각각 기록 |
| 2. 입력 고정 | 후보 2~3개로 축소. 원본 버전·SHA-256·라이선스·예약 이름 기록. cmap/메트릭 조사 | 재현 가능한 입력 목록, 현대 한글 수록 수 확인 |
| 3. Regular 시안 | 동일 UPM으로 정규화. 영문 1셀·한글 완성형 2셀. 윤곽 비율을 보존하면서 크기·기준선·여백 조정 | 폴백 없이 한영 혼합 문장과 표 정렬, 시각 비교 |
| 4. 선택안 정교화 | 획 무게와 복잡한 받침 검토. 기호·자모·조합 문자·리거처 정책 조정 | 읽기 선호도와 자동 검사 모두 충족 |
| 5. 스타일 확장 | Regular/Bold 우선. Italic은 라틴 기울임·한글 정자 정책부터 시험 | 스타일 연결·굵기 전환·잘림 문제 없음 |
| 6. 배포 | TTF 우선, 필요하면 WOFF2. 이름·고지·빌드 명령·검증 결과 제공 | 새 환경에서 같은 입력으로 빌드 및 설치 가능 |

처음부터 가변 폰트, Nerd Font 패치, 모든 CJK, 옛한글까지 확대하지 않는다. 현대 한글 11,172자, 필요한 자모, ASCII, 코드 기호부터 완성한다. Unicode 폭 정책은 문자별로 정하며 결합 문자·zero-width 문자까지 두 칸으로 바꾸지 않는다.

## 검증 항목

- `fontTools`: cmap, 현대 한글 11,172자, hmtx, 이름, 스타일, UPM, ascent/descent 검사. ASCII printable은 한 셀, 한글 완성형은 두 셀인지 확인한다.
- HarfBuzz 계열 shaping 검사: NFC/NFD 한글, 자모, 결합 문자, 연산자 리거처. 폭 합계와 누락 글리프 확인.
- 폰트 sanitizer와 적절한 FontBakery 검사. 병합 후 GSUB/GPOS, 힌팅, 합성 글리프 참조를 확인한다.
- 실제 사용하는 편집기와 터미널에서 먼저 검증. 이후 macOS/Windows/Linux 지원 범위를 확인한 만큼만 표기한다.
- 12/14/16/18px, 밝은/어두운 배경, Regular/Bold. 같은 CSS 크기 비교와 시각 크기를 맞춘 비교를 별도로 한다.
- `0O o`, `1Il|`, `rn m`, `!= !== => ->`, `가각값꿇뷁힣`, 긴 한글 주석, 영문 식별자 옆 한글 문자열, 박스 선 정렬을 확인한다.
- 점수 제안: 한영 조화 35%, 작은 크기 가독성 30%, 문자 구분 20%, 취향 15%. 라이선스·커버리지·정렬은 점수와 별개로 필수 통과한다.

## 라이선스 적용

OFL 폰트는 조건에 따라 수정·병합·재배포할 수 있다. 파생 폰트도 OFL로 배포하며 원저작권과 라이선스를 포함한다. 예약 이름이 있으면 별도 허가 없이 파생본의 기본 폰트 이름으로 사용하지 않는다. 폰트 단독 판매는 허용되지 않는다. 폰트를 사용하는 앱 전체가 OFL이어야 한다는 뜻은 아니다. [OFL 공식 FAQ](https://openfontlicense.org/ofl-faq/)

확인된 예약 이름 예: Pretendard, Source, Inter, M PLUS 1, SUIT, Plex, Monoplex, Cascadia Code, D2Coding, Jetendard. 실제 채택 파일의 전체 고지를 다시 확인하고 새로운 패밀리 이름을 사용한다.

현재 상태: 기존 세 폰트 설치 후, JetBrains Mono·Iosevka Custom 550·Cascadia Mono·Fira Code 기반 Regular 네 시안을 제작했다. 최신 산출물과 검증 상태는 [시안 제작 기록](prototype-build.md)을 따른다. 최종 디자인 선택과 공개 릴리스는 아직 수행하지 않았다.
