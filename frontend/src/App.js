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
    mode: 'light',
    primary: {
      main: '#2563eb',
    },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
    },
    grey: {
      100: '#f1f5f9',
      200: '#e2e8f0',
    }
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          padding: '8px 16px',
          fontWeight: 500,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
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
      <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <AppBar position="static" elevation={0} sx={{ backgroundColor: 'white', borderBottom: 1, borderColor: 'grey.200' }}>
          <Container maxWidth="lg">
            <Toolbar disableGutters sx={{ justifyContent: 'space-between' }}>
              <Typography variant="h6" sx={{ color: 'text.primary', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Article /> Paper2Blog
              </Typography>
              <IconButton
                href="https://github.com/yourusername/paper2blog"
                target="_blank"
                rel="noopener noreferrer"
                sx={{ color: 'text.primary' }}
              >
                <GitHub />
              </IconButton>
            </Toolbar>
          </Container>
        </AppBar>

        <Container maxWidth="lg" sx={{ flex: 1, py: 4 }}>
          <Box sx={{ maxWidth: 800, mx: 'auto' }}>
            <Typography variant="h1" gutterBottom align="center" sx={{ mb: 2 }}>
              Convert Papers to Blog Posts
            </Typography>
            <Typography 
              variant="h6" 
              align="center" 
              color="text.secondary"
              sx={{ 
                mb: 4,
                fontWeight: 400,
                maxWidth: '600px',
                mx: 'auto',
                lineHeight: 1.5
              }}
            >
              Transform complex academic papers into engaging blog posts in seconds. Share your research with the world! 🚀
            </Typography>

            <Paper
              {...getRootProps()}
              sx={{
                p: 4,
                mb: 4,
                cursor: 'pointer',
                backgroundColor: isDragActive ? 'grey.100' : 'white',
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'grey.200',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  borderColor: 'primary.main',
                  backgroundColor: 'grey.100',
                },
              }}
            >
              <input {...getInputProps()} />
              <Box sx={{ textAlign: 'center' }}>
                <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  {isDragActive ? 'Drop your PDF here' : 'Drag and drop your PDF here'}
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
            </Paper>

            <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
              <Select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                sx={{ minWidth: 200 }}
                size="small"
              >
                <MenuItem value="english">English</MenuItem>
                <MenuItem value="chinese">Chinese</MenuItem>
                <MenuItem value="spanish">Spanish</MenuItem>
              </Select>

              <Button
                variant="contained"
                onClick={handleSubmit}
                disabled={!file || loading}
                startIcon={loading ? <CircularProgress size={20} /> : <Translate />}
                sx={{ flex: 1 }}
              >
                {loading ? 'Converting...' : 'Convert to Blog Post'}
              </Button>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 4 }}>
                {error}
              </Alert>
            )}

            {result && (
              <Paper sx={{ p: 4 }}>
                <Typography variant="h2" gutterBottom>
                  Generated Blog Post
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Box sx={{ 
                  '& .markdown': { 
                    '& h1': { fontSize: '1.75rem', fontWeight: 600, mt: 4, mb: 2 },
                    '& h2': { fontSize: '1.5rem', fontWeight: 600, mt: 3, mb: 2 },
                    '& p': { mb: 2, lineHeight: 1.7 },
                    '& ul, & ol': { mb: 2, pl: 4 },
                    '& code': { backgroundColor: 'grey.100', px: 1, borderRadius: 1 },
                    '& pre': { backgroundColor: 'grey.100', p: 2, borderRadius: 2, overflow: 'auto' },
                    '& img': { maxWidth: '100%', height: 'auto', borderRadius: 2 },
                    '& blockquote': { 
                      borderLeft: 4,
                      borderColor: 'grey.200',
                      pl: 2,
                      ml: 0,
                      fontStyle: 'italic'
                    }
                  }
                }}>
                  <ReactMarkdown className="markdown">{result}</ReactMarkdown>
                </Box>
              </Paper>
            )}
          </Box>
        </Container>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

export default App;
