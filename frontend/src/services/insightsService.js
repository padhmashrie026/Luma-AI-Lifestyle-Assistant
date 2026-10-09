import { apiRequest } from './apiClient.js'

export function getInsights(filters = {}) {
  const params = new URLSearchParams()
  if (filters.start_date) params.set('start_date', filters.start_date)
  if (filters.end_date) params.set('end_date', filters.end_date)
  const query = params.toString()
  return apiRequest(`/insights/${query ? `?${query}` : ''}`)
}
