import { Image, Carousel, Form, ProgressBar,Button } from 'react-bootstrap'
import './ManageView.css';
import './UserPageView.js';
import UserPageView from './UserPageView.js';
import { useEffect, useState } from 'react';

function ManageView( {LoggedIn, UserInfo,
                      URows, TRows, onManagesChange} ) 
{
  const [userName, setUserName] = useState('')

  const getUserPost = (e) => {

    e.preventDefault()
    const formData = new FormData();
    
    var userName = document.getElementById("manage-user-name").value;
    var pw = document.getElementById("manage-pw").value;

    formData.append('user_name',userName)
    formData.append('pw',pw)

    console.log(userName, pw)
    
    //우리 시나리오에 맞게 stae 변경하면서 구현하면됨
    const getRows = async () => {
      await fetch('http://127.0.0.1:3000/login', {
        method: 'POST',
        body: formData
      }).then(resp => {
        resp.json().then(data => {
          console.log(pw, userName)
          let matched = data['valid']
          console.log(matched)
          if (!matched){
            alert('not valid!!!')
          }else{
            alert('valid')
            const current_cash = data.manage_data.cash
            onManagesChange(prev => (
                {...prev,
                  uploads: data.manage_data.uploaded.rows,
                  transctions: data.manage_data.transactions.rows,
                  login: 'true',
                  userInfo: {
                    username: userName,
                    pw: pw,
                    cash: current_cash,
                  }
                })
              )
            console.log("URows: ", URows)
            console.log("TRows: ", TRows)
          }
        })
      })
    }
    getRows();
  }

  useEffect(() => {
    // 컴포넌트가 처음 렌더링될 때 저장된 데이터 설정
    // onURowsChange(URows);
    // onTRowsChange(TRows);
    onManagesChange({
      uploads: URows,
      transctions: TRows
    })
  }, []);

  return (
    <div>
        {LoggedIn !== "true" ? <form onSubmit={getUserPost} className="ids" enctype="multipart/form-data" >
            <div class="input-group identifier" style={{width: '50%', justifySelf: 'end'}}>
                <span class="input-group-text" style={{fontSize: '0.8rem'}}>ID and PW</span>
                <input type="text" aria-label="User Name" id="manage-user-name" placeholder="Username" class="form-control" style={{fontSize: '0.8rem', textAlign: 'center'}}/>
                <input type="password" aria-label="PW" id="manage-pw" placeholder="Password"  class="form-control" style={{fontSize: '0.8rem', textAlign: 'center'}}/>
            </div>
            <Button type="submit" variant="outline-secondary" style={{width: '20%', justifySelf: 'start', fontSize: '0.8rem'}}>Identify</Button>
        </form> : null}
        {LoggedIn === "true" ? <UserPageView user_name={userName} uploadedRows={URows} transactRows={TRows} UserInfo={UserInfo} onAddUserInfo={onManagesChange}/> : 'nothing'}
    </div>  

  );
}

export default ManageView;