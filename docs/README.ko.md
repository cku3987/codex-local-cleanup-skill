# Codex Local Cleanup Skill

`codex-local-cleanup`은 로컬 Codex Desktop 메타데이터(`~/.codex`)에 남은 오래된 프로젝트 흔적을 안전하게 정리하고, 기본 아카이브 기능으로 이동되지 않는 특정 활성 세션을 복구하기 위한 Codex 스킬입니다.

프로젝트를 삭제하거나 이름을 바꾼 뒤에도 Codex Desktop 또는 모바일 Codex에 예전 프로젝트, 아카이브 스레드, 삭제된 작업 경로가 계속 보일 때 사용합니다.

목표는 모바일에 보이는 프로젝트 목록도 Codex Desktop의 활성 로컬 프로젝트 목록과 같아지게 하는 것입니다.

현재 릴리스: [v0.3.0](https://github.com/cku3987/codex-local-cleanup-skill/releases/tag/v0.3.0)

![Codex Local Cleanup 흐름](../assets/codex-local-cleanup-flow.svg)

## 주요 기능

- `.codex-global-state.json`의 `local-projects`에서 현재 프로젝트 정의를, `thread-project-assignments`에서 스레드 연결 정보를 읽습니다.
- 각 프로젝트의 `rootPaths`를 사용해 여러 폴더가 연결된 프로젝트도 보존하며, 예전 saved root 정보는 fallback으로만 사용합니다.
- 기본적으로 활성 프로젝트, 일반 채팅(projectless), automation 스레드, 생성된 작업공간, 현재 스레드는 보존합니다.
- 세션 JSONL이나 SQLite를 직접 수정하기 전에 공식 Codex App Server의 `thread/delete` 절차를 우선합니다.
- 아카이브가 실패한 경우에도 공식 아카이브 기능을 먼저 재시도한 뒤, 본문 파일이 남아 있는 비현재 세션 하나만 ID로 복구합니다.
- 아카이브 복구 도구는 기본적으로 읽기 전용 진단만 수행하며, `--apply` 전 백업, Windows 구형 `\\?\` 경로 보존, 해시 검증, 아카이브 대화 재조회까지 요구합니다.
- `.codex/sqlite/codex-dev.db`는 삭제 원본이 아니라 Desktop이 다시 맞추는 파생 카탈로그로 보고 사후 검증에 사용합니다.
- `session_index.jsonl`과 legacy `.codex/sqlite/state_*.sqlite`는 기준 목록이 아니라 호환성 잔여물 확인용으로 다룹니다.
- 데스크탑에서 이름만 바뀐 프로젝트는 삭제 대상이 아니라 표시명 동기화 문제로 취급합니다.
- 끊어진 프로젝트 할당과 활성 프로젝트 밖의 비활성 프로젝트성 스레드를 찾습니다.
- 삭제된 `cwd` 항목과 오래된 아카이브 스레드를 찾습니다.
- 변경 전에 관련 메타데이터를 백업합니다.
- 표시 정리, 아카이브 정리, 용량 정리, 최후의 직접 복구를 서로 다른 범위로 구분합니다.
- 확인된 범위 안에서만 프로젝트 상태, 할당 정보, 세션 메타데이터, 신뢰 설정, 잔여 SQLite row를 정리합니다.
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
$codex-local-cleanup 현재 활성 로컬 프로젝트와 projectless 채팅은 유지하고, 활성 프로젝트 밖의 Codex 잔여 메타데이터를 백업 후 정리해줘.
```

```text
$codex-local-cleanup 삭제된 cwd를 가진 스레드만 찾아서 백업하고, 그 stale 항목만 제거한 뒤 검증해줘.
```

```text
$codex-local-cleanup 활성 로컬 프로젝트 밖의 프로젝트 흔적만 정리해줘. archived_sessions와 진단 로그는 삭제하지 마.
```

```text
$codex-local-cleanup 01a00000-0000-0000-0000-000000000000 세션이 아카이브 실패 후에도 남아 있어. 먼저 읽기 전용으로 진단하고, 안전하면 백업 후 이 세션만 아카이브 복구해줘.
```

## 안전 규칙

이 스킬은 로컬 Codex Desktop 상태를 다룹니다. 메타데이터를 수정하기 전에는 반드시 백업해야 합니다.

중요한 위험 및 권한 주의:

- 이 스킬은 소스코드 정리가 아니라 로컬 애플리케이션 상태 정리입니다.
- 선택된 대상의 Codex 스레드 메타데이터, 세션 JSONL, 사이드바 인덱스, 신뢰 설정, SQLite row가 삭제될 수 있습니다.
- Desktop의 **Remove** 기능과 공식 App Server 스레드 절차를 먼저 사용하고, 직접 메타데이터 수정은 검증된 잔여물에만 사용합니다.
- 아카이브 복구는 삭제가 아닙니다. 백업과 해시 검증 후 확인된 세션 JSONL 하나를 `archived_sessions`로 옮기고 해당 스레드의 아카이브 필드만 갱신합니다.
- 표시 정리를 요청했다고 해서 아카이브, 진단 로그, 백업 또는 DB 압축까지 자동으로 정리하지 않습니다.
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

이 스킬은 의도적으로 보수적으로 동작합니다. 사용자가 명시적으로 요청하지 않는 한 현재 로컬 프로젝트, 일반 채팅, 현재 스레드는 보존하며, 의미가 확인되지 않은 tombstone 형태의 상태는 삭제하지 않습니다.

## 라이선스

MIT
