import { apiRequest } from './apiClient.js'

export async function calculateBodyShape(measurements) {
  return apiRequest('/body-shape/calculate/', {
    method: 'POST',
    body: JSON.stringify(measurements),
  })
}
