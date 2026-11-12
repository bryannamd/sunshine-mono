# Sunshine Mono

**Sunshine Mono by SunWorks** · 햇살코드

한글과 영문, 같은 리듬으로. macOS와 Windows의 코드 편집기·터미널을 위한 한영 고정폭 폰트 프로젝트입니다.

## 다운로드 · v0.3.0

[**Sunshine Mono 다운로드**](https://github.com/bryannamd/sunshine-mono/releases/tag/v0.3.0) · [설치 안내](docs/sunshine-install.md) · [릴리스 노트](docs/releases/v0.3.0.md)

ZIP을 풀고 `SunshineMono-Regular.ttf`, `SunshineMono-Bold.ttf`를 설치한 뒤 앱에서 **Sunshine Mono**를 선택하세요. WOFF2는 웹사이트용입니다.

## 기능과 상태

Iosevka Custom 550과 Source Han Sans KR을 기반으로 한영 획의 균형, 받침 모서리, 작은 크기의 가독성을 다듬고 있습니다.

- 실제 Regular 400 / Bold 700 두 굵기
- 영문 한 칸, 한글 두 칸의 고정폭과 현대 한글 11,172자
- 구분하기 쉬운 `0`, `1`, `I`, `l`
- 받침 왼쪽 아래 모서리 라운딩
- 크기별 실험 힌팅과 기존 코딩 리거처

**v0.3.0은 첫 공식 공개 배포입니다.** 기존 B3의 윤곽·힌팅·리거처를 유지하며 내부 이름을 Sunshine Mono로 바꿨습니다. 예전 `MM Coding B3` 설치본과는 별도 패밀리입니다.

우선순위는 macOS VS Code·터미널, 그다음 Windows입니다. FreeType와 macOS CoreText 검증 결과를 기록했으며, 실제 앱별 검증과 Windows DirectWrite 검증은 남아 있습니다. 한글 힌팅은 실험적입니다.

## 설계와 검증

- [공개 폰트 검증 결과](docs/sunshine-release-verification.json)
- [공개 폰트 CoreText 검증 결과](docs/sunshine-coretext-verification.json)

- [B3 형태·굵기·힌팅과 검증 기록](docs/rounded-weights.md)
- [FreeType 검증 결과](docs/b3-verification.json)
- [macOS CoreText 검증 결과](docs/b3-coretext-verification.json)
- [문자 구분 개선 기록](docs/glyph-refinement.md)
- [시안 제작 과정](docs/prototype-build.md)
- [원천 폰트 조사](docs/font-research-and-plan.md)

## 제작 소스

`scripts/`는 제작·힌팅·검증·비교 화면 생성 코드, `sources/`는 Iosevka 빌드 설정과 원천 파일 해시를 보관합니다. Python 의존성은 `requirements.txt`에 있습니다. 원천 폰트, 생성한 폰트·ZIP·내장 폰트 HTML은 Git에 포함하지 않습니다. 비교 HTML과 배포 묶음은 로컬 빌드로 생성합니다. 배포 바이너리는 GitHub Releases에서 제공합니다. B3 빌드·힌팅 이후 `python scripts/release_sunshine.py`로 공개 이름 변경·전수 검사·패키징을 수행합니다. `swift -module-cache-path /tmp/mmcodingfont-swift-cache scripts/proof_coretext.swift --sunshine`으로 macOS 네이티브 검증을 실행합니다. 문서에 있는 기존 시안 링크 중 생성물 링크는 로컬 빌드 후 사용할 수 있습니다.

## 원천과 라이선스

선택한 기반 서체는 [Iosevka](https://github.com/be5invis/Iosevka)와 [Source Han Sans](https://github.com/adobe-fonts/source-han-sans)입니다. 폰트는 SIL Open Font License 1.1을 따르며, 원저작권과 라이선스 전문은 [sources/licenses](sources/licenses)에 보존합니다. 초기 비교에 사용한 다른 서체의 라이선스도 같은 폴더에 있습니다.

SunWorks의 파생 서체 프로젝트이며, 원천 서체 제작자의 공식 협업이나 보증을 의미하지 않습니다.
