import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import {
  Button,
  Grid,
  LinearProgress,
  Paper,
  Radio,
  RadioGroup,
  TextField,
  Typography,
  FormControlLabel,
} from '@mui/material';
import UploadTable from '../UploadTable';

const newRow = (label) => ({
  id: crypto.randomUUID(),
  backendId: null,
  name: label,
  type: '',
  description: '',
  author: '',
  status: 'In progress',
});

export default function Tab1_Select_Content() {
  const [rows, setRows] = useState([]);
  const [mode, setMode] = useState('file');
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState('');
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef();

  useEffect(() => {
    (async () => {
      const { data } = await axios.get('/api/masterlist');
      const mapped = data.entries.map((e) => ({
        id: e.id,
        backendId: e.id,
        name: e.content_name ?? e.filename ?? e.url ?? '',
        type: e.content_type ?? '',
        description: e.content_description ?? '',
        author: e.content_author ?? '',
        status: 'Completed',
      }));
      setRows(mapped);
    })();
  }, []);

  const resetInputs = () => {
    setFile(null);
    setUrl('');
  };

  const uploadDisabled = uploading || (mode === 'file' ? !file : !url.trim());

  const patchRow = (tmpId, patch) =>
    setRows((r) => r.map((row) => (row.id === tmpId ? { ...row, ...patch } : row)));

  const startUpload = async () => {
    const tmpId = crypto.randomUUID();
    const label = mode === 'file' ? file.name : url.trim();
    setRows((r) => [...r, { ...newRow(label), id: tmpId }]);
    setUploading(true);

    try {
      let res;
      if (mode === 'file') {
        const form = new FormData();
        form.append('file', file);
        res = await axios.post('/api/upload', form, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      } else {
        res = await axios.post('/api/url', { url: url.trim() });
      }

      const { id: backendId, metadata } = res.data;
      patchRow(tmpId, {
        backendId,
        name: metadata.content_name ?? label,
        type: metadata.content_type ?? '',
        description: metadata.content_description ?? '',
        author: metadata.content_author ?? '',
        status: 'Completed',
      });
    } catch (err) {
      console.error(err);
      patchRow(tmpId, { status: 'Failed' });
    } finally {
      resetInputs();
      setUploading(false);
    }
  };

  const handleRemove = async (rowId) => {
    const row = rows.find((r) => r.id === rowId);
    if (!row || !row.backendId) return;

    try {
      await axios.delete(`/api/masterlist/${row.backendId}`);
    } catch (e) {
      console.error('Delete failed on server:', e);
    }
    setRows((r) => r.filter((x) => x.id !== rowId));
  };

  return (
    <Paper elevation={0} variant="outlined" sx={{ p: 4, borderColor: 'grey.300' }}>
      <Typography variant="h6" gutterBottom sx={{ mb: 0 }}>
        Add content
      </Typography>

      <Grid container rowSpacing={0.5} columnSpacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <RadioGroup
            row
            value={mode}
            onChange={(e) => {
              setMode(e.target.value);
              resetInputs();
            }}
          >
            <FormControlLabel value="file" control={<Radio size="small" />} label="Local file" />
            <FormControlLabel value="url" control={<Radio size="small" />} label="Web URL" />
          </RadioGroup>
        </Grid>

        <Grid item xs={12}>
          {mode === 'file' ? (
            <>
              <TextField
                size="small"
                placeholder="Local file *"
                value={file ? file.name : ''}
                InputProps={{ readOnly: true }}
                onClick={() => fileInputRef.current?.click()}
                sx={{ width: { xs: '100%', sm: 500 }, minHeight: 56, mb: -1, cursor: 'pointer' }}
              />
              <input
                hidden
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.pptx,.txt"
                onChange={(e) => setFile(e.target.files[0])}
              />
            </>
          ) : (
            <TextField
              size="small"
              placeholder="Web URL *"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={uploading}
              sx={{ width: { xs: '100%', sm: 500 }, minHeight: 56, mb: -1 }}
            />
          )}
        </Grid>

        <Grid item xs={12}>
          <Button
            variant="contained"
            disabled={uploadDisabled}
            onClick={startUpload}
            sx={{ width: { xs: '100%', sm: 500 }, minHeight: 45, mb: 5 }}
          >
            {uploading ? 'Uploading…' : 'Upload'}
          </Button>
        </Grid>
      </Grid>

      {uploading && <LinearProgress sx={{ mb: 3 }} />}

      <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
        Uploaded content
      </Typography>
      <UploadTable rows={rows} onRemove={handleRemove} />
    </Paper>
  );
}