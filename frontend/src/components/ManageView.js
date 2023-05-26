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

    //추후 구현 예정
    // const getRows = async () => {
    //   await fetch('http://0.0.0.0:3000/user_post', {
    //     method: 'POST',
    //     body: formData
    //   }).then(resp => {
    //     resp.json().then(data => {
    //       let matched = data['matched']
    //       if (!matched){
    //         alert('not matched')
    //       }else{
    //         setRows(data.data)
    //       }
    //       // setAnimalInfo(prev=>([...data.data]))
    //     })
    //   })
    // }
    // getRows();

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

    </div>  

  );
}

export default ManageView;