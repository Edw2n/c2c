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
  
  const [listInfo,setListInfo] = useState([dummyData]);

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
      if (!e.target[0].files[0]) {
        alert('Please select a file')
      }
      else if (!e.target[1].value) {
        alert('Please enter your ID')
      }
      else if (!e.target[2].value){
        alert('Please enter your PW')
      }
      else if (!e.target[3].value){
        alert('Please enter the title')
      }
      else if (!e.target[4].value){
        alert('Please enter the description')
      }
      else {
        await fetch('http://127.0.0.1:3000/upload', {
          method: 'POST',
          body: formData
        }).then(resp => {
          resp.json().then(data => {
            // if you want values of response, check!!
            // console.log("data", data.datasets)
            // console.log("user identification", data.valid)
            // console.log("upload complete", data.success)
            
            if (!data.valid) {
              alert('pw is not valid!!!!')  
            } else if (!data.success) {
              alert('upload failed!!!')  
            } else {
              alert('upload complete!!!')  
            }
            setListInfo(prev=>([...data.datasets.rows]))
          })
        })
      }
    }
    Upload();
  }

  
  useEffect(()=>{
    search()
  },[])

  
  const search = async () => {
    const formData = new FormData();

    await fetch('http://127.0.0.1:3000/read', {
      method: 'POST',
      body: formData
    }).then(resp => {
      resp.json().then(data => {
        console.log(data)
        setListInfo(prev=>([...data.datasets.rows]))
      })
    })}
  

  
  const handleSearch = (e) => {
    e.preventDefault()

    const formData = new FormData();
    console.log(e.target);

    var keyword = document.getElementById("keyword").value ? `${document.getElementById("keyword").value}` : 'none';
    var qcState = StateCheckbox.qc_state ? [...StateCheckbox.qc_state] : 'not selected';
    var qcScore = StateCheckbox.qc_score ? [...StateCheckbox.qc_score] : 'not selected';
    var qcObject = StateCheckbox.qc_object ? [...StateCheckbox.qc_object] : 'not selected';
    var roll = StateNumbers.Roll ? `(${StateNumbers.Roll.start || null},${StateNumbers.Roll.end || null})` : 'none';
    var pitch = StateNumbers.Pitch ? `(${StateNumbers.Pitch.start || null},${StateNumbers.Pitch.end || null})` : 'none';
    var yaw = StateNumbers.Yaw ? `(${StateNumbers.Yaw.start || null},${StateNumbers.Yaw.end || null})` : 'none';
    var wx = StateNumbers.Wx ? `(${StateNumbers.Wx.start || null},${StateNumbers.Wx.end || null})` : 'none';
    var wy = StateNumbers.Wy ? `(${StateNumbers.Wy.start || null},${StateNumbers.Wy.end || null})` : 'none';
    var wz = StateNumbers.Wz ? `(${StateNumbers.Wz.start || null},${StateNumbers.Wz.end || null})` : 'none';
    var vf = StateNumbers.Vf ? `(${StateNumbers.Vf.start || null},${StateNumbers.Vf.end || null})` : 'none';
    var vl = StateNumbers.Vl ? `(${StateNumbers.Vl.start || null},${StateNumbers.Vl.end || null})` : 'none';
    var vu = StateNumbers.Vu ? `(${StateNumbers.Vu.start || null},${StateNumbers.Vu.end || null})` : 'none';
    var ax = StateNumbers.Ax ? `(${StateNumbers.Ax.start || null},${StateNumbers.Ax.end || null})` : 'none';
    var ay = StateNumbers.Ay ? `(${StateNumbers.Ay.start || null},${StateNumbers.Ay.end || null})` : 'none';
    var az = StateNumbers.Az ? `(${StateNumbers.Az.start || null},${StateNumbers.Az.end || null})` : 'none';
   
    // console.log(selectedValue)
    // var customScript = document.getElementById('form-custom-script-file').value ? true : false;
    // TODO: customSCript form에 붙이기
    if (qcState.includes('All')) {
      qcState = 'none'
    }
    if (qcScore.includes('All')) {
      qcScore = 'none'
    }
    if (qcObject.includes('All')) {
      qcObject = 'none'
    }
    if (qcState == 'not selected') {
      alert("Please select at least one item from QC State!")
      return
    }
    else if (qcScore == 'not selected') {
      alert("Please select at least one item from QC Score!")
      return
    }
    else if (qcObject == 'not selected') {
      alert("Please select at least one item from QC Object!")
    }
    else {
      formData.append('keyword', keyword)
      formData.append('qc_state',qcState)
      formData.append('qc_score',qcScore)
      formData.append('objects',qcObject)
      formData.append('roll',roll)
      formData.append('pitch',pitch)
      formData.append('yaw',yaw)
      formData.append('wx',wx)
      formData.append('wy',wy)
      formData.append('wz',wz)
      formData.append('vf',vf)
      formData.append('vl',vl)
      formData.append('vu',vu)
      formData.append('ax',ax)
      formData.append('ay',ay)
      formData.append('az',az)
      formData.append('custom_script', document.getElementById('form-custom-script-file').files[0] ? document.getElementById('form-custom-script-file').files[0] : false)
      console.log(formData)
      const search = async () => {
        await fetch('http://127.0.0.1:3000/read', {
          method: 'POST',
          body: formData
        }).then(resp => {
          resp.json().then(data => {
            console.log(data.matched)
            console.log(data.datasets)
  
            setListInfo(prev=>([...data.datasets.rows]))
          })
        })
      }
      search();
      console.log('search')
      console.log('FormData Key-value pairs:')
      for (let pair of formData.entries()) {
        console.log(pair[0], pair[1]);
      }
    }
  }
  
  const handleOptions = (e)=> {
    console.log(e.currentTarget.id)
  }
  

  // 필터1: 퀵서치(검색창)
  const f1_titles = (
    <div className='LowLevelGroup' style={{gridRow: '1', borderBottom: '1px solid lightgray'}}>
      <text style={{marginLeft: '5px', fontSize: '0.8rem'}}>
        Quick Search
      </text>
    </div>
  )
  const f1_list = []
  f1_list.push(
    <div className='filters'>
      <input 
        type="text" id="keyword" placeholder="Search"
        style={{width: '35%', height: '80%', fontSize: '0.75rem'}}>
      </input>
    </div>
  )

  // 필터2: 체크박스
  const f2category = [
    {id: "qc_state", title:"QC State", sub:['All','Pending','In Progress','Done']},
    {id: "qc_score", title:"QC Score", sub:['All','Low','Medium','High']},
    {id: "qc_object", title:"QC Object", sub:['All', 'Car', 'Van', 'Truck', 'Pedestrian', 'Sitter', 'Cyclist', 'Tram', 'Misc']},
  ]
  // 필터2 - 체크박스 state
  const [StateCheckbox, setStateCheckbox] = useState({});

  // 필터2 -체크박스 (event handler)
  const handleCheckboxChange = (category, subItem) => {
    const isChecked = document.getElementById(`${category}-${subItem}`).checked;

    if (subItem === 'All') {
      const targetCategory = f2category.find(cat => cat.id === category);
      const subCheckboxes = targetCategory.sub.filter(sub => sub !== 'All');

      subCheckboxes.forEach(sub => {
        document.getElementById(`${category}-${sub}`).checked = isChecked;
      });

      setStateCheckbox(prevState => {
        const newCheckedItems = { ...prevState };
        if (isChecked) {
          newCheckedItems[category] = ['All'];
        } else {
          delete newCheckedItems[category];
        }
        return newCheckedItems;
      });
    } else {
      const allCheckbox = document.getElementById(`${category}-All`);
      const targetCategory = f2category.find(cat => cat.id === category);
      const subCheckboxes = targetCategory.sub.filter(sub => sub !== 'All');
      const checkedCount = subCheckboxes.reduce((count, sub) => {
        return document.getElementById(`${category}-${sub}`).checked ? count + 1 : count;
      }, 0);

      if (isChecked && checkedCount === subCheckboxes.length) {
        allCheckbox.checked = true;
      } else if (!isChecked && checkedCount === subCheckboxes.length - 1) {
        allCheckbox.checked = false;
      }

      setStateCheckbox(prevState => {
        const newCheckedItems = { ...prevState };
        newCheckedItems[category] = newCheckedItems[category] || [];
        if (isChecked) {
          if (!newCheckedItems[category].includes('All')) {
            newCheckedItems[category] = [...newCheckedItems[category], subItem];
          }
          if (newCheckedItems[category].length === subCheckboxes.length) {
            newCheckedItems[category] = ['All'];
          }
        } else {
          newCheckedItems[category] = newCheckedItems[category].filter(item => item !== subItem);
          if (newCheckedItems[category].length === 0) {
            delete newCheckedItems[category];
          } else if (newCheckedItems[category].includes('All')) {
            newCheckedItems[category] = newCheckedItems[category].filter(item => item !== 'All');
          }
        }
        return newCheckedItems;
      });
    }
  };
  const f2category_titles = (
    <div className='LowLevelGroup' style={{gridRow: '2',  gridTemplateRows: '25% 25% 25% 25%', borderBottom: '1px solid lightgray'}}>
    {f2category.map((catdata, index) => (
      <text
        key={catdata.id} 
        style={{height: '80%', marginLeft: '5px', textAlign: 'left', fontSize: '0.8rem'}}>
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
                fontSize: '0.75rem',
                verticalAlign: 'middle',
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
              <input id={`${catdata.id}-${subItem}`} type="checkbox" style={{alignSelf: 'center', height: '100%'}} onChange={() => handleCheckboxChange(catdata.id, subItem)}/>
            </label>
          </React.Fragment>
        ))
      ))}
    </div>
  );

  // 필터3: 항목 별 범위 설정
  const f3category = [
    {id: 'angle', title:"Angle(rad)", sub:['Roll', 'Pitch', 'Yaw']},
    {id: 'angular_rate', title:"Angular Rate(rad/s)", sub:['Wx','Wy','Wz']},
    {id: 'velocity', title:"Velocity(m/s)", sub:['Vf','Vl','Vu']},
    {id: 'acceleration', title:"Accel(m/s^2)", sub:['Ax','Ay','Az']}
  ]
  // 필터3 - 숫자 엔트리 state
  const [StateNumbers, setStateNumbers] = useState({});
  // 필터3 - 숫자 엔트리 (event handler)
  const handleInputChange = (subItem, inputType, value) => {
    setStateNumbers(prevState => {
      const newNumbers = { ...prevState[subItem], [inputType]: value };
      const { start, end } = newNumbers;
      const hasStart = start !== undefined && start !== '';
      const hasEnd = end !== undefined && end !== '';
  
      if (!hasStart && !hasEnd) {
        return { ...prevState, [subItem]: undefined };
      }
  
      return { ...prevState, [subItem]: newNumbers };
    });
  };
  const f3category_titles = (
    <div className='LowLevelGroup' style={{gridRow: '3', borderBottom: '1px solid lightgray'}}>
    {f3category.map((catdata, index) => (
      <text 
        key={catdata.id} 
        style={{marginLeft: '5px', textAlign: 'left', fontSize: '0.8rem'}}>
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
                type="number" id={`${subItem}-start`} placeholder='Start'
                value={StateNumbers[subItem]?.start || ''}
                onChange={(e) => handleInputChange(subItem, 'start', e.target.value)}/>
              <span>  -  </span>
              <input style={{ width: '30%' , height: '75%', fontSize: '0.7rem'}} 
                type="number" id={`${subItem}-end`} placeholder='End'
                value={StateNumbers[subItem]?.end || ''}
                onChange={(e) => handleInputChange(subItem, 'end', e.target.value)}/>
            </label>
          </React.Fragment>
        ))
      ))}
    </div>
  );

  // Display
  return (
    // 전체 화면: 각 Part들이 가로로 쌓이도록 구성
    <div style={{height: '100%', display: 'grid', gridTemplateRows: '7% 3% 36% 3% 51%', gridTemplateColumns: '13% 74% 13%', alignItems: 'center'}}> 
    
    {/* Part 1: 업로드 */}
      <div className='UploadContainer'>
        
      {/* Part 1-1: 제목 */}
        <h5 className='ContainerTitle'>
          Uploading Dataset
        </h5>

      {/* Part 1-2: 업로드 창 */}
        <div className='ContainerDetail'>
          <form onSubmit={handleSubmit} className="Uploaderbar" enctype="multipart/form-data" >
            <Form.Group controlId="formFile" style={{width: '99%', height: '100%', gridColumn: '1'}}>
              <Form.Control type="file" controlId="file" name="file" style={{width: '99%', height: '70%', fontSize: '0.75rem'}}/>
            </Form.Group>
            <div class="input-group" style={{width: '99%', height: '100%', gridColumn: '2'}}>
              <span class="input-group-text" style={{fontSize: '0.7rem', width: '13%', height: '70%', textAlign: 'center', justifyContent: 'center'}}>
                Information
              </span>
              <input type="text" aria-label="ID" placeholder="ID" class="form-control" style={{fontSize: '0.75rem', width: '10%', height: '70%'}}/>
              <input type="password" aria-label="PW" placeholder="pw"  class="form-control" style={{fontSize: '0.75rem', width: '10%', height: '70%'}}/>
              <input type="text" aria-label="Title" placeholder="title"  class="form-control" style={{fontSize: '0.75rem', width: '13%', height: '70%'}}/>
              <input type="text" aria-label="Description" placeholder="description"  class="form-control" style={{fontSize: '0.75rem', width: '33%', height: '70%' }}/>
            </div>
            <div className="input-group" style={{width: '100%', height: '100%', gridColumn: '3'}}>
              <Button type="submit" variant="outline-secondary" style={{fontSize: '0.75rem', width: '100%', height: '70%', color: 'white', fontWeight: 'bold', background: 'rgb(38, 73, 132)'}} >
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
          Searching Datasets
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
          
          {/* Part 2-2-4: Custom Filter Upload */}
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
                  <Form.Group controlId="form-custom-script-file" style={{height: '90%', width: '90%'}}>
                    <Form.Control type="file" controlId="file" name="file" style={{marginBottom:'0px' , fontSize: '0.7rem', height: '100%'}}/>
                  </Form.Group>
              </form>
            </CInputGroup>
          </div>
        </div>
      </div>
          
      {/* ############## 검색 버튼 ############## */}
      <div style={{gridRow: '4', gridColumn: '2', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr 1fr', justifyItems: 'end', marginTop: '35px'}}>
          <CButton type="button" color="secondary" className="mb-3" variant="outline" id="button-addon2" 
            style={{width: '35%', height: '60%', gridColumn: 5, display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'rgb(38, 73, 132)'}} onClick={handleSearch}>
              <span style={{fontSize: '0.75rem', color: 'white', fontWeight: 'bold'}}>Search</span>
          </CButton>
      </div> 

      {/* Part 3: 리스트뷰 */}
      <div className='ListviewContainer'>
          
        {/* Part 3-1: 제목 */}
        <h5 className='ContainerTitle' style={{marginTop: '15px'}}>
          Dataset List
        </h5>
        
        {/* Part 3-2: 리스트뷰 창 */}
        {listInfo.length>0 ? <DatasetListView listInfo={listInfo}/> : 'No results'}

      </div>

    </div> // end of all
  );
}

export default SearchView;