import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import {
  Box,
  Button,
  Divider,
  IconButton,
  InputAdornment,
  Menu,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';

const SIDEBAR_WIDTH = 340;

export default function Tab4_Administration() {
  const [mode, setMode] = useState('generate');
  const [presets, setPresets] = useState([]);
  const [selected, setSelected] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [newLabel, setNewLabel] = useState('');
  const [editingLabel, setEditingLabel] = useState('');
  const [renameActive, setRenameActive] = useState(false);
  const inputRef = useRef(null);

  const loadPresets = async (m = mode) => {
    const { data } = await axios.get(`/api/presets?mode=${m}`);
    setPresets(data);
    if (data.length) {
      setSelected(data[0].key);
      setPrompt(data[0].prompt);
      setEditingLabel(data[0].label);
    } else {
      setSelected(null);
      setPrompt('');
      setEditingLabel('');
    }
  };

  useEffect(() => {
    loadPresets();
  }, [mode]);

  const commitLabel = async () => {
    const trimmed = editingLabel.trim();
    if (!selected) return;
    const current = presets.find((p) => p.key === selected);
    if (!current || current.label === trimmed || !trimmed) {
      setRenameActive(false);
      return;
    }
    await axios.put(`/api/presets/${selected}`, {
      mode,
      label: trimmed,
      prompt,
    });
    setRenameActive(false);
    loadPresets();
  };

  const save = async () => {
    await commitLabel();
    if (!selected) return;
    await axios.put(`/api/presets/${selected}`, { mode, prompt, label: editingLabel.trim() });
    loadPresets();
  };

  const addPreset = async () => {
    const label = newLabel.trim();
    if (!label) return;
    const { data } = await axios.post('/api/presets', { mode, label, prompt: '' });
    setNewLabel('');
    setSelected(data.key);
    setPrompt('');
    setEditingLabel(label);
    loadPresets();
  };

  const copyPreset = async (key) => {
    const p = presets.find((x) => x.key === key);
    if (!p) return;
    await axios.post('/api/presets', {
      mode,
      label: `${p.label} (Copy)`,
      prompt: p.prompt,
    });
    loadPresets();
  };

  const deletePreset = async (key) => {
    await axios.delete(`/api/presets/${key}`, { data: { mode } });
    if (selected === key) {
      setSelected(null);
      setPrompt('');
      setEditingLabel('');
    }
    loadPresets();
  };

  const [menuAnchor, setMenuAnchor] = useState(null);
  const [menuKey, setMenuKey] = useState(null);
  const openMenu = (e, key) => {
    setMenuAnchor(e.currentTarget);
    setMenuKey(key);
  };
  const closeMenu = () => setMenuAnchor(null);

  const triggerRename = () => {
    closeMenu();
    const p = presets.find((x) => x.key === menuKey);
    if (!p) return;
    setSelected(p.key);
    setPrompt(p.prompt);
    setEditingLabel(p.label);
    setRenameActive(true);
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  return (
    <Paper elevation={0} variant="outlined" sx={{ p: 4, borderColor: 'grey.300' }}>
      <Typography variant="h6" gutterBottom>
        Manage presets
      </Typography>

      <TextField
        select
        size="small"
        value={mode}
        onChange={(e) => setMode(e.target.value)}
        sx={{ width: { xs: '100%', sm: SIDEBAR_WIDTH }, mb: 3 }}
      >
        <option value="generate">Presets for content generation</option>
        <option value="edit">Presets for editing</option>
      </TextField>

      <Stack
        direction={{ xs: 'column', md: 'row' }}
        spacing={3}
        divider={<Divider orientation="vertical" flexItem />}
      >
        <Box sx={{ width: { xs: '100%', md: SIDEBAR_WIDTH }, flexShrink: 0 }}>
          <Paper elevation={0} variant="outlined" sx={{ p: 2, mb: 2 }}>
            <TextField
              size="small"
              placeholder="New preset label"
              value={newLabel}
              onChange={(e) => setNewLabel(e.target.value)}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      color="primary"
                      disabled={!newLabel.trim()}
                      onClick={addPreset}
                    >
                      <AddIcon />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              fullWidth
            />
          </Paper>

          <Paper elevation={0} variant="outlined" sx={{ maxHeight: '70vh', overflow: 'auto', p: 1 }}>
            <Stack spacing={1}>
              {presets.map((p) => {
                const isSel = p.key === selected;
                return (
                  <Paper
                    key={p.key}
                    sx={{
                      p: 1,
                      border: isSel ? '2px solid' : '1px solid',
                      borderColor: isSel ? 'primary.main' : 'grey.300',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 1,
                      cursor: 'pointer',
                    }}
                    onClick={() => {
                      if (selected !== p.key) {
                        commitLabel();
                        setSelected(p.key);
                        setPrompt(p.prompt);
                        setEditingLabel(p.label);
                        setRenameActive(false);
                      }
                    }}
                  >
                    <DragIndicatorIcon fontSize="small" sx={{ color: 'text.disabled' }} />

                    <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                      {isSel && renameActive ? (
                        <TextField
                          variant="standard"
                          value={editingLabel}
                          inputRef={inputRef}
                          onChange={(e) => setEditingLabel(e.target.value)}
                          onBlur={commitLabel}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              e.preventDefault();
                              commitLabel();
                            }
                          }}
                          fullWidth
                        />
                      ) : (
                        <Typography noWrap variant="body2" fontWeight={500}>
                          {p.label}
                        </Typography>
                      )}
                    </Box>

                    <IconButton size="small" onClick={(e) => openMenu(e, p.key)}>
                      <MoreVertIcon fontSize="small" />
                    </IconButton>
                  </Paper>
                );
              })}
            </Stack>
          </Paper>
        </Box>

        <Box sx={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
          <TextField
            multiline
            minRows={12}
            fullWidth
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Prompt text…"
          />

          <Box sx={{ mt: 2 }}>
            <Button variant="contained" color="primary" disableElevation onClick={save}>
              Save changes
            </Button>
          </Box>
        </Box>
      </Stack>

      <Menu anchorEl={menuAnchor} open={Boolean(menuAnchor)} onClose={closeMenu}>
        <MenuItem onClick={triggerRename}>Rename</MenuItem>
        <MenuItem
          onClick={() => {
            closeMenu();
            copyPreset(menuKey);
          }}
        >
          Copy
        </MenuItem>
        <MenuItem
          onClick={() => {
            closeMenu();
            deletePreset(menuKey);
          }}
        >
          Delete
        </MenuItem>
      </Menu>
    </Paper>
  );
}