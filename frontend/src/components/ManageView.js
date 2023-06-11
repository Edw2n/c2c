import { Image, Carousel, Form, ProgressBar,Button } from 'react-bootstrap'
import './ManageView.css';
import './UserPageView.js';
import UserPageView from './UserPageView.js';
import { useEffect, useState } from 'react';

function ManageView() {
  
  const dummyData = [
    {id: 1, Uploader:'ksofg', Title: 'abc.zip', Description: 'such is life...', 
    QCstate: 'Done', QCscore: 'High', Objects: '3 Objects (Car: 1, Truck: 2)', UploadDate: '2022-03-01',
    SalesCount: 22, MatchedData: 10, Price: 30, PricePerImage: 0.3
    },
    {id: 2, Uploader:'henry', Title: 'afaf.zip',  
    QCstate: 'In Progress', QCscore: '', Objects: 'Car', UploadDate: '2022-03-02',
    SalesCount: 23, MatchedData: 5, Price: 40, PricePerImage: 0.4
    },
    {id: 3, Uploader:'son', Title: 'sdfsdf.zip', 
    QCstate: 'Done', QCscore: 'Low', Objects: 'Car', UploadDate: '2022-03-03',
    SalesCount: 24, MatchedData: 10, Price: 60, PricePerImage: 0.6
    },
    {id: 4, Uploader:'bale', Title: 'wrq.zip', 
    QCstate: 'Done', QCscore: 'High', Objects: 'Car', UploadDate: '2022-03-04',
    SalesCount: 55, MatchedData: 20, Price: 70, PricePerImage: 0.7
    },
    {id: 5, Uploader:'rooney', Title: 'zzz.zip', 
    QCstate: 'Pending', QCscore: 'Low', Objects: 'Car', UploadDate: '2022-03-05',
    SalesCount: 6, MatchedData: 25, Price: 10, PricePerImage: 0.1
    }
  ]
  const [userName, setUserName] = useState(null)
  const [rows,setRows] = useState(dummyData)

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
      await fetch('http://127.0.0.1:3000/login', {
        method: 'POST',
        body: formData
      }).then(resp => {
        resp.json().then(data => {
          let matched = data['valid']
          if (!matched){
            alert('not valid!!!')
          }else{
            alert('valid')
            // setRows(data.data)
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
      await fetch('http://127.0.0.1:3000/buy', {
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

  const downloadDataset = (e) => {

    e.preventDefault()
    const formData = new FormData();
    
    var txp_id = document.getElementById("d-txp-id").value;

    formData.append('txp_id', txp_id)
    formData.append('test_mode', "true") // ui 구현 후에는 이부분을 false로 해서 붙이면 됨, 지금은 transaction data가 없는데 다운로드 되는걸 보고싶으니 이렇게 넣는것임

    //우리 시나리오에 맞게 stae 변경하면서 구현하면됨
    const download = async () => {
      await fetch('http://127.0.0.1:3000/download', {
        method: 'POST',
        body: formData
      }).then(resp => {
        resp.blob().then(blob => {
          const url = window.URL.createObjectURL(new Blob([blob]));
          console.log(url)
          const a = document.createElement('a');
          a.href = url;
          a.download = "dataset.zip";
          a.click();
        });
      });
    };
    download();

  }
  
  return (
    <div>
        <form onSubmit={getUserPost} className="ids" enctype="multipart/form-data" >
            <div class="input-group identifier" style={{width: '50%', justifySelf: 'end'}}>
                <span class="input-group-text" style={{fontSize: '0.8rem'}}>ID and PW</span>
                <input type="text" aria-label="User Name" id="manage-user-name" placeholder="Username" class="form-control" style={{fontSize: '0.8rem', textAlign: 'center'}}/>
                <input type="password" aria-label="PW" id="manage-pw" placeholder="Password"  class="form-control" style={{fontSize: '0.8rem', textAlign: 'center'}}/>
            </div>
            <Button type="submit" variant="outline-secondary" style={{width: '20%', justifySelf: 'start', fontSize: '0.8rem'}}>Identify</Button>
        </form>

        <form onSubmit={downloadDataset} className="ids" enctype="multipart/form-data" >
            <div class="input-group identifier" style={{width: '50%', justifySelf: 'end'}}>
                <span class="input-group-text" style={{fontSize: '0.8rem'}}>TXP_ID</span>
                <input type="text" aria-label="txp_id" id="d-txp-id" placeholder="txp-id"  class="form-control" style={{fontSize: '0.8rem', textAlign: 'center'}}/>
            </div>
            <Button type="submit" variant="outline-secondary" style={{width: '20%', justifySelf: 'start', fontSize: '0.8rem'}}>Downloads</Button>
        </form>
        {/*rows ? <UserPageView user_name={document.getElementById("manage-user-name").value} rows={rows}/> : 'nothing'*/}

        {/*<form onSubmit={buyDataset} className="ids" enctype="multipart/form-data" >
            <Button type="submit" variant="outline-secondary" >Buy</Button>
        </form>*/}
    </div>  

  );
}

export default ManageView;