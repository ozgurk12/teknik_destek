import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { Warning } from '@mui/icons-material';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '60vh',
            p: 3,
          }}
        >
          <Paper
            sx={{
              p: 4,
              maxWidth: 500,
              textAlign: 'center',
            }}
          >
            <Warning sx={{ fontSize: 60, color: 'warning.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Bir şeyler yanlış gitti
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Sayfa yüklenirken bir hata oluştu. Lütfen sayfayı yenileyerek tekrar deneyin.
            </Typography>
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <Typography
                variant="caption"
                component="pre"
                sx={{
                  textAlign: 'left',
                  bgcolor: 'grey.100',
                  p: 1,
                  mb: 2,
                  borderRadius: 1,
                  overflow: 'auto',
                }}
              >
                {this.state.error.message}
              </Typography>
            )}
            <Button variant="contained" onClick={this.handleReset}>
              Sayfayı Yenile
            </Button>
          </Paper>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;