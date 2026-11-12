# Sunshine Mono 0.4.2 — 영문 갈고리 곡선 정리

한글 0.4.1의 받침 라운딩을 보존하고 영문 `f t r j l J`의 과하게 말린 끝과 넓은 굽힘을 조정한 로컬 시안이다.

기존 Iosevka에 포함된 평평한 끝 모양을 사용하고, f·t·l·j·J의 접합부를 Regular 100 / Bold 132 units의 짧은 원호로 다시 그린다. 내부 곡선 반경은 외부 반경에서 원래 획 두께를 빼서 결정한다. r은 아래로 되감기는 끝을 제거한 기존 대체 자형을 사용한다. O·C·S·U 등 글자의 기본 구조를 이루는 곡선은 그대로 둔다. I·l·1의 구분과 영문 550 / 한글 1100 units를 유지한다.

같은 윤곽을 공유하는 별칭과 합성 악센트 글리프도 함께 반영한다. 임의의 `cvXX`·스타일 세트를 사용자가 별도로 켜면 기존 대체 자형이 나올 수 있다. 이번 수정은 기본 자형에 적용하며, 리거처 규칙이나 타 폰트의 리거처를 새로 도입하지 않는다.

한글과 자모의 윤곽·힌팅 바이트코드는 0.4.1 설치본에서 그대로 복사하고 바이트 동일성을 검증한다. 영문 힌팅만 새로 생성한다.

## 재현

```sh
.venv/bin/python scripts/build_latin_balance.py
swift -module-cache-path /private/tmp/sunshine-swift-cache scripts/proof_latin_balance.swift
```

- `latin-balance-verification.json`: 바뀐 영문, 다른 ASCII 보존, 한글·자모 보존, 고정폭·레이아웃 보존.
- `latin-balance-release-verification.json`: 두 굵기 전수 렌더링, 기존 리거처 15종, 이름·WOFF2 검사.
- `latin-balance-coretext-verification.json`: macOS 1배·2배, 밝고 어두운 배경의 비교.
- `proofs/latin-balance-comparison-1x.png`, `proofs/latin-balance-comparison-2x.png`: 대소문자 전체와 한영 혼합 문장, 수정 글자 확대 비교.

결과는 `fonts/releases/0.4.2/`에 생성한다. 0.4.1은 보존한다. 실제 앱 UI 및 Windows DirectWrite 검증은 별도다.

SIL Open Font License 1.1. Iosevka·Source Han Sans 원저작권과 라이선스를 보존한다.
