import './CardView.css';
import '@coreui/coreui/dist/css/coreui.min.css'
import { CCard,CCardImage,CCardTitle,CCardBody,CCardText, CRow, CCol} from '@coreui/react'
import { useState } from 'react';

function CardView({cardviewInfo}) {
  return (
    <div className="ResultList">
        <CRow xs={{ cols: 1 }} md={{ cols: 3 }} className="g-4">
          {cardviewInfo.map((item,idx) => (
            <CCol xs>
              <CCard className='mb-3 border-black' >
                <CCardImage orientation="top" src={item.image_path} />
                <CCardBody>
                  <CCardTitle>{`${item.object_count} Objects`} </CCardTitle>
                  <CCardText >
                    {`${item.Objects}`} 
                  </CCardText>
                  <CCardText>
                    <small className="text-medium-emphasis"> {`qc score: ${item.qc_score}`}  </small>
                  </CCardText>
                </CCardBody>
              </CCard>
            </CCol>
          ))}
        </CRow>
    </div>
  );
}

export default CardView;