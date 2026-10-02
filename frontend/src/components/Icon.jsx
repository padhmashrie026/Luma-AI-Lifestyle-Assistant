const iconPaths = {
  grid: <><rect x="3.5" y="3.5" width="7" height="7" rx="1.5" /><rect x="13.5" y="3.5" width="7" height="7" rx="1.5" /><rect x="3.5" y="13.5" width="7" height="7" rx="1.5" /><rect x="13.5" y="13.5" width="7" height="7" rx="1.5" /></>,
  clothes: <><path d="m8 4-4 2-2 4 4 2v8h12v-8l4-2-2-4-4-2c-.5 2-1.8 3-4 3S8.5 6 8 4Z" /><path d="M8 4c.5 2 1.8 3 4 3s3.5-1 4-3" /></>,
  leaf: <><path d="M20.5 3.5C12 3.5 5 5 5 12c0 4 2.5 6.5 6 6.5 6.5 0 8-8.5 9.5-15Z" /><path d="M3.5 21c3-5 7-8 12-10" /></>,
  wallet: <><rect x="3" y="5" width="18" height="15" rx="2.5" /><path d="M3 8V6a2 2 0 0 1 2-2h13" /><path d="M21 11h-5a2 2 0 0 0 0 4h5" /><path d="M16 13h.01" /></>,
  calendar: <><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M16 3v4M8 3v4M3 10h18" /><path d="m9 15 2 2 4-4" /></>,
  chart: <><path d="M4 19V5M4 19h17" /><path d="m7 15 4-4 3 2 6-7" /><path d="M17 6h3v3" /></>,
  user: <><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></>,
  settings: <><circle cx="12" cy="12" r="3" /><path d="M12 3v2m0 14v2m9-9h-2M5 12H3m15.4-6.4-1.4 1.4M7 17l-1.4 1.4m12.8 0L17 17M7 7 5.6 5.6" /><circle cx="12" cy="12" r="8" /></>,
  search: <><circle cx="10.8" cy="10.8" r="6.8" /><path d="m16 16 4.5 4.5" /></>,
  bell: <><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9ZM10 21h4" /></>,
  menu: <><path d="M4 6h16M4 12h16M4 18h16" /></>,
  arrow: <><path d="M5 12h14M13 6l6 6-6 6" /></>,
  plus: <><path d="M12 5v14M5 12h14" /></>,
  coffee: <><path d="M5 8h12v7a4 4 0 0 1-4 4H9a4 4 0 0 1-4-4V8ZM17 10h1a2.5 2.5 0 0 1 0 5h-2" /><path d="M8 4c-1 1 1 1.5 0 2.5M12 4c-1 1 1 1.5 0 2.5" /></>,
  check: <><path d="m5 12 4 4L19 6" /></>,
  sparkle: <><path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z" /><path d="m19 16 .8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16Z" /></>,
}

function Icon({ name, size = 18, strokeWidth = 1.7 }) {
  return <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">{iconPaths[name] ?? iconPaths.sparkle}</svg>
}

export default Icon
