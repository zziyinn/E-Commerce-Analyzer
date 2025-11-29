/**
 * 数据分析服务
 * 提供各种数据分析功能的 API 调用
 */

// 生产环境：如果 VITE_API_BASE_URL 为空或未设置，使用相对路径（前后端同域）
// 开发环境：使用 localhost:8000
// 注意：import.meta.env.PROD 在 Vite 构建时会被替换为布尔值
// 使用多种方式检测生产环境，确保可靠性
const isProduction = import.meta.env.MODE === 'production' || 
                     import.meta.env.PROD === true ||
                     (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1')

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (isProduction ? '' : 'http://localhost:8000')

export class AnalysisService {
  /**
   * 获取价格趋势分析
   * @param {Object} options - 分析选项
   * @param {number} options.days - 分析天数（默认30）
   * @param {string} options.category - 分类筛选
   * @param {string} options.platform - 平台筛选
   */
  async getPriceTrend(options = {}) {
    const { days = 30, category, platform } = options
    const params = new URLSearchParams()
    params.append('days', days)
    if (category) params.append('category', category)
    if (platform) params.append('platform', platform)
    
    const response = await fetch(`${API_BASE_URL}/api/analysis/price-trend?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to get price trend: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * 获取分类分布分析
   * @param {string} platform - 平台筛选（可选）
   */
  async getCategoryDistribution(platform = null) {
    const params = new URLSearchParams()
    if (platform) params.append('platform', platform)
    
    const url = `${API_BASE_URL}/api/analysis/category-distribution${params.toString() ? '?' + params : ''}`
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`Failed to get category distribution: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * 获取数据质量分析
   */
  async getDataQuality() {
    const response = await fetch(`${API_BASE_URL}/api/analysis/data-quality`)
    if (!response.ok) {
      throw new Error(`Failed to get data quality: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * 获取竞争度分析
   * @param {Object} options - 分析选项
   * @param {string} options.category - 分类筛选
   * @param {string} options.platform - 平台筛选
   */
  async getCompetitionAnalysis(options = {}) {
    const { category, platform } = options
    const params = new URLSearchParams()
    if (category) params.append('category', category)
    if (platform) params.append('platform', platform)
    
    const url = `${API_BASE_URL}/api/analysis/competition-analysis${params.toString() ? '?' + params : ''}`
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`Failed to get competition analysis: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * 获取批次分析
   * @param {number} limit - 分析最近 N 个批次（默认10）
   */
  async getBatchAnalysis(limit = 10) {
    const response = await fetch(`${API_BASE_URL}/api/analysis/batch-analysis?limit=${limit}`)
    if (!response.ok) {
      throw new Error(`Failed to get batch analysis: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * 获取平台对比分析
   */
  async getPlatformComparison() {
    const response = await fetch(`${API_BASE_URL}/api/analysis/platform-comparison`)
    if (!response.ok) {
      throw new Error(`Failed to get platform comparison: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * 获取 AI 分析洞察
   * @param {Object} options - 分析选项
   * @param {number} options.limit - 分析的产品数量限制（默认50）
   * @param {string} options.category - 分类筛选
   * @param {string} options.platform - 平台筛选
   */
  async getAIInsights(options = {}) {
    const { limit = 50, category, platform } = options
    const params = new URLSearchParams()
    params.append('limit', limit)
    if (category) params.append('category', category)
    if (platform) params.append('platform', platform)
    
    const response = await fetch(`${API_BASE_URL}/api/analysis/ai-insights?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to get AI insights: ${response.statusText}`)
    }
    return response.json()
  }
}

// 单例模式
export const analysisService = new AnalysisService()

