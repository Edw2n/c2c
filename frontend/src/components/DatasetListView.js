import './DatasetListView.css';
import '@coreui/coreui/dist/css/coreui.min.css';
import { CInputGroup, CFormSelect, CButton } from '@coreui/react';
import { DataGrid, GRID_CHECKBOX_SELECTION_COL_DEF } from '@mui/x-data-grid';
import { Button, Checkbox } from '@mui/material';
import React, { useEffect, useState } from 'react';

function DatasetListView({listInfo}) {
  console.log(listInfo[0].url)

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
///////////////
/*  
  const handleRowClick = (params) => {
    setSelectedRow(params.d_id);
  };
  
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
    } else {
      setSelectedPrices([]);
      setTotalPrice([]);
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
  };

  const calculateTotalPrice = (newSelectedPrices) => {
    const sum = newSelectedPrices.reduce((acc, price) => acc + price, 0);
    setTotalPrice(sum);
  };
*/
  // 기본 datagrid column, row 정의
  const columns = [
    { field: 'Uploader', headerName: 'Uploader', width: 65},
    { field: 'Title', headerName: 'Dataset Name', width: 90},
    { field: 'Description', headerName: 'Description', width: 130},
    { field: 'QCstate', headerName: 'QC State', width: 80},
    { field: 'QCscore', headerName: 'QC Score', width: 70},
    { field: 'Objects', headerName: 'Objects', width: 130},
    { field: 'UploadDate', headerName: 'Upload Date', width: 80},
    { field: 'SalesCount', headerName: 'Sales Count', width: 80},
    { field: 'Likes', headerName: 'Likes', width: 70},
    { field: 'MatchedData', headerName: 'Matched Data', width: 90},
    { field: 'Price', headerName: 'Price($)', width: 80},
    { field: 'PricePerImage', headerName: 'Price per Image($)', width: 110},
    { field: 'Like', headerName: '', width:'80',
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
          checked={selectedCheckboxes[params.row.d_id] || false}
          onChange={(event) => handleCheckboxChange(event, params.row.d_id, params.row.Price)}
        />
      ),
    }

  ];
  const rows = items.map((row) => (
    {id: row.d_id, Uploader: row.Uploader, Title: row.Title, Description: row.Description,
      QCstate: row.QCstate, QCscore: row.QCscore, Objects: row.Objects, UploadDate: row.UploadDate, 
      SalesCount: row.SalesCount, MatchedData: row.MatchedData, Price: row.Price,  PricePerImage: row.PricePerImage}
  ));

  // detail datagrid
  const [showDetail, setShowDetail] = useState(false);
  const [selectedForDetail, setSelectedForDetail] = useState([]); // detail 보려고 선택한 row의 id를 저장하는 배열

  const [DetailListview, setDetailListview] = useState([]);
  const [DetailCardview, setDetailCardview] = useState([]);
  
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

  };

  const columns_detail = [
    { field: 'filename', headerName: 'File Name', width: 90},
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
          checked={selectedCheckboxes[params.row.img_id] || false}
          onChange={(event) => handleCheckboxChange(event, params.row.img_id, params.row.Price)}
        />
      ),
    }
  ];
  
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
  const rows_detail = [
    { id: 1, filename: 'Snow', QCstate: 'QCed', QCscore: 0.9, Objects: 'Snow', roll: 0.1, pitch: 0.2, yaw: 0.3, wx: 0.4, wy: 0.5, wz: 0.6, vf: 0.7, vl: 0.8, vu: 0.9, ax: 0.1, ay: 0.2, az: 0.3, Price: 100},
  ]

  // 리스트뷰 표시 부분
  return (
    <div className='ListViewContainerDetail'>
        <DataGrid
          rows={rows}
          checkboxSelection 
          columns={columns}
          pageSize={10}
          initialState={{
            pagination: { paginationModel: {pageSize: 10}}
          }}
          style={{fontSize: '0.7rem'}}
          onRowClick={handleRowClick}
        />

        <div style={{display: 'grid', gridTemplateColumns: '30% 30% 10% 22% 8%', justifyItems: 'end', marginTop: '5px'}}>
            <span style={{fontSize: '0.8rem', fontWeight: 'bold', gridColumn: '4', justifySelf: 'end', marginTop: '5px', marginRight: '5px'}}>Price for Selected Items : {totalPrice} $</span>
            <CButton type="button" color="secondary" className="mb-3" variant="outline" id="button-addon2" 
              style={{width: '92%', height: '60%', gridColumn: '5', display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'rgb(38, 73, 132)'}}>
                <span style={{fontSize: '0.7rem', color: 'white', fontWeight: 'bold'}}>Add to Cart</span>
            </CButton>
        </div> 

        {/*
        <div style={{justifyContent: 'start', textAlign: 'left'}}>
          <h5 style={{fontWeight: 'bold'}}>
            Detail Info
          </h5>
          <DataGrid
            rows={rows_detail}
            columns={columns_detail}
            pageSize={10}
            disableColumnMenu
            disableSelectionOnClick
            hideFooterSelectedRowCount
            autoHeight
            style={{fontSize: '0.7rem'}}
          />
        </div>
  */}
    </div>
  );
};

export default DatasetListView;