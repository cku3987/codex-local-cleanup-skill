# Codex Local Cleanup Skill

`codex-local-cleanup`은 로컬 Codex Desktop 메타데이터(`~/.codex`)에 남은 오래된 프로젝트 흔적을 안전하게 정리하기 위한 Codex 스킬입니다.

프로젝트를 삭제하거나 이름을 바꾼 뒤에도 Codex Desktop 또는 모바일 Codex에 예전 프로젝트, 아카이브 스레드, 삭제된 작업 경로가 계속 보일 때 사용합니다.

목표는 모바일에 보이는 프로젝트 목록도 Codex Desktop의 활성 saved project 목록과 같아지게 하는 것입니다.

![Codex Local Cleanup 흐름](../assets/codex-local-cleanup-flow.svg)

## 주요 기능

- `.codex-global-state.json`에서 현재 저장된 프로젝트 루트를 읽습니다.
- `state_*.sqlite`의 스레드를 `cwd` 기준으로 분류합니다.
- 기본적으로 현재 저장된 프로젝트, 일반 채팅(projectless), 현재 스레드는 보존합니다.
- 저장된 프로젝트 밖의 비활성 프로젝트성 스레드를 찾습니다.
- 삭제된 `cwd` 항목과 오래된 아카이브 스레드를 찾습니다.
- 변경 전에 관련 메타데이터를 백업합니다.
- 대상 세션 JSONL, 스레드 인덱스, global state, `config.toml`, SQLite row를 정리합니다.
- SQLite 무결성과 잔여 대상 여부를 검증합니다.

## 설치

권장 방식: Codex의 기본 `skill-installer` 스킬로 이 GitHub 경로를 설치합니다.

```text
$skill-installer Install the skill from https://github.com/cku3987/codex-local-cleanup-skill/tree/main/codex-local-cleanup
```

수동 설치: 스킬 폴더를 Codex 스킬 디렉터리로 복사합니다.

```powershell
Copy-Item -Recurse .\codex-local-cleanup "$env:USERPROFILE\.codex\skills\codex-local-cleanup"
```

스킬이 바로 보이지 않으면 Codex Desktop을 재시작하세요.

## 사용 예시

```text
$codex-local-cleanup 현재 saved project와 projectless 채팅은 유지하고, saved project 밖의 프로젝트성 Codex 잔여 메타데이터를 백업 후 정리해줘.
```

```text
$codex-local-cleanup 삭제된 cwd를 가진 스레드만 찾아서 백업하고, 그 stale 항목만 제거한 뒤 검증해줘.
```

```text
$codex-local-cleanup saved project 밖의 프로젝트 흔적만 정리해줘. archived_sessions는 삭제하지 마.
```

## 안전 규칙

이 스킬은 로컬 Codex Desktop 상태를 다룹니다. 메타데이터를 수정하기 전에는 반드시 백업해야 합니다.

중요한 위험 및 권한 주의:

- 이 스킬은 소스코드 정리가 아니라 로컬 애플리케이션 상태 정리입니다.
- 선택된 대상의 Codex 스레드 메타데이터, 세션 JSONL, 사이드바 인덱스, 신뢰 설정, SQLite row가 삭제될 수 있습니다.
- 전체 권한 또는 승인 없이 실행되는 환경에서는 Codex가 곧바로 쓰기 작업을 할 수 있습니다. 확실하지 않으면 먼저 읽기 전용 목록 확인을 요청하세요.
- 범위가 모호한 프롬프트로 바로 정리하지 마세요. 쓰기 작업 전에 대상 목록, 백업 경로, 보존 규칙을 확인해야 합니다.
- 백업에는 로컬 경로, 스레드 제목, 프롬프트, 대화 내용이 포함될 수 있습니다. 백업은 외부에 공유하지 마세요.

다음 항목은 삭제하거나 수정하면 안 됩니다.

- `auth.json`
- `installation_id`
- `skills/`
- `plugins/`
- `automations/`
- `.sandbox-secrets/`
- 사용자 소스 프로젝트

이 스킬은 의도적으로 보수적으로 동작합니다. 사용자가 명시적으로 요청하지 않는 한 저장된 프로젝트, 일반 채팅, 현재 스레드는 보존합니다.

## 라이선스

MIT
