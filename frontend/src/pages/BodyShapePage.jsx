import { useState } from 'react'
import Button from '../components/Button.jsx'
import Card from '../components/Card.jsx'
import SectionHeader from '../components/SectionHeader.jsx'
import { calculateBodyShape } from '../services/bodyShapeService.js'

const fields = [
  { name: 'shoulder', label: 'Shoulder' },
  { name: 'bust', label: 'Bust' },
  { name: 'waist', label: 'Waist' },
  { name: 'hip', label: 'Hip' },
]

function BodyShapePage() {
  const [measurements, setMeasurements] = useState({ shoulder: '', bust: '', waist: '', hip: '' })
  const [errors, setErrors] = useState({})
  const [result, setResult] = useState(null)
  const [requestError, setRequestError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const validate = () => {
    const nextErrors = {}
    fields.forEach(({ name, label }) => {
      const rawValue = measurements[name].trim()
      if (!rawValue) nextErrors[name] = `${label} measurement is required.`
      else if (!/^(?:\d+\.?\d*|\.\d+)$/.test(rawValue) || !Number.isFinite(Number(rawValue))) {
        nextErrors[name] = 'Enter a valid number.'
      } else if (Number(rawValue) <= 0) nextErrors[name] = 'Enter a value greater than zero.'
    })
    return nextErrors
  }

  const handleChange = (event) => {
    const { name, value } = event.target
    setMeasurements((current) => ({ ...current, [name]: value }))
    setErrors((current) => ({ ...current, [name]: undefined }))
    setRequestError('')
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setResult(null)
    setRequestError('')
    const nextErrors = validate()
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length) return

    setIsLoading(true)
    try {
      const response = await calculateBodyShape(
        Object.fromEntries(Object.entries(measurements).map(([key, value]) => [key, Number(value)])),
      )
      if (!response || typeof response.estimated_body_shape !== 'string' || typeof response.styling_suggestion !== 'string') {
        throw new Error('The server returned an unexpected result. Please try again.')
      }
      setResult(response)
    } catch (error) {
      setRequestError(error.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setMeasurements({ shoulder: '', bust: '', waist: '', hip: '' })
    setErrors({})
    setResult(null)
    setRequestError('')
  }

  return <div className="body-shape-page">
    <section className="dashboard-welcome body-shape-welcome">
      <div><p className="eyebrow">Personal styling</p><h2 className="welcome-title">Body Shape Calculator</h2><p className="welcome-copy">Add your measurements for a simple, proportion-based styling guide.</p></div>
    </section>
    <div className="body-shape-layout">
      <Card className="measurement-card">
        <SectionHeader title="Your measurements" description="Measure around the fullest area. Enter each value in centimetres." />
        <form onSubmit={handleSubmit} noValidate>
          <div className="measurement-fields">
            {fields.map(({ name, label }) => <div className="measurement-field" key={name}>
              <label htmlFor={`measurement-${name}`}>{label} <span>(cm)</span></label>
              <div className="measurement-input-wrap">
                <input id={`measurement-${name}`} name={name} type="number" inputMode="decimal" min="0.01" step="any" value={measurements[name]} onChange={handleChange} aria-invalid={Boolean(errors[name])} aria-describedby={errors[name] ? `error-${name}` : undefined} placeholder="e.g. 90" />
                <span aria-hidden="true">cm</span>
              </div>
              {errors[name] && <p className="field-error" id={`error-${name}`} role="alert">{errors[name]}</p>}
            </div>)}
          </div>
          <p className="measurement-help">Use a flexible tape measure and keep it level. Measurements are used only for this calculation.</p>
          {requestError && <p className="request-error" role="alert">{requestError}</p>}
          <div className="form-actions">
            <Button type="submit" className="primary-button" disabled={isLoading}>{isLoading ? 'Calculating…' : 'Calculate shape'}</Button>
            <Button type="button" className="secondary-button" onClick={handleReset} disabled={isLoading}>Reset</Button>
          </div>
        </form>
      </Card>
      <Card className={`result-card ${result ? 'has-result' : ''}`} aria-live="polite">
        {result ? <div className="result-content">
          <p className="eyebrow">Your result</p>
          <h3 className="result-shape">{result.estimated_body_shape.replaceAll('_', ' ')}</h3>
          <div className="result-detail"><h4>Styling guidance</h4><p>{result.styling_suggestion}</p></div>
          {result.approximate_size_guidance && <div className="result-detail"><h4>Approximate size guidance</h4><p>{result.approximate_size_guidance}</p></div>}
          <p className="result-note">{result.note || 'This result is approximate styling guidance, not a medical diagnosis.'}</p>
        </div> : <div className="result-empty"><span className="result-empty-mark" aria-hidden="true">✦</span><h3>Your result will appear here</h3><p>Enter all four measurements to receive a styling guide based on the Django calculator.</p></div>}
      </Card>
    </div>
  </div>
}

export default BodyShapePage
