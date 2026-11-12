# 본고딕 한글 비율과 중간 폭 영문 후보

조사일: 2026-11-12. 사용자 방향: Source Han Sans 한글의 가로:세로 비율 약 0.85:1, JetBrains Mono와 Iosevka 사이의 영문 비율, 높은 시인성, 향후 공개 배포.

이 문서는 시안 제작 전의 후보 조사다. 이후 Fira Code를 포함한 네 시안 제작·검증을 완료했으며, 최신 상태는 [시안 제작 기록](prototype-build.md)에 있다. 한글 배율도 아래 11자 표본 추정에서 전체 11,172자 측정값으로 갱신했다.

## 추천

1. **Iosevka Custom, unit width 550**: 우선 시안. 원본 자형 생성 단계에서 폭을 설계하고 혼동 문자의 모양도 선택할 수 있다. 540/550/560을 비교한다.
2. **Inconsolata Variable, wdth=112.5, wght=400**: 실측 advance가 0.55em인 대안. 다만 소문자 높이가 작아 같은 크기에서 JetBrains Mono보다 작게 보일 수 있다. 폭만으로 시인성이 동등하다고 판단하지 않는다.
3. **Cascadia Code / Mono**: 별도 폭 커스텀 없이 쓰는 비교군. 0.5859375em으로 범위 안이지만 JetBrains 쪽에 가깝다.

Iosevka Custom은 아직 빌드하지 않았다. 이 문서의 추천은 설계 적합성 판단이며 실제 읽기 성능을 입증한 순위가 아니다. 새 후보는 시스템에 추가 설치하지 않았다.

## 확인한 폭

em은 폰트 설계 단위다. advance는 다음 글자까지 이동하는 거리로, 눈에 보이는 윤곽의 가로/세로 비율과 다르다.

| 후보 | 영문 셀 폭 | 근거 | 판단 |
|---|---:|---|---|
| Iosevka Normal | 0.500em | 공식 build-plans.toml의 shape=500 | 좁은 기준 |
| Iosevka Custom | 0.550em 목표 | 공식 custom build의 폭 지정 지원 | 1순위. 아직 빌드 실측 전 |
| Inconsolata Normal | 0.500em | VF 3.001, wdth=100 바이너리 실측 | 기본판은 중간 폭이 아님 |
| Inconsolata SemiExpanded | 0.540em | VF 3.001, wdth=110 실측 | 기성 폭 후보 |
| Inconsolata 사용자 폭 | 0.550em | VF 3.001, wdth=112.5 실측 | 정확한 산술 중간값 |
| Cascadia Code Regular | 1200/2048 = 0.5859375em | 공식 UFO의 A advance와 unitsPerEm | JetBrains에 가까운 비교군 |
| JetBrains Mono Regular | 0.600em | 2.305 바이너리 실측 | 넓은 기준 |
| Iosevka Extended | 0.600em | 현재 공식 build-plans.toml | 현재 버전에서는 중간값 후보가 아님 |

Inconsolata wdth=110을 단순히 0.5×1.1=0.55em으로 계산하면 틀린다. 실제 보간 결과를 측정해야 한다. x-height는 JetBrains Mono 0.550em, Inconsolata 0.457em, Cascadia 소스 1060/2048≈0.518em이다. 높이를 맞춰 비교하면 상대적인 폭도 달라진다.

출처: [Iosevka 빌드 설정](https://github.com/be5invis/Iosevka/blob/main/build-plans.toml), [사용자 빌드 예제](https://github.com/be5invis/Iosevka/blob/main/private-build-plans.sample.toml), [Inconsolata 소스](https://github.com/googlefonts/Inconsolata), [Google Fonts 바이너리](https://github.com/google/fonts/tree/main/ofl/inconsolata), [Cascadia UFO](https://github.com/microsoft/cascadia-code/tree/main/sources/CascadiaCode-Regular.ufo), [JetBrains Mono TTF](https://github.com/JetBrains/JetBrainsMono/tree/master/fonts/ttf).

## 0.85:1을 어떻게 적용할 것인가

**기본 해석은 한글의 보이는 윤곽 비율을 약 0.85:1로 만든다는 것이다.** 원본 윤곽의 가로 좌표에 0.85를 곱하는 요청과는 다르다.

SourceHanSansK-Regular 2.005에서 `가나다라마바사값꿇뷁힣`의 실제 윤곽 바운딩 박스를 측정했다. 11자 표본의 가로/세로 중앙값은 약 **0.8917**이다. 이에 공통 가로 배율 0.85를 곱하면 중앙값은 약 **0.7580**으로 내려간다. 표본 중앙값을 0.85로 맞추는 공통 배율은 약 **0.9532**다. 예를 들어 `가`는 원래 834/904≈0.9226이고 가로 85% 적용 후 약 0.7842가 된다.

이 값은 표본 결과이며 전체 한글을 대표한다고 확정하지 않는다. 초성·중성·종성 배치 유형별로 표본을 늘려 배율을 정한다. 모든 글자의 개별 박스를 강제로 0.85로 맞추면 글자마다 획 굵기가 달라지므로 피한다. 실제 의도가 '원본 대비 가로 15% 압축'이라면 별도의 시안으로 비교한다.

한글의 윤곽 폭과 셀 폭도 분리한다. 영문 셀을 550 units로 선택하면 한글 완성형 advance는 1100 units여야 두 칸 정렬을 유지한다. 압축된 한글이 이 셀 안에서 너무 헐거워 보이면 한글 윤곽 크기·영문 전체 스케일·최종 셀 크기를 함께 다시 정한다. 한글 advance만 850으로 바꾸고 영문 550을 유지하면 정렬이 깨진다.

단순 가로 축소는 세로획의 두께도 줄인다. 처음에는 공통 배율로 시안을 만들되, 최종본에서는 획 무게와 내부 공간을 별도로 보정한다. `ㅁ·ㅂ·ㅍ`, `꿇·뚫·뷁·값`을 작은 크기에서 확인한다.

## 시인성 중심의 첫 시안

- 영문: Iosevka Custom 550, Regular. 0은 점 또는 사선, 1은 받침, 대문자 I는 가로획, 소문자 l은 구별되는 꼬리 형태를 비교한다. 구체 옵션 이름은 선택 버전의 문서로 확정한다.
- 한글: Source Han Sans **K**의 한글 윤곽. 전체 CJK를 처음부터 병합하지 않는다.
- 한글 비율: 원본, 표본 목표 0.85, 원본 가로 85%의 세 가지를 명확히 구분해 비교한다.
- 가로 배율뿐 아니라 기준선·시각적 높이·획 굵기를 조정한다. 두 원본의 Regular가 같은 무게라고 가정하지 않는다.
- 검증: 12/14/16/18px, 밝은/어두운 배경, 같은 폰트 크기와 시각 높이를 맞춘 비교 모두 수행한다.
- 합격 조건: 한영 혼합 주석의 자연스러움, 0O/1Il/rn/m 구분, 복잡한 받침 식별, 한글 두 칸 정렬, 글리프 잘림 없음.
- 후보 1개를 고른 후 Bold와 Italic 정책으로 확장한다. 영문과 한글 원본을 그대로 수평 변형한 결과만으로 최종 품질을 선언하지 않는다.

## 공개 배포 조건

Source Han Sans, Iosevka, Inconsolata, Cascadia Code, JetBrains Mono는 공식 라이선스상 OFL 1.1로 수정·재배포 가능한 후보다. 병합한 파생 폰트는 OFL 1.1로 배포하고, 포함한 원천의 저작권·라이선스를 보존한다. Source Han Sans에는 예약 이름 **Source**, Cascadia에는 **Cascadia Code**가 있으므로 새 기본 패밀리 이름을 사용한다. 실제 채택 버전의 모든 예약 이름을 다시 확인한다.

공개 저장소에는 입력 버전/커밋, 다운로드 URL, SHA-256, 원저작권 고지, 변경 내역, 빌드 설정과 재현 명령을 남긴다. OFL이 소스 공개를 일률적으로 강제한다는 뜻은 아니며, 이는 이 프로젝트의 재현성과 기여 편의를 위한 권장 정책이다. 빌드 도구의 라이선스는 폰트와 구분한다. 아직 원격 저장소를 생성하거나 공개하지 않았다.

라이선스 원문: [Source Han Sans](https://github.com/adobe-fonts/source-han-sans/blob/master/LICENSE.txt), [Iosevka](https://github.com/be5invis/Iosevka/blob/main/LICENSE.md), [Inconsolata](https://github.com/googlefonts/Inconsolata/blob/main/OFL.txt), [Cascadia](https://github.com/microsoft/cascadia-code/blob/main/LICENSE), [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono/blob/master/OFL.txt), [OFL FAQ](https://openfontlicense.org/ofl-faq/).

측정 원자료: [latin-candidate-metrics.json](latin-candidate-metrics.json). Inconsolata wdth=112.5와 Iosevka/Cascadia 소스 수치는 이 문서에 별도로 기록했다. 설치된 기존 세 폰트와 비교 페이지는 유지한다.
