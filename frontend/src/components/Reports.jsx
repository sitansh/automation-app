import React, {useEffect, useState, useRef} from 'react'
import axios from 'axios'

export default function Reports(){
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(false)
  const [imgs, setImgs] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [selected, setSelected] = useState(null)
  const [analysisOpen, setAnalysisOpen] = useState(false)
  const [analysisText, setAnalysisText] = useState(null)
  const [analysisStructured, setAnalysisStructured] = useState(null)
  const [analysisLoading, setAnalysisLoading] = useState(false)
  const visualsModalRef = useRef(null)
  const analysisModalRef = useRef(null)
  const [visualsFullscreen, setVisualsFullscreen] = useState(false)
  const [analysisFullscreen, setAnalysisFullscreen] = useState(false)

  useEffect(()=>{
    function onChange(){
      const el = document.fullscreenElement
      setVisualsFullscreen(el === visualsModalRef.current)
      setAnalysisFullscreen(el === analysisModalRef.current)
    }
    document.addEventListener('fullscreenchange', onChange)
    return ()=> document.removeEventListener('fullscreenchange', onChange)
  },[])

  useEffect(()=>{
    loadReports()
  },[])

  async function loadReports(){
    setLoading(true)
    try{
      const res = await axios.get('/reports')
      setReports(res.data || [])
    }catch(e){
      console.error(e)
    }finally{setLoading(false)}
  }

  async function viewVisuals(r){
    try{
      const res = await axios.get('/reports/visuals', {params:{path: r.path}})
      setImgs(res.data.images || [])
      setSelected(r)
      setModalOpen(true)
    }catch(e){
      console.error(e)
      alert('Failed to load visuals')
    }
  }

  async function analyzeReport(r){
    setAnalysisLoading(true)
    setSelected(r)
    try{
      const form = new FormData()
      form.append('path', r.path)
      const res = await axios.post('/reports/analysis', form, {timeout: 120000})
      if(res.data?.analysis){
        setAnalysisText(res.data.analysis)
        setAnalysisStructured(res.data.structured || null)
        setAnalysisOpen(true)
      }else if(res.data?.error){
        alert('Analysis failed: ' + res.data.error)
      }else{
        alert('Analysis failed: unknown response')
      }
    }catch(e){
      console.error(e)
      const resp = e?.response?.data
      if(resp && resp.error){
        alert('Analysis failed: ' + resp.error)
      } else {
        alert('Analysis request failed')
      }
    }finally{
      setAnalysisLoading(false)
    }
  }

  async function deleteReport(r){
    if(!confirm(`Delete ${r.name}?`)) return
    try{
      const form = new FormData()
      form.append('path', r.path)
      const res = await axios.post('/reports/delete', form)
      if(res.data?.ok){
        loadReports()
      }else{
        alert('Delete failed')
      }
    }catch(e){
      console.error(e)
      alert('Delete failed')
    }
  }

  return (
    <div>
      <div className="card">
        <h4 style={{margin:0}}>Reports</h4>
        <div style={{marginTop:8}}>
          {loading ? <div className="text-muted">Loading...</div> : (
            reports.length === 0 ? <div className="text-muted">No reports available</div> : (
              <div style={{display:'flex',flexDirection:'column',gap:8}}>
                {reports.map(r => (
                  <div key={r.path} style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:8,borderRadius:6,background:'rgba(255,255,255,0.01)'}}>
                    <div style={{flex:1}}>
                      <div style={{fontWeight:700}}>{r.name}</div>
                      <div style={{fontSize:12,color:'var(--muted)'}}>{new Date(r.modified).toLocaleString()} • {r.size} bytes</div>
                    </div>
                    <div style={{display:'flex',gap:8}}>
                      <a className="btn" href={`/download?path=${encodeURIComponent(r.path)}`} target="_blank" rel="noreferrer">Download</a>
                      <button className="btn" onClick={()=>viewVisuals(r)}>Visuals</button>
                      <button className="btn" onClick={()=>analyzeReport(r)} title="Request full-length analysis via Generative AI">Full length report</button>
                      <button className="btn" onClick={()=>deleteReport(r)} style={{background:'#7f1d1d',color:'#fff'}}>Delete</button>
                    </div>
                  </div>
                ))}
              </div>
            )
          )}
        </div>
      </div>

      {modalOpen && (
        <div className="modal-overlay" onClick={()=>{setModalOpen(false); setImgs(null)}}>
          <div ref={visualsModalRef} className={"modal " + (visualsFullscreen ? 'fullscreen' : '')} onClick={(e)=>e.stopPropagation()} style={{maxWidth:1000}}>
            <div className="modal-header">
              <div style={{fontWeight:700}}>{selected?.name} — Visuals</div>
              <div>
                <button className="btn" onClick={async ()=>{
                    try{
                      if(!visualsFullscreen){
                        await visualsModalRef.current.requestFullscreen()
                      } else {
                        await document.exitFullscreen()
                      }
                    }catch(e){console.error(e)}
                }}>{visualsFullscreen ? 'Exit fullscreen' : 'Fullscreen'}</button>
                <button className="close-btn" onClick={()=>{setModalOpen(false); setImgs(null)}}>✕</button>
              </div>
            </div>
            <div className="modal-body">
              {(!imgs || imgs.length===0) ? <div className="text-muted">No visuals available</div> : (
                <div className="visuals-grid">
                  {imgs.map(u => (<img key={u} src={u} alt="visual"/>))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {analysisOpen && (
        <div className="modal-overlay" onClick={()=>{setAnalysisOpen(false); setAnalysisText(null)}}>
          <div ref={analysisModalRef} className={"modal " + (analysisFullscreen ? 'fullscreen' : '')} onClick={(e)=>e.stopPropagation()} style={{maxWidth:1000}}>
            <div className="modal-header">
              <div style={{fontWeight:700}}>{selected?.name} — Full Analysis</div>
              <div>
                <button className="btn" onClick={async ()=>{
                    try{
                      if(!analysisFullscreen){
                        await analysisModalRef.current.requestFullscreen()
                      } else {
                        await document.exitFullscreen()
                      }
                    }catch(e){console.error(e)}
                }}>{analysisFullscreen ? 'Exit fullscreen' : 'Fullscreen'}</button>
                <button className="close-btn" onClick={()=>{setAnalysisOpen(false); setAnalysisText(null)}}>✕</button>
              </div>
            </div>
            <div className="modal-body">
              {analysisLoading ? <div className="text-muted">Generating analysis…</div> : (
                analysisText ? (
                  <div>
                    <div style={{marginBottom:8, display:'flex', gap:8, alignItems:'center'}}>
                      <button className="btn" onClick={()=>{navigator.clipboard?.writeText(analysisText); alert('copied')}}>Copy analysis</button>
                      {analysisStructured && (
                        <button className="btn" onClick={()=>{navigator.clipboard?.writeText(JSON.stringify(analysisStructured, null, 2)); alert('copied structured')}}>Copy JSON</button>
                      )}
                    </div>
                    {analysisStructured && (
                      <div style={{marginBottom:12}}>
                        <div style={{fontWeight:700}}>Structured result</div>
                        <pre style={{background:'#071017',padding:12,borderRadius:6,color:'var(--muted)'}}>{JSON.stringify(analysisStructured, null, 2)}</pre>
                        {analysisStructured.examples && analysisStructured.examples.length > 0 && (
                          <div style={{marginTop:8}}>
                            <div style={{fontWeight:700}}>Top mismatches (examples)</div>
                            <div style={{display:'flex',flexDirection:'column',gap:8,marginTop:6}}>
                              {analysisStructured.examples.slice(0,8).map((ex,i)=> (
                                <div key={i} style={{padding:8,background:'rgba(255,255,255,0.01)',borderRadius:6,fontSize:13}}>
                                  <div><strong>req_id:</strong> {ex.req_id || ex.reqId || ex['req_id']}</div>
                                  <div><strong>field:</strong> {ex.field_key}</div>
                                  <div><strong>status:</strong> {ex.status}</div>
                                  <div style={{marginTop:6,color:'var(--muted)',whiteSpace:'pre-wrap',fontSize:12}}>{ex.raw_snippet?.slice(0,400)}</div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                    <div style={{whiteSpace:'pre-wrap'}}>{analysisText}</div>
                  </div>
                ) : <div className="text-muted">No analysis available</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
