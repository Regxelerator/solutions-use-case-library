import React, { useEffect, useMemo, useRef, useState } from 'react';
import axios from 'axios';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  IconButton,
  LinearProgress,
  List,
  Menu,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material';

import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import MoreVertIcon from '@mui/icons-material/MoreVert';

import { DragDropContext, Draggable, Droppable } from 'react-beautiful-dnd';

/* ========================================================================== */
/*  Helper – top instruction panel                                            */
/* ========================================================================== */

function InstructionPanel({
  contentInstr,
  setContentInstr,
  styleInstr,
  setStyleInstr,
  onGenerate,
  generating,
  progress,
}) {
  const hasInput = contentInstr.trim() || styleInstr.trim();

  return (
    <>
      <Typography variant="h6" gutterBottom sx={{ mb: 0 }}>
        Create memo
      </Typography>

      <Grid container rowSpacing={1.5} columnSpacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12}>
          <Typography variant="body1">
            Provide your instructions for memo creation
          </Typography>
        </Grid>

        {/* -------- two side‑by‑side instruction fields -------- */}
        <Grid item xs={12} sm={6}>
          <TextField
            multiline
            minRows={4}
            fullWidth
            placeholder="Content instructions (topics, focus areas) *"
            value={contentInstr}
            onChange={(e) => setContentInstr(e.target.value)}
            disabled={generating}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            multiline
            minRows={4}
            fullWidth
            placeholder="Stylistic instructions (format, tone, length)"
            value={styleInstr}
            onChange={(e) => setStyleInstr(e.target.value)}
            disabled={generating}
          />
        </Grid>

        {/* ---------------- action button --------------------- */}
        <Grid item xs={12}>
          <Button
            variant="contained"
            disableElevation
            onClick={onGenerate}
            disabled={generating || !hasInput}
            sx={{ width: { xs: '100%', sm: 500 }, minHeight: 45 }}
          >
            {generating ? 'Generating…' : 'Create memo'}
          </Button>
        </Grid>

        {/* ---------------- progress bar ---------------------- */}
        {generating && (
          <Grid item xs={12}>
            <LinearProgress sx={{ mt: 2, mb: 2 }} />
            <Stack spacing={0.5}>
              {progress.map((p, i) => (
                <Typography key={i} variant="body2">
                  {p}
                </Typography>
              ))}
            </Stack>
          </Grid>
        )}
      </Grid>
    </>
  );
}

/* -------------------------------------------------------------------------- */

const statusColor = (s) =>
  s === 'Ready'
    ? 'success'
    : s === 'Draft'
    ? 'default'
    : s.startsWith('Gen') || s.startsWith('Trans')
    ? 'info'
    : 'default';

/* ========================================================================== */
/*  Component                                                                 */
/* ========================================================================== */

export default function Tab2_Create_Memo() {
  /* ---------------- agentic generation state ------------------------- */
  const [contentInstr, setContentInstr] = useState('');
  const [styleInstr, setStyleInstr] = useState('');
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState([]);

  /* ---------------- workspace (draft memo) state --------------------- */
  const [sections, setSections] = useState([]);
  const [selected, setSelected] = useState(null);
  const [contentBank, setContentBank] = useState([]);

  /* -------------- rename helpers & menu ------------------------------ */
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [menuTargetId, setMenuTargetId] = useState(null);
  const [renameActiveId, setRenameActiveId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');

  /* ---- ref for auto‑save -------------------------------------------- */
  const sectionsRef = useRef(sections);
  useEffect(() => {
    sectionsRef.current = sections;
  }, [sections]);

  /* ---------------- initial load of existing memo -------------------- */
  useEffect(() => {
    (async () => {
      const memo = await axios.get('/api/memo');
      setSections(memo.data.sections);
      if (memo.data.sections.length) setSelected(memo.data.sections[0].id);

      const bank = await axios.get('/api/masterlist');
      setContentBank(bank.data.entries);
    })();
  }, []);

  /* ---------------- trigger agentic workflow ------------------------- */
  const runAgenticWorkflow = async () => {
    const ci = contentInstr.trim();
    const si = styleInstr.trim();
    if (!ci && !si) return;

    setProgress([]);
    setGenerating(true);

    /* optional SSE progress feed */
    let es;
    try {
      es = new EventSource('/api/memo/agentic/progress');
      es.onmessage = (evt) =>
        evt?.data && setProgress((p) => [...p, evt.data]);
      es.onerror = () => es.close();
    } catch {
      /* ignore if SSE not available */
    }

    const combined = [
      ci && `Content instructions:\n${ci}`,
      si && `Stylistic instructions:\n${si}`,
    ]
      .filter(Boolean)
      .join('\n\n');

    try {
      const { data } = await axios.post('/api/memo/agentic', {
        instruction: combined,
      });
      setSections(data.sections);
      if (data.sections.length) setSelected(data.sections[0].id);
    } catch (err) {
      console.error(err);
      alert('Memo generation failed. See console for details.');
    } finally {
      es?.close?.();
      setGenerating(false);
    }
  };

  /* ---------------- workspace helpers (rename / delete) -------------- */
  const patchSection = (id, patch) =>
    setSections((s) => s.map((sec) => (sec.id === id ? { ...sec, ...patch } : sec)));

  const saveContent = (id, content) =>
    axios
      .patch(`/api/memo/section/${id}`, { content, status: 'Draft' })
      .catch(() => {});

  const active = useMemo(
    () => sections.find((s) => s.id === selected) ?? null,
    [sections, selected]
  );

  const reorderSections = async (result) => {
    const { destination, source, type } = result;
    if (!destination || type !== 'SECTION') return;
    const reordered = [...sections];
    const [moved] = reordered.splice(source.index, 1);
    reordered.splice(destination.index, 0, moved);
    setSections(reordered);
    await axios.post('/api/memo/reorder', { order: reordered.map((s) => s.id) });
  };

  const commitTitle = async () => {
    if (!renameActiveId) return;
    const trimmed = editingTitle.trim();
    const sec = sections.find((s) => s.id === renameActiveId);
    setRenameActiveId(null);

    if (!sec || !trimmed || sec.title === trimmed) return;

    patchSection(sec.id, { title: trimmed });
    await axios.patch(`/api/memo/section/${sec.id}`, { title: trimmed });
  };

  const openMenu = (e, id) => {
    setMenuAnchor(e.currentTarget);
    setMenuTargetId(id);
  };
  const closeMenu = () => setMenuAnchor(null);

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

  const deleteSection = async (id) => {
    await axios.delete(`/api/memo/section/${id}`);
    setSections((s) => s.filter((sec) => sec.id !== id));
    if (selected === id) setSelected(null);
  };

  /* ---- auto‑save every 10 s ----------------------------------------- */
  useEffect(() => {
    if (!selected) return;
    const t = setInterval(() => {
      const sec = sectionsRef.current.find((s) => s.id === selected);
      if (sec && sec.status === 'Draft') saveContent(selected, sec.content);
    }, 10_000);
    return () => clearInterval(t);
  }, [selected]);

  /* =================================================================== */
  /*  Render                                                             */
  /* =================================================================== */

  return (
    <Paper elevation={0} variant="outlined" sx={{ p: 4, borderColor: 'grey.300' }}>
      {/* --------------------------- top input panel -------------------- */}
      <InstructionPanel
        contentInstr={contentInstr}
        setContentInstr={setContentInstr}
        styleInstr={styleInstr}
        setStyleInstr={setStyleInstr}
        onGenerate={runAgenticWorkflow}
        generating={generating}
        progress={progress}
      />

      {/* --------------------- workspace (shown only after draft) -------- */}
      {sections.length > 0 && (
        <Stack direction="row" spacing={3}>
          {/* ---------- left sidebar (sections) ---------- */}
          <Box sx={{ width: { xs: '35%', md: 340 }, minWidth: 260 }}>
            <Paper
              elevation={0}
              variant="outlined"
              sx={{ maxHeight: '72vh', overflow: 'auto', p: 1 }}
            >
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
                                borderColor:
                                  selected === sec.id ? 'primary.main' : 'grey.300',
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
                                sx={{
                                  cursor: 'grab',
                                  color: 'text.disabled',
                                  pointerEvents: 'auto',
                                }}
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

          {/* ---------- right pane (editor) ------------- */}
          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            <Card elevation={0} sx={{ border: '1px solid', borderColor: 'grey.300' }}>
              {active ? (
                <>
                  <Box sx={{ p: 2 }}>
                    <TextField
                      fullWidth
                      size="small"
                      placeholder="Section title"
                      value={active.title}
                      onChange={(e) => {
                        patchSection(selected, { title: e.target.value });
                        axios
                          .patch(`/api/memo/section/${selected}`, { title: e.target.value })
                          .catch(() => {});
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
                  >
                    {active.sources.length ? (
                      active.sources.map((sid) => {
                        const src = contentBank.find((c) => c.id === sid);
                        const label = src?.content_name || src?.filename || sid;
                        return <Chip key={sid} label={label} size="small" />;
                      })
                    ) : (
                      <Typography
                        variant="body1"
                        color="text.secondary"
                        sx={{ ml: 2, mt: 1.5 }}
                      >
                        No content mapped to this section
                      </Typography>
                    )}
                  </Box>

                  <CardContent sx={{ p: 0 }}>
                    <TextField
                      multiline
                      fullWidth
                      minRows={18}
                      placeholder="Section content"
                      value={active.content}
                      onChange={(e) =>
                        patchSection(selected, {
                          content: e.target.value,
                          status: 'Draft',
                        })
                      }
                      onBlur={(e) => saveContent(selected, e.target.value)}
                      sx={{ p: 2 }}
                    />
                  </CardContent>
                </>
              ) : (
                <Box
                  sx={{
                    height: 420,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'text.secondary',
                  }}
                >
                  Select a section on the left.
                </Box>
              )}
            </Card>
          </Box>
        </Stack>
      )}

      {/* ----------------------------- menu ----------------------------- */}
      <Menu anchorEl={menuAnchor} open={Boolean(menuAnchor)} onClose={closeMenu}>
        <MenuItem onClick={renameSection}>Rename</MenuItem>
        <MenuItem
          onClick={() => {
            deleteSection(menuTargetId);
            closeMenu();
          }}
        >
          Delete
        </MenuItem>
      </Menu>
    </Paper>
  );
}