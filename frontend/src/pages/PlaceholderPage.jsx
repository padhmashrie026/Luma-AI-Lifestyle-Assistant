import Card from '../components/Card.jsx'
import Icon from '../components/Icon.jsx'

function PlaceholderPage({ title }) {
  return <Card className="placeholder-panel"><div className="placeholder-content"><span className="placeholder-icon"><Icon name="sparkle" size={23} /></span><span className="eyebrow">Coming soon</span><h2>{title} is under development</h2><p>This area is part of the Lifestyle Assistant foundation. Its tools and content will be added in a future project step.</p><span className="demo-badge"><span className="demo-dot" />No personal data yet</span></div></Card>
}

export default PlaceholderPage
