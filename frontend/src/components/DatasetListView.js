import './DatasetListView.css';
import '@coreui/coreui/dist/css/coreui.min.css';
import { CInputGroup, CFormSelect, CButtonGroup, CButton, CFormCheck } from '@coreui/react';
import { DataGrid, GRID_CHECKBOX_SELECTION_COL_DEF } from '@mui/x-data-grid';
import { Button, Checkbox } from '@mui/material';
import React, { useEffect, useState } from 'react';

function DatasetListView({listInfo}) {
  console.log("listinfo: ", listInfo)

  // return (
  //  <div className="ResultList">
  //      {listInfo.map((item,idx) => <p> row {item}</p>)}
  //  </div>
  //);

  const [items, setItems] = useState(listInfo);
  const [selectedRow, setSelectedRow] = useState([]);
  const [selectedCheckboxes, setSelectedCheckboxes] = useState([]);
  const [selectedPrices, setSelectedPrices] = useState([]);
  const [totalPrice, setTotalPrice] = useState(0);

  // 체크박스 핸들러
  const handleHeaderCheckboxChange = (event) => {
    const isChecked = event.target.checked;
    const updatedCheckboxes = {};

    items.forEach((row) => {
      updatedCheckboxes[row.d_id] = isChecked;
    });

    setSelectedCheckboxes(updatedCheckboxes);

    if (isChecked) {
      const prices = items.map((row) => row.Price);
      setSelectedPrices(prices);
      calculateTotalPrice(prices);
      setSelectedRow(items.map((row) => row.d_id));
    } else {
      setSelectedPrices([]);
      setTotalPrice([]);
      setSelectedRow([]);
    }
  };
  
  useEffect(() => {
    const defaultCheckboxes = {};
    items.forEach((row) => {
      defaultCheckboxes[row.d_id] = false;
    });
    setSelectedCheckboxes(defaultCheckboxes);
  }, [items]);

  const handleCheckboxChange = (event, rowId, price) => {
    setSelectedCheckboxes((prevState) => ({
      ...prevState,
      [rowId]: event.target.checked,
      }));


      setSelectedPrices((prevPrices) => {
        const updatedPrices = event.target.checked
          ? [...prevPrices, price]
          : prevPrices.filter((p) => p !== price);
        calculateTotalPrice(updatedPrices);
        return updatedPrices;
      });

      setSelectedRow((prevSelectedRow) => {
        if (event.target.checked) {
          return [...prevSelectedRow, rowId];
        } else {
          return prevSelectedRow.filter((selected) => selected !== rowId);
        }
      });
  };

  const calculateTotalPrice = (newSelectedPrices) => {
    const sum = newSelectedPrices.reduce((acc, price) => acc + price, 0);
    setTotalPrice(sum);
  };

  // defaul datagrid column, row 정의
  const columns = [
    { field: 'Uploader', headerName: 'Uploader', width: 65},
    { field: 'Title', headerName: 'Dataset Name', width: 90},
    { field: 'Description', headerName: 'Description', width: 130},
    { field: 'QCstate', headerName: 'QC State', width: 80},
    { field: 'QCscore', headerName: 'QC Score', width: 70},
    { field: 'Objects', headerName: 'Objects', width: 160},
    { field: 'UploadDate', headerName: 'Upload Date', width: 80},
    { field: 'SalesCount', headerName: 'Sales Count', width: 80},
    { field: 'Likes', headerName: 'Likes', width: 50},
    { field: 'MatchedData', headerName: 'Matched Data', width: 90},
    { field: 'Price', headerName: 'Price($)', width: 80},
    { field: 'PricePerImage', headerName: 'Price per Image($)', width: 110},
    { field: 'LikeButton', headerName: '', width:'80',
      renderCell: (params) => (
        <strong>
          <Button
            variant="contained"
            color="primary"
            size="small"
            style={{fontSize: '0.6rem'}}>
            Like
          </Button>
        </strong>
      )
    },
    {
      ...GRID_CHECKBOX_SELECTION_COL_DEF,
      width: '80',
      headerName: '',
      renderHeader: () => (
        <Checkbox
          color="primary"
          checked={Object.values(selectedCheckboxes).every((value) => value)}
          onChange={handleHeaderCheckboxChange}
        />
      ),
      renderCell: (params) => (
        <Checkbox
          color="primary"
          checked={selectedCheckboxes[params.row.id] || false}
          onChange={(event) => handleCheckboxChange(event, params.row.id, params.row.Price)}
        />
      ),
    }

  ];
  const rows = items.map((row) => (
    {id: row.d_id, Uploader: row.Uploader, Title: row.Title, Description: row.Description,
      QCstate: row.QCstate, QCscore: row.QCscore, Objects: row.Objects, UploadDate: row.UploadDate, 
      SalesCount: row.SalesCount, Likes: row.Likes, MatchedData: row.MatchedData, Price: row.Price, PricePerImage: row.PricePerImage}
  ));


  // detail info
  const [showDetail, setShowDetail] = useState(false);
  const [selectedForDetail, setSelectedForDetail] = useState([]); // detail 보려고 선택한 row의 id를 저장하는 배열
  
      // 여기 받아오는 data 형태에 따라 setdetailRow 수정해야함
  const [DetailListview, setDetailListview] = useState([]);
  const [DetailCardview, setDetailCardview] = useState([]);

  /*
  const handleRowClick = (param) => {
    if (param.row.d_id === selectedForDetail) {
      setSelectedForDetail(null);
      setShowDetail(false);
      setDetailListview([]);
      setDetailCardview([]);
    } else {
      const selectedDetailListview = items.items.listview.filter((row) => row.dataset_id === param.row.d_id);
      const selectedDetailCardview = items.items.cardview.filter((row) => row.dataset_id === param.row.d_id);
      setSelectedForDetail(param.row.d_id);
      setShowDetail(true);
      setDetailListview(selectedDetailListview);
      setDetailCardview(selectedDetailCardview);
    }

  };*/
    // 추가로, detail info에서 선택하여 장바구니에 담는 경우 dataset 전체가 아니라 dataset의 subset이 들어가야 함



  const [DetailMode,setDetailMode] = useState('listview')

  const handleDetailMode = (e) => {
    setDetailMode(e.currentTarget.id) // 여기 수정
  }

  const columns_detail = [
    { field: 'img_id', headerName: 'Image ID', width: 90},
    { field: 'QCstate', headerName: 'QC State', width: 70},
    { field: 'QCscore', headerName: 'QC Score', width: 80},
    { field: 'Objects', headerName: 'Objects', width: 130},
    { field: 'roll', headerName: 'Roll', width: 60},
    { field: 'pitch', headerName: 'Pitch', width: 60},
    { field: 'yaw', headerName: 'Yaw', width: 60},
    { field: 'wx', headerName: 'Wx', width: 60},
    { field: 'wy', headerName: 'Wy', width: 60},
    { field: 'wz', headerName: 'Wz', width: 60},
    { field: 'vf', headerName: 'Vf', width: 60},
    { field: 'vl', headerName: 'Vl', width: 60},
    { field: 'vu', headerName: 'Vu', width: 60},
    { field: 'ax', headerName: 'Ax', width: 60},
    { field: 'ay', headerName: 'Ay', width: 60},
    { field: 'az', headerName: 'Az', width: 60},
    { field: 'Price', headerName: 'Price($)', width: 70},
    {
      ...GRID_CHECKBOX_SELECTION_COL_DEF,
      width: '70',
      headerName: '',
      renderHeader: () => (
        <Checkbox
          color="primary"
          checked={Object.values(selectedCheckboxes).every((value) => value)}
          onChange={handleHeaderCheckboxChange}
        />
      ),
      renderCell: (params) => (
        <Checkbox
          color="primary"
          checked={selectedCheckboxes[params.row.id] || false}
          onChange={(event) => handleCheckboxChange(event, params.row.id, params.row.Price)}
        />
      ),
    }
  ];

  /*
  const rows_detail = items.items.listview.map((row) => (
    {dataset_id: row.dataset_id, img_id: row.img_id, QCstate: row.QCstate, QCscore: row.QCscore, Objects: row.Objects,
      roll: row.roll, pitch: row.pitch, yaw: row.yaw, wx: row.wx, wy: row.wy, wz: row.wz, vf: row.vf, vl: row.vl, vu: row.vu, ax: row.ax, ay: row.ay, az: row.az, Price: row.Price}
  ));
*/



/*
  const handleAddToCart = () => {
    const selectedRows = items.filter((row) => selectedCheckboxes[row.d_id]);
    if (selectedRows.length === 0) {
      alert('Please select at least one item!');
    }
    else {
      alert('Added to Cart!');
      onAddToCart(selectedRows);
    }
  };
*/
  // 리스트뷰 표시 부분
  return (
    <div className='ListViewContainerDetail'>
        <DataGrid
          rows={rows}
          checkboxSelection 
          columns={columns}
          initialState={{
            pagination: { paginationModel: {pageSize: 10}}
          }}
          style={{fontSize: '0.7rem'}}

        />

        <div style={{display: 'grid', gridTemplateColumns: '30% 30% 10% 22% 8%', justifyItems: 'end', marginTop: '5px'}}>
            <span style={{fontSize: '0.8rem', fontWeight: 'bold', gridColumn: '4', justifySelf: 'end', marginTop: '5px', marginRight: '5px'}}>Price for Selected Items : {totalPrice} $</span>
            <CButton type="button" color="secondary" className="mb-3" variant="outline" id="button-addon2" 
              style={{width: '90%', height: '60%', gridColumn: '5', display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'rgb(38, 73, 132)'}}>
                <span style={{fontSize: '0.7rem', color: 'white', fontWeight: 'bold'}}>Add to Cart</span>
            </CButton>
        </div> 
        {showDetail && (
          <div style={{justifyContent: 'start', textAlign: 'left'}}>
          <h5 style={{fontWeight: 'bold'}}>
            Detail Information
          </h5>
          <CButtonGroup horizontal role="group" aria-label="Vertical button group" style={{marginBottom:'10px', fontSize: '0.5rem'}}>
            <CFormCheck
              type="radio"
              onClick={handleDetailMode}
              button={{ color: 'danger', variant: 'outline', size: 'sm' }}
              name="vbtnradio"
              id="cardview"
              autoComplete="off"
              label="View Images"
            />
            <CFormCheck
              type="radio"
              onClick={handleDetailMode}
              button={{ color: 'danger', variant: 'outline', size: 'sm' }}
              name="vbtnradio"
              id="listview"
              autoComplete="off"
              label="View Lists"
              defaultChecked
            />
          </CButtonGroup>
          
          {/* DetailMode=='listview' ? 
            <DataGrid
              rows={DetailListview}
              checkboxSelection
              columns={columns_detail}
              initialState={{
                pagination: { paginationModel: {pageSize: 10}}
              }}
              disableColumnMenu
              disableSelectionOnClick
              hideFooterSelectedRowCount
              autoHeight
              style={{fontSize: '0.7rem'}}
            /> : 
            <div/> */}
        </div>
        )}
    </div>
  );
};

export default DatasetListView;