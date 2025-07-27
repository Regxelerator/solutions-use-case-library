import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Badge,
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  Chip,
  Divider,
  FormControl,
  MenuItem,
  Paper,
  Select,
  Snackbar,
  Stack,
  TextField,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import { DragDropContext, Draggable, Droppable } from 'react-beautiful-dnd';

const statusColour = (s) =>
  s === 'Ready' ? 'success' : s === 'Draft' ? 'default' : 'warning';

const downloadBlob = (blob, filename) => {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
};

export default function Tab3_Finalize_Memo() {
  const theme = useTheme();
  const isSmall = useMediaQuery(theme.breakpoints.down('sm'));

  const SIDEBAR_WIDTH = 340;

  const [sections, setSections] = useState([]);
  const [outline, setOutline] = useState([]);
  const [title, setTitle] = useState('Untitled memo');

  const [exportFmt, setExportFmt] = useState('docx');
  const [pending, setPending] = useState(false);
  const [snack, setSnack] = useState(false);

  /* ------------ initial & polling load ------------ */
  useEffect(() => {
    (async () => {
      const { data } = await axios.get('/api/memo');
      setSections(data.sections);
      setOutline(data.sections.map((s) => ({ id: s.id, included: true })));
    })();
  }, []);

  useEffect(() => {
    const int = setInterval(async () => {
      const { data } = await axios.get('/api/memo');
      setSections(data.sections);
    }, 10_000);
    return () => clearInterval(int);
  }, []);

  /* ------------ memo‑derived helpers ------------ */
  const mergedMd = useMemo(
    () =>
      outline
        .filter((o) => o.included)
        .map((o) => {
          const sec = sections.find((s) => s.id === o.id);
          return sec ? `## ${sec.title}\n\n${sec.content}` : '';
        })
        .join('\n\n'),
    [outline, sections]
  );

  const sortWithOutlineFirst = (arr) => {
    const idx = arr.findIndex((o) => o.label === 'OUTLINE_FIRST_SENTINEL');
    if (idx === -1) return arr;                            // nothing to do
    const [outline] = arr.splice(idx, 1);
    return [outline, ...arr];                              // move to front
  };

  const toggleInclude = (id) =>
    setOutline((o) =>
      o.map((x) => (x.id === id ? { ...x, included: !x.included } : x))
    );

  const handleDragEnd = ({ destination, source }) => {
    if (!destination) return;
    const reordered = [...outline];
    const [moved] = reordered.splice(source.index, 1);
    reordered.splice(destination.index, 0, moved);
    setOutline(sortWithOutlineFirst(reordered));           // keep outline first
  };

  /* ------------ actions ------------ */
  const markAllReady = async () => {
    await Promise.all(
      sections.map((s) =>
        axios.patch(`/api/memo/section/${s.id}`, { status: 'Ready' })
      )
    );
    setSections((s) => s.map((x) => ({ ...x, status: 'Ready' })));
  };

  const createOutline = async () => {
    const outlineLines = outline
      .map((o, i) => {
        const s = sections.find((sec) => sec.id === o.id);
        return s ? `* ${s.title}` : null;
      })
      .filter(Boolean)
      .join('\n');

    /* check if an Outline section already exists */
    let outlineSection = sections.find((s) => s.title === 'Outline');

    if (!outlineSection) {
      const { data } = await axios.post('/api/memo/section', {
        title: 'Outline',
      });
      outlineSection = { ...data, content: '', status: 'Draft', sources: [] };
      setSections((s) => [...s, outlineSection]);
      setOutline((o) => [{ id: outlineSection.id, included: true }, ...o]);
    }

    await axios.patch(`/api/memo/section/${outlineSection.id}`, {
      content: outlineLines,
      status: 'Ready',
    });

    setSections((s) =>
      s.map((sec) =>
        sec.id === outlineSection.id
          ? { ...sec, content: outlineLines, status: 'Ready' }
          : sec
      )
    );
  };

  const validate = () =>
    outline
      .filter((o) => o.included)
      .map((o) => {
        const s = sections.find((sec) => sec.id === o.id);
        if (!s) return null;
        if (s.status !== 'Ready') return `${s.title} is still ${s.status}`;
        if (!s.content.trim()) return `${s.title} is empty`;
        return null;
      })
      .filter(Boolean);

  const doExport = async (fmt) => {
    const errs = validate();
    if (errs.length) {
      alert(`Fix before export:\n• ${errs.join('\n• ')}`);
      return;
    }
    setPending(true);
    try {
      const { data } = await axios.post(
        '/api/memo/export',
        {
          format: fmt,
          title,
          section_order: outline.map((o) => o.id),
          include_ids: outline.filter((o) => o.included).map((o) => o.id),
        },
        { responseType: 'blob' }
      );
      downloadBlob(
        data,
        `${title.replace(/[^a-z0-9_\-]/gi, '_') || 'memo'}.${fmt}`
      );
      setSnack(true);
    } finally {
      setPending(false);
    }
  };

  /* ------------ outline pane ------------ */
  const outlineItems = (
    <DragDropContext onDragEnd={handleDragEnd}>
      <Droppable droppableId="toc">
        {(p) => (
          <Stack ref={p.innerRef} {...p.droppableProps} spacing={1}>
            {outline.map((o, idx) => {
              const sec = sections.find((s) => s.id === o.id);
              if (!sec) return null;
              const hasIssue =
                sec.status !== 'Ready' || !sec.content.trim();
              return (
                <Draggable key={o.id} draggableId={o.id} index={idx}>
                  {(pp) => (
                    <Stack
                      direction="row"
                      spacing={1}
                      ref={pp.innerRef}
                      {...pp.draggableProps}
                      {...pp.dragHandleProps}
                      sx={{
                        border: '1px solid',
                        borderColor: 'grey.300',
                        p: 1,
                        pr: 2,
                        alignItems: 'center',
                        width: '100%',
                      }}
                    >
                      <DragIndicatorIcon
                        fontSize="small"
                        sx={{ color: 'text.disabled', cursor: 'grab' }}
                      />
                      <Checkbox
                        checked={o.included}
                        onChange={() => toggleInclude(o.id)}
                        size="small"
                      />
                      <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                        <Typography variant="body2" noWrap sx={{ pr: 1 }}>
                          {sec.title}
                        </Typography>
                      </Box>

                      <Chip
                        label={sec.status}
                        size="small"
                        color={statusColour(sec.status)}
                        sx={{ alignSelf: 'center', mr: 2 }}
                      />

                      <Box
                        sx={{
                          width: 24,
                          height: 24,
                          position: 'relative',
                          flexShrink: 0,
                        }}
                      >
                        {hasIssue && (
                          <Badge
                            color="error"
                            variant="dot"
                            overlap="circular"
                            sx={{
                              position: 'absolute',
                              top: '50%',
                              right: 0,
                              transform: 'translateY(-50%)',
                            }}
                          >
                            <Box sx={{ width: 0, height: 0 }} />
                          </Badge>
                        )}
                      </Box>
                    </Stack>
                  )}
                </Draggable>
              );
            })}
            {p.placeholder}
          </Stack>
        )}
      </Droppable>
    </DragDropContext>
  );

  const outlinePanelContent = (
    <Stack
      spacing={2}
      sx={{ height: '100%', maxHeight: '80vh', overflow: 'hidden' }}
    >
      <Typography variant="subtitle1">Table of Contents</Typography>

      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>{outlineItems}</Box>

      <Box>
        <Button
          fullWidth
          variant="contained"
          color="primary"
          onClick={markAllReady}
          sx={{ color: '#fff' }}
        >
          Mark selected sections as complete
        </Button>
      </Box>
    </Stack>
  );

  const sidebar = isSmall ? (
    <Accordion sx={{ width: '100%' }}>
      <AccordionSummary>
        <Typography>Table of Contents</Typography>
      </AccordionSummary>
      <AccordionDetails>{outlinePanelContent}</AccordionDetails>
    </Accordion>
  ) : (
    <Paper
      variant="outlined"
      sx={{
        p: 2,
        width: SIDEBAR_WIDTH,
        flexShrink: 0,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {outlinePanelContent}
    </Paper>
  );

  /* ------------ preview pane ------------ */
  const preview = (
    <Card
      elevation={0}
      sx={{
        flex: 1,
        border: '1px solid',
        borderColor: 'grey.300',
        maxHeight: '80vh',
        display: 'flex',
        flexDirection: 'column',
        minWidth: 0,
        p: 2,
      }}
    >
      <CardContent sx={{ overflow: 'auto', flex: 1, p: 2 }} id="preview-scroll">
        <ReactMarkdown
          components={{
            h2: ({ node, ...props }) => (
              <Typography
                variant="subtitle1"
                fontWeight={600}
                gutterBottom
                {...props}
              />
            ),
            p: ({ node, ...props }) => (
              <Typography
                variant="body2"
                sx={{ fontSize: '0.9rem', lineHeight: 1.45, mb: 1 }}
                {...props}
              />
            ),
          }}
        >
          {mergedMd || '_Nothing to preview…_'}
        </ReactMarkdown>
      </CardContent>

      <Divider flexItem />
      <Stack
        direction="row"
        spacing={2}
        sx={{ p: 1 }}
        justifyContent="space-between"
        alignItems="center"
      >
      <Button
        variant="contained"
        color="primary"
        onClick={createOutline}
        sx={{ minWidth: 160, maxWidth: 260, px: 3, color: '#fff' }}
      >
        Create Outline
      </Button>


        <Stack direction="row" spacing={1} alignItems="center">
          <Button
            variant="contained"
            size="small"
            disabled={pending}
            onClick={() => doExport(exportFmt)}
            sx={{ minHeight: 36, height: 36, px: 3 }}
          >
            Export
          </Button>

          <FormControl
            size="small"
            sx={{
              minWidth: 100,
              '& .MuiInputBase-root': {
                minHeight: 36,
                height: 36,
                boxSizing: 'border-box',
                paddingTop: 0,
                paddingBottom: 0,
              },
              '& .MuiSelect-select': {
                display: 'flex',
                alignItems: 'center',
                paddingTop: '0 !important',
                paddingBottom: '0 !important',
              },
            }}
          >
            <Select
              value={exportFmt}
              onChange={(e) => setExportFmt(e.target.value)}
              size="small"
              sx={{
                minHeight: 36,
                height: 36,
                boxSizing: 'border-box',
                paddingTop: 0,
                paddingBottom: 0,
                display: 'flex',
                alignItems: 'center',
              }}
            >
              <MenuItem value="docx">Word</MenuItem>
              <MenuItem value="pdf">PDF</MenuItem>
            </Select>
          </FormControl>
        </Stack>
      </Stack>
    </Card>
  );

  /* ------------ render ------------ */
  return (
    <Paper elevation={0} variant="outlined" sx={{ p: 4, borderColor: 'grey.300' }}>
      <Typography variant="h6" gutterBottom>
        Draft memo
      </Typography>

      <Stack spacing={3}>
        <Stack direction="row" spacing={2} alignItems="center">
          <TextField
            size="small"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Memo title"
            sx={{ width: isSmall ? '100%' : SIDEBAR_WIDTH }}
          />
        </Stack>

        <Stack
          direction={isSmall ? 'column' : 'row'}
          spacing={3}
          divider={
            <Divider
              orientation={isSmall ? 'horizontal' : 'vertical'}
              flexItem
            />
          }
        >
          {sidebar}
          {preview}
        </Stack>
      </Stack>

      <Snackbar
        open={snack}
        autoHideDuration={3000}
        onClose={() => setSnack(false)}
        message="Done"
      />
    </Paper>
  );
}