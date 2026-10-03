import { apiRequest } from './apiClient.js'

export function recommendOutfit(request) {
  return apiRequest('/outfits/recommend/', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}
