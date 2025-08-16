import { createTheme, alpha } from '@mui/material/styles';

const primaryMain = '#3B82F6';   
const primaryLight = '#93C5FD';
const primaryDark = '#1E40AF';

const muiTheme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: primaryMain, light: primaryLight, dark: primaryDark, contrastText: '#ffffff' },
    secondary: { main: '#EB652B' },

    background: {
      default: '#F7FAFC',
      paper:   '#FFFFFF', 
    },
    divider: '#E5E7EB',
    text: {
      primary:   '#0F172A', 
      secondary: '#475569', 
    },
  },

  shape: { borderRadius: 12 },

  typography: {
    fontFamily: '"Roboto","Helvetica","Arial",sans-serif',
    h5: { fontSize: 22, fontWeight: 500 },
    body1: { fontSize: 16 },
    body2: { fontSize: 14 },     
    subtitle1: { fontSize: 16, fontWeight: 500 }, 
    caption: { fontSize: 14 },
    overline: { fontSize: 14 },
    button: { textTransform: 'none', fontWeight: 500 },
  },

  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#F7FAFC',
        },
      },
    },

    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 10,
          boxShadow: 'none',
        },
        contained: {
          boxShadow: 'none',
        },
      },
    },

    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
        outlined: {
          borderColor: '#E5E7EB',
        },
      },
    },

    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          '&.Mui-disabled': {
            backgroundColor: alpha(primaryMain, 0.04),
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: '#D1D5DB',
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: primaryMain,
          },
        },
        notchedOutline: {
          borderColor: '#E5E7EB',
        },
        input: {
          fontSize: 16,
          '&.Mui-disabled': {
            WebkitTextFillColor: 'inherit',
            opacity: 1,
          },
        },
      },
    },

    MuiInputLabel: {
      styleOverrides: {
        root: { fontSize: 16 },
      },
    },

    MuiFormHelperText: {
      styleOverrides: {
        root: { fontSize: 14 },
      },
    },

    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: '#E5E7EB',
        },
      },
    },
  },
});

export default muiTheme;