#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');

// Try uv first, fallback to python3
const pythonCmd = require('fs').existsSync(path.join(__dirname, 'pyproject.toml')) ? 'uv' : 'python3';
const args = pythonCmd === 'uv' ? ['run', 'python', 'src/prometheus_mcp_server/server.py'] : ['src/prometheus_mcp_server/server.py'];

const child = spawn(pythonCmd, args, {
  stdio: 'inherit',
  cwd: __dirname,
  env: { ...process.env }
});

child.on('close', (code) => {
  process.exit(code);
});
