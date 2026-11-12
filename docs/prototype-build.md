# 네 가지 한글 코딩 폰트 시안

2026-11-12. 시각 비교용 Regular 0.1.0. 공개 배포 최종본이 아니다.

| 시안 | 영문 원천 | 영문 한 칸 | 폰트 패밀리 이름 |
|---|---|---:|---|
| A | JetBrains Mono 2.305 | 0.600em | MM Coding A |
| B | Iosevka 34.9.1 Custom 550 | 0.550em | MM Coding B |
| C | Cascadia Mono 2407.024 | 0.5859375em | MM Coding C |
| D | Fira Code 6.002 | 0.6153846em | MM Coding D |

## 비교 방법

[비교 페이지](prototype-comparison.html)를 브라우저에서 연다. WOFF2가 HTML에 포함되어 네트워크·시스템 설치 없이 실제 시안으로 표시된다. 이름 가리기, 12~24px 크기, 행간, 밝은/어두운 배경, 리거처, 개별/전체 보기, 공통 코드 입력을 지원한다.

먼저 16px에서 이름을 가리고 선호하는 두 개를 고른다. 이후 12/14/18px에서 `0O`, `1Il`, `rn/m`, 복잡한 받침, 긴 혼합 주석을 읽는다. 폰트 크기가 같아도 영문의 실제 소문자 높이는 다르다. 크기를 보정한 비교는 별도 판단으로 기록한다. CSS `font-synthesis:none`으로 가짜 굵기·기울임을 막았다.

각 시안의 TTF는 `fonts/prototypes/`에 있다. 기존 설치 폰트는 바꾸지 않았으며 새 시안은 시스템에 설치하지 않았다. TTF를 직접 설치하면 위 패밀리 이름으로 선택할 수 있다. 재배포할 때는 동봉 라이선스가 포함된 ZIP을 사용한다.

## 한글 조정

원천은 Source Han Sans K Regular 2.005다. 현대 한글 **11,172자 전체**의 윤곽 가로/세로 비율 중앙값은 약 **0.884868**이었다. 전체에 같은 가로 배율 **0.960595**, 세로 배율 **1.0**을 적용해 중앙값을 약 **0.85:1**로 맞췄다. 초기 11자 표본의 추정치를 전체 측정으로 대체한 것이다.

이는 '원본을 가로 85%로 압축'한 결과가 아니다. 글자별 비율을 모두 0.85로 강제하지도 않는다. 같은 원천의 동일한 변환을 네 시안에 적용해 영문 차이를 비교한다. 각 영문 고정폭의 두 배를 한글 완성형 advance로 설정하고, 변환된 원본 셀을 중앙에 놓았다. 영문 폭이 다르므로 한글 좌우 여백은 시안마다 달라진다.

한글 CFF 윤곽을 quadratic TrueType 윤곽으로 변환해 각각의 영문 TTF에 넣었다. 원래 영문의 윤곽·폭·GSUB/GPOS를 보존한다. 기존 글리프 ID 뒤에 한글을 추가하며 새 패밀리 이름으로 구분한다. 현대 완성형, 원천에 있는 U+1100–11FF 자모, U+3130–318F 호환 자모를 포함한다. 원천 전체의 CJK 문자나 옛한글 조합 레이아웃을 이식한 것은 아니다.

Iosevka B는 소스를 `shape=550`으로 빌드했다. 완성된 Iosevka를 수평으로 늘린 파일이 아니다. 현재 B와 추가된 한글 윤곽은 unhinted다. 다른 영문은 원본 힌팅을 유지한다. 따라서 특히 Windows 저해상도에서 최종 가독성 순위로 단정하면 안 된다. 시안 선택 후 힌팅·획 무게·받침 내부 공간을 정교화한다.

## 재현

Python 가상환경에서 저장소 루트 기준:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/fetch_sources.py
```

Iosevka 입력은 `sources/inputs.lock.json`의 커밋으로 별도 빌드한다. Node/npm이 필요하며 최초 빌드에는 시간이 걸린다.

```sh
git clone https://github.com/be5invis/Iosevka /tmp/mmcodingfont-iosevka-rebuild
git -C /tmp/mmcodingfont-iosevka-rebuild checkout cea353b17b9b5c6e22da4f0fcae66f16d68a4edf
cp sources/iosevka-private-build-plans.toml /tmp/mmcodingfont-iosevka-rebuild/private-build-plans.toml
```

해당 Iosevka 작업 폴더에서 `npm ci`, `npm run build -- ttf-unhinted::MMCodingIosevka550 --jCmd=2`를 실행한다. 생성된 `dist/MMCodingIosevka550/TTF-Unhinted/MMCodingIosevka550-Regular.ttf`를 이 프로젝트의 `sources/upstream/iosevka.ttf`로 복사한다. 입력 SHA-256은 lock에 기록했다. 빌드 시각 등에 따라 재빌드 바이너리 해시가 달라질 가능성이 있으므로 해시 차이는 메트릭·윤곽 검증과 구분한다.

프로젝트 루트에서:

```sh
.venv/bin/python scripts/build_prototypes.py
.venv/bin/python scripts/verify_prototypes.py
.venv/bin/python scripts/render_comparison.py
```

빌드 스크립트는 임의의 한글 배율을 하드코딩하지 않고 원천의 전체 현대 한글 비율을 다시 계산한다. 원천 다운로드 URL과 SHA-256은 [입력 잠금 파일](../sources/inputs.lock.json), 출력 메트릭은 [폰트 manifest](../fonts/prototypes/manifest.json)에 기록된다. 변경한 소스의 고지·OFL 전문은 `sources/licenses/` 및 배포 폴더의 `licenses/`에 있다.

## 검증 범위

자동 검증 결과는 [prototype-verification.json](prototype-verification.json)에 기록한다. 검증 대상은 현대 한글 전체 수록, ASCII:한글 1:2 폭, 한글 셀 이탈·수직 잘림, 실제 비율 중앙값, ASCII 원형·메트릭 불변, Latin 리거처 on/off shaping 회귀, 현대 한글 NFC/NFD 문장 shaping, TTF와 WOFF2의 cmap 일치다.

자동 검사 네 시안 모두 통과. 최종 한글 비율 중앙값은 A/B 0.849890, C 0.850027, D 0.849943이다.

ego-lite TaskSpace 7 (`mmCodingFont four prototypes`)에서 실제 WOFF2 네 종 로드, 이름 가리기, 12px 크기 변경, 밝은/어두운 배경, 리거처 토글, 샘플 변경, D 단독 보기, 공통 코드 입력을 검증했다. Canvas에서 `한글`과 `abcd`의 폭 비율은 네 시안 모두 오차 0.000001 이내로 1이었다. 390px에서는 한 열로 전환되고 문서 가로 넘침이 없었으며, 긴 코드는 각 샘플 안에서 가로 스크롤된다. 원천 라이선스 다섯 개도 HTML에 포함했다.

화면 증거: [데스크톱 밝은 화면](evidence/prototypes-desktop-light.png), [데스크톱 어두운 화면](evidence/prototypes-desktop-dark.png), [모바일 390px](evidence/prototypes-mobile-dark.png). ZIP 15개 항목의 무결성 검사를 통과했다. Impeccable 기계 검사에서 발견 항목은 없었다.

macOS 브라우저에서의 비교는 편집기·터미널·Windows/Linux 검증을 대체하지 않는다. 최종 OFL 공개 배포 전에 스타일 확장, 전체 문자 범위 정책, 추가 sanitizer 검사와 플랫폼 검증이 필요하다.
