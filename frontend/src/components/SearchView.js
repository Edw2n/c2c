import './SearchView.css';
import '@coreui/coreui/dist/css/coreui.min.css'
import { CInputGroup, CFormSelect, CButton } from '@coreui/react'
import { Form, Button } from 'react-bootstrap'
import { useEffect, useState } from 'react';
import DatasetListView from './DatasetListView';

function SearchView() {
  const [listInfo,setListInfo] = useState([])

  const animalTypes = ['all','cat','dog']
  const breedTypesDict = {
    'all' : ['all'],
    'cat' : ['all', 'Korean cat', 'Norwegian mix', 'Persian', 'Russian Blue', 'Turkish Angora'],
    'dog' : ['all', 'Afghan Hound', 'American Bully', 'beagle', 'Chihuahua', 'Chow Chow', 'french bulldog', 'German Wirehaired Pointer',
    'golden retriever', 'greyhound', 'Jindo dog', 'labrador retriever', 'Maltese', 'Mixed dog', 'Pomeranian', 'poodle',
    'Samoyed', 'Sapsalgae', 'Shetland Sheepdog', 'Shih Tzu', 'Siberian Husky', 'spitz', 'Toy Poodle', 'Welsh Corgi Pembroke', 'yorkshire terrier']
  }
  const [breedDetailTypes,setBreedTypes] = useState(breedTypesDict['all'])
  const colorTypes = ['all','gray','black','brown','white']
  const neuteringTypes = ['all','Y','N','U']
  const genderTypes = ['all','M','F']
  const cityTypes = ['all','Gwacheon','Paju','Hanam']


  useEffect(()=>{
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

  const handleSubmit = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target);
    console.log(formData)
    console.log(e.target)
    console.log(e.currentTarget)

    formData.append('user_name', e.target[1].value)
    formData.append('pw', e.target[2].value)
    formData.append('title', e.target[3].value)

    const Upload = async () => {

      await fetch('http://0.0.0.0:3000/upload', {
        method: 'POST',
        body: formData
      }).then(resp => {
        resp.json().then(data => {
          console.log(data)
          alert('upload complete')
          setListInfo(prev=>([...data.data]))
        })
      })
    }
    Upload();
  }

  const handleSearch = (e) => {
    e.preventDefault()

    const formData = new FormData();
    console.log(e.target);

    var animal = document.getElementById("animal-type").value;
    var breed = document.getElementById("breed-detail").value;
    var color = document.getElementById("color").value;
    var gender = document.getElementById("gender").value;
    var neutering = document.getElementById("neutering").value;
    var city = document.getElementById("city").value;

    // console.log(selectedValue)
    // var customScript = document.getElementById('form-custom-script-file').value ? true : false;
    // TODO: customSCript form에 붙이기

    formData.append('Breed',animal)
    formData.append('Gender',gender)
    formData.append('Breed_detail',breed)
    formData.append('Color',color)
    formData.append('Neutering',neutering)
    formData.append('City',city)

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

    if(e.currentTarget.id=='animal-type'){
      setBreedTypes(breedTypesDict[e.target.value])

    }
  }
  return (
    <div>
        <div>
        <form onSubmit={handleSubmit} className="mb-3 Uploader" enctype="multipart/form-data" >
          <Form.Group controlId="formFile" >
            <Form.Control type="file" controlId="file" name="file" style={{marginBottom:'0px'}}/>
          </Form.Group>
          <div class="input-group">
            <span class="input-group-text">Information</span>
            <input type="text" aria-label="ID" placeholder="ID" class="form-control"/>
            <input type="password" aria-label="PW" placeholder="pw"  class="form-control"/>
            <input type="text" aria-label="Title" placeholder="title"  class="form-control"/>
          </div>
          <div className="input-group">
            <Button type="submit" variant="outline-secondary" >Upload</Button>
          </div>
        </form>
        </div>
        <div className='Searcher'>
          <text className='leftAlignedText'>Custom Filtering Script Upload</text>
          <text className='leftAlignedText'>Filter 1</text>
          <text className='leftAlignedText'>Filter 2</text>
          <text className='leftAlignedText'>Filter 3</text>
          <text className='leftAlignedText'>Filter 4</text>
          <text className='leftAlignedText'>Filter 5</text>
          <text className='leftAlignedText'>Filter 6</text>
          <text></text>


        </div>
        <CInputGroup className="mb-3">
        <form className='Searcher'>
            <Form.Group controlId="form-custom-script-file" >
              <Form.Control type="file" controlId="file" name="file" style={{marginBottom:'0px'}}/>
            </Form.Group>
            <CFormSelect id='animal-type' size="sm" className="mb-3" aria-label="Small select example" style={{'marginRight':'20px'}} onChange={handleOptions}>
            {animalTypes.map((item,idx)=>(
            <option value={item}>{item}</option>
            ))}
            </CFormSelect>
            <CFormSelect id='breed-detail' size="sm" className="mb-3" aria-label="Small select example" style={{'marginRight':'20px'}} onChange={handleOptions}>
            {breedDetailTypes.map((item,idx)=>(
            <option value={item}>{item}</option>
            ))}
            </CFormSelect>
            <CFormSelect id='color' size="sm" className="mb-3" aria-label="Small select example" style={{'marginRight':'20px'}} onChange={handleOptions}>
            {colorTypes.map((item,idx)=>(
            <option value={item}>{item}</option>
            ))}
            </CFormSelect>
            <CFormSelect id='gender' size="sm" className="mb-3" aria-label="Small select example" onChange={handleOptions}>
                {genderTypes.map((item,idx)=>(
                <option value={item}>{item}</option>
                ))}
            </CFormSelect>
            <CFormSelect id='neutering' size="sm" className="mb-3" aria-label="Small select example" onChange={handleOptions}>
                {neuteringTypes.map((item,idx)=>(
                <option value={item}>{item}</option>
                ))}
            </CFormSelect>
            <CFormSelect id='city' size="sm" className="mb-3" aria-label="Small select example" onChange={handleOptions}>
                {cityTypes.map((item,idx)=>(
                <option value={item}>{item}</option>
                ))}
            </CFormSelect>
            <CButton type="button" color="secondary" className="mb-3" variant="outline" id="button-addon2" onClick={handleSearch}>Search</CButton>
        </form>
        </CInputGroup>
        {listInfo.length>0 ? <DatasetListView listInfo={listInfo}/> : 'No results'}
   </div>
  );
}

export default SearchView;