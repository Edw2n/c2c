import './DatasetListView.css';
import '@coreui/coreui/dist/css/coreui.min.css'

function DatasetListView({listInfo}) {
  console.log(listInfo[0].url)

  return (
    <div className="ResultList">
        {listInfo.map((item,idx) => <p> row {item}</p>)}
    </div>
  );
}

export default DatasetListView;