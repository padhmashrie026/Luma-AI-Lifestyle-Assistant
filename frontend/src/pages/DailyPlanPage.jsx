import { useCallback, useEffect, useState } from 'react'
import Button from '../components/Button.jsx'
import Card from '../components/Card.jsx'
import SectionHeader from '../components/SectionHeader.jsx'
import { isValidISODate, localDateString } from '../utils/date.js'
import {
  createDailyPlan,
  createTrackingRecord,
  deleteDailyPlan,
  getDailyPlan,
  getDailyPlans,
  getTrackingRecords,
  getTrackingSummary,
  updateDailyPlan,
  updateTrackingRecord,
} from '../services/dailyPlanService.js'

const completionFields = [
  ['outfit_completed', 'Outfit'],
  ['meals_completed', 'Meals'],
  ['expenses_reviewed', 'Expense review'],
  ['daily_plan_completed', 'Daily plan'],
]
const emptyPlan = { plan_date: '', outfit: '', meal_plan: '', notes: '' }

function DailyPlanPage() {
  const [selectedDate, setSelectedDate] = useState(localDateString)
  const [plan, setPlan] = useState(null)
  const [tracking, setTracking] = useState(null)
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [formError, setFormError] = useState('')
  const [notice, setNotice] = useState('')
  const [formOpen, setFormOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(emptyPlan)
  const [saving, setSaving] = useState(false)
  const [updatingField, setUpdatingField] = useState('')

  const loadDay = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const [planResponse, trackingResponse, summaryResponse] = await Promise.all([
        getDailyPlans(selectedDate),
        getTrackingRecords(selectedDate),
        getTrackingSummary(selectedDate),
      ])
      if (!Array.isArray(planResponse) || !Array.isArray(trackingResponse)
        || !summaryResponse || typeof summaryResponse.completion_percentage !== 'number'
        || !Array.isArray(summaryResponse.daily_progress) || !summaryResponse.progress_by_field) {
        throw new Error('The server returned unexpected daily plan or tracking data. Please try again.')
      }
      const plans = planResponse
      const records = trackingResponse
      setPlan(plans.find((item) => item.plan_date === selectedDate) || null)
      setTracking(records.find((item) => item.track_date === selectedDate) || null)
      setSummary(summaryResponse)
    } catch (requestError) {
      setError(requestError.message)
    } finally { setLoading(false) }
  }, [selectedDate])

  useEffect(() => { loadDay() }, [loadDay])

  const openCreate = () => {
    setNotice(''); setFormError(''); setEditingId(null)
    setForm({ ...emptyPlan, plan_date: selectedDate })
    setFormOpen(true)
  }

  const openEdit = async () => {
    if (!plan) return
    setNotice(''); setFormError('')
    try {
      const detail = await getDailyPlan(plan.id)
      setEditingId(detail.id)
      setForm({
        plan_date: detail.plan_date,
        outfit: detail.outfit ? String(detail.outfit) : '',
        meal_plan: detail.meal_plan ? String(detail.meal_plan) : '',
        notes: detail.notes || '',
      })
      setFormOpen(true)
    } catch (requestError) { setError(requestError.message) }
  }

  const closeForm = () => {
    setFormOpen(false); setEditingId(null); setForm(emptyPlan); setFormError('')
  }

  const savePlan = async (event) => {
    event.preventDefault(); setFormError('')
    if (!isValidISODate(form.plan_date)) return setFormError('Choose a valid plan date.')
    for (const field of ['outfit', 'meal_plan']) {
      if (form[field] && (!/^\d+$/.test(form[field]) || !Number.isSafeInteger(Number(form[field])) || Number(form[field]) < 1)) return setFormError(`Enter a valid positive ${field === 'outfit' ? 'outfit' : 'meal plan'} ID, or leave it blank.`)
    }
    const payload = {
      plan_date: form.plan_date,
      outfit: form.outfit ? Number(form.outfit) : null,
      meal_plan: form.meal_plan ? Number(form.meal_plan) : null,
      notes: form.notes.trim(),
    }
    setSaving(true)
    try {
      if (editingId) { await updateDailyPlan(editingId, payload); setNotice('Daily plan updated.') }
      else { await createDailyPlan(payload); setNotice('Daily plan created.') }
      setSelectedDate(form.plan_date)
      closeForm()
    } catch (requestError) { setFormError(requestError.message) }
    finally { setSaving(false) }
  }

  const removePlan = async () => {
    if (!plan || !window.confirm(`Delete the daily plan for ${plan.plan_date}? This cannot be undone.`)) return
    setError(''); setNotice('')
    try { await deleteDailyPlan(plan.id); setNotice('Daily plan deleted.'); await loadDay() }
    catch (requestError) { setError(requestError.message) }
  }

  const toggleCompletion = async (field, checked) => {
    setUpdatingField(field); setError(''); setNotice('')
    try {
      if (tracking) {
        const updated = await updateTrackingRecord(tracking.id, { [field]: checked })
        setTracking(updated)
      } else {
        const newRecord = {
          daily_plan: plan?.id || null,
          track_date: selectedDate,
          outfit_completed: false, meals_completed: false,
          expenses_reviewed: false, daily_plan_completed: false,
          [field]: checked,
        }
        const created = await createTrackingRecord(newRecord)
        setTracking(created)
      }
      const updatedSummary = await getTrackingSummary(selectedDate)
      setSummary(updatedSummary)
      setNotice('Progress updated.')
    } catch (requestError) { setError(requestError.message) }
    finally { setUpdatingField('') }
  }

  const changeForm = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  const progress = summary?.completion_percentage ?? 0

  return <div className="daily-plan-page">
    <section className="dashboard-welcome wardrobe-welcome">
      <div><p className="eyebrow">A clear view of today</p><h2 className="welcome-title">Daily Plan &amp; Tracking</h2><p className="welcome-copy">Review the plan for a date and record progress on the available check-ins.</p></div>
      <Button className="primary-button" onClick={openCreate} disabled={Boolean(plan)}>＋ Create daily plan</Button>
    </section>
    {notice && <p className="daily-notice" role="status">{notice}</p>}
    <Card className="daily-scope-card"><div className="daily-scope-grid">
      <div><label htmlFor="daily-date">Plan date</label><input id="daily-date" type="date" value={selectedDate} onChange={(event) => setSelectedDate(event.target.value)} /></div>
    </div></Card>

    {formOpen && <Card className="daily-form-card"><SectionHeader title={editingId ? 'Edit daily plan' : 'Create daily plan'} description="Only fields supported by the Daily Plan API are shown." />
      <form onSubmit={savePlan} noValidate><div className="daily-form-grid">
        <div><label htmlFor="daily-form-date">Plan date <span>Required</span></label><input id="daily-form-date" name="plan_date" type="date" value={form.plan_date} onChange={changeForm} required /></div>
        <div><label htmlFor="daily-form-outfit">Outfit ID <span>Optional</span></label><input id="daily-form-outfit" name="outfit" type="number" min="1" step="1" value={form.outfit} onChange={changeForm} /><small>Enter an outfit ID from this profile.</small></div>
        <div><label htmlFor="daily-form-meal">Meal plan ID <span>Optional</span></label><input id="daily-form-meal" name="meal_plan" type="number" min="1" step="1" value={form.meal_plan} onChange={changeForm} /><small>The meal plan must belong to this profile and date.</small></div>
        <div className="daily-notes-field"><label htmlFor="daily-form-notes">Notes</label><textarea id="daily-form-notes" name="notes" maxLength="400" rows="3" value={form.notes} onChange={changeForm} /></div>
      </div>{formError && <p className="daily-error" role="alert">{formError}</p>}<div className="form-actions"><Button type="submit" className="primary-button" disabled={saving}>{saving ? 'Saving…' : editingId ? 'Save changes' : 'Create plan'}</Button><Button type="button" className="secondary-button" onClick={() => { setForm({ ...emptyPlan, plan_date: selectedDate }); setFormError('') }} disabled={saving}>Reset</Button><Button type="button" className="secondary-button" onClick={closeForm} disabled={saving}>Cancel</Button></div></form>
    </Card>}

    {error && <div className="daily-error-box" role="alert"><span>{error}</span><Button className="secondary-button" onClick={loadDay}>Try again</Button></div>}
    {loading ? <Card className="daily-loading" aria-live="polite">Loading the selected day…</Card> : !error && <div className="daily-content-grid">
      <div className="daily-main-column">
        <Card className="daily-plan-card"><SectionHeader title="Plan for this day" description={selectedDate} action={plan && <div className="daily-plan-actions"><Button className="secondary-button" onClick={openEdit}>Edit</Button><Button className="item-delete-button" onClick={removePlan}>Delete</Button></div>} />
          {plan ? <div className="daily-plan-details"><div className="daily-linked-items">
            <div className="daily-linked-item"><span className="daily-item-icon" aria-hidden="true">◈</span><span><strong>Outfit</strong><small>{plan.outfit ? `Linked outfit · ID ${plan.outfit}` : 'No outfit linked'}</small></span></div>
            <div className="daily-linked-item"><span className="daily-item-icon" aria-hidden="true">◷</span><span><strong>Meal plan</strong><small>{plan.meal_plan ? `Linked meal plan · ID ${plan.meal_plan}` : 'No meal plan linked'}</small></span></div>
          </div><div className="daily-plan-notes"><strong>Notes</strong><p>{plan.notes || 'No notes for this plan.'}</p></div></div> : <div className="daily-empty-inline"><h3>No plan for this date</h3><p>Create a plan with optional outfit and meal plan links, plus notes.</p><Button className="primary-button" onClick={openCreate}>Create daily plan</Button></div>}
        </Card>

        <Card className="daily-checkins-card"><SectionHeader title="Daily check-ins" description="Completion controls are saved to this date’s tracking record." />
          <div className="daily-checkin-list">{completionFields.map(([field, label]) => {
            const checked = Boolean(tracking?.[field])
            return <label className={`daily-checkin ${checked ? 'is-complete' : ''}`} key={field}>
              <input type="checkbox" checked={checked} disabled={Boolean(updatingField)} onChange={(event) => toggleCompletion(field, event.target.checked)} />
              <span className="daily-checkin-copy"><strong>{label}</strong><small>{checked ? 'Completed' : 'Pending'}</small></span>
              {updatingField === field && <span className="daily-checkin-saving" aria-live="polite">Saving…</span>}
            </label>
          })}</div>
          {tracking?.notes && <p className="daily-tracking-notes"><strong>Tracking notes:</strong> {tracking.notes}</p>}
        </Card>
      </div>

      <aside className="daily-progress-column" aria-label="Progress summary">
        <Card className="daily-progress-card"><SectionHeader title="Progress summary" description={summary ? `${summary.start_date} to ${summary.end_date}` : 'Selected date'} />
          {summary && <><div className="daily-progress-top"><strong>{summary.completion_percentage}%</strong><span>completion</span></div><div className="daily-progress-track" role="img" aria-label={`${summary.completion_percentage}% completion`}><span style={{ width: `${Math.min(100, Math.max(0, progress))}%` }} /></div>
            <dl className="daily-progress-counts"><div><dt>Completed tasks</dt><dd>{summary.completed_tasks}</dd></div><div><dt>Pending tasks</dt><dd>{summary.pending_tasks}</dd></div><div><dt>Tracking days</dt><dd>{summary.tracking_days}</dd></div></dl>
            <div className="daily-progress-fields"><h3>By check-in</h3>{completionFields.map(([field, label]) => { const metric = summary.progress_by_field?.[field]; return <div className="daily-progress-row" key={field}><span>{label}</span><strong>{metric ? `${metric.completed_days}/${metric.tracking_days} days` : '—'}</strong></div> })}</div>
          </>}
        </Card>
      </aside>
    </div>}
  </div>
}

export default DailyPlanPage
