const tseslint = require('@typescript-eslint/eslint-plugin');
const tsparser = require('@typescript-eslint/parser');

module.exports = [
  {
    files: ['src/**/*.ts'],
    languageOptions: {
      parser: tsparser,
      parserOptions: {
        ecmaVersion: 2020,
        sourceType: 'module'
      }
    },
    plugins: {
      '@typescript-eslint': tseslint
    },
    rules: {
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/no-explicit-any': 'warn'
    }
  },
  {
    // Renderer-specific rules - no browser dialogs!
    files: ['src/renderer/**/*.ts', 'src/**/renderer.ts'],
    rules: {
      'no-restricted-globals': ['error',
        { name: 'prompt', message: 'prompt() not supported in Electron. Use custom modal.' },
        { name: 'alert', message: 'alert() not supported in Electron. Use toast/notification.' },
        { name: 'confirm', message: 'confirm() not supported in Electron. Use custom dialog.' }
      ],
      'no-restricted-properties': ['error',
        { object: 'window', property: 'prompt', message: 'prompt() not supported in Electron.' },
        { object: 'window', property: 'alert', message: 'alert() not supported in Electron.' },
        { object: 'window', property: 'confirm', message: 'confirm() not supported in Electron.' }
      ]
    }
  }
];
