import Card from '../components/Card.jsx'
import EmptyState from '../components/EmptyState.jsx'
import Icon from '../components/Icon.jsx'
import SectionHeader from '../components/SectionHeader.jsx'
import StatCard from '../components/StatCard.jsx'

function Dashboard() {
  const actions = [
    { title: 'Get outfit ideas', detail: 'Build a look from your wardrobe', icon: 'clothes', path: '/outfits' },
    { title: 'Plan your week', detail: 'Build a meal plan', icon: 'leaf', path: '/diet' },
    { title: 'Log spending', detail: 'Keep your budget close', icon: 'wallet', path: '/expenses' },
    { title: 'View daily plan', detail: 'See your routine', icon: 'calendar', path: '/daily-plan' },
  ]

  return <>
    <section className="dashboard-welcome" aria-labelledby="welcome-title"><div><p className="eyebrow">{new Intl.DateTimeFormat('en', { weekday: 'long', month: 'long', day: 'numeric' }).format(new Date())}</p><h2 className="welcome-title" id="welcome-title">A little more balance, Jamie.</h2><p className="welcome-copy">Here’s a calm snapshot of what’s on your day.</p></div><span className="demo-badge"><span className="demo-dot" />Demo preview · sample information</span></section>
    <section className="overview-grid" aria-label="Today's overview">
      <StatCard icon="clothes" title="Today's outfit" action={<a className="text-link" href="/wardrobe">Open wardrobe <Icon name="arrow" size={12} /></a>}><p className="summary-primary">Easy layers</p><p className="summary-detail">A relaxed look for a day in the city.</p><span className="small-tag">Outfit preview</span></StatCard>
      <StatCard icon="leaf" title="Today's meals" action={<a className="text-link" href="/diet">View plan <Icon name="arrow" size={12} /></a>}><p className="summary-primary">A simple, balanced day</p><p className="summary-detail">Breakfast, lunch and dinner are ready to plan.</p><span className="small-tag">Meal plan preview</span></StatCard>
      <StatCard icon="wallet" title="Today's spending" action={<a className="text-link" href="/expenses">View expenses <Icon name="arrow" size={12} /></a>}><p className="summary-primary">$24.50 <span className="summary-detail">sample total</span></p><p className="summary-detail">Example entry: lunch and coffee</p><span className="small-tag">Demo amount</span></StatCard>
      <StatCard icon="chart" title="Budget overview" action={<a className="text-link" href="/expenses">Budget details <Icon name="arrow" size={12} /></a>}><p className="summary-primary">Monthly spending plan</p><div className="budget-progress"><div className="budget-meta"><span>Sample progress</span><strong>$620 of $1,000</strong></div><div className="progress-track" role="img" aria-label="Demo budget progress: 62 percent"><div className="progress-fill" /></div><div className="budget-foot"><span>Demo budget</span><span>62% shown for preview</span></div></div></StatCard>
    </section>
    <section className="section-block" aria-labelledby="quick-actions-title"><SectionHeader id="quick-actions-title" title="Quick actions" description="Pick up where you want to focus today." /><div className="actions-grid">{actions.map((action) => <a className="action-button" key={action.title} href={action.path} aria-label={`${action.title}, coming soon`}><span className="action-icon"><Icon name={action.icon} size={17} /></span><span><span className="action-title">{action.title}</span><span className="action-description">{action.detail}</span></span><span className="visually-hidden">This shortcut will be available when the module is implemented.</span></a>)}</div></section>
    <section className="section-block"><SectionHeader title="Weekly overview" description="A simple view of your routines across the week." action={<span className="small-tag">Preview only</span>} /><Card className="weekly-card"><div className="weekly-placeholder"><EmptyState icon="chart" title="Your weekly view will grow with you" description="Once you start using your planner, this space can bring your routines together." /><div className="week-days" aria-label="Decorative weekly placeholder, not user activity" role="img">{['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, index) => <div className={`week-day ${index === 3 ? 'is-demo' : ''}`} key={`${day}-${index}`} aria-hidden="true"><span className={`week-bar ${index === 3 ? 'demo' : ''}`} /><span>{day}</span></div>)}</div></div></Card></section>
  </>
}

export default Dashboard
