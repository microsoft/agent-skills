// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

// https://astro.build/config
export default defineConfig({
  integrations: [react()],
  outDir: '../docs',
  base: '/skills/',
  build: {
    assets: '_astro'
  }
});