import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    assetsDir: '_app',
    target: 'es2022',
    cssMinify: true,
  },
});
