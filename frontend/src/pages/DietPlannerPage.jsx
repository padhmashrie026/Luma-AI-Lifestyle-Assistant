import { useCallback, useEffect, useState } from 'react'
import Button from '../components/Button.jsx'
import Card from '../components/Card.jsx'
import SectionHeader from '../components/SectionHeader.jsx'
import { isValidISODate } from '../utils/date.js'
import { createMeal, deleteMeal, generateWeeklyMealPlan, getMeals, getSavedWeeklyMealPlan, saveWeeklyMealPlan, updateMeal } from '../services/dietService.js'

const mealSlots = [
  ['breakfast', 'Breakfast'], ['lunch', 'Lunch'], ['dinner', 'Dinner'], ['snack', 'Snack'],
]
const nutritionLabels = {
  protein: 'Protein match',
  healthy_fats: 'Healthy-fat match',
  fibre_vegetables: 'Fibre / vegetable match',
}
const mealTypes = [['breakfast', 'Breakfast'], ['lunch', 'Lunch'], ['dinner', 'Dinner'], ['snack', 'Snack'], ['other', 'Other']]
const blankMeal = { name: '', meal_type: 'other', description: '', preparation_minutes: '', servings: '1', ingredients: [] }

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
  const [meals, setMeals] = useState([])
  const [mealsLoading, setMealsLoading] = useState(true)
  const [mealsError, setMealsError] = useState('')
  const [mealForm, setMealForm] = useState(blankMeal)
  const [editingMeal, setEditingMeal] = useState(null)
  const [mealSaving, setMealSaving] = useState(false)
  const [mealNotice, setMealNotice] = useState('')
  const [isSavingPlan, setIsSavingPlan] = useState(false)
  const [saveNotice, setSaveNotice] = useState('')
  const [saveError, setSaveError] = useState('')
  const loadMeals = useCallback(async () => {
    setMealsLoading(true); setMealsError('')
    try { const data = await getMeals(); if (!Array.isArray(data)) throw new Error('Unexpected meals response.'); setMeals(data) }
    catch (error) { setMealsError(error.message) } finally { setMealsLoading(false) }
  }, [])
  useEffect(() => { loadMeals() }, [loadMeals])
  const [weekStart, setWeekStart] = useState('')
  const [errors, setErrors] = useState({})
  const [plan, setPlan] = useState(null)
  const [requestError, setRequestError] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let active = true
    getSavedWeeklyMealPlan().then((savedPlan) => {
      if (!active) return
      if (savedPlan?.plan_available) {
        setPlan(savedPlan)
        setWeekStart(savedPlan.week_start)
      }
    }).catch((error) => {
      if (active) setRequestError(`Could not load your saved plan. ${error.message}`)
    }).finally(() => { if (active) setIsLoading(false) })
    return () => { active = false }
  }, [])

  const submit = async (event) => {
    event.preventDefault()
    setPlan(null)
    setRequestError('')
    setSaveNotice('')
    setSaveError('')
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
    setSaveNotice('')
    setSaveError('')
  }

  const savePlan = async () => {
    if (!plan?.plan_available || plan.saved || isSavingPlan) return
    setIsSavingPlan(true)
    setSaveError('')
    setSaveNotice('')
    try {
      const saved = await saveWeeklyMealPlan({
        week_start: plan.week_start,
        weekly_plan: plan.weekly_plan.map((day) => ({
          date: day.date,
          meals: Object.fromEntries(['breakfast', 'lunch', 'dinner', 'snack'].map((slot) => [slot, day.meals?.[slot]?.id ?? null])),
        })),
      })
      setPlan(saved)
      setSaveNotice('Your weekly meal plan has been saved.')
    } catch (error) {
      setSaveError(error.message)
    } finally {
      setIsSavingPlan(false)
    }
  }

  const allMeals = plan?.weekly_plan?.flatMap((day) => Object.entries(day.meals || {})
    .filter(([, meal]) => Boolean(meal))
    .map(([slot, meal]) => ({ slot, meal, date: day.date }))) || []

  const saveMeal = async (event) => {
    event.preventDefault()
    if (!mealForm.name.trim()) return
    setMealSaving(true); setMealNotice('')
    const payload = { ...mealForm, name: mealForm.name.trim(), preparation_minutes: mealForm.preparation_minutes === '' ? null : Number(mealForm.preparation_minutes), servings: Number(mealForm.servings), ingredients: mealForm.ingredients.filter((item) => item.name.trim()) }
    try {
      if (editingMeal) await updateMeal(editingMeal, payload); else await createMeal(payload)
      setMealForm(blankMeal); setEditingMeal(null); setMealNotice(editingMeal ? 'Meal updated.' : 'Meal added.'); await loadMeals()
    } catch (error) { setMealsError(error.message) } finally { setMealSaving(false) }
  }
  const editMeal = (meal) => { setEditingMeal(meal.id); setMealForm({ name: meal.name, meal_type: meal.meal_type, description: meal.description || '', preparation_minutes: meal.preparation_minutes ?? '', servings: String(meal.servings), ingredients: meal.ingredients || [] }) }
  const removeMeal = async (meal) => {
    if (!window.confirm(`Delete “${meal.name}”? This cannot be undone.`)) return
    try { await deleteMeal(meal.id); setMealNotice('Meal deleted.'); await loadMeals() } catch (error) { setMealsError(error.message) }
  }

  return <div className="diet-page">
    <section className="dashboard-welcome diet-welcome">
      <div><p className="eyebrow">A week at a time</p><h2 className="welcome-title">Diet Planner</h2><p className="welcome-copy">Build a simple weekly meal plan from meals already saved to your profile.</p></div>
    </section>

    <Card className="diet-meals-card">
      <SectionHeader title="Your saved meals" description={mealsLoading ? 'Loading meals…' : `${meals.length} saved ${meals.length === 1 ? 'meal' : 'meals'}`} />
      {mealNotice && <p className="diet-notice" role="status">{mealNotice}</p>}
      {mealsError && <p className="diet-request-error" role="alert">{mealsError}</p>}
      <form className="diet-meal-form" onSubmit={saveMeal}>
        <h3>{editingMeal ? 'Edit meal' : 'Add a meal'}</h3>
        <div className="diet-meal-form-grid">
          <label>Meal name <span>Required</span><input required maxLength="120" value={mealForm.name} onChange={(e) => setMealForm({ ...mealForm, name: e.target.value })} /></label>
          <label>Meal type<select value={mealForm.meal_type} onChange={(e) => setMealForm({ ...mealForm, meal_type: e.target.value })}>{mealTypes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
          <label>Description<input maxLength="300" value={mealForm.description} onChange={(e) => setMealForm({ ...mealForm, description: e.target.value })} /></label>
          <label>Preparation minutes<input type="number" min="0" max="1440" value={mealForm.preparation_minutes} onChange={(e) => setMealForm({ ...mealForm, preparation_minutes: e.target.value })} /></label>
          <label>Servings<input type="number" min="1" max="100" required value={mealForm.servings} onChange={(e) => setMealForm({ ...mealForm, servings: e.target.value })} /></label>
        </div>
        <p className="diet-field-help">Ingredients, quantity and unit can be recorded below. Nutrition values are not part of saved meal data.</p>
        <div className="diet-ingredient-editor">{mealForm.ingredients.map((item, index) => <div className="diet-ingredient-row" key={index}><input aria-label="Ingredient name" placeholder="Ingredient name" value={item.name} onChange={(e) => setMealForm({ ...mealForm, ingredients: mealForm.ingredients.map((x, i) => i === index ? { ...x, name: e.target.value } : x) })} /><input aria-label="Quantity" type="number" min="0.01" step="0.01" placeholder="Quantity" value={item.quantity ?? ''} onChange={(e) => setMealForm({ ...mealForm, ingredients: mealForm.ingredients.map((x, i) => i === index ? { ...x, quantity: e.target.value || null } : x) })} /><input aria-label="Unit" maxLength="24" placeholder="Unit" value={item.unit || ''} onChange={(e) => setMealForm({ ...mealForm, ingredients: mealForm.ingredients.map((x, i) => i === index ? { ...x, unit: e.target.value } : x) })} /><Button type="button" className="secondary-button" onClick={() => setMealForm({ ...mealForm, ingredients: mealForm.ingredients.filter((_, i) => i !== index) })}>Remove</Button></div>)}</div>
        <div className="form-actions"><Button type="button" className="secondary-button" onClick={() => setMealForm({ ...mealForm, ingredients: [...mealForm.ingredients, { name: '', quantity: null, unit: '' }] })}>Add ingredient</Button><Button type="submit" className="primary-button" disabled={mealSaving}>{mealSaving ? 'Saving…' : editingMeal ? 'Save changes' : 'Add meal'}</Button>{editingMeal && <Button type="button" className="secondary-button" onClick={() => { setEditingMeal(null); setMealForm(blankMeal) }}>Cancel</Button>}</div>
      </form>
      {mealsLoading ? <p>Loading your saved meals…</p> : meals.length === 0 ? <p className="diet-field-help">No meals saved yet. Add one above; a complete weekly plan needs a breakfast, lunch and dinner.</p> : <div className="diet-saved-meals">{meals.map((meal) => <article className="diet-saved-meal" key={meal.id}><div><span className="diet-meal-slot">{mealTypes.find(([value]) => value === meal.meal_type)?.[1] || meal.meal_type}</span><h4>{meal.name}</h4><p>{meal.description || 'No description saved.'}</p><small>{meal.servings} servings{meal.preparation_minutes !== null ? ` · ${meal.preparation_minutes} minutes` : ''}</small></div><div className="form-actions"><Button className="secondary-button" onClick={() => editMeal(meal)}>Edit</Button><Button className="secondary-button" onClick={() => removeMeal(meal)}>Delete</Button></div></article>)}</div>}
    </Card>

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
        <div className="diet-plan-heading"><div><p className="eyebrow">{plan.saved ? 'Saved weekly plan' : 'Weekly preview'}</p><h3>{formatDate(plan.week_start)} – {formatDate(plan.week_end)}</h3></div><span className="diet-preview-badge">{plan.saved ? 'Saved plan' : 'Preview · not saved'}</span></div>
        {!plan.saved && <div className="diet-save-plan-actions"><Button type="button" className="primary-button" onClick={savePlan} disabled={isSavingPlan}>{isSavingPlan ? 'Saving plan…' : 'Save Weekly Plan'}</Button></div>}
        {saveNotice && <p className="diet-notice" role="status">{saveNotice}</p>}
        {saveError && <p className="diet-request-error" role="alert">{saveError}</p>}

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
