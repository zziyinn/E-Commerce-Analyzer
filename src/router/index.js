/**
 * Vue Router 配置
 * 统一的路由管理，消除原型中的手动DOM操作路由切换
 */

import { createRouter, createWebHistory } from 'vue-router'

/**
 * 统一的懒加载工厂
 * 直接返回箭头函数，符合 Vue Router 推荐方式，避免警告
 */
const lazy = (loader) => loader

// 多语言路由前缀暂时停用；恢复方案见 docs/i18n-reenable.md
const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: lazy(() => import('@/views/Dashboard.vue')),
    meta: {
      title: 'Dashboard',
      icon: '📊'
    }
  },
  {
    path: '/search',
    name: 'Search',
    component: lazy(() => import('@/views/Search.vue')),
    meta: {
      title: 'Product Search',
      icon: '🔍'
    }
  },
  {
    path: '/products/:id',
    name: 'ProductDetail',
    component: lazy(() => import('@/views/ProductDetail.vue')),
    meta: {
      title: 'Product Details',
      icon: '📦'
    },
    props: true
  },
  {
    path: '/compare',
    name: 'Compare',
    component: lazy(() => import('@/views/Compare.vue')),
    meta: {
      title: 'Product Compare',
      icon: '⚖️'
    }
  },
  {
    path: '/watchlist',
    name: 'Watchlist',
    component: lazy(() => import('@/views/Watchlist.vue')),
    meta: {
      title: 'Watchlist',
      icon: '👁️'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: lazy(() => import('@/views/Settings.vue')),
    meta: {
      title: 'Settings',
      icon: '⚙️'
    }
  },
  {
    path: '/products',
    name: 'Products',
    component: lazy(() => import('@/views/Products.vue')),
    meta: { title: 'Product Management' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: lazy(() => import('@/views/NotFound.vue')),
    meta: { title: '404' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - Bestseller Analyzer`
  }

  next()
})

export default router
