import { useState } from 'react'
import Button from '../components/Button.jsx'
import Card from '../components/Card.jsx'
import SectionHeader from '../components/SectionHeader.jsx'
import { recommendOutfit } from '../services/outfitService.js'

const occasions = [
  ['everyday', 'Everyday'], ['work', 'Work'], ['formal', 'Formal'], ['event', 'Event'], ['other', 'Other'],
]
const bodyShapes = [
  ['hourglass', 'Hourglass'], ['pear', 'Pear'], ['apple', 'Apple'],
  ['rectangle', 'Rectangle'], ['inverted_triangle', 'Inverted triangle'],
]
const recommendationSlots = [
  ['selected_one_piece', 'One-piece'],
  ['selected_top', 'Top'],
  ['selected_bottom', 'Bottom'],
  ['selected_outerwear', 'Outer layer'],
  ['selected_accessory', 'Accessory'],
]

function OutfitItem({ title, item }) {
  if (!item) return null
  const details = [item.category, item.color, item.brand, item.size_label].filter(Boolean)
  return <div className="outfit-piece">
    <span className="outfit-piece-label">{title}</span>
    <h4>{item.name}</h4>
    {details.length > 0 && <p>{details.join(' · ')}</p>}
    <span className="outfit-piece-status">{item.status}</span>
  </div>
}

function OutfitRecommendationPage() {
  const [profileId, setProfileId] = useState('')
  const [occasion, setOccasion] = useState('')
  const [bodyShape, setBodyShape] = useState('')
  const [errors, setErrors] = useState({})
  const [result, setResult] = useState(null)
  const [requestError, setRequestError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const submit = async (event) => {
    event.preventDefault()
    setResult(null)
    setRequestError('')
    const nextErrors = {}
    if (!profileId.trim()) nextErrors.profileId = 'Profile ID is required.'
    else if (!/^\d+$/.test(profileId.trim()) || Number(profileId) < 1) nextErrors.profileId = 'Enter a valid positive profile ID.'
    if (!occasion) nextErrors.occasion = 'Choose an occasion.'
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length) return

    const request = { profile_id: Number(profileId), occasion }
    if (bodyShape) request.body_shape = bodyShape
    setIsLoading(true)
    try {
      setResult(await recommendOutfit(request))
    } catch (error) {
      setRequestError(error.message)
    } finally {
      setIsLoading(false)
    }
  }

  const reset = () => {
    setProfileId('')
    setOccasion('')
    setBodyShape('')
    setErrors({})
    setResult(null)
    setRequestError('')
  }

  const recommendation = result?.recommendation
  const selectedPieces = recommendation
    ? recommendationSlots.filter(([key]) => recommendation[key])
    : []

  return <div className="outfit-page">
    <section className="dashboard-welcome outfit-welcome">
      <div><p className="eyebrow">From your wardrobe</p><h2 className="welcome-title">Outfit Recommendation</h2><p className="welcome-copy">Get a transparent, rule-based outfit suggestion using items you already have.</p></div>
    </section>

    <div className="outfit-layout">
      <Card className="outfit-request-card">
        <SectionHeader title="Set your preferences" description="Choose an occasion and optionally add a styling shape." />
        <form onSubmit={submit} noValidate>
          <div className="outfit-form-fields">
            <div className="outfit-field outfit-profile-field">
              <label htmlFor="outfit-profile-id">Profile ID <span>Required</span></label>
              <input id="outfit-profile-id" type="number" min="1" step="1" value={profileId} onChange={(event) => { setProfileId(event.target.value); setErrors((current) => ({ ...current, profileId: undefined })) }} aria-invalid={Boolean(errors.profileId)} aria-describedby={errors.profileId ? 'outfit-profile-error' : 'outfit-profile-help'} />
              {errors.profileId ? <small className="outfit-field-error" id="outfit-profile-error" role="alert">{errors.profileId}</small> : <small className="outfit-field-help" id="outfit-profile-help">Profile ID is used temporarily to find your wardrobe until sign-in is available.</small>}
            </div>
            <div className="outfit-field">
              <label htmlFor="outfit-occasion">Occasion <span>Required</span></label>
              <select id="outfit-occasion" value={occasion} onChange={(event) => { setOccasion(event.target.value); setErrors((current) => ({ ...current, occasion: undefined })) }} aria-invalid={Boolean(errors.occasion)} aria-describedby={errors.occasion ? 'outfit-occasion-error' : undefined}>
                <option value="">Choose an occasion</option>{occasions.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
              {errors.occasion && <small className="outfit-field-error" id="outfit-occasion-error" role="alert">{errors.occasion}</small>}
            </div>
            <div className="outfit-field outfit-profile-field">
              <label htmlFor="outfit-body-shape">Body shape <span>Optional</span></label>
              <select id="outfit-body-shape" value={bodyShape} onChange={(event) => setBodyShape(event.target.value)}>
                <option value="">Use saved shape, if available</option>{bodyShapes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
              <small className="outfit-field-help">This is approximate styling guidance. Leave blank to use the latest saved shape.</small>
            </div>
          </div>
          <p className="outfit-season-note">Season is not requested because wardrobe items do not currently store season information.</p>
          {requestError && <p className="outfit-request-error" role="alert">{requestError}</p>}
          <div className="form-actions">
            <Button type="submit" className="primary-button" disabled={isLoading}>{isLoading ? 'Finding a look…' : 'Recommend outfit'}</Button>
            <Button type="button" className="secondary-button" onClick={reset} disabled={isLoading}>Reset</Button>
          </div>
        </form>
      </Card>

      <section className="outfit-result-section" aria-live="polite" aria-busy={isLoading}>
        {isLoading ? <Card className="outfit-result-empty"><p>Checking your available wardrobe…</p></Card>
          : !result ? <Card className="outfit-result-empty"><span className="outfit-empty-mark" aria-hidden="true">✦</span><h3>Your outfit will appear here</h3><p>Choose an occasion to ask Django for a recommendation from your saved wardrobe.</p></Card>
          : !result.recommendation_available ? <Card className="outfit-insufficient-card"><span className="outfit-result-kicker">Wardrobe check</span><h3>There aren’t enough available pieces yet</h3><p>{result.message}</p>{result.missing_items?.length > 0 && <div className="missing-items"><span>Needed to complete a look</span><ul>{result.missing_items.map((item) => <li key={item}>{item}</li>)}</ul></div>}<p className="outfit-explanation">{result.explanation}</p></Card>
          : <Card className="outfit-result-card">
            <span className="outfit-result-kicker">Your suggestion</span>
            <h3>Ready for {occasions.find(([value]) => value === result.occasion)?.[1]?.toLowerCase() || result.occasion}</h3>
            <p className="outfit-result-message">{result.message}</p>
            <div className="outfit-pieces-grid">{selectedPieces.map(([key, title]) => <OutfitItem key={key} title={title} item={recommendation[key]} />)}</div>
            <div className="outfit-reasoning"><h4>Why this was suggested</h4><p>{result.explanation}</p></div>
            {result.body_shape && <p className="outfit-shape-note">Styling shape used: <strong>{bodyShapes.find(([value]) => value === result.body_shape)?.[1] || result.body_shape}</strong> · approximate styling guidance</p>}
            {!result.season_applied && <p className="outfit-season-note result-season-note">Season was not applied because the current wardrobe data does not include season.</p>}
          </Card>}
      </section>
    </div>
  </div>
}

export default OutfitRecommendationPage
