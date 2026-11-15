import { defineConfig } from 'astro/config';

export default defineConfig({
  redirects: {
    '/mission': '/mission-control'
  },
  vite: {
    optimizeDeps: {
      include: ['three', 'three/addons/controls/OrbitControls.js', 'echarts']
    }
  }
});
