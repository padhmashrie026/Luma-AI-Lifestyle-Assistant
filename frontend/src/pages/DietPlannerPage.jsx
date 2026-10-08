import { useState } from 'react'
import Button from '../components/Button.jsx'
import Card from '../components/Card.jsx'
import SectionHeader from '../components/SectionHeader.jsx'
import { isValidISODate } from '../utils/date.js'
import { generateWeeklyMealPlan } from '../services/dietService.js'

const mealSlots = [
  ['breakfast', 'Breakfast'], ['lunch', 'Lunch'], ['dinner', 'Dinner'], ['snack', 'Snack'],
]
const nutritionLabels = {
  protein: 'Protein match',
  healthy_fats: 'Healthy-fat match',
  fibre_vegetables: 'Fibre / vegetable match',
}

function formatDate(value, options = { weekday: 'long', month: 'short', day: 'numeric' }) {
  return new Intl.DateTimeFormat(undefined, options).format(new Date(`${value}T00:00:00`))
}

function MealCard({ title, meal }) {
  return <section className="diet-meal-card" aria-label={title}>
    <span className="diet-meal-slot">{title}</span>
    {meal ? <>
      <h4>{meal.name}</h4>
      {meal.description && <p className="diet-meal-description">{meal.description}</p>}
      {meal.nutrition_focus?.length > 0 && <div className="nutrition-tags" aria-label="Ingredient-name planning hints">{meal.nutrition_focus.map((focus) => <span className="nutrition-tag" key={focus}>{nutritionLabels[focus] || focus}</span>)}</div>}
      {meal.preparation_guidance && <p className="diet-meal-prep">{meal.preparation_guidance}</p>}
      {meal.ingredients?.length > 0 && <details className="diet-ingredients"><summary>Saved ingredients ({meal.ingredients.length})</summary><ul>{meal.ingredients.map((ingredient, index) => <li key={`${ingredient.name}-${index}`}><span>{ingredient.name}</span><span>{ingredient.quantity === null ? 'Quantity not recorded' : `${ingredient.quantity}${ingredient.unit ? ` ${ingredient.unit}` : ''}`}</span></li>)}</ul></details>}
    </> : <p className="diet-slot-empty">No snack suggestion was returned for this day.</p>}
  </section>
}

function DietPlannerPage() {
  const [weekStart, setWeekStart] = useState('')
  const [errors, setErrors] = useState({})
  const [plan, setPlan] = useState(null)
  const [requestError, setRequestError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const submit = async (event) => {
    event.preventDefault()
    setPlan(null)
    setRequestError('')
    const nextErrors = {}
    if (!weekStart) nextErrors.weekStart = 'Choose the first date of the week.'
    else if (!isValidISODate(weekStart)) {
      nextErrors.weekStart = 'Enter a valid date.'
    }
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length) return

    setIsLoading(true)
    try {
      const response = await generateWeeklyMealPlan({ week_start: weekStart })
      if (!response || typeof response.plan_available !== 'boolean' || !Array.isArray(response.weekly_plan) || !Array.isArray(response.grocery_list)) {
        throw new Error('The server returned an unexpected meal plan. Please try again.')
      }
      setPlan(response)
    } catch (error) {
      setRequestError(error.message)
    } finally {
      setIsLoading(false)
    }
  }

  const reset = () => {
    setWeekStart('')
    setErrors({})
    setPlan(null)
    setRequestError('')
  }

  const allMeals = plan?.weekly_plan?.flatMap((day) => Object.entries(day.meals || {})
    .filter(([, meal]) => Boolean(meal))
    .map(([slot, meal]) => ({ slot, meal, date: day.date }))) || []

  return <div className="diet-page">
    <section className="dashboard-welcome diet-welcome">
      <div><p className="eyebrow">A week at a time</p><h2 className="welcome-title">Diet Planner</h2><p className="welcome-copy">Build a simple weekly meal plan from meals already saved to your profile.</p></div>
    </section>

    <Card className="diet-request-card">
      <SectionHeader title="Plan your week" description="Choose a starting date for your seven-day preview." />
      <form className="diet-request-form" onSubmit={submit} noValidate>
        <div className="diet-field">
          <label htmlFor="diet-week-start">Week starting <span>Required</span></label>
          <input id="diet-week-start" type="date" value={weekStart} onChange={(event) => { setWeekStart(event.target.value); setErrors((current) => ({ ...current, weekStart: undefined })) }} aria-invalid={Boolean(errors.weekStart)} aria-describedby={errors.weekStart ? 'diet-date-error' : 'diet-date-help'} />
          {errors.weekStart ? <small className="diet-field-error" id="diet-date-error" role="alert">{errors.weekStart}</small> : <small className="diet-field-help" id="diet-date-help">The plan covers this date and the following six days.</small>}
        </div>
        <div className="diet-request-actions">
          <Button type="submit" className="primary-button" disabled={isLoading}>{isLoading ? 'Generating plan…' : 'Generate weekly plan'}</Button>
          <Button type="button" className="secondary-button" onClick={reset} disabled={isLoading}>Reset</Button>
        </div>
      </form>
      {requestError && <p className="diet-request-error" role="alert">{requestError}</p>}
      <p className="diet-disclaimer">General meal-planning suggestions only. Ingredient-name tags are broad hints, not nutrition analysis or medical advice.</p>
    </Card>

    <section className="diet-plan-section" aria-live="polite" aria-busy={isLoading}>
      {!plan && !isLoading && !requestError && <Card className="diet-empty-state"><span className="diet-empty-mark" aria-hidden="true">▤</span><h3>Your weekly plan will appear here</h3><p>Submit the form to build a plan from meals saved to your account.</p></Card>}
      {isLoading && <Card className="diet-empty-state"><p>Building your week from saved meals…</p></Card>}
      {plan && !plan.plan_available && <><Card className="diet-unavailable-card" role="status"><span className="diet-result-kicker">Plan unavailable</span><h3>{plan.meals_empty ? 'No meals saved yet' : 'Some meal types are missing'}</h3><p>{plan.meals_empty ? 'Your account has no saved meals to plan from yet. Add meals to your diet data and try again.' : plan.explanation}</p>{!plan.meals_empty && plan.missing_meal_types?.length > 0 && <div className="diet-missing-slots"><span>Needed meal types</span><ul>{plan.missing_meal_types.map((slot) => <li key={slot}>{slot}</li>)}</ul></div>}</Card>{plan.budget && <Card className="diet-budget-card diet-unavailable-budget"><SectionHeader title="Budget information" description="Budget estimates are not supported by stored meal data." /><p>{plan.budget.reason}</p></Card>}</>}
      {plan?.plan_available && <>
        <div className="diet-plan-heading"><div><p className="eyebrow">Weekly preview</p><h3>{formatDate(plan.week_start)} – {formatDate(plan.week_end)}</h3></div><span className="diet-preview-badge">{plan.saved ? 'Saved plan' : 'Preview · not saved'}</span></div>

        {plan.nutrition_note && <p className="diet-nutrition-note">{plan.nutrition_note}</p>}

        <section className="diet-days-grid" aria-label="Meals by day">{plan.weekly_plan.map((day) => <Card className="diet-day-card" key={day.date}>
          <h3>{formatDate(day.date)}</h3>
          <div className="diet-day-meals">{mealSlots.map(([slot, label]) => <MealCard key={slot} title={label} meal={day.meals?.[slot] || null} />)}</div>
        </Card>)}</section>

        <div className="diet-support-grid">
          <Card className="diet-grocery-card"><SectionHeader title="Grocery list" description="Ingredients aggregated from the planned meals." />
            {plan.grocery_list?.length > 0 ? <ul className="diet-grocery-list">{plan.grocery_list.map((item, index) => <li key={`${item.ingredient}-${item.unit}-${index}`}><span className="grocery-item-name">{item.ingredient}<small>{item.planned_occurrences} planned uses</small></span><strong>{item.quantity === null ? 'Quantity not recorded' : `${item.quantity}${item.unit ? ` ${item.unit}` : ''}`}</strong></li>)}</ul> : <p className="diet-no-groceries">No stored ingredients were returned for this plan.</p>}
          </Card>
          <Card className="diet-budget-card"><SectionHeader title="Budget information" description="Shown only as returned by the planner." />
            {plan.budget ? <><div className="diet-budget-values"><div><span>Estimated daily</span><strong>{plan.budget.estimated_daily ?? 'Not available'}</strong></div><div><span>Estimated weekly</span><strong>{plan.budget.estimated_weekly ?? 'Not available'}</strong></div></div><p>{plan.budget.reason}</p></> : <p>No budget information was returned.</p>}
          </Card>
        </div>

        <Card className="diet-preparation-card"><SectionHeader title="Meal preparation guidance" description={plan.preparation_note || 'Guidance returned for meals in this plan.'} />
          {allMeals.length > 0 ? <ul>{allMeals.map(({ slot, meal, date }, index) => <li key={`${date}-${slot}-${meal.id}-${index}`}><span><strong>{formatDate(date, { weekday: 'short', month: 'short', day: 'numeric' })} · {meal.name}</strong><small>{mealSlots.find(([key]) => key === slot)?.[1]}</small></span><p>{meal.preparation_guidance || 'No preparation guidance was returned.'}</p></li>)}</ul> : <p>No meal-preparation guidance was returned.</p>}
        </Card>
      </>}
    </section>
  </div>
}

export default DietPlannerPage
