import React, { useState, useCallback } from 'react';
import { Button } from '../ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';

interface CsvRow {
  [key: string]: string;
}

interface MappingColumn {
  csvColumn: string;
  appField: string;
}

export const CsvImport: React.FC = () => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [previewData, setPreviewData] = useState<CsvRow[]>([]);
  const [csvColumns, setCsvColumns] = useState<string[]>([]);
  const [columnMappings, setColumnMappings] = useState<MappingColumn[]>([]);
  const [validationErrors, setValidationErrors] = useState<number[]>([]);
  const [isImporting, setIsImporting] = useState(false);

  const availableFields = [
    { value: 'assessment_date', label: 'Date' },
    { value: 'weight', label: 'Weight' },
    { value: 'resting_hr', label: 'Resting HR' },
    { value: 'bp_systolic', label: 'BP Systolic' },
    { value: 'bp_diastolic', label: 'BP Diastolic' },
    { value: 'arm_right', label: 'Arm Right' },
    { value: 'arm_left', label: 'Arm Left' },
    { value: 'chest', label: 'Chest' },
    { value: 'waist', label: 'Waist' },
    { value: 'hip', label: 'Hip' },
  ];

  const parseCsv = (text: string): { headers: string[]; rows: CsvRow[] } => {
    const lines = text.split('\n').filter(line => line.trim());
    if (lines.length === 0) return { headers: [], rows: [] };
    const headers = lines[0].split(',').map(h => h.trim());
    const rows = lines.slice(1, 6).map(line => {
      const values = line.split(',').map(v => v.trim());
      const row: CsvRow = {};
      headers.forEach((header, index) => {
        row[header] = values[index] || '';
      });
      return row;
    });
    return { headers, rows };
  };

  const handleFile = (selectedFile: File) => {
    setFile(selectedFile);
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const { headers, rows } = parseCsv(text);
      setCsvColumns(headers);
      setPreviewData(rows);
      const initialMappings = headers.map(header => ({
        csvColumn: header,
        appField: '',
      }));
      setColumnMappings(initialMappings);
      setValidationErrors([]);
    };
    reader.readAsText(selectedFile);
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const updateMapping = (index: number, appField: string) => {
    const newMappings = [...columnMappings];
    newMappings[index].appField = appField;
    setColumnMappings(newMappings);
  };

  const validateRow = (row: CsvRow): boolean => {
    for (const mapping of columnMappings) {
      if (mapping.appField && !row[mapping.csvColumn]) {
        return false;
      }
    }
    return true;
  };

  const validatePreview = () => {
    const errors: number[] = [];
    previewData.forEach((row, index) => {
      if (!validateRow(row)) {
        errors.push(index);
      }
    });
    setValidationErrors(errors);
    return errors.length === 0;
  };

  const handleImport = async () => {
    if (!validatePreview()) return;
    setIsImporting(true);
    try {
      const formData = new FormData();
      if (file) {
        formData.append('file', file);
        formData.append('mappings', JSON.stringify(columnMappings));
        const response = await fetch('/api/v1/assessments/import', {
          method: 'POST',
          body: formData,
        });
        if (!response.ok) throw new Error('Import failed');
        setFile(null);
        setPreviewData([]);
        setCsvColumns([]);
        setColumnMappings([]);
      }
    } catch (error) {
      console.error('Import error:', error);
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">Import CSV</h1>
      <Card className="mb-6">
        <CardContent className="p-8">
          <div
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {file ? (
              <div>
                <p className="text-lg font-semibold mb-2">{file.name}</p>
                <p className="text-sm text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                <Button type="button" variant="secondary" onClick={() => { setFile(null); setPreviewData([]); setCsvColumns([]); setColumnMappings([]); }} className="mt-4">Remove</Button>
              </div>
            ) : (
              <div>
                <p className="text-lg mb-4">Drag & drop your CSV file here</p>
                <p className="text-sm text-gray-500 mb-4">or</p>
                <label className="cursor-pointer">
                  <span className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">Browse Files</span>
                  <input type="file" accept=".csv" onChange={handleFileInput} className="hidden" />
                </label>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      {csvColumns.length > 0 && (
        <Card className="mb-6">
          <CardHeader><CardTitle>Map Columns</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-600">Map your CSV columns to the application fields</p>
            <div className="grid grid-cols-2 gap-4">
              {columnMappings.map((mapping) => (
                <div key={mapping.csvColumn} className="flex items-center gap-2">
                  <span className="text-sm font-medium w-32 truncate" title={mapping.csvColumn}>{mapping.csvColumn}</span>
                  <span className="text-gray-400">→</span>
                  <select value={mapping.appField} onChange={(e) => updateMapping(columnMappings.indexOf(mapping), e.target.value)} className="flex-1 h-10 rounded-md border border-gray-300 bg-white px-3 py-2 text-sm">
                    <option value="">-- Select Field --</option>
                    {availableFields.map((field) => (<option key={field.value} value={field.value}>{field.label}</option>))}
                  </select>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
      {previewData.length > 0 && (
        <Card className="mb-6">
          <CardHeader><CardTitle>Preview (First 5 Rows)</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    {csvColumns.map((column) => (
                      <th key={column} className="text-left p-3 font-medium">{column}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {previewData.map((row, rowIndex) => (
                    <tr key={rowIndex} className={`border-b ${validationErrors.includes(rowIndex) ? 'bg-red-50' : ''}`}>
                      {csvColumns.map((column) => (<td key={column} className="p-3">{row[column] || <span className="text-gray-400 italic">empty</span>}</td>))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {validationErrors.length > 0 && (<p className="mt-4 text-sm text-red-600">{validationErrors.length} row(s) have validation errors</p>)}
          </CardContent>
        </Card>
      )}
      {previewData.length > 0 && (
        <div className="flex justify-end gap-4">
          <Button type="button" variant="secondary" onClick={validatePreview}>Validate</Button>
          <Button type="button" variant="primary" onClick={handleImport} disabled={isImporting || validationErrors.length > 0}>{isImporting ? 'Importing...' : 'Import CSV'}</Button>
        </div>
      )}
    </div>
  );
};
