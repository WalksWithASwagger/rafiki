#!/usr/bin/env node

const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function commandWorks(command) {
  const result = spawnSync(command, ['--version'], { encoding: 'utf8' });
  return result.status === 0;
}

function getPythonExecutable() {
  const root = path.resolve(__dirname, '..');
  const winVenv = path.join(root, '.venv', 'Scripts', 'python.exe');
  const unixVenv = path.join(root, '.venv', 'bin', 'python');
  const unixVenvPython3 = path.join(root, '.venv', 'bin', 'python3');

  if (process.platform === 'win32' && fs.existsSync(winVenv)) {
    return winVenv;
  }
  if (fs.existsSync(unixVenv)) {
    return unixVenv;
  }
  if (fs.existsSync(unixVenvPython3)) {
    return unixVenvPython3;
  }
  if (commandWorks('python3')) {
    return 'python3';
  }
  return 'python';
}

const python = getPythonExecutable();
const result = spawnSync(python, ['-m', 'pytest', '-q'], {
  stdio: 'inherit',
  env: process.env,
});

if (result.error) {
  console.error(`Failed to start Python: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 1);

