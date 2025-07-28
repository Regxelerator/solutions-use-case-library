import { createTheme } from '@mui/material/styles';

const muiTheme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#192841' },
    secondary: { main: '#EB652B' },
  },

  typography: {
    fontFamily: '"Roboto","Helvetica","Arial",sans-serif',
  },

  components: {
    MuiTabs: {
      styleOverrides: {
        indicator: { display: 'none' },
        flexContainer: { gap: 8 },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: ({ theme }) => ({
          textTransform: 'none',
          minHeight: 44,
          paddingInline: theme.spacing(3),
          fontWeight: 500,
          border: `1px solid ${theme.palette.grey[300]}`,
          borderRadius: '8px 8px 0 0',
          backgroundColor: theme.palette.grey[50],
          '&.Mui-selected': {
            backgroundColor: theme.palette.common.white,
            borderBottomColor: 'transparent',
          },
        }),
      },
    },

    MuiButton: { styleOverrides: { root: { textTransform: 'none' } } },
  },
});

export default muiTheme;