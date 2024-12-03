import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import ReactMarkdown from 'react-markdown';
import {
  Container,
  Paper,
  Typography,
  Button,
  Select,
  MenuItem,
  CircularProgress,
  Box,
  AppBar,
  Toolbar,
  IconButton,
  Snackbar,
  Alert,
  Divider,
  ThemeProvider,
  createTheme,
  CssBaseline
} from '@mui/material';
import { CloudUpload, Article, Translate, GitHub } from '@mui/icons-material';

// Create a custom theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#2563eb',
    },
    background: {
      default: '#f8fafc',
    },
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

function App() {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState('english');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf']
    },
    onDrop: acceptedFiles => {
      setFile(acceptedFiles[0]);
      setError('');
      setSnackbar({ open: true, message: 'File uploaded successfully!', severity: 'success' });
    }
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a PDF file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);

    try {
      setLoading(true);
      setError('');
      const response = await fetch('http://localhost:8000/convert', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        },
        credentials: 'omit'
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Network error occurred' }));
        throw new Error(errorData.detail || 'Conversion failed');
      }

      const data = await response.json();
      setResult(data.content);
      setSnackbar({ open: true, message: 'Conversion successful!', severity: 'success' });
    } catch (err) {
      console.error('Error:', err);
      if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
        setError('Cannot connect to the server. Please make sure the backend is running on port 8000.');
      } else {
        setError(err.message || 'Failed to convert the PDF. Please try again.');
      }
      setSnackbar({ open: true, message: err.message, severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" color="transparent" elevation={0}>
          <Toolbar>
            <Article sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Paper2Blog
            </Typography>
            <IconButton
              href="https://github.com/yourusername/Paper2Blog"
              target="_blank"
              rel="noopener noreferrer"
            >
              <GitHub />
            </IconButton>
          </Toolbar>
        </AppBar>

        <Container maxWidth="md" sx={{ py: 4 }}>
          <Paper elevation={0} sx={{ p: 4, mb: 4, border: '1px solid #e2e8f0' }}>
            <Typography variant="h5" gutterBottom align="center" sx={{ mb: 3 }}>
              Convert Academic Papers to Blog Posts
            </Typography>

            <form onSubmit={handleSubmit}>
              <Box
                {...getRootProps()}
                sx={{
                  border: '2px dashed',
                  borderColor: isDragActive ? 'primary.main' : 'grey.300',
                  borderRadius: 3,
                  p: 4,
                  mb: 3,
                  textAlign: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'action.hover'
                  }
                }}
              >
                <input {...getInputProps()} />
                <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  {isDragActive ? 'Drop your PDF here' : 'Drag & drop your PDF here'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  or click to select a file
                </Typography>
                {file && (
                  <Typography variant="body2" color="primary" sx={{ mt: 2 }}>
                    Selected: {file.name}
                  </Typography>
                )}
              </Box>

              <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                <Select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  fullWidth
                  sx={{ 
                    borderRadius: 2,
                    '& .MuiSelect-select': {
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1
                    }
                  }}
                >
                  <MenuItem value="english">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Translate fontSize="small" />
                      English
                    </Box>
                  </MenuItem>
                  <MenuItem value="chinese">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Translate fontSize="small" />
                      Chinese
                    </Box>
                  </MenuItem>
                </Select>

                <Button
                  type="submit"
                  variant="contained"
                  fullWidth
                  disabled={loading || !file}
                  sx={{
                    py: 1.5,
                    px: 4,
                  }}
                >
                  {loading ? (
                    <CircularProgress size={24} sx={{ color: 'common.white' }} />
                  ) : (
                    'Convert to Blog'
                  )}
                </Button>
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}
            </form>
          </Paper>

          {result && (
            <Paper 
              elevation={0} 
              sx={{ 
                p: 4, 
                border: '1px solid #e2e8f0',
                '& img': {
                  maxWidth: '100%',
                  height: 'auto',
                  borderRadius: 1
                }
              }}
            >
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Generated Blog Post
                </Typography>
                <Divider />
              </Box>
              <Box sx={{ 
                '& .markdown-body': { 
                  fontFamily: 'inherit',
                  lineHeight: 1.7
                } 
              }}>
                <ReactMarkdown className="markdown-body">{result}</ReactMarkdown>
              </Box>
            </Paper>
          )}
        </Container>

        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
        >
          <Alert 
            onClose={() => setSnackbar({ ...snackbar, open: false })} 
            severity={snackbar.severity}
            sx={{ width: '100%' }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
        <footer className="footer">
          &copy; 2024 Paper2Blog by <a href="https://github.com/pprp" target="_blank" rel="noopener noreferrer">pprp</a>. All rights reserved.
        </footer>
      </Box>
    </ThemeProvider>
  );
}

export default App;
