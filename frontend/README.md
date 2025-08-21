# AI Document Organizer - Frontend

A modern React-based frontend for the AI Document Organizer system, featuring drag-and-drop file uploads, advanced search capabilities, and real-time analytics.

## Features

- **📁 Document Upload**: Drag-and-drop interface supporting PDF, DOCX, TXT, Excel, PowerPoint, and image files
- **🔍 Advanced Search**: Keyword and semantic search with filters and search history
- **📊 Analytics Dashboard**: Real-time system performance metrics and accuracy statistics
- **🏷️ AI Classification**: Automatic document categorization with confidence scores
- **🌍 Multilingual Support**: English and Amharic language detection
- **💬 User Feedback**: Submit feedback to improve AI classification accuracy
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices

## Tech Stack

- **React 18** - Modern React with hooks and functional components
- **React Router** - Client-side routing
- **React Query** - Server state management and caching
- **Tailwind CSS** - Utility-first CSS framework
- **Heroicons** - Beautiful SVG icons
- **React Dropzone** - Drag-and-drop file uploads
- **React Hot Toast** - Toast notifications

## Prerequisites

- Node.js 16+ and npm
- Backend API running on `http://localhost:8000`

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm start
```

The frontend will be available at `http://localhost:3000`

### 3. Using PowerShell Script (Windows)

```powershell
.\start.ps1
```

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

## Project Structure

```
src/
├── components/          # Reusable UI components
│   └── Layout.js       # Main layout with navigation
├── pages/              # Page components
│   ├── Dashboard.js    # Main dashboard with stats
│   ├── Upload.js       # File upload interface
│   ├── Documents.js    # Document management
│   ├── Search.js       # Advanced search
│   ├── DocumentDetail.js # Document details and feedback
│   └── Analytics.js    # System analytics
├── utils/              # Utility functions
│   └── api.js         # API client configuration
├── App.js             # Main app component
└── index.js           # App entry point
```

## API Integration

The frontend integrates with the following backend endpoints:

### Document Management
- `GET /api/v1/documents` - List documents with pagination and filters
- `GET /api/v1/documents/{id}` - Get document details
- `PUT /api/v1/documents/{id}` - Update document
- `DELETE /api/v1/documents/{id}` - Delete document
- `GET /api/v1/documents/{id}/download` - Download document

### File Upload
- `POST /api/v1/upload` - Upload multiple files
- `POST /api/v1/upload/process` - Upload and process single file

### Search
- `POST /api/v1/search` - Search documents
- `GET /api/v1/search/recent` - Get recent documents

### Analytics & Feedback
- `GET /api/v1/analytics` - Get system analytics
- `POST /api/v1/feedback` - Submit user feedback
- `GET /api/v1/stats` - Get system statistics

## Key Features

### 1. Dashboard
- Overview of system statistics
- Recent documents
- Quick action buttons
- System health status

### 2. Upload Interface
- Drag-and-drop file upload
- Multiple file support
- Real-time upload status
- File validation and error handling

### 3. Document Management
- Grid view of all documents
- Advanced filtering (category, status, search)
- Pagination
- Bulk actions (delete, download)

### 4. Advanced Search
- Keyword and semantic search
- Category and tag filters
- Search history
- Recent documents suggestions

### 5. Document Details
- Complete document information
- Content preview
- Key phrases extraction
- User feedback submission

### 6. Analytics
- System accuracy metrics
- Category performance
- Learning potential
- Feedback analysis

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

### API Configuration

The API client is configured in `src/utils/api.js`:

```javascript
const BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api/v1' 
  : 'http://localhost:8000/api/v1';
```

## Styling

The project uses Tailwind CSS for styling. Key design patterns:

- **Color Scheme**: Blue primary, with semantic colors for different states
- **Layout**: Responsive grid system with sidebar navigation
- **Components**: Consistent card-based design with shadows and rounded corners
- **Typography**: Clear hierarchy with proper spacing

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

### Adding New Pages

1. Create a new component in `src/pages/`
2. Add the route to `src/App.js`
3. Update navigation in `src/components/Layout.js`

### Adding New API Endpoints

1. Add the endpoint function to `src/utils/api.js`
2. Use React Query for data fetching
3. Handle loading and error states

### Styling Guidelines

- Use Tailwind utility classes
- Follow the existing color scheme
- Maintain consistent spacing and typography
- Ensure responsive design

## Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure backend is running on port 8000
   - Check CORS configuration in backend

2. **File Upload Issues**
   - Verify file size limits
   - Check supported file types
   - Ensure proper MIME type detection

3. **Search Not Working**
   - Verify search endpoint is available
   - Check search parameters format

### Debug Mode

Enable debug logging by setting:

```javascript
localStorage.setItem('debug', 'true');
```

## Contributing

1. Follow the existing code style
2. Add proper error handling
3. Include loading states
4. Test on different screen sizes
5. Update documentation

## License

This project is part of the AI Document Organizer system.
