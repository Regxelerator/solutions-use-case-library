import React, { useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Typography,
  Divider,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { useIncidentStore } from '../store/incident';
import { sendUserMsg } from '../api/ws';
import { alpha, useTheme } from '@mui/material/styles';

const TOPBAR_H = 64;
const BOTTOMBAR_H = 72; 

function getFieldBorderRadiusCss(theme) {
  const oi = theme.components?.MuiOutlinedInput?.styleOverrides;
  let r =
    (oi && typeof oi.root === 'object' && oi.root?.borderRadius) ??
    (oi && typeof oi.notchedOutline === 'object' && oi.notchedOutline?.borderRadius) ??
    theme.shape?.borderRadius;

  if (typeof r === 'number') return `${r}px`;
  if (typeof r === 'string') return r;
  return '4px';
}

function Bubble({ role, children }) {
  const isUser = role === 'user';
  const theme = useTheme();

  const fieldRadiusCss = getFieldBorderRadiusCss(theme);

  const userBg = alpha(theme.palette.primary.main, 0.12);
  const userBorder = alpha(theme.palette.primary.main, 0.24);

  return (
    <Box sx={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', mb: 1 }}>
      <Box
        sx={{
          px: 2,
          py: 1,
          maxWidth: '75%',
          borderRadius: fieldRadiusCss, 
          bgcolor: isUser ? userBg : 'background.paper',
          color: 'text.primary',
          border: '1px solid',
          borderColor: isUser ? userBorder : 'divider',
        }}
      >
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.5 }}>
          {children}
        </Typography>
      </Box>
    </Box>
  );
}

export default function ChatPane() {
  const transcript = useIncidentStore((s) => s.transcript);
  const [draft, setDraft] = React.useState('');
  const listRef = useRef();

  useEffect(() => {
    listRef.current?.lastElementChild?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript.length]);

  const submit = () => {
    const text = draft.trim();
    if (!text) return;
    sendUserMsg(text);
    useIncidentStore.getState().appendChat({ role: 'user', content: text });
    setDraft('');
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
          Conversation
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Start a conversation with the agent to capture the details of the risk incident.
        </Typography>
      </Box>
      <Divider />

      <Box
        ref={listRef}
        sx={{ flex: 1, overflow: 'auto', px: 1.25, pt: 1.25, pb: 1, minHeight: 0 }}
      >
        {transcript.length === 0 && (
          <Bubble role="assistant">
            Good day! Start by describing the risk incident. I will then guide you through the rest and update the risk incident reporting form with the information provided.
          </Bubble>
        )}
        {transcript.map((m, i) => (
          <div key={i}>
            <Bubble role={m.role}>{m.content}</Bubble>
          </div>
        ))}
      </Box>

      <Divider />
      <Box
        sx={{
          display: 'flex',
          gap: 1,
          px: 1,
          height: BOTTOMBAR_H,
          alignItems: 'center',
          bgcolor: 'background.default',
          borderTop: '1px solid',
          borderColor: 'divider',
        }}
      >
        <TextField
          fullWidth
          size="small"
          placeholder="Type a message…"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), submit())}
          sx={{
            '& .MuiOutlinedInput-root': { borderRadius: '6px' },
            '& .MuiInputBase-input': { padding: '14px' },
          }}
        />
        <IconButton
          color="primary"
          onClick={submit}
          sx={{ borderRadius: 3 }}
          aria-label="Send message"
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
}
