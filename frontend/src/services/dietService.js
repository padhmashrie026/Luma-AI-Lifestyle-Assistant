import { apiRequest } from './apiClient.js'

const MEALS_PATH = '/diet/meals/'
const SAVED_PLAN_PATH = '/diet/plan/saved/'

export function getMeals() { return apiRequest(MEALS_PATH) }
export function getMeal(id) { return apiRequest(`${MEALS_PATH}${id}/`) }
export function createMeal(meal) { return apiRequest(MEALS_PATH, { method: 'POST', body: JSON.stringify(meal) }) }
export function updateMeal(id, meal) { return apiRequest(`${MEALS_PATH}${id}/`, { method: 'PATCH', body: JSON.stringify(meal) }) }
export function deleteMeal(id) { return apiRequest(`${MEALS_PATH}${id}/`, { method: 'DELETE' }) }

export function getSavedWeeklyMealPlan() { return apiRequest(SAVED_PLAN_PATH) }
export function saveWeeklyMealPlan(plan) {
  return apiRequest(SAVED_PLAN_PATH, { method: 'POST', body: JSON.stringify(plan) })
}

export function generateWeeklyMealPlan(request) {
  return apiRequest('/diet/plan/', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}
