function SectionHeader({ title, description, action, id }) {
  return <div className="section-header"><div><h2 className="section-title" id={id}>{title}</h2>{description && <p className="section-description">{description}</p>}</div>{action}</div>
}

export default SectionHeader
