import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';

const InfoIcon = ({ desc, benefit }: { desc: string; benefit: string }) => {
  const { t, i18n } = useTranslation();
  const [show, setShow] = useState(false);
  const containerRef = useRef<HTMLSpanElement>(null);
  const isRtl = i18n.dir() === 'rtl';

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setShow(false);
      }
    };

    if (show) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [show]);

  return (
    <span ref={containerRef} style={{ position: 'relative', display: 'inline-block', marginLeft: '8px' }}>
      <span 
        onClick={() => setShow(!show)}
        style={{ cursor: 'pointer', color: 'var(--nebula-accent-cyan)', fontWeight: 'bold', border: '1px solid var(--nebula-accent-cyan)', borderRadius: '50%', width: '16px', height: '16px', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px' }}
      >
        ?
      </span>
      {show && (
        <div style={{ 
            position: 'absolute', top: '100%', 
            right: isRtl ? '0' : 'auto', 
            left: isRtl ? 'auto' : '0', 
            width: '250px', 
            padding: '10px', backgroundColor: 'var(--nebula-bg-glass)', border: '1px solid var(--nebula-border)', 
            borderRadius: '8px', zIndex: 1000, boxShadow: '0 4px 6px var(--nebula-border-strong)',
            fontSize: '0.85em', marginTop: '5px', textAlign: 'start'
        }}>
          <p style={{ margin: '0 0 5px 0' }}><strong>{t('common.description')}:</strong> {desc}</p>
          <p style={{ margin: 0 }}><strong>{t('common.benefit')}:</strong> {benefit}</p>
        </div>
      )}
    </span>
  );
};

export default InfoIcon;
