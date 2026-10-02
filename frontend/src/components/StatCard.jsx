import Card from './Card.jsx'
import Icon from './Icon.jsx'

function StatCard({ icon, title, action, children }) {
  return <Card className="summary-card"><div className="card-heading"><h2 className="card-heading-title"><span className="heading-icon"><Icon name={icon} size={16} /></span>{title}</h2>{action}</div><div className="summary-content">{children}</div></Card>
}

export default StatCard
