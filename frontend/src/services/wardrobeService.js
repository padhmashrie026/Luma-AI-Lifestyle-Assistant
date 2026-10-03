import { apiRequest } from './apiClient.js'

const ITEMS_PATH = '/wardrobe/items/'

export function getWardrobeItems(filters = {}) {
  const query = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value) query.set(key, value)
  })
  const suffix = query.toString()
  return apiRequest(`${ITEMS_PATH}${suffix ? `?${suffix}` : ''}`)
}

export function getWardrobeItem(id) {
  return apiRequest(`${ITEMS_PATH}${id}/`)
}

export function createWardrobeItem(item) {
  return apiRequest(ITEMS_PATH, { method: 'POST', body: JSON.stringify(item) })
}

export function updateWardrobeItem(id, item) {
  return apiRequest(`${ITEMS_PATH}${id}/`, { method: 'PATCH', body: JSON.stringify(item) })
}

export function deleteWardrobeItem(id) {
  return apiRequest(`${ITEMS_PATH}${id}/`, { method: 'DELETE' })
}
