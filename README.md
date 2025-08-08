# 📊 Google Sheets Internship Journey Agent

A clean, professional Streamlit-based chat interface that intelligently updates your Google Sheets internship journey tracking table using natural language daily updates. Powered by Google's Gemini API through LiteLLM for intelligent task parsing and status inference.

## ✨ Key Features

- **🗣️ Natural Language Processing**: Enter daily updates in plain English
- **🧠 Smart Task Matching**: Automatically matches updates to existing tasks or creates new ones
- **📊 Status Inference**: Intelligently determines task status based on update context and tense
- **👀 Changes Preview**: Review all proposed changes with clean preview cards before applying
- **🎯 Workstream Intelligence**: Adds tasks to existing workstreams and reuses appropriate tags
- **⏱️ Effort Estimation**: Automatically calculates man-hours based on task complexity
- **🔧 Development Mode**: Works with local CSV data when Google Sheets isn't available
- **🖥️ Full-Screen UI**: Clean, professional interface that utilizes the entire browser width

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create your `.env` file:

```bash
# Required: Google API Key for Gemini (through LiteLLM)
GOOGLE_API_KEY="your_gemini_api_key_here"

# Fallback options (if Google API not available)
OPENAI_API_KEY="your_openai_key_here"
GROQ_API_KEY="your_groq_key_here"

# Optional: Google Sheets Integration
GOOGLE_SHEETS_ID="your_google_sheets_id_here"
GOOGLE_SERVICE_ACCOUNT_JSON="path/to/your/service-account.json"
```

### 3. Run the Application

```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## 🔧 API Setup

### Gemini API (Recommended)
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Add it to your `.env` file as `GOOGLE_API_KEY`

### Google Sheets Integration (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Google Sheets API** and **Google Drive API**
3. Create a Service Account and download JSON credentials
4. Share your Google Sheet with the service account email
5. Add credentials path and sheet ID to `.env`

## 💬 How to Use

### Basic Workflow

1. **Start the app** with `streamlit run app.py`
2. **Enter daily updates** in the chat input using natural language
3. **Review proposed changes** in clean, color-coded preview cards
4. **Apply or reject changes** based on your preference
5. **View updated data** in the sidebar dashboard

### Example Updates

```
✅ "Today I completed the user authentication module and started database integration"

✅ "Spent the morning debugging API endpoints and finished unit tests for auth system"

✅ "Working on BigQuery ML model for stock prediction, experimenting with different algorithms"

✅ "Attended team meeting and reviewed health checks, will define analytics questions next week"
```

### What the Agent Does

- **📝 Parses Tasks**: Extracts individual tasks and activities from your updates
- **🔍 Infers Status**: 
  - Past tense ("completed", "finished") → **"Complete"**
  - Present continuous ("working on", "currently") → **"In Progress"**
  - Future tense ("will", "planning to") → **"Upcoming"**
  - Conditional language → **"On Hold"**
- **🔗 Smart Matching**: Prioritizes updating existing rows over creating duplicates
- **⚖️ Effort Estimation**: Calculates man-days based on task complexity and time context
- **📅 Timeline Coherence**: Ensures tasks flow logically in chronological order

## 🏗️ Project Structure

```
📁 ResearchAgent/
├── 🎯 app.py                          # Main Streamlit application (clean UI)
├── 🧠 sheets_agent.py                 # Core agent with Gemini/LiteLLM integration
├── 📊 sheets_tools.py                 # Google Sheets API operations
├── 🧪 test_sheets_agent.py           # Comprehensive test suite
├── 📋 requirements.txt               # Python dependencies
├── 🔐 .env                          # Environment variables (API keys)
├── 📄 Copy of internshipjourney - Sheet1.csv  # Sample data for development
├── 📖 README.md                     # This documentation
└── 🔧 .gitignore                    # Git ignore rules
```

## 📊 Expected Sheet Format

Your Google Sheet should have these columns for optimal functionality:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| **Workstream** | Text | Project/category name | "DataE GPT", "Marketing Analytics" |
| **Task** | Text | Main task description | "Implement user authentication" |
| **Sub Task** | Text | Specific subtask details | "Set up JWT token validation" |
| **Start Date** | Date | MM/DD/YYYY format | "06/01/2025" |
| **End Date** | Date | MM/DD/YYYY format | "06/05/2025" |
| **Effort** | Number | Man-days (decimal) | 0.5, 1.0, 2.5 |
| **Status** | Text | Current status | "Complete", "In Progress", "Upcoming" |
| **Priority** | Text | Task priority level | "High", "Medium", "Low" |
| **Tags** | Text | Comma-separated tags | "Research, AI, Backend" |

## 🖥️ UI Features

### Clean & Professional Design
- **Full-screen layout** that utilizes entire browser width
- **Minimal styling** with subtle colors and clean typography
- **Responsive design** that works on different screen sizes

### Interactive Elements
- **Color-coded change cards** (green for create, blue for update)
- **Status badges** with appropriate colors for each status type
- **Processing steps** with clear visual progress indicators
- **Sidebar dashboard** with essential metrics and workstream overview

### Smart Feedback
- **Real-time processing** with step-by-step progress
- **Clear error messages** with actionable suggestions
- **Helpful examples** and usage tips built into the interface

## 🔧 Development Mode

When Google Sheets isn't configured, the app automatically runs in development mode:

- ✅ **Test agent functionality** using local CSV data
- ✅ **Preview changes** without affecting real sheets
- ✅ **Debug and develop** without API dependencies
- ✅ **Learn the interface** before setting up integrations

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_sheets_agent.py
```

**Tests include:**
- 📊 Sheet data loading and validation
- 🤖 Agent initialization with different API keys
- 📝 Update parsing with various input formats
- 👀 Change preview generation and formatting
- 🔄 Status inference accuracy

## 🚨 Troubleshooting

### API Issues

**❌ "Generative Language API not enabled" or model not found**
```bash
# Solution: Use the correct Gemini model
# Update your .env with a valid Google API key
# The agent uses gemini/gemini-2.5-pro through LiteLLM
```

**❌ "No API key found"**
```bash
# Solution: Check your .env file
# Ensure at least one of these is set:
GOOGLE_API_KEY="your_key"     # Primary option
OPENAI_API_KEY="your_key"     # Fallback option
GROQ_API_KEY="your_key"       # Alternative fallback
```

### Installation Issues

**❌ "No module named 'smolagents' or 'plotly'"**
```bash
pip install -r requirements.txt
# If still failing, try:
pip install smolagents[toolkit] plotly streamlit pandas
```

### Google Sheets Issues

**❌ "Google Sheets connection failed"**
- Check service account JSON file path in `.env`
- Verify `GOOGLE_SHEETS_ID` matches your sheet
- Ensure service account email has edit access to your sheet
- The app works fine without Sheets (development mode)

## 📈 Real-World Usage Examples

### Daily Standup Updates
```
Input: "Yesterday I completed the API documentation and started frontend integration. 
Today I'll focus on testing the authentication flow and fixing redirect issues."

Result: 
✅ Updates existing "API documentation" task to "Complete"
🆕 Creates new "Frontend integration testing" task as "In Progress"
🆕 Creates new "Fix authentication redirects" task as "Upcoming"
```

### Weekly Progress Reports
```
Input: "This week I finished the user management system, conducted performance testing, 
and began working on the reporting dashboard. Next week I plan to implement data visualization."

Result:
✅ Marks "User management system" as "Complete"
✅ Marks "Performance testing" as "Complete"  
🆕 Creates "Reporting dashboard" as "In Progress"
🆕 Creates "Data visualization implementation" as "Upcoming"
```

### Project Milestones
```
Input: "Successfully deployed the ML model to production with 85% accuracy. 
The stock prediction system is live. Moving on to real-time data feeds integration."

Result:
✅ Updates "ML model development" to "Complete"
🆕 Creates "Production deployment" as "Complete"
🆕 Creates "Real-time data feeds integration" as "In Progress"
```

## 🔄 Recent Updates

- ✨ **Clean UI overhaul** with full-screen layout and professional styling
- 🚀 **LiteLLM integration** for better API handling and model flexibility
- 🎯 **Gemini 2.5-pro support** for improved natural language understanding
- 📊 **Enhanced processing feedback** with clear step-by-step indicators
- 🎨 **Color-coded change preview** cards for better visual distinction
- 🔧 **Improved error handling** with actionable error messages

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes with clean, readable code
4. **Test** thoroughly with `python test_sheets_agent.py`
5. **Submit** a pull request with clear description

## 📄 License

This project is open source and available under the **MIT License**.

---

**🚀 Built with modern tools:** Streamlit • Google Gemini API • LiteLLM • Python

*Transform your daily updates into structured progress tracking with the power of AI.*