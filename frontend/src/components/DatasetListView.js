import './DatasetListView.css';
import '@coreui/coreui/dist/css/coreui.min.css';
import { CInputGroup, CFormSelect, CButtonGroup, CButton, CFormCheck } from '@coreui/react';
import { DataGrid, GRID_CHECKBOX_SELECTION_COL_DEF } from '@mui/x-data-grid';
import { Button, Checkbox } from '@mui/material';
import React, { useEffect, useState } from 'react';
import CardView from './CardView';

function DatasetListView({listInfo, userName, onManagesInfo}) {
  console.log("listinfo: ", listInfo)

  const [RowsInfo, setRowsInfo] = useState(listInfo);
  const [selectedRow, setSelectedRow] = useState([]);
  const [selectedCheckboxes, setSelectedCheckboxes] = useState([]);
  const [selectedPrices, setSelectedPrices] = useState([]);
  const [totalPrice, setTotalPrice] = useState(0);

  // 체크박스 핸들러
  const handleHeaderCheckboxChange = (event) => {
    const isChecked = event.target.checked;
    const updatedCheckboxes = {};

    RowsInfo.forEach((row) => {
      updatedCheckboxes[row.d_id] = isChecked;
    });

    setSelectedCheckboxes(updatedCheckboxes);

    if (isChecked) {
      const prices = RowsInfo.map((row) => row.Price);
      setSelectedPrices(prices);
      calculateTotalPrice(prices);
      setSelectedRow(RowsInfo.map((row) => row.d_id));
    } else {
      setSelectedPrices([]);
      setTotalPrice([]);
      setSelectedRow([]);
    }
  };
  
  useEffect(() => {
    const defaultCheckboxes = {};
    RowsInfo.forEach((row) => {
      defaultCheckboxes[row.d_id] = false;
    });
    setSelectedCheckboxes(defaultCheckboxes);
  }, [RowsInfo]);

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
    { field: 'Description', headerName: 'Description', width: 200},
    { field: 'QCstate', headerName: 'QC State', width: 80},
    { field: 'QCscore', headerName: 'QC Score', width: 70},
    { field: 'Objects', headerName: 'Objects', width: 320},
    { field: 'UploadDate', headerName: 'Upload Date', width: 150},
    { field: 'SalesCount', headerName: 'Sales Count', width: 80},
    { field: 'MatchedData', headerName: 'Matched Data', width: 90},
    { field: 'Price', headerName: 'Price($)', width: 80},
    { field: 'PricePerImage', headerName: 'Avg. Price($)', width: 110},
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
  const rows = RowsInfo.map((row) => (
    {id: row.d_id, Uploader: row.Uploader, Title: row.Title, Description: row.Description,
      QCstate: row.QCstate, QCscore: row.QCscore, Objects: row.Objects, UploadDate: row.UploadDate, 
      SalesCount: row.SalesCount, Likes: row.Likes, MatchedData: row.MatchedData, Price: row.Price, PricePerImage: row.PricePerImage, Listview: row.items.listview, Cardview: row.items.cardview}
  ));


  // detail info
  const [showDetail, setShowDetail] = useState(false);
  const [selectedForDetail, setSelectedForDetail] = useState([]); // detail 보려고 선택한 row의 id를 저장하는 배열
  
      // 여기 받아오는 data 형태에 따라 setdetailRow 수정해야함
  const [DetailListview, setDetailListview] = useState([]);
  const [DetailCardview, setDetailCardview] = useState([]);

  const handleRowClick = (param) => {
    console.log("param.row.items: ", param.items)
    if (param.row.id === selectedForDetail) {
      setSelectedForDetail(null);
      setShowDetail(false);
      setDetailListview([]);
      setDetailCardview([]);
    } else {
      const current_row = RowsInfo.filter((rows) => rows.d_id === param.row.id);
      const selectedDetailListview = current_row[0].items.listview;
      const selectedDetailCardview = current_row[0].items.cardview;
      setSelectedForDetail(param.row.id);
      setShowDetail(true);
      setDetailListview(selectedDetailListview);
      setDetailCardview(selectedDetailCardview);
    }
  }

  // 체크박스핸들러_디테일
  const [selectedRow_img, setSelectedRow_img] = useState([]);
  const [selectedCheckboxes_img, setSelectedCheckboxes_img] = useState([]);

  const handleHeaderCheckboxChange_img = (event) => {
    const isChecked = event.target.checked;
    const updatedCheckboxes = {};

    RowsInfo.forEach((row) => {
      updatedCheckboxes[row.items.listview.img_id] = isChecked;
    });

    setSelectedCheckboxes_img(updatedCheckboxes);

    if (isChecked) {
      const prices = RowsInfo.map((row) => row.Price);
      setSelectedPrices(prices);
      calculateTotalPrice(prices);
      setSelectedRow_img(RowsInfo.map((row) => row.items.listview.img_id));
    } else {
      setSelectedPrices([]);
      setTotalPrice([]);
      setSelectedRow_img([]);
    }
  };
  
  useEffect(() => {
    const defaultCheckboxes = {};
    RowsInfo.forEach((row) => {
      defaultCheckboxes[row.items.listview.img_id] = false;
    });
    setSelectedCheckboxes_img(defaultCheckboxes);
  }, [RowsInfo]);
  
  const handleCheckboxChange_img = (event, rowId, price) => {
    setSelectedCheckboxes_img((prevState) => ({
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

      setSelectedRow_img((prevSelectedRow) => {
        if (event.target.checked) {
          return [...prevSelectedRow, rowId];
        } else {
          return prevSelectedRow.filter((selected) => selected !== rowId);
        }
      });
  };

    // 추가로, detail info에서 선택하여 장바구니에 담는 경우 dataset 전체가 아니라 dataset의 subset이 들어가야 함



  const [DetailMode,setDetailMode] = useState('cardview')

  const handleDetailMode = (e) => {
    setDetailMode(e.currentTarget.id) // 여기 수정
  }

  const columns_listview = [
    { field: 'id', headerName: 'Image ID', width: 90},
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
          checked={Object.values(selectedCheckboxes_img).every((value) => value)}
          onChange={handleHeaderCheckboxChange_img}
        />
      ),
      renderCell: (params) => (
        <Checkbox
          color="primary"
          checked={selectedCheckboxes_img[params.row.id] || false}
          onChange={(event) => handleCheckboxChange_img(event, params.row.id, params.row.Price)}
        />
      ),
    }
  ];


  const rows_listview = DetailListview.map((row) => (
    {dataset_id: row.dataset_id, id: row.img_id, QCstate: row.QCstate, QCscore: row.QCscore, Objects: row.Objects,
      roll: row.roll, pitch: row.pitch, yaw: row.yaw, wx: row.wx, wy: row.wy, wz: row.wz, vf: row.vf, vl: row.vl, vu: row.vu, ax: row.ax, ay: row.ay, az: row.az, Price: row.Price}
  ));

  const handleAddToCart = () => {
    const selectedRows = RowsInfo.filter((row) => selectedCheckboxes[row.d_id]);
    if (selectedRows.length === 0 && selectedRow_img.length == 0) {
      alert('Please select at least one item!');
    }
    else {
      alert('Added to Cart!');
      const formData = new FormData();
      

      const rowsItems = selectedRows
                                .map((row) => row.items.listview
                                .map((row)=> row.img_id)
                                );                                
      const selected = selectedRow_img.concat(...rowsItems)
      console.log("selected:", selected)

      formData.append('user_name',userName)
      formData.append('items',selected)
      formData.append('dataset-name',"mine") // todo update

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
              onManagesInfo(prev => (
                {...prev,
                  uploads: data.manage_data.uploaded.rows,
                  transctions: data.manage_data.transactions.rows,
                  login: 'true',
                  userInfo: {
                    username: userName,
                    pw: prev.userInfo.pw,
                    cash: data.manage_data.cachecash,
                  }
                }))
              // console.log("bought data: ", data.manage_data.transactions.rows)
              // const newRows = data.manage_data.transactions.rows
              // setTransactRows(prevRows => [...prevRows,...newRows]);
              // console.log("trows: ", TRows)
              // setShowInput(false);
              // // 캐시 추가되면 주석 해제 처리할 것
              // const cash_remain = data.manage_data.cache;
              // console.log("cash: ", cash_remain)
              // onAddUserInfo(userName, UserInfo.pw, cash_remain)
            }
          })
        })
      }
      buy();
    }
    
  };
 
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
          onRowClick={handleRowClick}
          style={{fontSize: '0.7rem'}}

        />

        <div style={{display: 'grid', gridTemplateColumns: '30% 30% 10% 22% 8%', justifyItems: 'end', marginTop: '5px'}}>
            <span style={{fontSize: '0.8rem', fontWeight: 'bold', gridColumn: '4', justifySelf: 'end', marginTop: '5px', marginRight: '5px'}}>Price for Selected Items : {totalPrice} $</span>
            <CButton type="button" color="secondary" className="mb-3" variant="outline" id="button-addon2" 
              style={{width: '90%', height: '60%', gridColumn: '5', display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'rgb(38, 73, 132)'}}
              onClick={handleAddToCart}>
                <span style={{fontSize: '0.7rem', color: 'white', fontWeight: 'bold'}}>Buy</span>
            </CButton>
        </div> 
        {showDetail && (
          <div>  
            <div style={{justifyContent: 'start', textAlign: 'left', display: 'grid', gridTemplateColumns: '50% 50%'}}>
              <h5 style={{gridColumn: '1', fontWeight: 'bold'}}>
                Detail Information
              </h5>
              <CButtonGroup horizontal role="group" aria-label="Vertical button group" style={{justifySelf: 'end', width: '30%', marginBottom:'10px'}}>
                <CFormCheck
                  type="radio"
                  onClick={handleDetailMode}
                  button={{ color: 'danger', variant: 'outline', size: 'sm' }}
                  name="vbtnradio"
                  id="cardview"
                  autoComplete="off"
                  label="View Images"
                  defaultChecked
                />
                <CFormCheck
                  type="radio"
                  onClick={handleDetailMode}
                  button={{ color: 'danger', variant: 'outline', size: 'sm' }}
                  name="vbtnradio"
                  id="listview"
                  autoComplete="off"
                  label="View Lists"
                />
              </CButtonGroup>
            </div>
            {DetailMode === 'listview' ? ( 
              <DataGrid
              rows={rows_listview}
              checkboxSelection
              columns={columns_listview}
              initialState={{
                pagination: { paginationModel: {pageSize: 10}}
              }}
              disableColumnMenu
              disableSelectionOnClick
              hideFooterSelectedRowCount
              autoHeight
              style={{fontSize: '0.7rem'}}
            />
            ) : (
              <CardView cardviewInfo={DetailCardview}/>
            )}
          </div>
        )}
    </div>
  ); 
}


export default DatasetListView;