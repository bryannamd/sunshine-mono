# B2: Iosevka 550 문자 구분 개선

기존 B안은 그대로 보존한다. B2는 같은 Iosevka 34.9.1 소스·550 폭·Regular 굵기에서 아래 자형 옵션을 선택한 비교안이다. JetBrains Mono의 윤곽을 복사하지 않았다.

| 문자 | B2 옵션 | 형태 |
|---|---|---|
| `0` | `zero = "dotted"` | 중앙 점으로 O와 구분 |
| `1` | `one = "base"` | 위쪽 사선과 아래 받침 |
| `I` | `capital-i = "serifed"` | 위아래 가로획. 기존 B안과 동일 |
| `l` | `l = "serifed-flat-tailed"` | 위쪽 가로획과 오른쪽으로 평평하게 끝나는 곡선 꼬리 |

비교: [B와 B2 오프라인 비교 페이지](b2-comparison.html). 위쪽 확대 자형과 아래 실제 코드에서 확인한다. 특히 `0O`, `1Il`, `null`, `ill`, `1001`을 12·14·16px와 밝은/어두운 배경에서 비교한다.

설치용 패밀리 이름은 **MM Coding B2**다. 이번 작업에서 시스템 폰트로 설치하지 않았다. [B/B2 폰트·라이선스 묶음](../fonts/refinement/MMCoding-B-B2-comparison.zip)을 제공한다. 기존 네 시안 페이지와 파일은 유지한다.

## 재현

Iosevka 커밋은 기존 `sources/iosevka-commit.txt`와 같다. Iosevka 체크아웃에 `sources/iosevka-b2-build-plans.toml`을 `private-build-plans.toml`로 복사하고 다음 타깃을 빌드한다.

```sh
npm run build -- ttf-unhinted::MMCodingIosevka550B2 --jCmd=2
```

출력 `dist/MMCodingIosevka550B2/TTF-Unhinted/MMCodingIosevka550B2-Regular.ttf`를 프로젝트의 `sources/upstream/iosevka-b2.ttf`로 복사한다. 프로젝트 루트에서:

```sh
.venv/bin/python scripts/build_prototypes.py --refine-b
.venv/bin/python scripts/verify_prototypes.py --refine-b
.venv/bin/python scripts/render_comparison.py --refine-b
```

`--refine-b`를 생략하면 기존 네 시안 흐름을 사용한다. 입력 해시는 `sources/inputs.lock.json`, 출력 메트릭과 해시는 `fonts/refinement/manifest.json`에 기록한다.

## 검증과 한계

검증 결과는 [b2-verification.json](b2-verification.json)에 기록한다. 기존 B 대비 ASCII 윤곽 변화는 `0`, `1`, `l`에 한정하는지 검사한다. `I`를 포함한 나머지 ASCII와 현대 한글 11,172자 윤곽이 동일한지, 영문 550·한글 1100 units, 한글 비율 약 0.85, NFC/NFD, 영문 shaping과 WOFF2를 검사한다. Iosevka가 자동 생성하는 비ASCII 파생 문자·대체 자형은 해당 기본 자형 변경을 따를 수 있다.

Regular 시안이며 한글과 Iosevka는 unhinted다. 획 보정, 저해상도 Windows 렌더링, Bold/Italic은 후속 검증 대상이다. 원천은 Iosevka와 Source Han Sans이며 OFL 고지를 보존한다. 아직 공개 릴리스하지 않았다.

검증 완료: ASCII 변화는 `0`, `1`, `l` 세 글자만 확인했고, `I`와 현대 한글 전체 윤곽은 B와 동일했다. 한글 비율 중앙값은 0.849890, 영문/한글 advance는 550/1100이다. 나머지 바이너리 검사도 통과했으며 기존 네 TTF의 SHA-256은 원래 manifest와 일치했다.

ego-lite TaskSpace 8 (`mmCodingFont B2 glyph refinement`)에서 B/B2 웹폰트 로드, 12·14·16px, 밝은/어두운 배경, 샘플 변경, B2 단독 보기, 이름 가리기, 390px 반응형을 확인했다. 확대 자형은 좁은 화면에서 크기를 줄여 다섯 글자를 한눈에 표시한다. 긴 코드만 샘플 내부에서 스크롤된다. [데스크톱](evidence/b2-desktop.png) · [모바일](evidence/b2-mobile-dark.png). 실제 편집기·터미널·Windows 검증은 아직 수행하지 않았다.
