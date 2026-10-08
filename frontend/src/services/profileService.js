import { apiRequest } from './apiClient.js'

export function getProfile() {
  return apiRequest('/profile/')
}

export function updateProfile(fields) {
  return apiRequest('/profile/', { method: 'PATCH', body: JSON.stringify(fields) })
}

export function getSettings() {
  return apiRequest('/settings/')
}

export function updateSettings(fields) {
  return apiRequest('/settings/', { method: 'PATCH', body: JSON.stringify(fields) })
}
