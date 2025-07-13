import React, { useEffect, useMemo, useRef, useState } from 'react';
import axios from 'axios';
import {
  Badge,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  Drawer,
  Grid,
  IconButton,
  InputAdornment,
  List,
  Menu,
  MenuItem,
  Paper,
  Skeleton,
  Snackbar,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';

import AddIcon from '@mui/icons-material/Add';
import CloseIcon from '@mui/icons-material/Close';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import UndoIcon from '@mui/icons-material/Undo';

import { DragDropContext, Draggable, Droppable } from 'react-beautiful-dnd';

import UploadTable from '../UploadTable';

const newSection = (title) => ({
  id: crypto.randomUUID(),
  title,
  status: 'Draft',
  order: 0,
  content: '',
  sources: [],
});

const statusColor = (s) =>
  s === 'Ready'
    ? 'success'
    : s === 'Draft'
    ? 'default'
    : s === 'Done'
    ? 'success'
    : s.startsWith('Gen') || s.startsWith('Trans')
    ? 'info'
    : 'default';

export default function Tab2_Create_Memo() {
  const [sections, setSections] = useState([]);
  const [selected, setSelected] = useState(null);
  const [contentBank, setContentBank] = useState([]);

  const [titleInput, setTitleInput] = useState('');
  const [mode, setMode] = useState('create'); 
  const [busy, setBusy] = useState(false);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, prev: '' });

  const [renameActiveId, setRenameActiveId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');

  const saveContent = (id, content) =>
    axios
      .patch(`/api/memo/section/${id}`, { content, status: 'Draft' })
      .catch(() => {});

  const sectionsRef = useRef(sections);
  useEffect(() => {
    sectionsRef.current = sections;
  }, [sections]);

  const genPresetRef = useRef('summary');
  const genCustomRef = useRef('');
  const editPresetRef = useRef('shorter');
  const editCustomRef = useRef('');

  useEffect(() => {
    (async () => {
      const memo = await axios.get('/api/memo');
      setSections(memo.data.sections);
      if (memo.data.sections.length) setSelected(memo.data.sections[0].id);

      const bank = await axios.get('/api/masterlist');
      setContentBank(bank.data.entries);
    })();
  }, []);

  const patchSection = (id, patch) =>
    setSections((s) => s.map((sec) => (sec.id === id ? { ...sec, ...patch } : sec)));

  const active = useMemo(
    () => sections.find((s) => s.id === selected) ?? null,
    [sections, selected]
  );

  const createSection = async () => {
    const title = titleInput.trim();
    if (!title) return;
    const { data } = await axios.post('/api/memo/section', { title });
    setSections((s) => [...s, { ...newSection(title), ...data }]);
    setSelected(data.id);
    setTitleInput('');
  };

  const deleteSection = async (id) => {
    await axios.delete(`/api/memo/section/${id}`);
    setSections((s) => s.filter((sec) => sec.id !== id));
    if (selected === id) setSelected(null);
  };

  const reorderSections = async (result) => {
    const { destination, source, type } = result;
    if (!destination || type !== 'SECTION') return;
    const reordered = [...sections];
    const [moved] = reordered.splice(source.index, 1);
    reordered.splice(destination.index, 0, moved);
    setSections(reordered);
    await axios.post('/api/memo/reorder', { order: reordered.map((s) => s.id) });
  };

  const handleDragStart = (e, row) => e.dataTransfer.setData('text/plain', row.id);

  const onSourceDrop = (e) => {
    e.preventDefault();
    if (!selected) return;
    const id = e.dataTransfer.getData('text/plain');
    if (!id) return;
    if (active.sources.includes(id)) return;
    const ns = [...active.sources, id];
    patchSection(selected, { sources: ns });
    axios.patch(`/api/memo/section/${selected}`, { sources: ns });
  };

  const runGenerate = async () => {
    if (!selected || !active.sources.length) return;

    setBusy(true);
    patchSection(selected, { status: 'Generating' });

    try {
      const { data } = await axios.post(
        `/api/memo/section/${selected}/generate`,
        {
          source_ids: active.sources,          
          preset: genPresetRef.current,        
          custom_prompt: genCustomRef.current,
        }
      );

      setSnackbar({ open: true, prev: active.content });
      patchSection(selected, { content: data.content, status: 'Draft' });
    } finally {
      setBusy(false);
    }
  };

  const runTransform = async () => {
    if (!selected || !active.content) return;

    setBusy(true);
    patchSection(selected, { status: 'Transforming' });

    try {
      const { data } = await axios.post(
        `/api/memo/section/${selected}/transform`,
        {
          preset: editPresetRef.current,       
          custom_prompt: editCustomRef.current,
          text: active.content,                
        }
      );

      setSnackbar({ open: true, prev: active.content });
      patchSection(selected, { content: data.content, status: 'Draft' });
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    if (!selected) return;
    const t = setInterval(() => {
      const sec = sectionsRef.current.find((s) => s.id === selected);
      if (sec && sec.status === 'Draft') saveContent(selected, sec.content);
    }, 10_000);                              
    return () => clearInterval(t);           
  }, [selected]); 

  const coveredIds = new Set(sections.flatMap((s) => s.sources));
  const uploadRows = contentBank.map((c) => ({
    id: c.id,
    name: c.content_name || c.filename,
    description: c.content_description || '',
    covered: coveredIds.has(c.id),
  }));

  const [menuAnchor, setMenuAnchor] = useState(null);
  const [menuTargetId, setMenuTargetId] = useState(null);
  const openMenu = (e, id) => {
    setMenuAnchor(e.currentTarget);
    setMenuTargetId(id);
  };
  const closeMenu = () => setMenuAnchor(null);

  const commitTitle = async () => {
    if (!renameActiveId) return;
    const trimmed = editingTitle.trim();
    const sec = sections.find((s) => s.id === renameActiveId);
    setRenameActiveId(null);

    if (!sec || !trimmed || sec.title === trimmed) return;

    patchSection(sec.id, { title: trimmed });
    await axios.patch(`/api/memo/section/${sec.id}`, { title: trimmed });
  };

  const renameSection = () => {
    const sec = sections.find((s) => s.id === menuTargetId);
    closeMenu();
    if (!sec) return;
    setRenameActiveId(sec.id);
    setEditingTitle(sec.title);
    setTimeout(() => {
      document.getElementById(`sec-title-input-${sec.id}`)?.focus();
    }, 0);
  };

  const copySection = async () => {
    const sec = sections.find((s) => s.id === menuTargetId);
    closeMenu();
    if (!sec) return;
    const { data } = await axios.post('/api/memo/section', { title: sec.title + ' (Copy)' });
    setSections((s) => [...s, { ...sec, id: data.id, title: sec.title + ' (Copy)' }]);
  };

  const [genPresets, setGenPresets] = useState([]);
  const [editPresets, setEditPresets] = useState([]);

  useEffect(() => {
    (async () => {
      const gp = await axios.get('/api/presets?mode=generate');
      const ep = await axios.get('/api/presets?mode=edit');
      setGenPresets(gp.data);
      setEditPresets(ep.data);
      genPresetRef.current = gp.data[0]?.key ?? '';
      editPresetRef.current = ep.data[0]?.key ?? '';
    })();
  }, []);

  const isCreateActive = mode === 'create';
  const isEditActive = mode === 'edit';

  return (
    <>
      <Paper elevation={0} variant="outlined" sx={{ p: 4, borderColor: 'grey.300' }}>
        <Typography variant="h6" gutterBottom>
          Workspace
        </Typography>

        <Stack direction="row" spacing={3}>
          <Box sx={{ width: { xs: '35%', md: 340 }, minWidth: 260 }}>
            <Paper elevation={0} variant="outlined" sx={{ p: 2, mb: 2 }}>
              <TextField
                size="small"
                placeholder="New section title"
                value={titleInput}
                onChange={(e) => setTitleInput(e.target.value)}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        color="primary"
                        disabled={!titleInput.trim()}
                        onClick={createSection}
                      >
                        <AddIcon />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                fullWidth
              />
            </Paper>

            <Paper elevation={0} variant="outlined" sx={{ maxHeight: '72vh', overflow: 'auto', p: 1 }}>
              <DragDropContext onDragEnd={reorderSections}>
                <Droppable droppableId="sections" type="SECTION">
                  {(provided) => (
                    <List ref={provided.innerRef} {...provided.droppableProps} disablePadding>
                      {sections.map((sec, idx) => (
                        <Draggable key={sec.id} draggableId={sec.id} index={idx}>
                          {(p) => (
                            <Paper
                              ref={p.innerRef}
                              {...p.draggableProps}
                              {...p.dragHandleProps} 
                              sx={{
                                p: 1,
                                mb: 1,
                                border: selected === sec.id ? '2px solid' : '1px solid',
                                borderColor: selected === sec.id ? 'primary.main' : 'grey.300',
                                display: 'flex',
                                alignItems: 'flex-start',
                                gap: 1,
                                cursor: 'pointer',
                              }}
                              onClick={() => {
                                if (renameActiveId) commitTitle();
                                setSelected(sec.id);
                              }}
                            >

                              <DragIndicatorIcon
                                fontSize="small"
                                sx={{ cursor: 'grab', color: 'text.disabled', pointerEvents: 'auto' }}
                                {...p.dragHandleProps}
                              />
                              <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                                {sec.id === renameActiveId ? (
                                  <TextField
                                    variant="standard"
                                    value={editingTitle}
                                    id={`sec-title-input-${sec.id}`}
                                    onChange={(e) => setEditingTitle(e.target.value)}
                                    onBlur={commitTitle}
                                    onKeyDown={(e) => {
                                      if (e.key === 'Enter') {
                                        e.preventDefault();
                                        commitTitle();
                                      }
                                      if (e.key === 'Escape') setRenameActiveId(null);
                                    }}
                                    fullWidth
                                  />
                                ) : (
                                  <Typography noWrap variant="body2" fontWeight={500}>
                                    {sec.title}
                                  </Typography>
                                )}
                              </Box>

                              <Chip
                                label={sec.status}
                                size="small"
                                clickable
                                onClick={(e) => {
                                  e.stopPropagation();
                                  const newStatus = sec.status === 'Ready' ? 'Draft' : 'Ready';
                                  patchSection(sec.id, { status: newStatus });
                                  axios
                                    .patch(`/api/memo/section/${sec.id}`, { status: newStatus })
                                    .catch(() => {});
                                }}
                                color={statusColor(sec.status)}
                              />

                              <IconButton size="small" onClick={(e) => openMenu(e, sec.id)}>
                                <MoreVertIcon fontSize="small" />
                              </IconButton>
                            </Paper>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </List>
                  )}
                </Droppable>
              </DragDropContext>
            </Paper>
          </Box>

          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            {!active ? (
              <Paper
                variant="outlined"
                sx={{
                  height: 420,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'text.secondary',
                }}
              >
                Select or create a section on the left.
              </Paper>
            ) : (
              <Card elevation={0} sx={{ border: '1px solid', borderColor: 'grey.300' }}>
                <Box sx={{ p: 2 }}>
                  <TextField
                    fullWidth
                    size="small"
                    placeholder="Section title"
                    value={active.title}
                    onChange={(e) => {
                      patchSection(selected, { title: e.target.value });
                      axios.patch(`/api/memo/section/${selected}`, { title: e.target.value });
                    }}
                  />
                </Box>

                <Box
                  sx={{
                    px: 2,
                    py: 1,
                    borderTop: '1px solid',
                    borderColor: 'divider',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    flexWrap: 'wrap',
                  }}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={onSourceDrop}
                >
                  {active.sources.length ? (
                    active.sources.map((sid) => {
                      const src = contentBank.find((c) => c.id === sid);
                      const label = src?.content_name || src?.filename || sid;
                      return (
                        <Chip
                          key={sid}
                          label={label}
                          size="small"
                          onDelete={() => {
                            const ns = active.sources.filter((x) => x !== sid);
                            patchSection(selected, { sources: ns });
                            axios.patch(`/api/memo/section/${selected}`, { sources: ns });
                          }}
                        />
                      );
                    })
                  ) : (
                    <Typography variant="body1" color="text.secondary" sx={{ ml: 2, mt: 1.5 }}>
                      Selected content will appear here
                    </Typography>
                  )}

                  <Box sx={{ flexGrow: 1 }} />

                  <Button
                    variant="contained"
                    color="primary"
                    disableElevation
                    sx={{ minHeight: 42, px: 3 }}
                    onClick={() => setDrawerOpen(true)}
                  >
                    Select content
                  </Button>
                </Box>

                <CardContent
                  sx={{ p: 0 }}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={onSourceDrop}
                >
                  {busy ? (
                    <Skeleton variant="rectangular" height={360} sx={{ m: 2 }} animation="wave" />
                  ) : (
                    <TextField
                      multiline
                      fullWidth
                      minRows={18}
                      placeholder="Generated / edited content will appear here"
                      value={active.content}
                      onChange={(e) =>
                        patchSection(selected, { content: e.target.value, status: 'Draft' })
                      }
                      onBlur={(e) => saveContent(selected, e.target.value)}   
                      sx={{ p: 2 }}
                    />
                  )}
                </CardContent>

                <Stack direction={{ xs: 'column', md: 'row' }} divider={<Divider flexItem />}>
                  <Box
                    sx={{
                      flex: 1,
                      borderTop: 2,
                      borderTopColor: isCreateActive ? 'secondary.main' : 'divider',
                    }}
                  >
                    <Box sx={{ px: 2, py: 1, cursor: 'pointer' }} onClick={() => setMode('create')}>
                      <Typography
                        variant="subtitle2"
                        sx={{ color: isCreateActive ? 'secondary.main' : 'text.primary', mb: 4 }}
                      >
                        Create content
                      </Typography>
                    </Box>

                    <Box sx={{ px: 2, pb: 2 }}>
                      <Stack spacing={2}>
                        <TextField
                          select
                          size="small"
                          label="Preset"
                          defaultValue="summary"
                          onChange={(e) => (genPresetRef.current = e.target.value)}
                          disabled={!isCreateActive}
                          fullWidth
                        >
                          {genPresets.map((p) => (
                            <MenuItem key={p.key} value={p.key}>
                              {p.label}
                            </MenuItem>
                          ))}
                        </TextField>

                        <TextField
                          label="Additional guidance (optional)"
                          multiline
                          minRows={3}
                          size="small"
                          onChange={(e) => (genCustomRef.current = e.target.value)}
                          disabled={!isCreateActive}
                          fullWidth
                        />

                        <Button
                          variant="contained"
                          color="secondary"
                          onClick={runGenerate}
                          disabled={busy || !active.sources.length || !isCreateActive}
                          fullWidth
                          disableElevation
                        >
                          {busy && active.status.startsWith('Gen') ? 'Generating…' : 'Create'}
                        </Button>
                      </Stack>
                    </Box>
                  </Box>

                  <Box
                    sx={{
                      flex: 1,
                      borderTop: 2,
                      borderTopColor: isEditActive ? 'secondary.main' : 'divider',
                    }}
                  >
                    <Box sx={{ px: 2, py: 1, cursor: 'pointer' }} onClick={() => setMode('edit')}>
                      <Typography
                        variant="subtitle2"
                        sx={{ color: isEditActive ? 'secondary.main' : 'text.primary', mb: 4 }}
                      >
                        Edit content
                      </Typography>
                    </Box>

                    <Box sx={{ px: 2, pb: 2 }}>
                      <Stack spacing={2}>
                        <TextField
                          select
                          size="small"
                          label="Preset"
                          defaultValue="shorter"
                          onChange={(e) => (editPresetRef.current = e.target.value)}
                          disabled={!isEditActive}
                          fullWidth
                        >
                          {editPresets.map((p) => (
                            <MenuItem key={p.key} value={p.key}>
                              {p.label}
                            </MenuItem>
                          ))}
                        </TextField>

                        <TextField
                          label="Additional guidance (optional)"
                          multiline
                          minRows={3}
                          size="small"
                          onChange={(e) => (editCustomRef.current = e.target.value)}
                          disabled={!isEditActive}
                          fullWidth
                        />

                        <Button
                          variant="contained"
                          color="secondary"
                          onClick={runTransform}
                          disabled={busy || !active.content || !isEditActive}
                          fullWidth
                          disableElevation
                        >
                          {busy && active.status.startsWith('Trans') ? 'Transforming…' : 'Transform'}
                        </Button>
                      </Stack>
                    </Box>
                  </Box>
                </Stack>
              </Card>
            )}
          </Box>
        </Stack>
      </Paper>

      <Drawer
        anchor="right"
        variant="persistent"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        hideBackdrop
        PaperProps={{ sx: { width: { xs: '100%', sm: 800 } } }}
      >
        <Box sx={{ p: 2 }}>
          <Stack direction="row" alignItems="center" justifyContent="space-between">
            <Typography variant="h6">
              Uploaded&nbsp;Content&nbsp;
              <Badge
                badgeContent={active?.sources.length ?? 0}
                color="secondary"
                sx={{ '& .MuiBadge-badge': { right: -12 } }}
              />
            </Typography>
            <IconButton onClick={() => setDrawerOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Stack>

          <Divider sx={{ my: 2 }} />

          <Box sx={{ height: 480, width: '100%' }}>
            <DataGrid
              rows={uploadRows}
              disableRowSelectionOnClick
              density="compact"
              getRowId={(r) => r.id}
              initialState={{
                pagination: { paginationModel: { pageSize: 20, page: 0 } },
              }}
              columns={[
                {
                  field: 'name',
                  headerName: 'Name / label',
                  flex: 1,
                  renderCell: (params) => (
                    <span
                      draggable
                      onDragStart={(e) => handleDragStart(e, params.row)}
                      style={{ cursor: 'grab' }}
                    >
                      {params.value}
                    </span>
                  ),
                },
                { field: 'description', headerName: 'Description', flex: 2 },
                {
                  field: 'covered',
                  headerName: 'Covered in Memo',
                  width: 150,
                  renderCell: (params) => (
                    <Chip
                      label={params.value ? 'Yes' : 'No'}
                      color={params.value ? 'success' : 'default'}
                      size="small"
                    />
                  ),
                },
              ]}
            />
          </Box>
        </Box>
      </Drawer>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        message="Content updated"
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        action={
          <Button
            size="small"
            startIcon={<UndoIcon />}
            onClick={() => {
              patchSection(selected, { content: snackbar.prev });
              setSnackbar({ ...snackbar, open: false });
            }}
          >
            Undo
          </Button>
        }
      />

      {active && (
        <Box
          onDragOver={(e) => e.preventDefault()}
          onDrop={onSourceDrop}
          sx={{ position: 'fixed', inset: 0, zIndex: 998, pointerEvents: 'none' }}
        />
      )}

      <Menu anchorEl={menuAnchor} open={Boolean(menuAnchor)} onClose={closeMenu}>
        <MenuItem onClick={renameSection}>Rename</MenuItem>
        <MenuItem onClick={copySection}>Copy</MenuItem>
        <MenuItem
          onClick={() => {
            deleteSection(menuTargetId);
            closeMenu();
          }}
        >
          Delete
        </MenuItem>
      </Menu>
    </>
  );
}