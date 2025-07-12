import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import SimpleTradingDashboard from './components/SimpleTradingDashboard';
import './App.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <SimpleTradingDashboard />
    </ThemeProvider>
  );
}

export default App;
