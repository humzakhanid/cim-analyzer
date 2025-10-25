# CIM Analyzer - Investment Analysis Platform

A full-stack investment analysis application that processes CIM (Confidential Information Memorandum) PDFs using AI to extract investment insights. Features user authentication, file upload/analysis, and a dashboard for managing past analyses.

##  Recent Improvements

###  Authentication System
- **Proper Clerk JWT Validation**: Replaced temporary authentication bypass with proper Clerk JWT verification
- **Backward Compatibility**: Maintains support for custom JWT tokens
- **Secure Token Handling**: Validates tokens against Clerk's JWKS endpoint

###  Persistent Ratings & Confidence
- **Database Storage**: User ratings and confidence scores now persist in the database
- **API Endpoints**: New PUT endpoints for updating ratings and confidence
- **Frontend Integration**: Real-time updates with proper error handling

###  Enhanced Database Schema
- **User Model**: Updated to support Clerk string IDs
- **Analysis Results**: Added `user_rating` and `confidence_score` fields
- **Migration Script**: Automated database migration for existing installations

##  Technical Stack

- **Backend**: FastAPI (Python) with SQLAlchemy ORM
- **Frontend**: React with Clerk authentication
- **Database**: SQLite with enhanced AnalysisResult model
- **AI**: OpenAI API for PDF analysis
- **Storage**: Amazon S3 for PDF files
- **Authentication**: Clerk (JWT-based) with backward compatibility

##  Key Features

### 1. Authentication System
- Clerk integration with proper JWT validation
- Backward compatibility with custom JWT tokens
- Secure user session management

### 2. File Upload & Analysis Pipeline
- PDF upload with drag-and-drop interface
- OpenAI GPT-4 analysis with structured JSON output
- S3 storage integration
- Real-time analysis progress

### 3. Dashboard & Management
- CIM analysis history with search and filtering
- Persistent user ratings (thumbs up/down)
- Confidence score tracking (0-100%)
- Delete functionality with confirmation

### 4. Analysis Results
- Structured JSON output with company info, financials, thesis, and red flags
- Confidence scoring for each analysis section
- Detailed view with navigation between analyses

##  Database Schema

```sql
-- Users table (supports both Clerk and custom auth)
users:
- id (String, Primary Key) - Supports Clerk string IDs
- email (String, nullable) - Made nullable for Clerk users
- hashed_password (String, nullable) - Made nullable for Clerk users
- full_name (String)

-- Analysis results with ratings and confidence
analysis_results:
- id (Integer, Primary Key)
- user_id (String, Foreign Key) - Links to users.id
- filename (String)
- preview_text (Text)
- summary_json (Text)
- timestamp (DateTime)
- user_rating (Float, nullable) - 1-5 rating scale
- confidence_score (Float, nullable) - 0-1 confidence scale
```

##  Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- AWS S3 bucket
- Clerk account
- OpenAI API key

### Backend Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_key
   AWS_ACCESS_KEY_ID=your_aws_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your_bucket_name
   CLERK_SECRET_KEY=your_clerk_secret
   SECRET_KEY=your_jwt_secret
   ```

3. **Database Migration**
   ```bash
   python migrate_database.py
   ```

4. **Start Backend**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to Frontend Directory**
   ```bash
   cd cim-analyzer-frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Environment Variables**
   Create a `.env` file:
   ```env
   REACT_APP_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
   ```

4. **Start Frontend**
   ```bash
   npm start
   ```

##  API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login

### File Management
- `POST /api/upload` - Upload and analyze PDF
- `GET /api/results` - Fetch user's analysis history
- `DELETE /api/results/{id}` - Delete specific analysis

### Ratings & Confidence
- `PUT /api/results/{id}/rating` - Update user rating (1-5 scale)
- `PUT /api/results/{id}/confidence` - Update confidence score (0-1 scale)

##  Authentication Flow

1. **Clerk Integration**: Frontend uses Clerk's `getToken()` to obtain JWT
2. **Token Validation**: Backend validates against Clerk's JWKS endpoint
3. **Fallback Support**: Custom JWT tokens still supported for backward compatibility
4. **User Creation**: Automatic user creation for new Clerk users

##  Analysis Output Format

The AI analysis returns structured JSON with:
- **Company Info**: Name, description, industry
- **Financials**: Revenue, EBITDA, margins, cash flow
- **Investment Thesis**: Key investment points
- **Red Flags**: Risks and concerns
- **Confidence Scoring**: Per-section confidence levels

##  Usage Workflow

1. **Authentication**: Users sign in via Clerk
2. **Upload**: Drag-and-drop PDF files for analysis
3. **Analysis**: AI processes and extracts investment insights
4. **Review**: View structured results with ratings and confidence
5. **Management**: Organize and delete analyses as needed

##  Development Notes

### Database Migrations
- Run `python migrate_database.py` to add new columns
- Existing data is preserved during migration
- New installations automatically include all fields

### Authentication Testing
- Clerk JWT validation is now properly implemented
- Custom JWT tokens still work for testing
- Error handling includes detailed logging

### Frontend State Management
- Ratings and confidence now persist to database
- Real-time updates with optimistic UI
- Proper error handling and user feedback

##  Known Limitations

- Email validation temporarily disabled (requires MailboxLayer API key)
- Some older database installations may need manual migration
- Confidence scores are stored as 0-1 but displayed as 0-100%

##  Future Enhancements

1. **Email Validation**: Re-enable with proper API key
2. **Advanced Filtering**: Search and filter by company, date, rating
3. **Export Functionality**: Export analyses to PDF/Excel
4. **Collaboration**: Share analyses with team members
5. **Advanced Analytics**: Trend analysis and insights dashboard

##  License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Built with ❤️ for investment professionals** 
