import React, { useState } from 'react';

// A simple searchable dropdown component
const SearchableSelect = ({ options, value, onChange, placeholder }: any) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredOptions = options.filter((o: any) =>
    o.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div style={{ position: 'relative', width: '100%', marginBottom: '10px' }}>
      <input
        type="text"
        placeholder={value ? options.find((o:any) => o.id == value)?.name : placeholder}
        value={isOpen ? searchTerm : ''}
        onClick={() => setIsOpen(!isOpen)}
        onChange={(e) => setSearchTerm(e.target.value)}
        style={{ width: '100%', padding: '10px', boxSizing: 'border-box', border: '1px solid var(--nebula-border)', borderRadius: '4px' }}
      />
      {isOpen && (
        <ul style={{ position: 'absolute', top: '100%', left: 0, width: '100%', maxHeight: '200px', overflowY: 'auto', background: 'transparent', border: '1px solid var(--nebula-border)', zIndex: 10, listStyle: 'none', padding: 0, margin: 0 }}>
          <li onClick={() => { onChange(''); setIsOpen(false); setSearchTerm(''); }} style={{ padding: '8px', cursor: 'pointer' }}>- Select -</li>
          {filteredOptions.map((o: any) => (
            <li key={o.id} onClick={() => { onChange(o.id); setIsOpen(false); setSearchTerm(''); }} style={{ padding: '8px', cursor: 'pointer' }}>
              {o.name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SearchableSelect;
