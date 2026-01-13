import React, {useEffect, useState} from 'react'
import axios from 'axios'

export default function SummaryModal({open, onClose, data}){
  const [images, setImages] = useState(null)
  const [loading, setLoading] = useState(false)
  const [fullscreen, setFullscreen] = useState(false)
  useEffect(()=>{
    if(!open) return
    setImages(null)
    const rp = data?.report?.path
    if(!rp) return
    setLoading(true)
    axios.get(`/reports/visuals?path=${encodeURIComponent(rp)}`)
      .then(r=> setImages(r.data.images || []))
      .catch(()=> setImages([]))
      .finally(()=> setLoading(false))
  },[open, data])

  if(!open) return null

  const counts = data?.counts
  const rows = data?.rows || []
  const total = counts ? (Number(counts.MATCHED||0) + Number(counts.MISMATCH||0) + Number(counts.MISSING||0) + Number(counts.POSSIBLE_MATCH||0)) : 0
  function pct(n){
    if(!total) return '0%'
    return Math.round((Number(n||0) / total) * 100) + '%'
  }

  function toggleFullscreen(){
    const el = document.getElementById('summary-modal')
    if(!el) { setFullscreen(s=>!s); return }
    if(!document.fullscreenElement){
      el.requestFullscreen?.()
      setFullscreen(true)
    } else {
      document.exitFullscreen?.()
      setFullscreen(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div id="summary-modal" className={"modal" + (fullscreen? ' fullscreen' : '')} onClick={e=>e.stopPropagation()}>
        <div className="modal-header">
          <h3>Summary & Visuals</h3>
          <div style={{display:'flex',gap:8,alignItems:'center'}}>
            <button className="btn" onClick={toggleFullscreen} style={{padding:'6px 8px'}}>{fullscreen? 'Exit Full' : 'Full screen'}</button>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
        </div>
        <div className="modal-body">
          <div className="summary-grid">
            <div>
              <h4>Counts</h4>
              {counts ? (
                <div style={{lineHeight:1.6}}>
                  <div className="pct-row">MATCHED: <strong>{counts.MATCHED}</strong> <span className="text-muted">({pct(counts.MATCHED)})</span>
                    <div className="pct-bar"><div className="fill matched" style={{width:pct(counts.MATCHED)}}/></div>
                  </div>
                  <div className="pct-row">MISMATCH: <strong>{counts.MISMATCH}</strong> <span className="text-muted">({pct(counts.MISMATCH)})</span>
                    <div className="pct-bar"><div className="fill mismatch" style={{width:pct(counts.MISMATCH)}}/></div>
                  </div>
                  <div className="pct-row">MISSING: <strong>{counts.MISSING}</strong> <span className="text-muted">({pct(counts.MISSING)})</span>
                    <div className="pct-bar"><div className="fill missing" style={{width:pct(counts.MISSING)}}/></div>
                  </div>
                  <div className="pct-row">POSSIBLE_MATCH: <strong>{counts.POSSIBLE_MATCH}</strong> <span className="text-muted">({pct(counts.POSSIBLE_MATCH)})</span>
                    <div className="pct-bar"><div className="fill possible" style={{width:pct(counts.POSSIBLE_MATCH)}}/></div>
                  </div>
                </div>
              ) : <div className="text-muted">No summary yet</div>}
            </div>

            <div>
              <h4>Report</h4>
              {data?.report?.url ? <a className="btn" href={data.report.url} target="_blank" rel="noreferrer">Download report</a> : <div className="text-muted">No report</div>}
            </div>
          </div>

          <div style={{marginTop:12}}>
            <h4>Top rows</h4>
            <div className="rows-list">
              {rows.slice(0,10).map((r,i)=>(
                <div key={i} className="row-item">
                  <div style={{fontWeight:700}}>{r.field_key}</div>
                  <div className="text-muted">{r.status} • best: {r.best_match_key || '-'}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={{marginTop:12}}>
            <h4>Visuals</h4>
            {loading ? <div className="text-muted">Generating visuals...</div> : null}
            {images && images.length===0 && !loading ? <div className="text-muted">No visuals available</div> : null}
            <div className="visuals-grid">
              {images && images.map((u,i)=>(
                <img key={i} src={u} alt={`visual-${i}`} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
