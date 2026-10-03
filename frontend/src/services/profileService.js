import { apiRequest } from './apiClient.js'

function scopedPath(path, profileId) {
  const query = new URLSearchParams({ profile_id: profileId })
  return `${path}?${query}`
}

export function getProfile(profileId) {
  return apiRequest(scopedPath('/profile/', profileId))
}

export function updateProfile(profileId, fields) {
  return apiRequest(scopedPath('/profile/', profileId), {
    method: 'PATCH',
    body: JSON.stringify(fields),
  })
}

export function getSettings(profileId) {
  return apiRequest(scopedPath('/settings/', profileId))
}

export function updateSettings(profileId, fields) {
  return apiRequest(scopedPath('/settings/', profileId), {
    method: 'PATCH',
    body: JSON.stringify(fields),
  })
}
