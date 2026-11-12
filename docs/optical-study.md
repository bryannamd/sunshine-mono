# Sunshine Mono 0.4.0 — 한글 밀도 조정 시안

0.3.0의 한글이 무겁고 영문보다 글자 사이가 벌어져 보인다는 사용 의견을 반영한 로컬 시안이다. 공개 배포 버전은 변경하지 않는다.

한글 외곽 가로:세로 비율 중앙값 목표를 0.85에서 0.884로 높인다. Source Han 가변 원본에서 더 낮은 굵기를 선택하여 가로 확대에 따른 세로획 증가를 함께 보정한다. 기준 획 목표는 영문 H의 92.5%이며, 이전 한글과의 실제 변화는 `optical-verification.json`에 기록한다. ㅁ 기준 측정이 모든 글자의 지각적 굵기를 대표하지는 않는다.

영문 550·한글 1100 units와 행 높이, 영문 윤곽, 리거처를 유지한다. 한글 수평획 힌팅 목표도 측정된 획 감소 비율만큼 낮춘다. 받침 라운딩 범위와 반경은 0.3.0 그대로 유지한다. 이번 시안의 목적은 가벼운 획과 좁아진 좌우 여백이며, 둥글기 강화는 포함하지 않는다.

## 재현과 검증

```sh
.venv/bin/python scripts/build_optical.py
swift -module-cache-path /private/tmp/sunshine-swift-cache scripts/proof_optical.swift
```

- `optical-release-verification.json`: 두 굵기의 전수 FreeType 렌더링, 이름, 리거처, WOFF2 검사.
- `optical-verification.json`: 한글 11,172자 칸 경계, 변경 전후 여백, 영문 보존, NFC/NFD, 힌팅 전후 윤곽 검사.
- `proofs/optical-comparison-1x.png`, `proofs/optical-comparison-2x.png`: CoreText의 이전/이후 비교. 2x 이미지는 원본 배율에서 확인한다.

폰트는 `fonts/releases/0.4.0/`에 생성한다. Regular와 Bold를 함께 설치하고 앱을 다시 열어 Sunshine Mono를 선택한다. 이전 버전은 `fonts/releases/0.3.0/`에 보존한다. 실제 편집기·터미널 UI, Windows DirectWrite, 장시간 사용 평가는 별도이며 사용자의 시각적 선호는 아직 확인되지 않았다.

SIL Open Font License 1.1. Iosevka 및 Source Han Sans 기반. 원저작권과 라이선스는 배포 파일에 보존한다.
