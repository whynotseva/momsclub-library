/**
 * Утилиты для Mom's Club Library
 */

export interface LinkTypeInfo {
  type: string
  icon: string
  label: string
  color: string
}

/**
 * Определяет тип ссылки по URL
 */
export const getLinkType = (url: string): LinkTypeInfo => {
  if (!url) return { type: 'none', icon: '🔗', label: 'Нет ссылки', color: 'text-gray-400' }
  if (url.includes('notion.so') || url.includes('notion.site')) 
    return { type: 'notion', icon: '📝', label: 'Notion', color: 'text-blue-600' }
  if (url.includes('t.me') || url.includes('telegram')) 
    return { type: 'telegram', icon: '💬', label: 'Telegram', color: 'text-purple-600' }
  if (url.includes('youtube.com') || url.includes('youtu.be')) 
    return { type: 'youtube', icon: '▶️', label: 'YouTube', color: 'text-red-600' }
  if (url.includes('instagram.com')) 
    return { type: 'instagram', icon: '📸', label: 'Instagram', color: 'text-pink-600' }
  return { type: 'link', icon: '🌐', label: 'Ссылка', color: 'text-gray-600' }
}
