import Icon from '../components/Icon.jsx'
import SectionHeader from '../components/SectionHeader.jsx'

const destinations = [
  { title: 'Body Shape', detail: 'Get approximate styling guidance from measurements.', icon: 'user', path: '/body-shape' },
  { title: 'Wardrobe', detail: 'Organize the clothing items saved to a profile.', icon: 'clothes', path: '/wardrobe' },
  { title: 'Outfit ideas', detail: 'Get a rule-based suggestion from available wardrobe items.', icon: 'sparkle', path: '/outfits' },
  { title: 'Diet Planner', detail: 'Preview a week using meals saved to a profile.', icon: 'leaf', path: '/diet' },
  { title: 'Expenses', detail: 'Record expenses and review returned totals.', icon: 'wallet', path: '/expenses' },
  { title: 'Daily Plan', detail: 'Plan a day and update its completion check-ins.', icon: 'calendar', path: '/daily-plan' },
  { title: 'Profile', detail: 'Review and update stored profile details.', icon: 'user', path: '/profile' },
  { title: 'Settings', detail: 'Update the currency preference stored for a profile.', icon: 'settings', path: '/settings' },
]

function Dashboard({ onNavigate }) {
  return <>
    <section className="dashboard-welcome" aria-labelledby="welcome-title">
      <div><p className="eyebrow">Workspace</p><h2 className="welcome-title" id="welcome-title">Your lifestyle workspace</h2><p className="welcome-copy">Choose a tool to plan, organize, or review information stored in the application.</p></div>
    </section>
    <section className="section-block" aria-labelledby="workspace-tools-title">
      <SectionHeader id="workspace-tools-title" title="Your tools" description="Each module uses the information returned by its Django API." />
      <div className="actions-grid">{destinations.map((item) => <a className="action-button" key={item.path} href={item.path} onClick={(event) => { event.preventDefault(); onNavigate(item.path) }}>
        <span className="action-icon"><Icon name={item.icon} size={17} /></span>
        <span><span className="action-title">{item.title}</span><span className="action-description">{item.detail}</span></span>
      </a>)}</div>
    </section>
  </>
}

export default Dashboard
