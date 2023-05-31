import './DatasetListView.css';
import '@coreui/coreui/dist/css/coreui.min.css';
import { DataGrid } from '@mui/x-data-grid';
import { DataGridCell, HeaderRow } from 'react-data-grid';
import React, { useEffect, useState } from 'react';

function DatasetListView({listInfo}) {
  console.log(listInfo[0].url)

  // return (
  //  <div className="ResultList">
  //      {listInfo.map((item,idx) => <p> row {item}</p>)}
  //  </div>
  //);

  const [items, setItems] = useState(listInfo);

  // column, row 정의
  const columns = [
    { field: 'Uploader', headerName: 'Uploader', width: 65},
    { field: 'Title', headerName: 'Dataset Name', width: 90},
    { field: 'Description', headerName: 'Description', width: 130},
    { field: 'QCstate', headerName: 'QC State', width: 80},
    { field: 'QCscore', headerName: 'QC Score', width: 70},
    { field: 'Objects', headerName: 'Objects', width: 130},
    { field: 'UploadDate', headerName: 'Upload Date', width: 80},
    { field: 'SalesCount', headerName: 'Sales Count', width: 80},
    { field: 'MatchedData', headerName: 'Matched Data', width: 90},
    { field: 'Price', headerName: 'Price($)', width: 80},
    { field: 'PricePerImage', headerName: 'Price per Image($)', width: 110}
    // { field: 'Likes', headerName: 'Likes', width:  },
  ];

  const rows = items.map((row) => (
    {id: row.id, Uploader: row.Uploader, Title: row.Title, Description: row.Description,
      QCstate: row.QCstate, QCscore: row.QCscore, Objects: row.Objects, UploadDate: row.UploadDate, 
      SalesCount: row.SalesCount, MatchedData: row.MatchedData, Price: row.Price,  PricePerImage: row.PricePerImage}
  ));

  // 리스트뷰 표시 부분
  return (
    <div className='ListViewContainerDetail'>
        <DataGrid
          rows={rows}
          columns={columns}
          pageSize={10}
          style={{fontSize: '0.7rem'}}
        />
    </div>
  );
};

export default DatasetListView;