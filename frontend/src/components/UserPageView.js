import { Image, Carousel, Form, ProgressBar } from 'react-bootstrap'
import { DataGrid, GridColDef, GridValueGetterParams, GRID_CHECKBOX_SELECTION_COL_DEF } from '@mui/x-data-grid';
import React, { useEffect, useState } from 'react';
import './UserpageView.css'
import { textAlign } from '@mui/system';
import '@coreui/coreui/dist/css/coreui.min.css';
import { Dialog, DialogTitle, DialogContent, DialogActions, TextField } from '@material-ui/core';
import { CInputGroup, CFormSelect, CButtonGroup, CButton, CFormCheck } from '@coreui/react';
import { Button, Checkbox } from '@mui/material';

function UserPageView({user_name, uploadedRows, transactRows, UserInfo, onAddUserInfo}) {
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
    
    formData.append('test_mode', "false") // ui 구현 후에는 이부분을 false로 해서 붙이면 됨, 지금은 transaction data가 없는데 다운로드 되는걸 보고싶으니 이렇게 넣는것임
  
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