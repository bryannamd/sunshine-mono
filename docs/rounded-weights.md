# B3 — 받침 라운딩, Regular/Bold와 크기별 힌팅

목표는 macOS VS Code·터미널에서 오래 읽기 좋은 한영 코딩 폰트다. Windows VS Code·터미널은 다음 우선순위다. B3는 검증 가능한 제작 시안이며, 최종 공개 릴리스나 모든 환경에서의 완벽한 조화를 주장하지 않는다.

## 형태와 굵기

- Iosevka Custom 550의 실제 Regular 400 / Bold 700을 사용한다. 인위적인 굵게 처리를 쓰지 않는다.
- 점 있는 `0`, 밑받침 있는 `1`, 세리프 `I`, 꼬리가 있는 `l`을 유지한다.
- Source Han Sans KR 가변 원본에서 Regular 410 / Bold 618을 선택했다. 영문 H와 한글 ㅁ의 세로·가로 획을 함께 비교한 수치다.
- Regular 기준 획: 영문 세로 80 / 가로 71 units, 한글 약 81.32 / 69.68 units.
- Bold 기준 획: 영문 115 / 98 units, 한글 약 114.88 / 97.26 units.
- 기준 획 오차는 3% 이내다. H·ㅁ 한 쌍의 측정이 모든 글자의 시각적 굵기 일치를 증명하지는 않는다. 복잡한 겹받침과 곡선은 별도 시각 검토가 필요하다.
- 현대 한글 외곽 가로:세로 비율의 중앙값을 약 0.85:1로 맞춘다. 글자마다 동일한 비율을 강제하지 않는다.
- 영문 advance 550, 한글 1100 units. 동일한 행 높이와 실제 Bold 스타일 연결을 사용한다.

## 받침 라운딩

Source Han 가변 글자는 획 윤곽이 겹칠 수 있다. 먼저 윤곽 합집합으로 바깥 테두리를 구하고, 받침이 있는 음절의 하단 22%에서 각진 왼쪽 아래 바깥 모서리만 찾는다. 내부 공간과 짧은 획 끝은 보존한다. 이미 둥근 ㅇ은 대상에서 제외한다.

Regular 반경 최대 24 units, Bold 36 units. 긴 직선 두 개가 만나는 모서리에 2차 곡선을 넣는다. 모든 받침을 무조건 둥글게 만들지 않으며, 검출한 위치와 개수는 `fonts/rounded/manifest.json`에 기록한다. 12px에서는 라운딩이 미묘한 정도이며, 큰 확대 화면의 효과와 혼동하지 않아야 한다.

## 힌팅 범위

- 영문: ttfautohint의 natural 모드, x-height 확대 없음.
- 한글: 수평획 검출 후 크기별 y축 SHPIX/IUP 명령을 생성한다. 수직획과 advance는 이동하지 않는다.
- 물리 PPEM 12·13·14·16 및 Retina 2배에 대응하는 24·26·28·32를 다룬다.
- 목표 수평획 두께는 `sources/b3-hint-profiles.json`에 직접 지정한다. 최대 이동 0.375px를 넘거나 획 순서를 뒤집는 보정은 생략한다.
- 이는 크기별 정책을 적용한 실험적 자동 생성 힌팅이다. 11,172자 각각을 수작업으로 조정하거나 눈으로 검수했다는 뜻이 아니다.
- FreeType의 엄격한 인터프리터 검증은 바이트코드 유효성 검사다. Windows DirectWrite나 macOS 앱 실기 검증을 대신하지 않는다.
- macOS의 형태 조화는 우선 윤곽 자체로 확보한다. 브라우저에서 보이는 결과와 VS Code·각 터미널의 렌더링은 구분한다.

`*-Unhinted.ttf`는 같은 윤곽의 비교용이다. 일반 설치에는 `MMCodingB3-Regular.ttf`와 `MMCodingB3-Bold.ttf`를 사용한다. 힌팅 유무 파일은 내부 패밀리 이름이 같으므로 동시에 설치하지 않는다.

## 리거처와 터미널

Iosevka의 기존 contextual ligature를 보존했다. `!= !== == === => -> <= >= || :: := <=> /* */ //` 15종의 치환과 동일 advance를 검사한다. 현재 추가 글리프를 새로 그린 것은 아니다. 기존 리거처를 검증·노출하는 단계다. `&&`는 기본 형태를 유지한다.

VS Code 사용 예:

```json
{
  "editor.fontFamily": "'MM Coding B3', monospace",
  "editor.fontSize": 14,
  "editor.fontWeight": "400",
  "editor.fontLigatures": true,
  "terminal.integrated.fontFamily": "'MM Coding B3'",
  "terminal.integrated.fontSize": 14,
  "terminal.integrated.fontWeight": "400",
  "terminal.integrated.fontWeightBold": "700"
}
```

설정은 사용 예이며 사용자 설정 파일을 수정하지 않았다. 터미널별 리거처 지원은 다르다. 폰트 설치 후 앱을 다시 열고 확인한다. 상자선·한영 혼합·커서 위치·선택 영역·Bold 전환을 실제 앱에서 확인해야 한다.

## 재현

```sh
python scripts/build_rounded.py
python scripts/hint_rounded.py
python scripts/verify_rounded.py
python scripts/render_rounded.py
```

의존성은 `requirements.txt`, 입력 해시는 `sources/inputs.lock.json` 및 배포 manifest, Iosevka Bold 설정은 `sources/iosevka-b3-bold-build-plans.toml`에 있다. OFL 원문과 원저작권은 폰트 메타데이터와 배포 압축 파일에 보존한다.

## 공개 전 남은 기준

1. 실제 macOS VS Code·Terminal/iTerm2에서 1배·2배 화면, 밝고 어두운 배경을 확인한다.
2. Windows VS Code·Windows Terminal에서 DirectWrite 결과를 확인하고 힌트 목표값을 조정한다.
3. 복잡한 겹받침, 유사 문자, 기호, 테두리, 합성 자모의 시각 회귀 표본을 확대한다.
4. 블라인드 비교와 장시간 코딩 사용 평가 후 Regular/Bold 광학 균형을 확정한다.

완벽함이나 세계 최고라는 평가는 이 검증과 사용자 평가를 통과한 뒤에도 객관적으로 보장할 수 없다. 비교 가능한 근거를 축적하는 것을 품질 기준으로 삼는다.

## 이번 검증 결과 — 2026-11-12

- 받침 모서리 수정: Regular 3,987자, Bold 3,985자. 각 굵기의 실제 윤곽에 따라 검출 수가 다르다.
- FreeType 엄격 모드: 2굵기 × 8크기 × (현대 한글 11,172 + ASCII 95) = **180,272회**, 오류 없음.
- ASCII 윤곽은 해당 굵기의 원본 Iosevka와 동일하다. 힌팅 전후 한글 윤곽도 동일하다.
- NFC/NFD 표본, 리거처 15종의 치환과 칸 너비 보존을 검사했다. [기계 검증 결과](b3-verification.json)
- macOS CoreText: 32개 굵기·크기·배율 조합. 표본 대체 폰트 없음, 실제 Bold 연결, 한글/영문 2:1 advance 통과. [CoreText 결과](b3-coretext-verification.json)
- CoreText [1배 픽셀 표본](proofs/b3-coretext-1x.png), [2배 픽셀 표본](proofs/b3-coretext-2x.png)을 생성하고 눈으로 확인했다. 고밀도 표본은 원본 크기에서 확인해야 한다.
- ego-lite TaskSpace 9에서 실제 WOFF2 3개 로딩, 크기 전환, 리거처 토글, 배경 토글을 확인했다. 데스크톱 및 390px 레이아웃을 확인했다. 브라우저 캡처는 CSS 픽셀 크기로 저장되므로 Retina 증거로 쓰지 않는다.
- [어두운 배경](proofs/b3-macos-browser-dark.png), [밝은 배경](proofs/b3-macos-browser-light.png), [좁은 화면](proofs/b3-mobile-layout.png).
- FreeType 힌팅 비교: [Regular](proofs/b3-regular-freetype.png), [Bold](proofs/b3-bold-freetype.png). 20 PPEM 미만은 픽셀 확인을 위해 nearest-neighbor 2배 확대했다. Windows 화면이 아니다.
- 실제 VS Code·터미널 UI 및 Windows DirectWrite 검증은 아직 수행하지 않았다. 현재 세션에 데스크톱 앱 제어 도구가 없다.

macOS에서 `swift -module-cache-path /tmp/mmcodingfont-swift-cache scripts/proof_coretext.swift`로 네이티브 표본을 재생성할 수 있다. `python scripts/render_raster_proof.py`는 FreeType 비교 표본을 만든다.
