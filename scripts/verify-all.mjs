import fs from 'fs';
import path from 'path';
import * as lucide from 'lucide-react';

function walk(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  for (const file of list) {
    const full = path.join(dir, file);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      results = results.concat(walk(full));
    } else if (file.endsWith('.jsx') || file.endsWith('.js')) {
      results.push(full);
    }
  }
  return results;
}

const files = walk('./src');
let errors = 0;

const hooks = ['useState', 'useEffect', 'useRef', 'useMemo', 'useCallback', 'useContext', 'useReducer'];

for (const file of files) {
  const content = fs.readFileSync(file, 'utf8');

  // 1. Check Lucide icon imports
  const lucideMatches = content.matchAll(/import\s*\{([^}]+)\}\s*from\s*['"]lucide-react['"]/g);
  for (const match of lucideMatches) {
    const rawNames = match[1].split(',');
    for (let raw of rawNames) {
      raw = raw.trim();
      if (!raw) continue;
      const originalName = raw.split(/\s+as\s+/)[0].trim();
      if (!lucide[originalName]) {
        console.error(`[ERROR] Invalid lucide-react icon '${originalName}' in ${file}`);
        errors++;
      }
    }
  }

  // 2. Check React hooks usage
  for (const hook of hooks) {
    const hookCallRegex = new RegExp(`\\b${hook}\\s*\\(`, 'g');
    if (hookCallRegex.test(content)) {
      const isImported = new RegExp(`import\\s*(?:React\\s*,\\s*)?\\{[^}]*\\b${hook}\\b[^}]*\\}\\s*from\\s*['"]react['"]`).test(content);
      const isReactDot = new RegExp(`React\\.${hook}`).test(content);
      if (!isImported && !isReactDot) {
        console.error(`[ERROR] Hook '${hook}' is used but not imported from 'react' in ${file}`);
        errors++;
      }
    }
  }

  // 3. Check React.* usage without React import
  if (/\bReact\.[A-Za-z]/.test(content)) {
    const importsReact = /import\s+React\b/.test(content);
    if (!importsReact) {
      console.error(`[ERROR] 'React.*' used without importing React in ${file}`);
      errors++;
    }
  }
}

if (errors === 0) {
  console.log('✅ All JSX/JS files passed all checks! (No undefined icons, no missing React hooks)');
} else {
  console.log(`❌ Found ${errors} error(s).`);
  process.exit(1);
}
