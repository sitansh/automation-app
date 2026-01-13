import React from 'react'

export default function Sidebar({showSummary = false, onToggleSummary = () => {}, summaryData = null, currentView = 'comparator', onSelectView = () => {}}){
  const counts = summaryData?.counts
  const report = summaryData?.report
  return (
    <div>
      <div className="brand" aria-hidden="true" style={{height:0,overflow:'hidden'}}></div>
      <div className="menu">
        <button className={"btn " + (currentView === 'comparator' ? 'active' : '')} onClick={()=>onSelectView('comparator')}>Comparator</button>
        <button className={"btn " + (currentView === 'reports' ? 'active' : '')} onClick={()=>onSelectView('reports')}>Reports</button>
        <button className={"btn " + (currentView === 'settings' ? 'active' : '')} onClick={()=>onSelectView('settings')}>Settings</button>
      </div>

      <div style={{marginTop:12,fontSize:13}}>
        <button className="btn" onClick={onToggleSummary} style={{padding:'6px 8px'}}>Show summary</button>
      </div>

      {showSummary && (
        <div style={{marginTop:12}}>
          <div className="card">
            <h4 style={{margin:0}}>Summary</h4>
            {counts ? (
              <div style={{marginTop:8,lineHeight:1.6}}>
                <div>MATCHED: <strong>{counts.MATCHED}</strong></div>
                <div>MISMATCH: <strong>{counts.MISMATCH}</strong></div>
                <div>MISSING: <strong>{counts.MISSING}</strong></div>
                <div>POSSIBLE_MATCH: <strong>{counts.POSSIBLE_MATCH}</strong></div>
                <div style={{marginTop:8}}>
                  {report?.url ? (
                    <a className="btn" href={report.url} target="_blank" rel="noreferrer">Download report</a>
                  ) : null}
                </div>
              </div>
            ) : (
              <div style={{marginTop:8,color:'var(--muted)'}}>No data yet</div>
            )}
          </div>
        </div>
      )}

      <div style={{marginTop:20,fontSize:13,color:'var(--muted)'}}>v0.1</div>
    </div>
  )
}
