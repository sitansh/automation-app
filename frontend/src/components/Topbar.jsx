import React from 'react'

export default function Topbar({showSidebar=true, onToggleSidebar=()=>{}}){
  return (
    <div style={{display:'flex',alignItems:'center',width:'100%',gap:12}}>
      <div>
        <button className="toggle-btn" onClick={onToggleSidebar} aria-pressed={!showSidebar} title={showSidebar? 'Hide sidebar' : 'Show sidebar'}>
          {showSidebar? '⟨' : '⟩'}
        </button>
      </div>
      <div style={{display:'flex',alignItems:'center',gap:12}}>
        {showSidebar && <div style={{fontWeight:700}}>QAPilot</div>}
      </div>
      <div style={{flex:1}} />
    </div>
  )
}
