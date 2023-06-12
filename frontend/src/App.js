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
  
  // 장바구니
  const [selectedRows, setSelectedRows] = useState([]);
  const [SelectedImgIds, setSelectedImgIds] = useState([]);

  const onAddToCart = (rows) => {
    setSelectedRows((prevSelectedRows) => [...prevSelectedRows,...rows]);
  };

  const onAddToCart_img = (newList) => {
    setSelectedImgIds((prevList) => [...prevList,...newList])
  }

  // 로그인 정보
  // const [LoggedIn, setLoggedIn] = useState('false');
  // const onAddLoggedIn = () => {
  //   setLoggedIn('true');
  // }

  // const [UserInfo, setUserInfo] = useState({username: '', pw: '', cash: 0})
  // const onAddUserInfo = (userName, pw, cash) => {
  //    setUserInfo({username: userName, pw: pw, cash: cash});
  // };
  
  // 로그아웃
  const handleLogout = () => {
    setManages(prev => (
      {...prev,
       login: 'false',
       userInfo: {username: '', pw: '', cash: 0},
      }
    ));
  }

  // Upload & Transaction rows => 페이지 바뀔 때마다 불러오는 용도
  // const [URows, setURows] = useState([]);
  // const [TRows, setTRows] = useState([]);

  const [Manages, setManages] = useState({
    uploads: [],
    transactions: [],
    login: 'false',
    userInfo: {
      username: '',
      pw: '',
      cash: '',
    }
  });

  const handleManagesChanges = (data) => {
    console.log("print",data)
    setManages(data)
    // setManages(prev => (
    //   {...prev,
    //     uploads: data.uploaded.rows,
    //     transctions: data.transactions.rows,
    //   }));
  }


  // const handleURowsChange = (data) => {
  //   setURows(data);
  // };
  // const handleTRowsChange = (data) => {
  //   setTRows(data);
  // };

  // app 화면
  return (
    <div className="App">
      <header className="App-header">  
        <p style={{gridColumn: '3'}}>
          C2C
        </p>
        {Manages.login === 'true' && (
          <span style={{gridColumn: '4', 
                        justifySelf: 'end', 
                        alignSelf: 'center', 
                        fontSize: '0.9rem', 
                        fontWeight: 'bold',
                        display: 'block',
                        textAlign: 'right',
                        marginTop: '5px'}}>
            {`Hello, ${Manages.userInfo.username} !`}
            <br />
            {`Current Points: ${Manages.userInfo.cash}`}
            <br />
            <button 
              variant="outline-secondary"
              style={{fontSize: '0.9rem', 
                      fontWeight: 'bold', 
                      color: 'rgb(38, 73, 132)', 
                      textAlign: 'right',
                      background: "#259a6d",
                      border: '0',
                      marginTop: '2px'}} 
              onClick={handleLogout}>
              Logout
            </button>
          </span>)}
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
      {mode=='search' ? <SearchView onAddToCart={onAddToCart} onAddToCart_img={onAddToCart_img}/> 
                      : <ManageView cartList={selectedRows} cartList_img={SelectedImgIds} 
                                    LoggedIn={Manages.login} 
                                    UserInfo={Manages.userInfo} 
                                    URows={Manages.uploads} 
                                    TRows={Manages.transctions} onManagesChange={handleManagesChanges}/>}
    </div>
  );
}

export default App;