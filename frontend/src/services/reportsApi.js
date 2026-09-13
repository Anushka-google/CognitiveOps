const API_URL = import.meta.env.VITE_API_URL;

export async function getAnalyticsDashboard() {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_URL}/api/reports/analytics/dashboard`, {
    headers: { "Authorization": token ? `Bearer ${token}` : "" }
  });
  if (!response.ok) throw new Error("Failed to fetch analytics dashboard data");
  return await response.json();
}

export async function downloadCsvExport(reportType) {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_URL}/api/reports/export/${reportType}`, {
    headers: { "Authorization": token ? `Bearer ${token}` : "" }
  });
  
  if (!response.ok) throw new Error(`Failed to export ${reportType}`);
  
  // Convert response to Blob and trigger download
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  // Get filename from Content-Disposition header if possible, else fallback
  const contentDisposition = response.headers.get('Content-Disposition');
  let filename = `${reportType}_export.csv`;
  if (contentDisposition && contentDisposition.includes('filename=')) {
    filename = contentDisposition.split('filename=')[1].replace(/["']/g, '');
  }
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}
