#!/usr/bin/env node
// Supabase MCP server 래퍼 (wave-double 프로젝트 전용)
//
// 목적: 프로젝트의 gitignored `.env.local`에서 이 프로젝트 전용
// `SUPABASE_ACCESS_TOKEN`을 읽어 주입한 뒤, 실제 `@supabase/mcp-server-supabase`
// 를 표준 입력/출력 pass-through로 실행한다.
//
// 왜 필요한가: opencode의 MCP `environment`는 리터럴 또는 `{env:VAR}`(실제 OS
// 환경변수)만 지원하고 파일을 로드하지 않는다. 그런데 `SUPABASE_ACCESS_TOKEN`은
// OS 셸 환경변수에도 다른(다른 조직용) 값이 세팅되어 있어 MCP가 그걸 잘못 읽고
// wave-double(`qqhjeumlecaudsiqhhdu`) 접근이 거부됐었다. 각 프로젝트가 자기
// supabase 토큰만 쓰도록, 이 래퍼는 토큰을 내장하지 않고 프로젝트 루트의
// `.env.local`에서만 읽는다.
//
// 구현 참고: opencode는 이 래퍼 프로세스의 stdin/stdout과 MCP JSON-RPC를 주고받는다.
// `stdio: 'inherit'` spawn은 자식의 fd를 부모와 동일하게 만들어 opencode <-> 래퍼
// <-> npx 서버가 직렬로 연결되므로 MCP 통신이 그대로 흘러간다.

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { spawn } from 'node:child_process';

// 프로젝트 루트 = 이 파일(.opencode/)의 한 단계 위.
const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

function readEnvLocalToken() {
  const envPath = path.join(projectRoot, '.env.local');
  const raw = readFileSync(envPath, 'utf8');
  const m = raw.match(/^SUPABASE_ACCESS_TOKEN=?(.*)$/m);
  if (!m || !m[1].trim()) {
    console.error(
      `[supabase-mcp] '.env.local'에 SUPABASE_ACCESS_TOKEN이 없습니다. ` +
      `이 프로젝트의 supabase 토큰을 .env.local에 추가하세요.`
    );
    process.exit(1);
  }
  return m[1].trim();
}

const token = readEnvLocalToken();
process.env.SUPABASE_ACCESS_TOKEN = token;

// (선택) 셸 전역에 다른 조직용 값이 있어도(있어도 무방) 위에서 이 프로젝트 값으로
// 덮어썼으므로 MCP 서버가 이 프로젝트의 토큰을 사용한다.

const npx = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const args = [
  '-y',
  '@supabase/mcp-server-supabase@latest',
  '--project-ref=qqhjeumlecaudsiqhhdu'
];

// Windows의 Node(v24+)는 `.cmd`/`.bat` 배치 파일을 직접 `spawn`하면 EINVAL로
// 실패한다(node Electron/Chromium의 known issue). `cmd.exe /c`를 경유해야
// 배치 파일을 실행할 수 있다. MCP는 래퍼의 stdio(opencode <-> 래퍼)를
// 자식으로 직렬 잇기 때문에 여기서는 `shell: true` 대신 `cmd.exe /c`를 쓴다.
const spawnCmd =
  process.platform === 'win32'
    ? ['cmd.exe', '/d', '/s', '/c', ...(shellQuoteCmd(joinCommand(npx, args)))]
    : [npx, ...args];

const child = spawn(spawnCmd[0], spawnCmd.slice(1), {
  stdio: 'inherit',
  env: process.env,
  cwd: projectRoot,
  shell: false
});

function joinCommand(prog, args) {
  const tokenize = (p) => (/^[^\s"]+$/.test(p) ? p : `"${p.replace(/"/g, '\\"')}"`);
  return [prog, ...args].map(tokenize).join(' ');
}

function shellQuoteCmd(cmd) {
  // `cmd /c`는 인자를 그대로 명령줄로 해석하므로 한 묶음 문자열 하나로 넘긴다.
  return [cmd];
}

child.on('error', (err) => {
  console.error(`[supabase-mcp] spawn 실패: ${err.message}`);
  process.exit(1);
});

child.on('exit', (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
  } else {
    process.exit(code ?? 0);
  }
});
