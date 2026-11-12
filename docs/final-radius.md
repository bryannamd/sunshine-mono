# Sunshine Mono 0.4.1 — 받침 왼쪽 아래 라운딩

0.4.0의 가벼운 한글 획·여백을 유지하면서, 받침의 왼쪽 자음이 ㄴ·ㄷ·ㄹ·ㅁ·ㅂ인 경우 왼쪽 아래 바깥 모서리에 원호 형태의 라운딩을 적용한 로컬 시안이다.

대상은 ㄴ·ㄵ·ㄶ·ㄷ·ㄹ·ㄺ·ㄻ·ㄼ·ㄽ·ㄾ·ㄿ·ㅀ·ㅁ·ㅂ·ㅄ이다. 각 받침의 399개 음절, 총 5,985자를 Regular와 Bold 각각 처리한다. 겹받침은 왼쪽 자음만 새로 수정한다. 초성·중성, 다른 받침과 독립 자모는 이번 변경의 대상이 아니다. 기존에 있던 다른 모서리의 라운딩은 보존한다.

반경은 Regular 88, Bold 112 units이다(1000 UPM). 14px에서 각각 약 1.23px·1.57px에 해당한다. CSS를 적용하는 것이 아니라 폰트 윤곽 자체를 변경한다. 원래의 꼭짓점을 같은 Source Han 가변 원본에서 찾아, 해당 모서리에 국한된 원호 절삭 영역을 기존 0.4.0 윤곽에서 뺀다. 짧은 직선 때문에 누락되던 ㄵ·ㄶ·ㄺ 등의 받침도 포함한다. 두 개의 2차 곡선으로 90도 원호를 근사하며, 내부 공간을 채우거나 획을 두껍게 하지 않는다.

## 재현

```sh
.venv/bin/python scripts/build_final_radius.py
swift -module-cache-path /private/tmp/sunshine-swift-cache scripts/proof_final_radius.swift
```

- `final-radius-verification.json`: 15종 전수 적용, 모서리 영역 밖 변화 제한, 비대상 글리프·모든 advance 보존. TTF 정수 좌표 반올림에 따른 기존 경계의 1 unit 오차만 허용한다.
- `final-radius-release-verification.json`: 두 굵기 전수 FreeType 렌더링, 패밀리 이름, 리거처, WOFF2 검사.
- `final-radius-coretext-verification.json`: 파일 기반 CoreText 비교·대체 폰트·2:1 칸 폭 검사.
- `proofs/final-radius-comparison-1x.png`, `proofs/final-radius-comparison-2x.png`: 실제 크기와 확대 자형의 이전·이후 비교. 확대 자형이 작은 크기에서의 둥글기 체감을 보장하지는 않는다.

결과는 `fonts/releases/0.4.1/`에 생성한다. 이전 0.4.0 및 공개 0.3.0은 보존한다. Regular·Bold를 함께 설치한 뒤 앱을 다시 열어 Sunshine Mono를 선택한다. 실제 앱 UI와 Windows DirectWrite 검증은 별도다.

SIL Open Font License 1.1. Iosevka·Source Han Sans 원저작권과 라이선스를 배포 파일에 보존한다.
