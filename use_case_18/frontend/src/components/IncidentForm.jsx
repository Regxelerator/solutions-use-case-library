import React from 'react';
import {
  Box,
  Typography,
  Grid,
  TextField,
  MenuItem,
  Divider,
  Checkbox,
  FormControlLabel,
  Button,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Stack,
} from '@mui/material';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import axios from 'axios';
import { useIncidentStore } from '../store/incident';

const TOPBAR_H = 64;
const BOTTOMBAR_H = 72; 

const REQUIRED_FIELDS = [
  'title',
  'description',
  'date_occured',
  'date_identified',
  'category',
  'severity',
  'impact',
  'mitigation',
  'remediation',
  'reporterName',
  'department',
];

const SEVERITY_OPTIONS = ['Low', 'Medium', 'High', 'Critical'];

const CATEGORY_OPTIONS = [
  'Strategy risk',
  'Cyber security risk',
  'Security risk',
  'Legal risk',
  'People risk',
  'Technology risk',
  'Information risk',
  'Financial risk',
];

const uniformOutlineSx = {
  '& .MuiOutlinedInput-root .MuiOutlinedInput-notchedOutline': {
    borderColor: 'divider !important',
  },
  '& .MuiOutlinedInput-root:hover .MuiOutlinedInput-notchedOutline': {
    borderColor: 'divider !important',
  },
  '& .MuiOutlinedInput-root.Mui-disabled .MuiOutlinedInput-notchedOutline': {
    borderColor: 'divider !important',
  },
  '& .MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline': {
    borderColor: 'divider !important',
  },
  '& fieldset': {
    borderColor: 'divider !important',
  },
};

function DisabledField({
  name,
  label,
  multiline = false,
  rows = 2,
  type = 'text',
  select = false,
  options = [],
  value = '',
  helperText,
}) {
  const hasValue =
    value !== undefined && value !== null && String(value).trim() !== '';

  const isDate = type === 'date';
  const effectiveType = isDate ? (hasValue ? 'date' : 'text') : type;
  const inputLabelProps = isDate ? { shrink: hasValue } : undefined;

  return (
    <TextField
      fullWidth
      disabled
      size="small"
      margin="dense"
      label={label}
      name={name}
      value={value ?? ''}
      multiline={multiline}
      rows={multiline ? rows : undefined}
      type={effectiveType}
      select={select}
      helperText={helperText}
      InputLabelProps={inputLabelProps}
      InputProps={{ readOnly: true }}
      placeholder=""
      sx={{
        ...uniformOutlineSx,
        '& .MuiInputBase-input.Mui-disabled': hasValue
          ? {
              color: 'text.primary',
              WebkitTextFillColor: 'inherit',
              opacity: 1,
              fontWeight: 300,
            }
          : undefined,
        '& .MuiFormLabel-root.Mui-disabled': hasValue
          ? { color: 'text.secondary' }
          : undefined,
      }}
    >
      {select &&
        options.map((opt) => (
          <MenuItem key={opt} value={opt} disabled>
            {opt}
          </MenuItem>
        ))}
    </TextField>
  );
}

export default function IncidentForm() {
  const draft = useIncidentStore((s) => s.draft);
  const [consent, setConsent] = React.useState(false);
  const [submitting, setSubmitting] = React.useState(false);

  const [dialog, setDialog] = React.useState({
    open: false,
    type: 'success',
    title: '',
    message: '',
  });

  const complete = REQUIRED_FIELDS.every((k) => {
    const v = draft?.[k];
    return v !== undefined && v !== null && String(v).trim() !== '';
  });

  const submit = async () => {
    try {
      setSubmitting(true);
      await axios.post('/api/incidents/submit', draft);
      setDialog({
        open: true,
        type: 'success',
        title: 'Incident submitted',
        message: 'Incident submitted – thank you.',
      });
    } catch (e) {
      console.error(e);
      setDialog({
        open: true,
        type: 'error',
        title: 'Submit failed',
        message: 'Submit failed – see console.',
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDialogClose = () => {
    const wasSuccess = dialog.type === 'success';
    setDialog((d) => ({ ...d, open: false }));
    if (wasSuccess) {
      location.reload();
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <Box
        sx={{
          px: 2,
          height: TOPBAR_H,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
        }}
      >
        <Typography variant="subtitle1" fontWeight={500}>
          Risk Incident Report
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Fields are visible but locked. The assistant will populate them as your chat progresses.
        </Typography>
      </Box>
      <Divider />

      <Box sx={{ flex: 1, p: 2, pt: 1, minHeight: 0, overflowY: 'auto' }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="overline">Reporter details</Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <DisabledField name="reporterName" label="Reporter name" value={draft?.reporterName} />
          </Grid>
          <Grid item xs={12} md={6}>
            <DisabledField name="department" label="Department / Team" value={draft?.department} />
          </Grid>

          <Grid item xs={12}>
            <Typography variant="overline">Incident details</Typography>
          </Grid>
          <Grid item xs={12}>
            <DisabledField name="title" label="Incident title" value={draft?.title} />
          </Grid>
          <Grid item xs={12}>
            <DisabledField
              name="description"
              label="Description"
              multiline
              rows={3}
              value={draft?.description}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <DisabledField
              name="date_occured"
              label="Date occurred"
              type="date"
              value={draft?.date_occured}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <DisabledField
              name="date_identified"
              label="Date identified"
              type="date"
              value={draft?.date_identified}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <DisabledField
              name="category"
              label="Category"
              select
              options={CATEGORY_OPTIONS}
              value={draft?.category}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <DisabledField
              name="severity"
              label="Severity"
              select
              options={SEVERITY_OPTIONS}
              value={draft?.severity}
            />
          </Grid>

          <Grid item xs={12}>
            <Typography variant="overline">Analysis & actions</Typography>
          </Grid>
          <Grid item xs={12}>
            <DisabledField
              name="impact"
              label="Observed / potential impact"
              multiline
              rows={3}
              value={draft?.impact}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <DisabledField
              name="mitigation"
              label="Immediate actions taken"
              multiline
              rows={5}
              value={draft?.mitigation}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <DisabledField
              name="remediation"
              label="Remediation / follow-up plan"
              multiline
              rows={5}
              value={draft?.remediation}
            />
          </Grid>

          <Grid item xs={12}>
            <DisabledField
              name="root cause"
              label="Root cause analysis"
              multiline
              rows={3}
              value={draft?.['root cause']}
            />
          </Grid>

          <Grid item xs={12}>
            <DisabledField
              name="notes"
              label="Additional notes"
              multiline
              rows={2}
              value={draft?.notes}
              helperText="Optional"
            />
          </Grid>

          {!complete && (
            <Grid item xs={12}>
              <Box sx={{ mt: 1 }}>
                <Alert severity="info" variant="outlined">
                  The risk incident form is not complete yet. Continue the conversation with risk incident agent — fields will be filled as the conversation progresses.
                </Alert>
              </Box>
            </Grid>
          )}
        </Grid>
      </Box>

      <Divider />
      <Box
        sx={{
          display: 'flex',
          flexDirection: { xs: 'row' },
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 1.5,
          px: 1.5,
          height: BOTTOMBAR_H,
          borderTop: '1px solid',
          borderColor: 'divider',
          overflow: 'hidden',
        }}
      >
        <FormControlLabel
          sx={{ m: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
          control={
            <Checkbox
              size="small"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
              disabled={!complete}
            />
          }
          label={<Typography variant="body2">I confirm the information above is accurate.</Typography>}
        />
        <Button
          variant="contained"
          color="primary"
          disabled={!complete || !consent || submitting}
          onClick={submit}
          sx={{ minWidth: 180 }}
        >
          {submitting ? 'Submitting…' : 'Submit incident'}
        </Button>
      </Box>

      <Dialog open={dialog.open} onClose={handleDialogClose} fullWidth maxWidth="xs">
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {dialog.type === 'success' ? (
            <CheckCircleOutlineIcon color="primary" />
          ) : (
            <ErrorOutlineIcon color="error" />
          )}
          {dialog.title}
        </DialogTitle>
        <DialogContent dividers>
          <DialogContentText>
            {dialog.message}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Stack direction="row" spacing={1} sx={{ px: 1, py: 0.5 }}>
            <Button onClick={handleDialogClose} variant="contained" autoFocus>
              Close
            </Button>
          </Stack>
        </DialogActions>
      </Dialog>
    </Box>
  );
}