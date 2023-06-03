import './App.css';
import '@coreui/coreui/dist/css/coreui.min.css'
import { CButtonGroup, CFormCheck } from '@coreui/react'
import { useState } from 'react';
import SearchView from './components/SearchView';
import ManageView from './components/ManageView';


function App() {

  const [mode,setMode] = useState('search')

  const handleMode = (e) => {
    console.log(e.currentTarget.id)
    setMode(e.currentTarget.id)
  }

  return (
    <div className="App">
      <header className="App-header">
        {     
        <p>
          C2C
        </p>}
      </header>
      <div>
      <CButtonGroup horizontal role="group" aria-label="Vertical button group" style={{marginBottom:'10px'}}>
        <CFormCheck
          type="radio"
          onClick={handleMode}
          button={{ color: 'danger', variant: 'outline', size: 'sm' }}
          name="vbtnradio"
          id="search"
          autoComplete="off"
          label="Search / Upload"
          defaultChecked
        />
        <CFormCheck
          type="radio"
          onClick={handleMode}
          button={{ color: 'danger', variant: 'outline', size: 'sm' }}
          name="vbtnradio"
          id="manage"
          autoComplete="off"
          label="Manage"
        />
      </CButtonGroup>
      </div>
      {mode=='search' ? <SearchView/> : <ManageView/>}
    </div>
  );
}

export default App;