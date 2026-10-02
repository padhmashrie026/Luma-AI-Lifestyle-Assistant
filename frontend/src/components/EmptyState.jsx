import Icon from './Icon.jsx'

function EmptyState({ title, description, icon = 'sparkle' }) {
  return <div className="empty-state"><span className="empty-symbol"><Icon name={icon} size={19} /></span><div><h3 className="empty-title">{title}</h3><p className="empty-copy">{description}</p></div></div>
}

export default EmptyState
