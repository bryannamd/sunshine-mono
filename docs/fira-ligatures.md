# Sunshine Mono 0.5.0 — Fira Code 연산자 리거처

0.4.2의 한글·영문 기본 글리프, 힌팅, 고정폭을 그대로 보존하고 Fira Code 6.2의 ASCII 연산자·구두점 문맥 치환 규칙과 관련 글리프를 이식한다. 기본 자형과 한글 받침 라운딩은 바뀌지 않는다.

Fira Code의 실제 `calt` 규칙을 사용한다. 단순 문자열 목록의 탐욕적 치환이 아니므로 원본의 조합·문맥 제외 규칙을 유지한다. 영문·숫자 자체에 대한 Fira의 특수 치환은 가져오지 않는다. `calt`를 끄면 기존 Sunshine의 글자 그대로 표시한다. Iosevka의 별도 언어별 리거처 기능을 중복으로 켜는 구성은 이번 검증 대상이 아니다.

## 형태 맞춤

- 가로: Fira 한 칸 1200 units를 Sunshine 550 units로 변환한다.
- 굵기: Fira 가변 원본에서 Regular 422, Bold 601을 선택해 Sunshine `+`의 세로획에 맞춘다.
- 세로: `+`의 가로획 두께와 연산자 중심선 340 units에 맞춘다.
- 한글은 기존 1100 units이며 기본 글리프의 윤곽·힌팅 바이트를 변경하지 않는다.
- 새 연산자 글리프는 기존 다른 폰트의 힌팅 프로그램을 억지로 복사하지 않고 윤곽으로 렌더링한다. Windows DirectWrite 실기 검증은 별도다.

## 검증

`fira-ligatures-verification.json`에 표본 149종, 구두점 주변 문맥, 무작위 연산자열 300개/굵기를 기록한다. 활성 표본 수는 전체 지원 개수가 아니다. 기본 설정에서 변형되지 않는 조합도 Fira 원본의 결과 그대로 보존한다.

기본 글리프·cmap·폭·GPOS 보존, Fira와의 글리프 치환 일치, 코드 칸 너비 유지, 추가 글리프의 FreeType 엄격 렌더링을 검사한다. 배포 검사는 `fira-ligatures-release-verification.json`에 기록한다.

```sh
.venv/bin/python scripts/build_fira_ligatures.py
swift -module-cache-path /private/tmp/sunshine-swift-cache scripts/proof_fira_ligatures.swift
```

## 출처와 라이선스

[Fira Code 6.2 공식 배포](https://github.com/tonsky/FiraCode/releases/tag/6.2)의 가변 TTF를 사용한다. 입력 해시는 `sources/fira-ligatures-inputs.json`에 고정한다. SIL OFL 1.1이며, 원저작권과 라이선스는 폰트 메타데이터 및 `licenses/fira-OFL.txt`에 포함한다. Iosevka와 Source Han Sans의 고지도 유지한다.
