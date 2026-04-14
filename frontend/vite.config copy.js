import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
// ArcoVue、VueUse 组件和指令的自动引入解析器
import {
  ArcoResolver,
  VueUseComponentsResolver,
  VueUseDirectiveResolver
} from 'unplugin-vue-components/resolvers'

// icon 插件
import Icons from 'unplugin-icons/vite'
// icon 自动引入解析器
import IconsResolver from 'unplugin-icons/resolver'
// icon 加载 loader
import { FileSystemIconLoader } from 'unplugin-icons/loaders'

// 原子化css
// Unocss 插件
import Unocss from 'unocss/vite'
// Unocss 默认预设
import presetUno from '@unocss/preset-uno'
// Unocss 属性模式预设
import presetAttributify from '@unocss/preset-attributify'
// Unocss 指令转换插件
import transformerDirective from '@unocss/transformer-directives'

// 添加 vite-plugin-html 插件
import { createHtmlPlugin } from 'vite-plugin-html'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const viteEnv = loadEnv(mode, './')
  const allowedHosts = viteEnv.VITE_ALLOWED_HOSTS ? viteEnv.VITE_ALLOWED_HOSTS.split(',') : []
  return {
    base: viteEnv.VITE_BASE || '/', // 默认部署在域名的根路径下
    // 开发环境的配置
    server: {
      host: '0.0.0.0',
      port: viteEnv.VITE_PORT,
      open: true,
      strictPort: true, // 端口占用直接退出
      allowedHosts: allowedHosts
    },
    build: {
      outDir: 'dist',
      assetsDir: 'static/assets',
      // sourcemap: true,
      // 规定触发警告的 chunk 大小，消除打包大小超过500kb警告
      chunkSizeWarningLimit: 2000,
      // 静态资源打包到dist下的不同目录
      rollupOptions: {
        output: {
          chunkFileNames: 'static/js/[name]-[hash].js',
          entryFileNames: 'static/js/[name]-[hash].js',
          assetFileNames: 'static/[ext]/[name]-[hash].[ext]'
        }
      }
    },
    // 预览环境的配置
    preview: {
      host: '0.0.0.0',
      port: viteEnv.VITE_PORT,
      open: true,
      strictPort: true // 端口占用直接退出
    },
    plugins: [
      vue(),
      // 添加HTML插件配置：构建时生成 index.html 文件
      createHtmlPlugin({
        minify: true,
        inject: {
          data: {
            title: viteEnv.VITE_APP_NAME
          }
        }
      }),
      AutoImport({
        // 需要去解析的文件
        include: [
          /\.[tj]sx?$/, // .ts, .tsx, .js, .jsx
          /\.vue$/,
          /\.vue\?vue/, // .vue
          /\.md$/ // .md
        ],
        // imports 指定自动引入的包位置（名）
        imports: ['vue', 'pinia', 'vue-router', '@vueuse/core'],
        // 生成相应的自动导入json文件。
        eslintrc: {
          // 启用
          enabled: true,
          // 生成自动导入json文件位置
          filepath: './.eslintrc-auto-import.json',
          // 全局属性值
          globalsPropValue: true
        },
        resolvers: [ArcoResolver()]
      }),
      Components({
        // imports 指定组件所在目录，默认为 src/components
        dirs: ['src/components/', 'src/view/', 'src/layout/', 'src/views/**/components/'],
        // 需要去解析的文件
        include: [/\.vue$/, /\.vue\?vue/, /\.md$/],
        resolvers: [
          ArcoResolver({ sideEffect: true }),
          VueUseComponentsResolver(),
          VueUseDirectiveResolver(),
          IconsResolver({
            // icon自动引入的组件前缀 - 为了统一组件icon组件名称格式
            prefix: 'icon',
            customCollections: ['user', 'home']
          })
        ]
      }),
      // Icon 插件配置
      Icons({
        compiler: 'vue3',
        customCollections: {
          // user图标集，给svg文件设置 fill="currentColor" 属性，使图标的颜色具有适应性
          user: FileSystemIconLoader('src/assets/svg/user', svg =>
            svg.replace(/^<svg /, '<svg fill="currentColor" ')
          ),
          // home 模块图标集
          home: FileSystemIconLoader('src/assets/svg/home', svg =>
            svg.replace(/^<svg /, '<svg fill="currentColor" ')
          )
        },
        autoInstall: true
      }),
      // Unocss 插件配置
      Unocss({
        // 预设
        presets: [presetUno(), presetAttributify()],
        // 指令转换
        transformers: [transformerDirective()],
        // 自定义规则
        rules: [[/^bg-color-(\d+)$/, ([, color]) => ({ 'background-color': `#${color}` })]]
      })
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)) // 创建相对于当前模块 URL 的 ./src 路径的 URL 对象
      }
    }
  }
})
