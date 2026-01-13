import React, {useState} from 'react'
import axios from 'axios'
import { toast } from 'react-toastify'

export default function UploadForm({onResult}){
  const [file, setFile] = useState(null)
  const [schemaUrl, setSchemaUrl] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(e){
    e.preventDefault()
    if(!file){ toast.error('Please select a file'); return }
    if(!schemaUrl){ toast.error('Please enter schema URL'); return }
    const fd = new FormData();
    fd.append('file', file)
    fd.append('schema_url', schemaUrl)
    try{
      setLoading(true)
      const r = await axios.post('/api/compare', fd, { headers: {'Content-Type':'multipart/form-data'} })
      if(r.data.error){ toast.error(r.data.error); return }
      onResult(r.data)
      toast.success('Comparison finished')
    }catch(err){
      console.error(err); toast.error('Failed to run comparison')
    }finally{ setLoading(false) }
  }

  return (
    <div className="card">
      <form onSubmit={submit} style={{display:'flex',flexDirection:'column',gap:10}}>
        <div className="url-row">
          <div className="method-pill">POST</div>
          <input className="url-input" placeholder="Schema JSON URL" value={schemaUrl} onChange={e=>setSchemaUrl(e.target.value)} />
          <button className="btn compare-btn" disabled={loading} type="submit">{loading? 'Running...' : 'Compare'}</button>
        </div>

        <div className="file-chooser">
          <label style={{background:'#071017',padding:'8px 10px',borderRadius:6,border:'1px solid #0d2930',cursor:'pointer'}}>
            Select requirements file
            <input type="file" style={{display:'none'}} onChange={e=> setFile(e.target.files[0])} />
          </label>
          <div style={{color:'var(--muted)'}}>{file? file.name : 'No file chosen'}</div>
        </div>
      </form>
    </div>
  )
}
