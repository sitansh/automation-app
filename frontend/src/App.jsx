import React, {useState} from 'react'

import UploadForm from './components/UploadForm'
import Results from './components/Results'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import SummaryModal from './components/SummaryModal'
import Reports from './components/Reports'
import { ToastContainer } from 'react-toastify'
import icon from '/favicon.png'

export default function App(){
  const [data, setData] = useState(null)
  const [showSidebar, setShowSidebar] = useState(true)
  const [sidebarWidth, setSidebarWidth] = useState(260)
  const [showSummaryModal, setShowSummaryModal] = useState(false)
  const [showSummary, setShowSummary] = useState(false)
  const [rightWidth, setRightWidth] = useState(380)
  const [view, setView] = useState('comparator')

  function startResize(e){
    e.preventDefault()
    const isTouch = e.type === 'touchstart'
    const startX = isTouch ? e.touches[0].clientX : e.clientX
    const startWidth = sidebarWidth
    document.body.style.userSelect = 'none'
    function onMove(ev){
      const curX = ev.clientX !== undefined ? ev.clientX : (ev.touches && ev.touches[0].clientX)
      if (curX === undefined) return
      const dx = curX - startX
      const next = Math.max(160, Math.min(520, startWidth + dx))
      setSidebarWidth(next)
    }
    function onUp(){
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
      window.removeEventListener('touchmove', onMove)
      window.removeEventListener('touchend', onUp)
      document.body.style.userSelect = ''
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    window.addEventListener('touchmove', onMove, {passive:false})
    window.addEventListener('touchend', onUp)
  }

  function startResizeRight(e){
    e.preventDefault()
    const isTouch = e.type === 'touchstart'
    const startX = isTouch ? e.touches[0].clientX : e.clientX
    const startWidth = rightWidth
    document.body.style.userSelect = 'none'
    function onMove(ev){
      const curX = ev.clientX !== undefined ? ev.clientX : (ev.touches && ev.touches[0].clientX)
      if (curX === undefined) return
      const dx = curX - startX
      const next = Math.max(200, Math.min(900, startWidth - dx))
      setRightWidth(next)
    }
    function onUp(){
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
      window.removeEventListener('touchmove', onMove)
      window.removeEventListener('touchend', onUp)
      document.body.style.userSelect = ''
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    window.addEventListener('touchmove', onMove, {passive:false})
    window.addEventListener('touchend', onUp)
  }

  return (
    <div className="app-shell">
      {/* Floating icon button, always visible */}
      <div
        style={{
          position: 'fixed',
          top: 16,
          left: 16,
          zIndex: 1001,
          background: '#101c2a',
          borderRadius: '12px',
          boxShadow: '0 2px 8px #0002',
          width: 44,
          height: 44,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          border: showSidebar ? '2px solid #1a2a3a' : '2px solid #2a3a4a',
          transition: 'border 0.2s',
        }}
        onClick={() => setShowSidebar(s => !s)}
        title={showSidebar ? 'Hide sidebar' : 'Show sidebar'}
      >
        <img src={icon} alt="App Icon" style={{width: 28, height: 28, pointerEvents: 'none'}} />
      </div>
      {showSidebar && (
        <div className="sidebar" style={{width: sidebarWidth}}>
          <Sidebar currentView={view} onSelectView={setView} showSummary={showSummary} onToggleSummary={()=>setShowSummaryModal(true)} summaryData={data} />
          <div className="resizer" onMouseDown={startResize} onTouchStart={startResize} />
        </div>
      )}
      <div className="main">
        <div className="topbar"><Topbar showSidebar={showSidebar} onToggleSidebar={()=>setShowSidebar(s=>!s)} /></div>
        <div className="workspace">
          <div className="center panel">
            {view === 'comparator' && (
              <>
                <UploadForm onResult={setData} />
                {data && <Results data={data} />}
              </>
            )}
            {view === 'reports' && (
              <Reports />
            )}
            {view === 'settings' && (
              <div className="card"><h4>Settings</h4><p className="text-muted">No settings yet.</p></div>
            )}
          </div>
          {view === 'comparator' && (
            <>
              <div className="splitter" onMouseDown={startResizeRight} onTouchStart={startResizeRight} />
              <div className="right panel" style={{width: rightWidth}}>
                <div className="card">
                  <h4>Details</h4>
                  <div id="rightPanel">
                    <p className="text-muted">Select a row to view details.</p>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
      <ToastContainer />
      {showSummaryModal && (
        <SummaryModal open={showSummaryModal} onClose={()=>setShowSummaryModal(false)} data={data} />
      )}
    </div>
  )
}
