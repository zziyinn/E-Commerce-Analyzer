<template>
  <div class="product-card">
    <div class="card-header">
      <img 
        v-img-fallback
        :src="product.imageUrl || placeholderImage" 
        :alt="product.title" 
        class="card-image"
        :class="{ 'clickable': hasProductUrl }"
        @click.stop="handleImageClick"
        @keyup.enter.stop="handleImageClick"
        tabindex="0"
        role="button"
        :aria-label="`View ${product.title} on Amazon`"
      >
      <div class="card-title">
        {{ product.title }}
      </div>
    </div>

    <div class="card-body">
      <div class="info-row">
        <span class="label">Price</span>
        <span class="value">{{ formatPrice(product.price) }}</span>
      </div>
      <div class="info-row">
        <span class="label">Profit Margin</span>
        <span
          class="value"
          :class="getMarginRateClass(product)"
        >
          {{ formatMarginRate(product) }}
          <span
            v-if="getMarginRateLabel(product)"
            class="margin-label"
          >{{ getMarginRateLabel(product) }}</span>
          <span
            v-if="getMarginRateIcon(product)"
            class="margin-icon"
          >{{ getMarginRateIcon(product) }}</span>
        </span>
      </div>
      <div class="info-row">
        <span class="label">Competition</span>
        <span
          class="value"
          :class="getCompetitionClass(product.competitionLevel)"
        >
          {{ getCompetitionText(product.competitionLevel) }}
          <span
            v-if="getCompetitionLabel(product.competitionLevel)"
            class="competition-label"
          >{{ getCompetitionLabel(product.competitionLevel) }}</span>
        </span>
      </div>
    </div>

    <div class="card-footer">
      <button
        class="btn btn-secondary"
        :disabled="isInCompare"
        @click="$emit('add-to-compare', product.id)"
      >
        {{ isInCompare ? 'In Compare' : 'Add to Compare' }}
      </button>
      <button
        class="btn btn-primary"
        :disabled="isWatched"
        @click="$emit('add-to-watch', product.id)"
      >
        {{ isWatched ? 'Unwatch' : 'Add to Watchlist' }}
      </button>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useSettingsStore } from '@/stores/useSettingsStore'
import { useI18n } from 'vue-i18n'

/**
 * ProductCard
 * 产品卡片组件：展示产品概要信息与操作按钮。
 * 函数职责：
 * - formatPrice: 按当前货币格式化价格
 * - getCompetitionClass: 返回竞争度样式类
 * - getCompetitionText: 返回竞争度的国际化文本
 * - placeholderImage: 统一占位图，使用 $t 国际化文本，避免语言条件判断
 */
export default {
  name: 'ProductCard',
  props: {
    product: { type: Object, required: true },
    isWatched: { type: Boolean, default: false },
    isInCompare: { type: Boolean, default: false }
  },
  emits: ['view-details', 'add-to-compare', 'add-to-watch'],
  setup(props) {
    const settingsStore = useSettingsStore()
    const { t } = useI18n()
    const placeholderImage = computed(() => {
      const label = t('common.product')
      return `https://via.placeholder.com/200x200?text=${encodeURIComponent(label)}`
    })

    /**
     * 格式化价格
     * @param {number} price - 原始价格
     * @returns {string} - 已格式化价格字符串
     */
    function formatPrice(price) {
      return settingsStore.formatCurrency(price)
    }

    function formatMarginRate(product) {
      if (product?.formattedMarginRate) {
        return product.formattedMarginRate
      }
      if (typeof product?.marginRate === 'number') {
        return `${product.marginRate}%`
      }
      return '--'
    }

    /**
     * 获取利润率样式类
     * @param {Object} product - 商品对象
     * @returns {string} - 样式类名
     */
    function getMarginRateClass(product) {
      if (!product || typeof product.marginRate !== 'number') return ''
      
      if (product.marginRate > 30) return 'margin-high'
      if (product.marginRate >= 15) return 'margin-medium'
      return 'margin-low'
    }
    
    /**
     * 获取利润率标签文本
     * @param {Object} product - 商品对象
     * @returns {string} - 标签文本
     */
    function getMarginRateLabel(product) {
      if (!product || typeof product.marginRate !== 'number') return ''
      
      if (product.marginRate > 30) return 'Bestseller Potential'
      if (product.marginRate >= 15) return 'Good Potential'
      return ''
    }
    
    /**
     * 获取利润率图标
     * @param {Object} product - 商品对象
     * @returns {string} - 图标
     */
    function getMarginRateIcon(product) {
      if (!product || typeof product.marginRate !== 'number') return ''
      
      if (product.marginRate > 30) return '🔥'
      return ''
    }

    /**
     * 获取竞争度样式类
     * @param {string} level - 竞争度：low|medium|high
     * @returns {string} - 样式类名
     */
    function getCompetitionClass(level) {
      switch (level) {
        case 'low': return 'competition-low'
        case 'medium': return 'competition-medium'
        case 'high': return 'competition-high'
        default: return ''
      }
    }

    /**
     * 获取竞争度国际化文本
     * @param {string} level - 竞争度：low|medium|high
     * @returns {string} - 国际化文本
     */
    function getCompetitionText(level) {
      const map = {
        low: t('productDetail.competition.low'),
        medium: t('productDetail.competition.medium'),
        high: t('productDetail.competition.high')
      }
      return map[level] || t('common.none')
    }
    
    /**
     * 获取竞争度标签文本
     * @param {string} level - 竞争度：low|medium|high
     * @returns {string} - 标签文本
     */
    function getCompetitionLabel(level) {
      switch (level) {
        case 'low': return 'Blue Ocean'
        case 'medium': return 'Competitive'
        case 'high': return 'Red Ocean'
        default: return ''
      }
    }

    /**
     * 检查是否有产品 URL
     */
    const hasProductUrl = computed(() => {
      const product = props.product
      return !!(product.productUrl || product.url || product.product_url)
    })

    /**
     * 获取产品 URL
     * 确保获取完整的 URL
     */
    const getProductUrl = () => {
      const product = props.product
      // 按优先级检查所有可能的字段
      const url = product.productUrl || product.url || product.product_url || null
      if (url) {
        // 确保 URL 是完整的字符串
        const fullUrl = String(url).trim()
        // 如果 URL 不完整（可能是被截断的），尝试修复
        if (fullUrl && !fullUrl.startsWith('http')) {
          console.warn('[ProductCard] Invalid URL format:', fullUrl)
          return null
        }
        return fullUrl
      }
      return null
    }

    /**
     * 处理图片点击，跳转到亚马逊链接
     */
    function handleImageClick(event) {
      event?.stopPropagation() // 阻止事件冒泡
      const url = getProductUrl()
      console.log('[ProductCard] Image clicked, product:', props.product)
      console.log('[ProductCard] All product keys:', Object.keys(props.product))
      console.log('[ProductCard] URL fields:', {
        productUrl: props.product.productUrl,
        url: props.product.url,
        product_url: props.product.product_url
      })
      console.log('[ProductCard] Final URL:', url)
      if (url) {
        window.open(url, '_blank', 'noopener,noreferrer')
      } else {
        console.warn('[ProductCard] No product URL found for product:', props.product.id)
        // 尝试从产品名称构建亚马逊搜索链接
        const searchUrl = `https://www.amazon.com/s?k=${encodeURIComponent(props.product.title || props.product.name || '')}`
        console.log('[ProductCard] Opening Amazon search instead:', searchUrl)
        window.open(searchUrl, '_blank', 'noopener,noreferrer')
      }
    }

    return {
      placeholderImage,
      formatPrice,
      formatMarginRate,
      getMarginRateClass,
      getMarginRateLabel,
      getMarginRateIcon,
      getCompetitionClass,
      getCompetitionText,
      getCompetitionLabel,
      hasProductUrl,
      handleImageClick
    }
  }
}
</script>

<style scoped>
.product-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 16px;
  transition: box-shadow 0.2s ease;
}

.product-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.card-image {
  width: 100%;
  height: 200px;
  min-height: 200px;
  border-radius: 8px;
  overflow: hidden;
  align-self: center;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  display: block;
  background-color: #f9fafb; /* 添加背景色，避免透明区域显示异常 */
  padding: 8px; /* 添加内边距，让图片有呼吸空间 */
  box-sizing: border-box;
}

.card-image.clickable {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card-image.clickable:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-image.clickable:focus {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

.product-image {
  width: 100%;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
  align-self: center;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background-color: #f9fafb; /* 添加背景色 */
}

.image-placeholder {
  width: 100%;
  height: 100%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 12px;
  font-weight: 500;
}

.product-info {
  text-align: center;
}

.product-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.4;
}

.product-meta {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}

.platform,
.category {
  font-size: 12px;
  color: #6b7280;
}

.product-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.tag {
  background: #eef2ff;
  color: #3730a3;
  padding: 2px 6px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 500;
  display: inline-block;
  white-space: nowrap;
  flex-shrink: 0;
}

.tag-more {
  background: #f3f4f6;
  color: #6b7280;
}

.product-metrics {
  display: flex;
  justify-content: space-around;
  gap: 16px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.metric {
  text-align: center;
  min-width: 60px;
}

.metric .label {
  display: block;
  font-size: 11px;
  color: #6b7280;
  margin-bottom: 2px;
}

.metric .value {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.margin-low {
  color: #6b7280 !important;
}

.margin-medium {
  color: #10b981 !important;
}

.margin-high {
  color: #f97316 !important;
}

.margin-label {
  display: inline-block;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  background-color: rgba(16, 185, 129, 0.1);
  color: #10b981;
  margin-left: 6px;
  vertical-align: middle;
}

.margin-high .margin-label {
  background-color: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.margin-icon {
  margin-left: 4px;
  font-size: 14px;
  vertical-align: middle;
}

.competition-low {
  color: #10b981 !important;
}

.competition-medium {
  color: #f59e0b !important;
}

.competition-high {
  color: #ef4444 !important;
}

.competition-label {
  display: inline-block;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 6px;
  vertical-align: middle;
}

.competition-low .competition-label {
  background-color: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.competition-medium .competition-label {
  background-color: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.competition-high .competition-label {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.product-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.btn {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-ghost {
  background: transparent;
  color: #374151;
  border: 1px solid #e5e7eb;
}

.btn-ghost:hover:not(:disabled) {
  background: #f9fafb;
}

.btn-primary {
  background: #2563eb;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .product-card {
    padding: 12px;
  }
  
  .product-image {
    height: 150px;
  }
  
  .product-title {
    font-size: 14px;
  }
  
  .product-metrics {
    padding: 8px;
    gap: 8px;
  }
}
</style>
