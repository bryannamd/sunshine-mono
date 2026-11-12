# Sunshine Mono 0.3.0

**Sunshine Mono by SunWorks · 햇살코드**

한글과 영문, 같은 리듬으로.

## 설치

ZIP을 풀고 `SunshineMono-Regular.ttf`와 `SunshineMono-Bold.ttf` 두 파일을 설치하세요.

- macOS: TTF를 열어 서체 관리자에서 설치합니다.
- Windows: TTF 두 파일을 선택해 설치합니다.
- 설치 후 VS Code·터미널 앱을 다시 열고 **Sunshine Mono**를 선택합니다.
- WOFF2는 웹사이트용입니다. 일반 앱에는 TTF를 설치하세요.
- 기존 `MM Coding B3`와 이름이 다릅니다. 새 이름을 선택해야 하며 기존 시안은 자동으로 교체되지 않습니다.

VS Code 설정 예:

```json
{
  "editor.fontFamily": "'Sunshine Mono', monospace",
  "editor.fontSize": 14,
  "editor.fontWeight": "400",
  "editor.fontLigatures": true,
  "terminal.integrated.fontFamily": "'Sunshine Mono'",
  "terminal.integrated.fontSize": 14,
  "terminal.integrated.fontWeight": "400",
  "terminal.integrated.fontWeightBold": "700"
}
```

터미널의 리거처 지원은 앱마다 다릅니다. Regular와 Bold를 함께 설치하면 실제 Bold를 사용할 수 있습니다.

## 포함 기능과 검증 범위

Regular/Bold, 현대 한글 11,172자, 영문 550 / 한글 1100 units, 받침 모서리 라운딩, 코딩 리거처를 포함합니다. 12·13·14·16 및 24·26·28·32 PPEM에 실험적 한글 힌팅을 적용했습니다.

이번 0.3.0은 첫 공식 공개 배포입니다. 기존 B3 시안의 윤곽·획·힌팅·리거처를 보존하고 이름을 Sunshine Mono로 바꿨습니다. 힌팅은 계속 개선 중이며, 모든 글자를 수작업으로 조정한 것은 아닙니다. FreeType 전수 검사와 macOS CoreText 검증을 수행했습니다. 실제 VS Code·터미널 UI 및 Windows DirectWrite 검증은 아직 완료하지 않았습니다.

## 라이선스와 출처

SIL Open Font License 1.1. 원저작권과 전문은 `licenses/` 및 폰트 메타데이터에 있습니다. Iosevka와 Source Han Sans를 기반으로 SunWorks가 수정한 서체입니다. 원천 제작자의 공식 협업이나 보증을 의미하지 않습니다.

프로젝트·소스·문제 제보: https://github.com/bryannamd/sunshine-mono
