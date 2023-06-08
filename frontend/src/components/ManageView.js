import { Image, Carousel, Form, ProgressBar,Button } from 'react-bootstrap'
import './ManageView.css';
import './UserPageView.js';
import UserPageView from './UserPageView.js';
import { useEffect, useState } from 'react';

function ManageView() {

  const [userName, setUserName] = useState(null)
  const [rows,setRows] = useState(null)

  useEffect(()=>{

  },)

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
      await fetch('http://0.0.0.0:3000/login', {
        method: 'POST',
        body: formData
      }).then(resp => {
        resp.json().then(data => {
          let matched = data['valid']
          if (!matched){
            alert('not valid!!!')
          }else{
            alert('valid')
          }
        })
      })
    }
    getRows();

  }
  
  const buyDataset = (e) => {

    e.preventDefault()
    const formData = new FormData();
    
    var userName = "whowho"
    var selectedImgIds = [1, 2, 3]
    var defiendDatasetname = "bought-123"

    formData.append('user_name',userName)
    formData.append('items',selectedImgIds)
    formData.append('dataset-name',defiendDatasetname)

    //우리 시나리오에 맞게 stae 변경하면서 구현하면됨
    const buy = async () => {
      await fetch('http://0.0.0.0:3000/buy', {
        method: 'POST',
        body: formData
      }).then(resp => {
        resp.json().then(data => {
          let success = data['success_transaction']
          if (!success){
            alert('failed!!!')
          }else{
            alert('success!!!')
          }
        })
      })
    }
    buy();
  }
  
  return (
    <div>
        <form onSubmit={getUserPost} className="ids" enctype="multipart/form-data" >

            <div class="input-group identifier">
                <span class="input-group-text">ID and PW</span>
                <input type="text" aria-label="User Name" id="manage-user-name" placeholder="Username" class="form-control"/>
                <input type="password" aria-label="PW" id="manage-pw" placeholder="Password"  class="form-control"/>
            </div>
            <Button type="submit" variant="outline-secondary" >Identify</Button>
        </form>
        {rows ? <UserPageView user_name={document.getElementById("manage-user-name").value} rows={rows}/> : 'nothing'}
        <form onSubmit={buyDataset} className="ids" enctype="multipart/form-data" >
            <Button type="submit" variant="outline-secondary" >Buy</Button>
        </form>

    </div>  

  );
}

export default ManageView;