import { Image, Carousel, Form, ProgressBar,Button } from 'react-bootstrap'
import { DataGrid, GridColDef, GridValueGetterParams } from '@mui/x-data-grid';
import { useEffect, useState } from 'react';
import './UserpageView.css'
import { textAlign } from '@mui/system';

function UserPageView({user_name,rows}) {

    const [selectedIDs, setSelectedIDs] = useState([])
    const [user_rows,setRows] = useState(rows)

    const deleteSelected = async (e) => {

        const formData = new FormData();
        formData.append('aid_list',JSON.stringify(selectedIDs))

        await fetch('http://0.0.0.0:3000/delete', {
          method: 'POST',
          body: formData
        }).then(resp => {
         
            setRows(prev => prev.filter( data => 
                !(selectedIDs.includes(data.id))))
        })}

    const columns: GridColDef[] = [
        { field: 'id', headerName: 'ID', width: 70 },
        { field: 'color', headerName: 'Color', width: 130 },
        { field: 'breed', headerName: 'Breed', width: 200 },
        { field: 'age', headerName: 'Age', width: 130 },
        { field: 'gender', headerName: 'Gender', width: 130 },
        { field: 'city', headerName: 'City', width: 130 },
        { field: 'state', headerName: 'State', width: 130 },
        {
          field: 'characteristic',
          headerName: 'Characteristic',
          description: 'This column has a value getter and is not sortable.',
          sortable: false,
          width: 500,
          valueGetter: (params: GridValueGetterParams) =>
            `${params.row.characteristic || ''} `,
        },
      ];
  
  return (
    <div>
      <div className='user-info' style={{marginTop:'10px'}}>
        <text>Hi {user_name}!</text>
        <Button onClick={deleteSelected}>delete</Button>
      </div>
      <div style={{ height:650, width:'75%', alignItems:'center', margin:'auto'}}>
        <DataGrid
            rows={user_rows}
            columns={columns}
            pageSize={10}
            rowsPerPageOptions={[5]}
            checkboxSelection
            onSelectionModelChange={(ids) => {
                setSelectedIDs(ids)
              }}
            style={{marginTop:'10px'}}
        />  
      </div>
    </div> 

  );
}

export default UserPageView;