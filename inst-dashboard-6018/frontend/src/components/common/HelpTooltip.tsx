import React, { useState, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
import { useTranslation } from 'react-i18next';

interface Props {
  title: string;
  description: string;
  benefit: string;
}

const HelpTooltip: React.FC<Props> = ({ title, description, benefit }) => {
  const { t, i18n } = useTranslation();
  const [show, setShow] = useState(false);
  const [coords, setCoords] = useState({ top: 0, left: 0 });
  const buttonRef = useRef<HTMLButtonElement>(null);
  const isRTL = i18n.dir() === 'rtl';

  useEffect(() => {
    if (show && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      setCoords({
        top: rect.top + window.scrollY + 25,
        left: isRTL ? rect.right + window.scrollX - 250 : rect.left + window.scrollX
      });
    }
  }, [show, isRTL]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (buttonRef.current && !buttonRef.current.contains(event.target as Node)) {
        setShow(false);
      }
    };
    if (show) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [show]);

  return (
    <>
      <button 
        ref={buttonRef}
        onClick={(e) => { e.stopPropagation(); setShow(!show); }}
        style={{
          background: '#1890ff',
          color: 'white',
          borderRadius: '50%',
          width: '20px',
          height: '20px',
          border: 'none',
          cursor: 'pointer',
          fontSize: '12px',
          fontWeight: 'bold',
          marginLeft: '8px'
        }}
      >
        ?
      </button>
      {show && ReactDOM.createPortal(
        <div style={{
          position: 'absolute',
          top: `${coords.top}px`,
          left: `${coords.left}px`,
          width: '250px',
          backgroundColor: '#fff',
          border: '1px solid #ccc',
          borderRadius: '8px',
          padding: '15px',
          boxShadow: '0 8px 16px rgba(0,0,0,0.2)',
          zIndex: 99999,
          textAlign: isRTL ? 'right' : 'left',
          fontSize: '0.9em',
          color: '#333'
        }}>
          <h4 style={{ margin: '0 0 5px 0' }}>{title}</h4>
          <p style={{ margin: '0 0 10px 0' }}><strong>{description}</strong></p>
          <p style={{ margin: 0 }}><em>{t('common.benefit', 'Benefit')}: {benefit}</em></p>
        </div>,
        document.body
      )}
    </>
  );
};

export default HelpTooltip;
