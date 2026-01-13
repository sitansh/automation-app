import React from 'react'
import { toast } from 'react-toastify'

export default function Results({data}){
  const {rows, report} = data || {}

  // expose a global copy helper that accepts an encoded string
  window.copyJSONEncoded = function(enc){
    try{
      const s = decodeURIComponent(enc || '')
      navigator.clipboard.writeText(s).then(()=>{
        try{ toast.success('JSON copied to clipboard') }catch(e){}
      }).catch(()=>{ try{ toast.error('Failed to copy') }catch(e){} })
    }catch(e){ try{ toast.error('Failed to copy') }catch(e){} }
  }
  return (
    <div style={{marginTop:20}}>
      <div style={{display:'flex', gap:20}}>
        <div style={{flex:1}} className="card">
          <h4>Details</h4>
          <table className="results-table">
            <thead>
              <tr><th>req_id</th><th>field_key</th><th>status</th><th>best</th></tr>
            </thead>
            <tbody>
              {rows && rows.map((r,i)=> (
                <tr key={i} onClick={()=>{
                  const el = document.getElementById('rightPanel');
                  const impl = r.raw_snippet || 'No snippet'
                  // build an "expected" snippet summarizing what was expected
                  const expectedObj = {
                    field_key: r.field_key || null,
                    expected_type: r.expected_type || null,
                    expected_required: r.expected_required || null,
                    req_id: r.req_id || null,
                  }
                  const expectedPretty = JSON.stringify(expectedObj, null, 2)
                  const encImpl = encodeURIComponent(impl)
                  const encExp = encodeURIComponent(expectedPretty)
                  el.innerHTML = `
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                      <div>
                        <h5 style=\"margin:0 0 8px 0\">${r.field_key}</h5>
                        <div class=\"meta\">Status: ${r.status} • Best: ${r.best_match_key||'-'}</div>
                      </div>
                      <div style=\"display:flex;gap:8px\"> 
                        <button class=\"btn\" onclick=\"window.copyJSONEncoded('${encExp}')\">Copy Expected</button>
                        <button class=\"btn\" onclick=\"window.copyJSONEncoded('${encImpl}')\">Copy Implemented</button>
                      </div>
                    </div>
                    <div style=\"margin-top:8px\"><strong>Expected</strong><pre>${expectedPretty}</pre></div>
                    <div style=\"margin-top:8px\"><strong>Implemented (schema)</strong><pre>${impl}</pre></div>
                  `
                }} style={{cursor:'pointer'}}>
                  <td style={{color:'var(--muted)'}}>{r.req_id}</td>
                  <td style={{fontWeight:700}}>{r.field_key}</td>
                  <td className="status">{r.status}</td>
                  <td style={{color:'var(--muted)'}}>{r.best_match_key}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
