import React from 'react';
import { Box, Tab, Tabs, Typography } from '@mui/material';

import Tab1_Select_Content from './components/tabs/Tab1_Select_Content';
import Tab2_Create_Memo from './components/tabs/Tab2_Create_Memo';
import Tab3_Finalize_Memo from './components/tabs/Tab3_Finalize_Memo';
import Tab4_Administration from './components/tabs/Tab4_Administration';

const TAB_STORAGE_KEY = 'bmc_active_tab';          

export default function App() {
  const [tab, setTab] = React.useState(() => {
    const saved = parseInt(localStorage.getItem(TAB_STORAGE_KEY), 10);
    return Number.isFinite(saved) && saved >= 0 && saved <= 3 ? saved : 0;
  });

  React.useEffect(() => {
    localStorage.setItem(TAB_STORAGE_KEY, String(tab));
  }, [tab]);

  return (
    <Box sx={{ p: 2 }}>
      <Typography
        variant="h4"
        component="h2"
        fontWeight={300}
        sx={{ mb: 5, mt: 1 }}
      >
        Briefing Memo Creator
      </Typography>

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 1 }}>
        <Tab label="Step 1 - Content Selection" />
        <Tab label="Step 2 - Memo Creation" />
        <Tab label="Step 3 - Memo Finalization" />
        <Tab label="Administration" />
      </Tabs>

      <Box sx={{ bgcolor: 'background.paper', p: 0 }}>
        {tab === 0 && <Tab1_Select_Content />}
        {tab === 1 && <Tab2_Create_Memo />}
        {tab === 2 && <Tab3_Finalize_Memo />}
        {tab === 3 && <Tab4_Administration />}
      </Box>
    </Box>
  );
}