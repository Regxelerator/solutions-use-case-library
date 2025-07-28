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
import DeleteIcon from '@mui/icons-material/Delete';
import UpgradeIcon from '@mui/icons-material/Upgrade';          

import { DragDropContext, Draggable, Droppable } from 'react-beautiful-dnd';

const SECTION_W = { xs: '100%', sm: 340 }; 
const FIELD_W = { xs: '100%', sm: 340 };

function InstructionPanel({
  contentInstr,
  setContentInstr,
  styleInstr,
  setStyleInstr,
  onGenerate,
  onClear,
  generating,
  progress,
  hasMemo,
}) {
  const hasInput = contentInstr.trim() || styleInstr.trim();
  const primaryLabel = hasMemo ? 'Recreate memo' : 'Create memo';

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

        <Grid item xs={12}>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={0}
            flexWrap="wrap"
          >
            <Button
              variant="contained"
              disableElevation
              onClick={onGenerate}
              disabled={generating || !hasInput}
              sx={{ width: SECTION_W, minHeight: 45 }}
            >
              {generating ? 'Generating…' : primaryLabel}
            </Button>

            <Button
              variant="outlined"
              color="secondary"
              onClick={onClear}
              disabled={generating && !hasInput}
              sx={{
                width: SECTION_W,
                minHeight: 45,
                ml: { xs: 0, sm: 3 }, 
                mt: { xs: 2, sm: 0 },
              }}
            >
              Clear instructions
            </Button>
          </Stack>
        </Grid>

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

const statusColor = (s) =>
  s === 'Ready'
    ? 'success'
    : s === 'Draft'
    ? 'default'
    : s.startsWith('Gen') || s.startsWith('Trans')
    ? 'info'
    : 'default';

export default function Tab2_Create_Memo() {
  const [contentInstr, setContentInstr] = useState('');
  const [styleInstr, setStyleInstr] = useState('');
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState([]);

  const [sections, setSections] = useState([]);
  const [selected, setSelected] = useState(null);
  const [contentBank, setContentBank] = useState([]);

  const [feedbackRows, setFeedbackRows] = useState([]);

  const [menuAnchor, setMenuAnchor] = useState(null);
  const [menuTargetId, setMenuTargetId] = useState(null);
  const [renameActiveId, setRenameActiveId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');

  const sectionsRef = useRef(sections);
  useEffect(() => void (sectionsRef.current = sections), [sections]);

  useEffect(() => {
    (async () => {
      const memo = await axios.get('/api/memo');
      setSections(memo.data.sections);
      if (memo.data.sections.length) setSelected(memo.data.sections[0].id);

      const bank = await axios.get('/api/masterlist');
      setContentBank(bank.data.entries);
    })();
  }, []);

  const clearInstructions = () => {
    setContentInstr('');
    setStyleInstr('');
  };

  const runAgenticWorkflow = async () => {
    const ci = contentInstr.trim();
    const si = styleInstr.trim();
    if (!ci && !si) return;

    setProgress([]);
    setGenerating(true);

    let es;
    try {
      es = new EventSource('/api/memo/agentic/progress');
      es.onmessage = (e) =>
        e?.data && setProgress((p) => [...p, e.data]);
      es.onerror = () => es.close();
    } catch {}

    const combined = [ci && `Content instructions:\n${ci}`, si && `Stylistic instructions:\n${si}`]
      .filter(Boolean)
      .join('\n\n');

    try {
      const { data } = await axios.post('/api/memo/agentic', { instruction: combined });
      setSections(data.sections);
      if (data.sections.length) setSelected(data.sections[0].id);
      setFeedbackRows([]);
    } catch (err) {
      console.error(err);
      alert('Memo generation failed. See console for details.');
    } finally {
      es?.close?.();
      setGenerating(false);
    }
  };

  const runFeedbackWorkflow = async () => {
    if (!feedbackRows.length) return;
    const ci = contentInstr.trim();
    const si = styleInstr.trim();

    setGenerating(true);

    try {
      const { data } = await axios.post('/api/memo/agentic_feedback', {
        feedback: feedbackRows,
        content_instructions: ci,
        style_instructions: si,
      });
      setSections(data.sections);
      setSelected(data.sections.length ? data.sections[0].id : null);
      setFeedbackRows([]);
    } catch (err) {
      console.error(err);
      alert('Updating memo with feedback failed. See console for details.');
    } finally {
      setGenerating(false);
    }
  };

  const patchSection = (id, patch) =>
    setSections((s) => s.map((sec) => (sec.id === id ? { ...sec, ...patch } : sec)));

  const saveContent = (id, content) =>
    axios.patch(`/api/memo/section/${id}`, { content, status: 'Draft' }).catch(() => {});

  const active = useMemo(
    () => sections.find((s) => s.id === selected) ?? null,
    [sections, selected]
  );

  const reorderSections = async ({ destination, source, type }) => {
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
    setTimeout(() => document.getElementById(`sec-title-input-${sec.id}`)?.focus(), 0);
  };

  const deleteSection = async (id) => {
    await axios.delete(`/api/memo/section/${id}`);
    setSections((s) => s.filter((sec) => sec.id !== id));
    if (selected === id) setSelected(null);
  };

  useEffect(() => {
    if (!selected) return;
    const t = setInterval(() => {
      const sec = sectionsRef.current.find((s) => s.id === selected);
      if (sec && sec.status === 'Draft') saveContent(selected, sec.content);
    }, 10_000);
    return () => clearInterval(t);
  }, [selected]);

  const deleteDraftMemo = async () => {
    if (!sections.length) return;
    if (!window.confirm('Delete the entire draft memo?')) return;
    try {
      await axios.delete('/api/memo');
      setSections([]);
      setSelected(null);
      setFeedbackRows([]);
    } catch (err) {
      console.error(err);
      alert('Failed to delete draft memo.');
    }
  };

  const addFeedbackRow = () =>
    setFeedbackRows((r) => [...r, { sectionId: 'cross', text: '' }]);

  const updateFeedbackRow = (idx, patch) =>
    setFeedbackRows((rows) => rows.map((r, i) => (i === idx ? { ...r, ...patch } : r)));

  const removeFeedbackRow = (idx) =>
    setFeedbackRows((rows) => rows.filter((_, i) => i !== idx));


  return (
    <Paper elevation={0} variant="outlined" sx={{ p: 4, borderColor: 'grey.300' }}>
      <InstructionPanel
        contentInstr={contentInstr}
        setContentInstr={setContentInstr}
        styleInstr={styleInstr}
        setStyleInstr={setStyleInstr}
        onGenerate={runAgenticWorkflow}
        onClear={clearInstructions}
        generating={generating}
        progress={progress}
        hasMemo={sections.length > 0}
      />

      {sections.length > 0 && (
        <>
          <Stack direction="row" spacing={3}>
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
                                  border:
                                    selected === sec.id ? '2px solid' : '1px solid',
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
                                          e.preventDefault(); commitTitle();
                                        }
                                        if (e.key === 'Escape')
                                          setRenameActiveId(null);
                                      }}
                                      fullWidth
                                    />
                                  ) : (
                                    <Typography
                                      noWrap
                                      variant="body2"
                                      fontWeight={500}
                                    >
                                      {sec.title}
                                    </Typography>
                                  )}
                                </Box>

                                <Chip
                                  label={sec.status}
                                  size="small"
                                  color={statusColor(sec.status)}
                                />

                                <IconButton
                                  size="small"
                                  onClick={(e) => openMenu(e, sec.id)}
                                >
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

              <Button
                variant="contained"
                color="secondary"
                onClick={deleteDraftMemo}
                sx={{
                  width: SECTION_W,
                  minHeight: 45,
                  mt: 2,
                  backgroundColor: 'secondary.main',
                  '&:hover': { backgroundColor: 'secondary.dark' },
                }}
              >
                Delete draft memo
              </Button>
            </Box>

            <Box sx={{ flexGrow: 1, minWidth: 0 }}>
              <Card
                elevation={0}
                sx={{ border: '1px solid', borderColor: 'grey.300', mb: 2 }}
              >
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
                            .patch(`/api/memo/section/${selected}`, {
                              title: e.target.value,
                            })
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
                          const label =
                            src?.content_name || src?.filename || sid;
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
                        onBlur={(e) =>
                          saveContent(selected, e.target.value)
                        }
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

              <Button
                variant="outlined"
                onClick={addFeedbackRow}
                sx={{ width: SECTION_W, minHeight: 45, mb: 2 }}
              >
                Add feedback
              </Button>

              <Button
                variant="contained"
                startIcon={<UpgradeIcon />}
                disabled={generating || !feedbackRows.length}
                onClick={runFeedbackWorkflow}
                sx={{
                  width: SECTION_W,
                  minHeight: 45,
                  ml: { xs: 0, sm: 2 },
                  mb: 2,
                  mt: { xs: 2, sm: 0 },
                }}
              >
                Update memo with feedback
              </Button>

              {feedbackRows.map((row, idx) => (
                <Stack
                  key={idx}
                  direction={{ xs: 'column', sm: 'row' }}
                  spacing={2}
                  sx={{ mb: 2 }}
                  alignItems="stretch"
                >
                  <TextField
                    select
                    size="small"
                    value={row.sectionId}
                    onChange={(e) => updateFeedbackRow(idx, { sectionId: e.target.value })}
                    sx={{
                      width: FIELD_W,
                      flexShrink: 0,
                      flexBasis: FIELD_W,

                      '& .MuiInputBase-root': {
                        height: '100%',
                        alignItems: 'flex-start',
                      },
                    }}
                  >
                    {sections.map((s) => (
                      <MenuItem key={s.id} value={s.id}>
                        {s.title}
                      </MenuItem>
                    ))}
                    <MenuItem value="cross">Cross‑cutting feedback</MenuItem>
                  </TextField>

                  <TextField
                    multiline
                    minRows={2}
                    fullWidth
                    placeholder="Your feedback"
                    value={row.text}
                    onChange={(e) =>
                      updateFeedbackRow(idx, { text: e.target.value })
                    }
                  />

                  <IconButton
                    onClick={() => removeFeedbackRow(idx)}
                    sx={{ alignSelf: 'flex-start', color: 'text.secondary' }}  // subtle grey
                  >
                    <DeleteIcon />
                  </IconButton>

                </Stack>
              ))}
            </Box>
          </Stack>

          <Menu
            anchorEl={menuAnchor}
            open={Boolean(menuAnchor)}
            onClose={closeMenu}
          >
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
        </>
      )}
    </Paper>
  );
}