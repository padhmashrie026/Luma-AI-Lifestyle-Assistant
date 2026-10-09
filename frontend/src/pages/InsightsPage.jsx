import { useEffect, useState } from 'react'
import Card from '../components/Card.jsx'
import Button from '../components/Button.jsx'
import SectionHeader from '../components/SectionHeader.jsx'
import { getInsights } from '../services/insightsService.js'

const countLabels = [
  ['wardrobe_items', 'Wardrobe items'], ['outfits', 'Outfits'], ['meals', 'Saved meals'],
  ['meal_plans', 'Meal plans'], ['daily_plans', 'Daily plans'], ['measurements', 'Measurements'],
]

function InsightsPage() {
  const [data, setData] = useState(null)
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try { setData(await getInsights({ start_date: startDate, end_date: endDate })) }
    catch (requestError) { setError(requestError.message) }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const isEmpty = data && Object.values(data.overview).every((count) => count === 0)
    && data.period.expense_count === 0 && data.period.tracking_days === 0
  const maxSpend = Math.max(1, ...(data?.spending_by_category || []).map((row) => Number(row.spent)))

  return <div className="insights-page">
    <section className="dashboard-welcome wardrobe-welcome"><div><p className="eyebrow">Your personal overview</p><h2 className="welcome-title">Insights</h2><p className="welcome-copy">A summary of records saved in your account.</p></div></section>
    <Card className="insights-filter"><form onSubmit={(event) => { event.preventDefault(); load() }}>
      <div><label htmlFor="insights-start">From</label><input id="insights-start" type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} /></div>
      <div><label htmlFor="insights-end">To</label><input id="insights-end" type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} /></div>
      <Button className="primary-button" type="submit" disabled={loading}>{loading ? 'Loading...' : 'Update insights'}</Button>
    </form></Card>
    {error && <div className="daily-error-box" role="alert"><span>{error}</span><Button className="secondary-button" onClick={load}>Try again</Button></div>}
    {loading && !data && <Card className="insights-empty"><p>Loading your insights...</p></Card>}
    {data && !error && <>
      {isEmpty && <Card className="insights-empty"><h3>Your insights will appear here</h3><p>There are no saved records in your account yet. Add items in your wardrobe, plans, meals, expenses, or daily tracking to see your personal activity.</p></Card>}
      <section className="insights-stat-grid" aria-label="Personal record counts">{countLabels.map(([key, label]) => <Card className="insights-stat" key={key}><span>{label}</span><strong>{data.overview[key]}</strong></Card>)}</section>
      <section className="insights-content-grid">
        <Card className="insights-card"><SectionHeader title="Activity summary" description={`${data.start_date} to ${data.end_date}`} />
          <div className="insights-period-grid"><div><span>Spending</span><strong>{data.currency_code} {data.period.expense_total}</strong><small>{data.period.expense_count} recorded expenses</small></div><div><span>Tracking days</span><strong>{data.period.tracking_days}</strong><small>{data.period.completed_tasks} tasks completed</small></div><div><span>Completion</span><strong>{data.period.completion_percentage}%</strong><small>{data.period.pending_tasks} tasks pending</small></div></div>
        </Card>
        <Card className="insights-card"><SectionHeader title="Spending by category" description="Expenses in the selected date range" />
          {data.spending_by_category.length ? <div className="insights-bars">{data.spending_by_category.map((row) => <div className="insights-bar-row" key={row.category_id}><div><span>{row.category}</span><strong>{data.currency_code} {row.spent}</strong></div><div className="insights-bar-track"><span style={{ width: `${Math.max(2, Number(row.spent) / maxSpend * 100)}%` }} /></div></div>)}</div> : <p className="insights-muted">No expenses in this date range.</p>}
        </Card>
        <Card className="insights-card insights-tracking"><SectionHeader title="Daily tracking" description="Completed tasks for each saved check-in" />
          {data.daily_progress.length ? data.daily_progress.map((row) => <div className="insights-day" key={row.date}><div><strong>{row.date}</strong><span>{row.completed_tasks}/4 tasks</span></div><div className="insights-bar-track"><span style={{ width: `${row.completion_percentage}%` }} /></div></div>) : <p className="insights-muted">No tracking entries in this date range.</p>}
        </Card>
      </section>
    </>}
  </div>
}

export default InsightsPage
