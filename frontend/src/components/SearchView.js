import './SearchView.css';
import '@coreui/coreui/dist/css/coreui.min.css'
import { CInputGroup, CFormSelect, CButton } from '@coreui/react'
import { Form, Button } from 'react-bootstrap'
import { useEffect, useState } from 'react';
import DatasetListView from './DatasetListView';
import { GridCellCheckboxRenderer } from '@mui/x-data-grid';
import { SpeedDialAction } from '@mui/material';
import React from 'react';
import styled from '@emotion/styled';

function SearchView() {
  
  // 지금은 dummy data -> listinfo 받아오도록 수정 필요
  // dummy data
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
    },
    {id: 6, Uploader:'asdasd', Title: 'xxx.zip', 
    QCstate: 'In Progress', QCscore: '', Objects: 'Car', UploadDate: '2022-03-06',
    SalesCount: 2, MatchedData: 9, Price: 90, PricePerImage: 0.9
    },
    {id: 7, Uploader:'nine', Title: 'yyyy.zip', 
    QCstate: 'Done', QCscore: 'High', Objects: 'Car', UploadDate: '2022-04-01',
    SalesCount: 12, MatchedData: 3, Price: 26, PricePerImage: 0.26
    },
    {id: 8, Uploader:'zoo', Title: 'asdfg.zip', 
    QCstate: 'Done', QCscore: 'Medium', Objects: 'Car', UploadDate: '2022-05-01',
    SalesCount: 14, MatchedData: 1, Price: 11, PricePerImage: 0.11
    },
    {id: 9, Uploader:'barn', Title: 'qwer.zip', 
    QCstate: 'Done', QCscore: 'Medium', Objects: 'Car', UploadDate: '2022-06-01',
    SalesCount: 1, MatchedData: 4, Price: 41, PricePerImage: 0.41
    },
    {id: 10, Uploader:'kookoo', Title: 'tqt.zip', 
    QCstate: 'Done', QCscore: 'High', Objects: 'Car', UploadDate: '2022-07-01',
    SalesCount: 3, MatchedData: 5, Price: 51, PricePerImage: 0.51
    }
  ]
  // end of dummy data
  
  const [listInfo,setListInfo] = useState(dummyData)

  /* useEffect(()=>{
    search()
  },[])

  
  const search = async () => {
    const formData = new FormData();

    await fetch('http://0.0.0.0:3000/read', {
      method: 'POST',
      body: formData
    }).then(resp => {
      resp.json().then(data => {
        console.log(data)
        setListInfo(prev=>([...data.data]))
      })
    })}
  */

  const handleSubmit = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target);
    console.log(formData)
    console.log(e.target)
    console.log(e.currentTarget)

    formData.append('user_name', e.target[1].value)
    formData.append('pw', e.target[2].value)
    formData.append('title', e.target[3].value)
    formData.append('description', e.target[4].value)

    const Upload = async () => {

      await fetch('http://0.0.0.0:3000/upload', {
        method: 'POST',
        body: formData
      }).then(resp => {
        resp.json().then(data => {
          // if you want values of response, check!!
          // console.log("data", data.data)
          // console.log("user identification", data.valid)
          // console.log("upload complete", data.success)
          
          if (!data.valid) {
            alert('pw is not valid!!!!')  
          } else if (!data.success) {
            alert('upload failed!!!')  
          } else {
            alert('upload complete!!!')  
          }

          setListInfo(prev=>([...data.data]))
        })
      })
    }
    Upload();
  }

  /*
  const handleSearch = (e) => {
    e.preventDefault()

    const formData = new FormData();
    console.log(e.target);

    var qcState = document.getElementById("qc-state").value;
    var qcScore = document.getElementById("qc-score").value;
    var qcObject = document.getElementById("qc-object").value;
    var angle = document.getElementById("angle").value;
    var angularRate = document.getElementById("angRate").value;
    var velocity = document.getElementById("velocity").value;
    var acceleration = document.getElementById("acceleration").value;
  
    // console.log(selectedValue)
    // var customScript = document.getElementById('form-custom-script-file').value ? true : false;
    // TODO: customSCript form에 붙이기
    
    formData.append('QC_state',qcState)
    formData.append('QC_score',qcScore)
    formData.append('QC_object',qcObject)
    formData.append('Angle',angle)
    formData.append('Angular_rate',angularRate)
    formData.append('Velocity',velocity)
    formData.append('Acceleration',acceleration)

    console.log(formData)
    const search = async () => {
      await fetch('http://0.0.0.0:3000/read', {
        method: 'POST',
        body: formData
      }).then(resp => {
        resp.json().then(data => {
          console.log(data.matched)
          console.log(data.data)

          setListInfo(prev=>([...data.data]))

        })
      })
    }
    search();
    console.log('search')
  }
  
  const handleOptions = (e)=> {
    console.log(e.currentTarget.id)
  }
  */

  // 필터1: 퀵서치(검색창)
  const f1_titles = (
    <div className='LowLevelGroup' style={{gridRow: '1', borderBottom: '1px solid lightgray'}}>
      <text style={{marginLeft: '5px', fontSize: '0.7rem'}}>
        Quick Search
      </text>
    </div>
  )
  const f1_list = []
  f1_list.push(
    <div className='filters'>
      <input 
        type="text" id="search" placeholder="Search"
        style={{width: '40%', height: '80%', fontSize: '0.7rem'}}>
      </input>
    </div>
  )

  // 필터2: 체크박스
  const f2category = [
    {id: 1, title:"QC State", sub:['All','Pending','In Progress','Done']},
    {id: 2, title:"QC Score", sub:['All','Low','Medium','High']},
    {id: 3, title:"QC Object", sub:['All', 'Car', 'Van', 'Truck', 'Pedestrian', 'Sitter', 'Cyclist', 'Tram', 'Misc']},
  ]
  const f2category_titles = (
    <div className='LowLevelGroup' style={{gridRow: '2',  gridTemplateRows: '25% 25% 25% 25%', borderBottom: '1px solid lightgray'}}>
    {f2category.map((catdata, index) => (
      <text
        key={catdata.id} 
        style={{height: '80%', marginLeft: '5px', textAlign: 'left', fontSize: '0.7rem'}}>
        {catdata.title}
      </text>))}
      <div>
      </div>
    </div>
  )
  const f2category_filters = (
    <div className='filters_qc'>
      {f2category.map((catdata, rowindex) => (
        catdata.sub.map((subItem, colIndex) => (
          <React.Fragment key={subItem}>
            <label
              key={subItem}
              htmlFor={subItem}
              style={{
                gridColumn: `${rowindex > 1 && colIndex > 4 ? 2 * (colIndex - 5) + 1 : 2 * colIndex + 1}`,
                gridRow: `${rowindex > 1 && colIndex > 4 ? rowindex + 2 : rowindex + 1}`,
                textAlign: 'left',
                width: '100%',
                height: '80%',
                fontSize: '0.7rem',
                verticalAlign: 'middle'
              }}>
              {subItem}
            </label>
            <label
              style={{
                gridColumn: `${rowindex > 1 && colIndex > 4 ? 2 * (colIndex - 5) + 2: 2 * colIndex + 2}`,
                gridRow: `${rowindex > 1 && colIndex > 4 ? rowindex + 2 : rowindex + 1}`,
                textAlign: 'left',
                width: '100%',
                height: '100%',
              }}
            >
              <input id={subItem} type="checkbox" style={{alignSelf: 'center', height: '100%'}}/>
            </label>
          </React.Fragment>
        ))
      ))}
    </div>
  );

  // 필터3: 항목 별 범위 설정
  const f3category = [
    {id: 1, title:"Angle(rad)", sub:['Roll', 'Pitch', 'Yaw']},
    {id: 2, title:"Angular Rate(rad/s)", sub:['Wx','Wy','Wz']},
    {id: 3, title:"Velocity(m/s)", sub:['Vf','Vl','Vu']},
    {id: 4, title:"Accel(m/s^2)", sub:['Ax','Ay','Az']}
  ]
  const f3category_titles = (
    <div className='LowLevelGroup' style={{gridRow: '3', borderBottom: '1px solid lightgray'}}>
    {f3category.map((catdata, index) => (
      <text 
        key={catdata.id} 
        style={{marginLeft: '5px', textAlign: 'left', fontSize: '0.7rem'}}>
        {catdata.title}
      </text>))}
    </div>
  )
  const f3category_filters = (
    <div className='filters_sensor'>
      {f3category.map((catdata, rowindex) => (
        catdata.sub.map((subItem, colIndex) => (
          <React.Fragment key={subItem}>
            <label 
              key={subItem} htmlFor={subItem} 
              style={{gridColumn: `${2 * colIndex + 1}`, gridRow: `${rowindex + 1}`, textAlign: 'left', fontSize: '0.7rem', width: '100%', height: '65%'}}>
              {subItem}
            </label>
            <label style={{textAlign: 'left', width: '100%', height: '100%'}}>
              <input style={{ width: '30%' , height: '75%', fontSize: '0.7rem'}} 
                type="number" id={`${subItem}-start`} placeholder='Start' />
              <span>  -  </span>
              <input style={{ width: '30%' , height: '75%', fontSize: '0.7rem'}} 
                type="number" id={`${subItem}-end`} placeholder='End' />
            </label>
          </React.Fragment>
        ))
      ))}
    </div>
  );

  // Display
  return (
    // 전체 화면: 각 Part들이 가로로 쌓이도록 구성
    <div style={{height: '100%', display: 'grid', gridTemplateRows: '7% 3% 30% 3% 57%'}}> 
    
    {/* Part 1: 업로드 */}
      <div className='UploadContainer'>
        
      {/* Part 1-1: 제목 */}
        <h5 className='ContainerTitle'>
          데이터셋 업로드하기
        </h5>

      {/* Part 1-2: 업로드 창 */}
        <div className='ContainerDetail'>
          <form onSubmit={handleSubmit} className="Uploaderbar" enctype="multipart/form-data" >
            <Form.Group controlId="formFile" style={{width: '98%', height: '100%', gridColumn: '1'}}>
              <Form.Control type="file" controlId="file" name="file" style={{width: '99%', height: '70%', fontSize: '0.7rem'}}/>
            </Form.Group>
            <div class="input-group" style={{width: '99%', height: '100%', gridColumn: '2'}}>
              <span class="input-group-text" style={{fontSize: '0.7rem', width: '12%', height: '70%', textAlign: 'center'}}>
                Information
              </span>
              <input type="text" aria-label="ID" placeholder="ID" class="form-control" style={{fontSize: '0.7rem', width: '10%', height: '70%'}}/>
              <input type="password" aria-label="PW" placeholder="pw"  class="form-control" style={{fontSize: '0.7rem', width: '10%', height: '70%'}}/>
              <input type="text" aria-label="Title" placeholder="title"  class="form-control" style={{fontSize: '0.7rem', width: '13%', height: '70%'}}/>
              <input type="text" aria-label="Description" placeholder="description"  class="form-control" style={{fontSize: '0.7rem', width: '32%', height: '70%' }}/>
            </div>
            <div className="input-group" style={{width: '100%', height: '100%', gridColumn: '3'}}>
              <Button type="submit" variant="outline-secondary" style={{fontSize: '0.7rem', width: '100%', height: '70%', color: 'white', fontWeight: 'bold', background: 'rgb(38, 73, 132)'}} >
                Upload
              </Button>
            </div>
          </form>
        </div> 
      
      </div>

    {/* Part 2: 필터 */}
      <div className='SearchContainer'>
      
      {/* Part 2-1: 제목 */}
        <h5 className='ContainerTitle' style={{marginTop: '5px'}}>
          데이터셋 검색하기
        </h5>

      {/* Part 2-2: 필터 창 */}
        <div className='SearchContainerDetail'>
        
        {/* Part 2-2-1: Basic Info */}
          <div className='HighLevelGroup' 
            style={{gridRow: '1', borderBottom: '2px solid white'}}>
            <text style={{marginLeft: '5px', fontSize: '0.8rem'}}>
              Basic Info
            </text>
          </div>
          {f1_titles}
          {f1_list}
          
          {/* Part 2-2-2: QC Info */}
          <div className='HighLevelGroup' 
            style={{gridRow: '2', borderBottom: '2px solid white'}}>  
            <text style={{marginLeft: '5px', fontSize: '0.8rem'}}>
              Quality Info
            </text>
          </div>
          {f2category_titles}
          {f2category_filters}


          {/* Part 2-2-3: Sensor Info */}
          <div className='HighLevelGroup' 
            style={{gridRow: '3', borderBottom: '2px solid white'}}>  
            <text style={{marginLeft: '5px', fontSize: '0.8rem'}}>
              Sensor Info
            </text>
          </div>
          {f3category_titles}
          {f3category_filters}
          
          {/* Part 2-2-4: Custom Filter Upload - 여기 뭔가 고쳐야 할 듯 */}
          <div className='HighLevelGroup' 
            style={{gridRow: '4'}}>
            <text style={{marginLeft: '5px', fontSize: '0.8rem'}}>
              Custom Filtering
            </text>
          </div>
          <div className='LowLevelGroup' 
            style={{marginLeft: '5px', gridRow: '4', gridColumn: '2  / span 2'}}>
            <CInputGroup 
              style={{alignSelf: 'center', width: '100%', height: '100%'}}>
              <form className='Searcher'>
                  <Form.Group controlId="form-custom-script-file" style={{height: '80%', width: '90%'}}>
                    <Form.Control type="file" controlId="file" name="file" style={{marginBottom:'0px' , fontSize: '0.7rem', height: '80%'}}/>
                  </Form.Group>
              </form>
            </CInputGroup>
          </div>
        </div>
      </div>
          
      {/* ############## 검색 버튼 ############## */}
      <div style={{gridRow: '4', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr 1fr', justifyItems: 'end', marginTop: '5px'}}>
          <CButton type="button" color="secondary" className="mb-3" variant="outline" id="button-addon2" 
            style={{width: '20%', height: '60%', gridColumn: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'rgb(38, 73, 132)'}}>
              <span style={{fontSize: '0.7rem', color: 'white', fontWeight: 'bold'}}>Search</span>
          </CButton>
      </div> 

      {/* Part 3: 리스트뷰 */}
      <div className='ListviewContainer'>
          
        {/* Part 3-1: 제목 */}
        <h5 className='ContainerTitle' style={{marginTop: '15px'}}>
          데이터셋 살펴보기
        </h5>
        
        {/* Part 3-2: 리스트뷰 창 */}
        {listInfo.length>0 ? <DatasetListView listInfo={listInfo}/> : 'No results'}

      </div>

    </div> // end of all
  );
}

export default SearchView;