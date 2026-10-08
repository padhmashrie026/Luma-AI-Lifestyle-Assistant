import { apiRequest } from './apiClient.js'

const DAILY_PLAN_PATH = '/lifestyle/daily-plan/'
const TRACKING_PATH = '/tracking/'

function queryPath(path, values) {
  const query = new URLSearchParams()
  Object.entries(values).forEach(([key, value]) => {
    if (value !== '' && value !== undefined && value !== null) query.set(key, value)
  })
  const suffix = query.toString()
  return `${path}${suffix ? `?${suffix}` : ''}`
}

export function getDailyPlans(date) {
  return apiRequest(queryPath(DAILY_PLAN_PATH, {
    start_date: date, end_date: date,
  }))
}

export function getDailyPlan(id) {
  return apiRequest(`${DAILY_PLAN_PATH}${id}/`)
}

export function createDailyPlan(plan) {
  return apiRequest(DAILY_PLAN_PATH, { method: 'POST', body: JSON.stringify(plan) })
}

export function updateDailyPlan(id, plan) {
  return apiRequest(`${DAILY_PLAN_PATH}${id}/`, { method: 'PATCH', body: JSON.stringify(plan) })
}

export function deleteDailyPlan(id) {
  return apiRequest(`${DAILY_PLAN_PATH}${id}/`, { method: 'DELETE' })
}

export function getTrackingRecords(date) {
  return apiRequest(queryPath(TRACKING_PATH, {
    start_date: date, end_date: date,
  }))
}

export function createTrackingRecord(record) {
  return apiRequest(TRACKING_PATH, { method: 'POST', body: JSON.stringify(record) })
}

export function updateTrackingRecord(id, record) {
  return apiRequest(`${TRACKING_PATH}${id}/`, { method: 'PATCH', body: JSON.stringify(record) })
}

export function getTrackingSummary(date) {
  return apiRequest(queryPath(`${TRACKING_PATH}summary/`, {
    start_date: date,
    end_date: date,
  }))
}
