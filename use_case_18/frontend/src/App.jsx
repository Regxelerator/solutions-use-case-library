import React from 'react';
import {
  AppBar,
  Box,
  Paper,
  Toolbar,
  Typography,
} from '@mui/material';
import ChatPane from './components/ChatPane';
import IncidentForm from './components/IncidentForm';
import { connectAgent } from './api/ws';

export default function App() {
  React.useEffect(() => { connectAgent(); }, []);

  const HEADER_HEIGHT = 64;

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="static" elevation={0} color="transparent">
        <Toolbar
          sx={{
            justifyContent: 'center',
            borderBottom: '1px solid',
            borderColor: 'divider',
            minHeight: `${HEADER_HEIGHT}px !important`,
          }}
        >
          <Typography variant="h5" fontWeight={300} textAlign="center">
            Risk Incident Reporting Platform
          </Typography>
        </Toolbar>
      </AppBar>

      <Box
        sx={{
          width: '100%',
          px: { xs: 1, sm: 2, md: 3 },
          py: 0,
          boxSizing: 'border-box',
        }}
      >
        <Paper
          elevation={0}
          variant="outlined"
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            width: '100%',
            height: `calc(100vh - ${HEADER_HEIGHT}px)`,
            borderColor: 'grey.300',
            overflow: 'hidden', 
          }}
        >
          <Box
            sx={{
              flex: 1,
              minWidth: 320,
              borderRight: { md: '1px solid' },
              borderColor: 'divider',
              bgcolor: 'grey.50',
              minHeight: 0, 
            }}
          >
            <ChatPane />
          </Box>

          <Box
            sx={{
              flex: 1,
              minWidth: 320,
              bgcolor: 'background.paper',
              minHeight: 0,
            }}
          >
            <IncidentForm />
          </Box>
        </Paper>
      </Box>
    </Box>
  );
}