import { apiRequest } from './apiClient.js'

export function generateWeeklyMealPlan(request) {
  return apiRequest('/diet/plan/', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}
