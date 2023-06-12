import { Image, Carousel, Form, ProgressBar } from 'react-bootstrap'
import { DataGrid, GridColDef, GridValueGetterParams, GRID_CHECKBOX_SELECTION_COL_DEF } from '@mui/x-data-grid';
import React, { useEffect, useState } from 'react';
import './UserpageView.css'
import { textAlign } from '@mui/system';
import '@coreui/coreui/dist/css/coreui.min.css';
import { Dialog, DialogTitle, DialogContent, DialogActions, TextField } from '@material-ui/core';
import { CInputGroup, CFormSelect, CButtonGroup, CButton, CFormCheck } from '@coreui/react';
import { Button, Checkbox } from '@mui/material';

function UserPageView({user_name, uploadedRows, transactRows, cartList, cartList_img, UserInfo, onAddUserInfo}) {
  console.log("uploaded rows: ", uploadedRows)
  console.log('trans: ', transactRows)
  const [selectedIDs, setSelectedIDs] = useState([])
  const [URows,setURows] = useState(uploadedRows)
  const [TRows,setTransactRows] = useState(transactRows || [])

  // Delete 버튼 기능
  const deleteSelected = async (e) => {

      const formData = new FormData();
      formData.append('aid_list',JSON.stringify(selectedIDs))

      await fetch('http://0.0.0.0:3000/delete', {
        method: 'POST',
        body: formData
      }).then(resp => {
        
          setURows(prev => prev.filter( data => 
              !(selectedIDs.includes(data.id))))
  })}

  // Buy 버튼 기능
  const [datasetName, setDatasetName] = useState('');
  const [showInput, setShowInput] = useState(false);
  
  const buyDataset = (e) => {
    e.preventDefault();
    setShowInput(true);
  };

  const handleInputChange = (e) => {
    setDatasetName(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData();
    
    var userName = UserInfo.username;
    var selectedImgIds = cartList_img;
    var defiendDatasetname = datasetName;

    console.log("user name: ", userName)
    console.log("cartlist_img: ", cartList_img)
    console.log("defined dataset name: ", defiendDatasetname)

    formData.append('user_name',userName)
    formData.append('items',selectedImgIds)
    formData.append('dataset-name',defiendDatasetname)

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
            console.log("bought data: ", data.manage_data.transactions.rows)
            const newRows = data.manage_data.transactions.rows
            setTransactRows(prevRows => [...prevRows,...newRows]);
            console.log("trows: ", TRows)
            setShowInput(false);
            // 캐시 추가되면 주석 해제 처리할 것
            const cash_remain = data.manage_data.cache;
            console.log("cash: ", cash_remain)
            onAddUserInfo(userName, UserInfo.pw, cash_remain)
          }
        })
      })
    }
    buy();
  }
    
   

  // 1. 장바구니

  const [selectedRow, setSelectedRow] = useState([]);
  const [selectedCheckboxes, setSelectedCheckboxes] = useState([]);
  const [selectedPrices, setSelectedPrices] = useState([]);
  const [totalPrice, setTotalPrice] = useState(0);
  
      // 여기 받아오는 data 형태에 따라 setdetailRow 수정해야함
  const [detailRow, setdetailRow] = useState([]);
/*
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
      // const selectedDetailCardview = current_row[0].items.cardview;
      setSelectedForDetail(param.row.id);
      setShowDetail(true);
      setDetailListview(selectedDetailListview);
      // setDetailCardview(selectedDetailCardview);
    }
  }
*/
  const handleHeaderCheckboxChange = (event) => {
    const isChecked = event.target.checked;
    const updatedCheckboxes = {};

    cartList.forEach((row) => {
      updatedCheckboxes[row.d_id] = isChecked;
    });

    setSelectedCheckboxes(updatedCheckboxes);

    if (isChecked) {
      const prices = cartList.map((row) => row.Price);
      setSelectedPrices(prices);
      calculateTotalPrice(prices);
    } else {
      setSelectedPrices([]);
      setTotalPrice(0);
    }
  };

  useEffect(() => {
    const defaultCheckboxes = {};
    cartList.forEach((row) => {
      defaultCheckboxes[row.d_id] = true; // 기본 값으로 true 설정
    });
    setSelectedCheckboxes(defaultCheckboxes);
    const prices = cartList.map((row) => row.Price);
    setSelectedPrices(prices);
    calculateTotalPrice(prices);
  }, [cartList]);

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

  const columns_cart = [
    { field: 'Uploader', headerName: 'Uploader', width: 65},
    { field: 'Title', headerName: 'Dataset Name', width: 90},
    { field: 'Description', headerName: 'Description', width: 130},
    { field: 'QCstate', headerName: 'QC State', width: 70},
    { field: 'QCscore', headerName: 'QC Score', width: 70},
    { field: 'Objects', headerName: 'Objects', width: 260},
    { field: 'UploadDate', headerName: 'Upload Date', width: 120},
    { field: 'Likes', headerName: 'Likes', width: 45},
    { field: 'SalesCount', headerName: 'Sales Count', width: 80},
    { field: 'MatchedData', headerName: 'Items', width: 50},
    { field: 'Price', headerName: 'Price($)', width: 60},
    { field: 'PricePerImage', headerName: 'Avg. Price($)', width: 80},
    {
      ...GRID_CHECKBOX_SELECTION_COL_DEF,
      width: '60',
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
  const rows_cart = cartList.map((row) => (
    {id: row.d_id, Uploader: row.Uploader, Title: row.Title, Description: row.Description,
      QCstate: row.QCstate, QCscore: row.QCscore, Objects: row.Objects, UploadDate: row.UploadDate, 
      Likes: row.Likes, SalesCount: row.SalesCount, MatchedData: row.MatchedData, Price: row.Price,  PricePerImage: row.PricePerImage}
  ));

  // 장바구니 - detail
  const [showDetail, setShowDetail] = useState(false);
  const [selectedForDetail, setSelectedForDetail] = useState([]); // detail 보려고 선택한 row의 id를 저장하는 배열
  
      // 여기 받아오는 data 형태에 따라 setdetailRow 수정해야함
  const [DetailListview, setDetailListview] = useState([]);
  const [DetailCardview, setDetailCardview] = useState([]);

  const columns_cart_detail = [
    { field: 'filename', headerName: 'Image ID', width: 100},
    { field: 'QCstate', headerName: 'QC State', width: 70},
    { field: 'QCscore', headerName: 'QC Score', width: 80},
    { field: 'Objects', headerName: 'Objects', width: 130},
    { field: 'roll', headerName: 'Roll', width: 50},
    { field: 'pitch', headerName: 'Pitch', width: 50},
    { field: 'yaw', headerName: 'Yaw', width: 50},
    { field: 'wx', headerName: 'Wx', width: 50},
    { field: 'wy', headerName: 'Wy', width: 50},
    { field: 'wz', headerName: 'Wz', width: 50},
    { field: 'vf', headerName: 'Vf', width: 50},
    { field: 'vl', headerName: 'Vl', width: 50},
    { field: 'vu', headerName: 'Vu', width: 50},
    { field: 'ax', headerName: 'Ax', width: 50},
    { field: 'ay', headerName: 'Ay', width: 50},
    { field: 'az', headerName: 'Az', width: 50},
    { field: 'Price', headerName: 'Price($)', width: 90},
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

  // 2. 업로드한 데이터셋
  const columns_uploaded = [
    { field: 'Uploader', headerName: 'Uploader', width: 65},
    { field: 'Title', headerName: 'Dataset Name', width: 90},
    { field: 'Description', headerName: 'Description', width: 130},
    { field: 'QCstate', headerName: 'QC State', width: 80},
    { field: 'QCscore', headerName: 'QC Score', width: 70},
    { field: 'Objects', headerName: 'Objects', width: 130},
    { field: 'UploadDate', headerName: 'Upload Date', width: 80},
    { field: 'Likes', headerName: 'Likes', width: 60},
    { field: 'SalesCount', headerName: 'Sales Count', width: 80},
    { field: 'MatchedData', headerName: 'Matched Data', width: 90},
    { field: 'Price', headerName: 'Price($)', width: 80},
    { field: 'PricePerImage', headerName: 'Avg. Price($)', width: 110},
    { field: 'Delete', headerName: '', width:'80',
    renderCell: (params) => (
      <strong>
        <Button
          variant="contained"
          color="primary"
          size="small"
          style={{fontSize: '0.6rem'}}>
          Delete
        </Button>
      </strong>
    )
  },
  ];    
  const rows_uploaded = URows.map((row) => (
    {id: row.d_id, Uploader: row.Uploader, Title: row.Title, Description: row.Description,
      QCstate: row.QCstate, QCscore: row.QCscore, Objects: row.Objects, UploadDate: row.UploadDate, 
      Likes: row.Likes, SalesCount: row.SalesCount, MatchedData: row.MatchedData, Price: row.Price,  PricePerImage: row.PricePerImage}
  ));

  // 3. 구/판매한 데이터셋
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);

  const openFeedbackDialog = () => {
    setIsFeedbackOpen(true);
  };

  const closeFeedbackDialog = () => {
    setIsFeedbackOpen(false);
  };
    
   // scoring
  const FeedbackDialog = ({ onClose }) => {
    const [rating, setRating] = useState(0);
    const [comment, setComment] = useState('');
  
    const handleRatingChange = (event) => {
      setRating(Number(event.target.value));
    };
  
    const handleCommentChange = (event) => {
      setComment(event.target.value);
    };
  
    const handleSubmit = (event) => {
      event.preventDefault();
      console.log('Rating:', rating);
      console.log('Comment:', comment);
      onClose();
      alert("Thanks for your feedback!!")
    };
  
    return (
      <Dialog open={true} onClose={onClose}>
        <DialogTitle>Leave Score</DialogTitle>
        <DialogContent>
          <form onSubmit={handleSubmit}>
            <TextField
              label="Rating"
              type="number"
              value={rating}
              onChange={handleRatingChange}
              inputProps={{ min: 0, max: 5, step: 1 }}
              required
            />
            <TextField
              label="Comment"
              value={comment}
              onChange={handleCommentChange}
              multiline
              rows={4}
              required
            />
            <DialogActions>
              <Button type="submit" color="primary">Submit</Button>
              <Button onClick={onClose} color="primary">Cancel</Button>
            </DialogActions>
          </form>
        </DialogContent>
      </Dialog>
    );
  };

  const leaveScore = (e) => {
    e.preventDefault();
    openFeedbackDialog();
  };

  const columns_transaction = [
    { field: 'Title', headerName: 'Dataset Name', width: 90},
    { field: 'Description', headerName: 'Description', width: 120},
    { field: 'QCstate', headerName: 'QC State', width: 80},
    { field: 'QCscore', headerName: 'QC Score', width: 70},
    { field: 'Objects', headerName: 'Objects', width: 130},
    { field: 'UploadDate', headerName: 'Upload Date', width: 80},
    { field: 'Likes', headerName: 'Likes', width: 60},
    { field: 'SalesCount', headerName: 'Sales Count', width: 80},
    { field: 'MatchedData', headerName: 'Matched Data', width: 90},
    { field: 'Price', headerName: 'Price($)', width: 80},
    { field: 'PricePerImage', headerName: 'Avg. Price($)', width: 90},
    { field: 'Download', headerName: '', width:'100',
      renderCell: (params) => (
        <strong>
          <Button
            variant="contained"
            color="primary"
            size="small"
            onClick={() => downloadDataset(params.row.id)}
            style={{fontSize: '0.6rem'}}>
            Download
          </Button>
        </strong>
      )
    },
    { field: 'Feedback', headerName: '', width:'110',
      renderCell: (params) => (
        <strong>
          <Button
            variant="contained"
            color="primary"
            size="small"
            onClick={leaveScore}
            style={{fontSize: '0.6rem'}}>
            Leave Score
          </Button>
          {isFeedbackOpen && (
            <FeedbackDialog onClose={closeFeedbackDialog} />
          )}
        </strong>
      )
    },
  ];
  const rows_transaction = TRows.map((row) => (
    {id: row.d_id, Uploader: row.Uploader, Title: row.Title, Description: row.Description,
      QCstate: row.QCstate, QCscore: row.QCscore, Objects: row.Objects, UploadDate: row.UploadDate, 
      Likes: row.Likes, SalesCount: row.SalesCount, MatchedData: row.MatchedData, Price: row.Price,  PricePerImage: row.PricePerImage}
  ));

  const downloadDataset = (rowId) => {

    const formData = new FormData();
    formData.append('txp_id', rowId); 
    
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

  // 화면에 띄울 부분
  return (
  <div>
    <div style={{ height:650, width:'70%', alignItems:'center', margin:'auto'}}>
      
      {/* 장바구니 */}
      <div style={{justifyContent: 'start', textAlign: 'left'}}>
        <h5 style={{fontWeight: 'bold', marginTop: '35px'}}>
          Shopping Cart
        </h5>
        <DataGrid
            rows={rows_cart}
            columns={columns_cart}
            initialState={{
              pagination: { paginationModel: {pageSize: 10}}
            }}
            checkboxSelection
            style={{fontSize: '0.7rem'}}
        />  
        <div style={{display: 'grid', gridTemplateColumns: '30% 30% 5% 28% 7%', justifyItems: 'end', marginTop: '5px'}}>
          <span style={{fontSize: '0.8rem', fontWeight: 'bold', gridColumn: '4', justifySelf: 'end', marginTop: '5px', marginRight: '10px'}}>Price for Selected Items : {totalPrice} $</span>
          {showInput? (
            <div style={{gridColumn: '4', textAlign: 'right'}}>
              <form onSubmit={handleSubmit}>
                <text style={{fontSize: '0.8rem', justifySelf: 'end', marginRight: '10px'}}>Please rename the dataset you're going to buy</text>
                <input type="text" value={datasetName} onChange={handleInputChange} style={{fontSize: '0.7rem', marginRight: '0px'}}/>
                <button type="submit" style={{fontSize: '0.7rem', marginRight: '10px'}}>Save</button>
              </form>
            </div>
            ) : (
            <CButton type="button" color="secondary" className="mb-3" variant="outline" id="button-addon2" 
            style={{width: '100%', height: '60%', gridColumn: '5', display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'rgb(38, 73, 132)'}}
            onClick={buyDataset}>
              <span style={{fontSize: '0.7rem', color: 'white', fontWeight: 'bold'}}>Buy</span>
          </CButton>)}
        </div> 
        {/*showDetail && (
          <div style={{justifyContent: 'start', textAlign: 'left'}}>
          <h5 style={{fontWeight: 'bold'}}>
            Detail Information
          </h5>
          <DataGrid
            rows={detailRow}
            checkboxSelection
            columns={columns_cart_detail}
            initialState={{
              pagination: { paginationModel: {pageSize: 10}}
            }}
            disableColumnMenu
            disableSelectionOnClick
            hideFooterSelectedRowCount
            autoHeight
            style={{fontSize: '0.7rem'}}
          />
        </div>
          )*/}
      </div>

      {/* 업로드한 데이터셋 */}
      <div style={{justifyContent: 'start', textAlign: 'left'}}>
        <h5 style={{fontWeight: 'bold', marginTop: '45px'}}>
          Uploaded Datasets
        </h5>
        <DataGrid
            rows={rows_uploaded}
            columns={columns_uploaded}
            initialState={{
              pagination: { paginationModel: {pageSize: 10}}
            }}
            style={{fontSize: '0.7rem'}}
        />
      </div>

      {/* 구/판매한 데이터셋 */}
      <div>
        <div style={{justifyContent: 'start', textAlign: 'left',  display: 'grid', gridTemplateColumns: '50% 50%'}}>
          <h5 style={{fontWeight: 'bold', marginTop: '45px', gridColumn: '1'}}>
            Transacted Datasets
          </h5>
          <CButtonGroup horizontal role="group" aria-label="Vertical button group" style={{gridColumn: '2', justifySelf: 'end', width: '25%', marginTop: '45px', marginBottom: '10px'}}>
            <CFormCheck
              type="radio"
              style={{width: '100%'}}
              button={{ color: 'danger', variant: 'outline', size: 'sm' }}
              name="vbtnradio"
              id="all_button"
              autoComplete="off"
              label="All"
              defaultChecked
            />
            <CFormCheck
              type="radio"

              button={{ color: 'danger', variant: 'outline', size: 'sm' }}
              name="vbtnradio"
              id="buy_button"
              autoComplete="off"
              label="Bought"
            />
            <CFormCheck
              type="radio"

              button={{ color: 'danger', variant: 'outline', size: 'sm' }}
              name="vbtnradio"
              id="sell_button"
              autoComplete="off"
              label="Sold"
            />
          </CButtonGroup>
        </div>
          <DataGrid
              rows={rows_transaction}
              columns={columns_transaction}
              initialState={{
                pagination: { paginationModel: {pageSize: 10}}
              }}
              style={{fontSize: '0.7rem', marginTop: '0px'}}
          />
      </div>
    
    </div> 
  </div>
  );
}


export default UserPageView;