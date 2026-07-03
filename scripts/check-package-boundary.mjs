#!/usr/bin/env node

import { spawnSync } from 'node:child_process';

const REQUIRED_PACKAGE_FILES = [
  'README.md',
  'docs/FRONTEND.md',
  'generate.py',
  'index.js',
  'lib/server.py',
  'package.json',
];

function fail(message) {
  console.error(message);
  process.exit(1);
}

const result = spawnSync('npm', ['pack', '--dry-run', '--json'], {
  encoding: 'utf8',
});

if (result.error) {
  fail(`Package boundary check failed to start npm: ${result.error.message}`);
}

if (result.status !== 0) {
  fail(
    [
      `Package boundary check failed: npm pack exited with ${result.status}`,
      result.stdout,
      result.stderr,
    ]
      .filter(Boolean)
      .join('\n'),
  );
}

let packs;
try {
  packs = JSON.parse(result.stdout);
} catch (error) {
  fail(`Package boundary check failed: could not parse npm pack JSON: ${error.message}`);
}

if (!Array.isArray(packs) || packs.length !== 1) {
  fail('Package boundary check failed: expected one npm pack result.');
}

const pack = packs[0];
const paths = new Set((pack.files || []).map((file) => file.path));
const failures = [];

for (const requiredPath of REQUIRED_PACKAGE_FILES) {
  if (!paths.has(requiredPath)) {
    failures.push(`missing expected package file: ${requiredPath}`);
  }
}

const frontendPaths = [...paths].filter((filePath) => filePath.startsWith('frontend/'));
if (frontendPaths.length > 0) {
  failures.push(
    [
      'frontend/ is currently excluded from the npm package by policy.',
      'Remove those paths or get maintainer approval for a package-content change.',
      `unexpected paths: ${frontendPaths.join(', ')}`,
    ].join(' '),
  );
}

if (failures.length > 0) {
  console.error('Package boundary check failed:');
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

const entryCount = pack.entryCount ?? paths.size;
console.log(
  `Package boundary check passed: ${entryCount} files in dry run; frontend/ excluded; docs/FRONTEND.md included.`,
);
