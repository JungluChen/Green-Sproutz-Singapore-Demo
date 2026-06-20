# Green Sproutz Singapore Demo

An interactive E-Learning platform built with Streamlit, featuring YouTube video integration with embedded quizzes and a community forum for collaborative learning.

## Features

### Interactive Video Learning
- **YouTube Integration**: Embed any YouTube video for interactive learning
- **Timestamp-based Quizzes**: Automatically pause videos at specific timestamps to display quiz questions
- **Real-time Scoring**: Track answers, accuracy, and progress in real-time
- **Persistent State**: Save learning progress and quiz results across sessions

### Community Forum
- **Threaded Discussions**: Create and participate in learning discussions
- **Category Organization**: Organize topics by categories (Accounting, Corporate Law, Public Finance, etc.)
- **User Profiles**: Set display names and track your contributions
- **Save Functionality**: Bookmark interesting threads for later reference
- **Search & Filter**: Find discussions by keyword, category, or author

### Settings & Configuration
- **Video Management**: Configure YouTube video URLs
- **Quiz Creation**: Create custom quiz questions with multiple choice options
- **Dynamic Content**: Add, edit, or remove quiz questions on-the-fly
- **Data Export**: Save and export quiz data for analysis

## Project Structure

```
Green-Sproutz-Singapore-Demo/
├── src/
│   ├── streamlit_app.py          # Main application entry point
│   └── pages/
│       ├── setting.py            # Video and quiz configuration
│       ├── test.py               # Interactive video quiz player
│       └── forum.py              # Community discussion forum
├── data/
│   └── forum.db                  # SQLite database for forum
├── .devcontainer/
│   └── devcontainer.json         # GitHub Codespaces configuration
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/JungluChen/Green-Sproutz-Singapore-Demo.git
   cd Green-Sproutz-Singapore-Demo
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run src/streamlit_app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501`

### GitHub Codespaces

1. Click the "Code" button and select "Open with Codespaces"
2. Wait for the environment to build
3. The application will automatically start and be available on port 8501

## Usage Guide

### Getting Started

1. **Configure Video**
   - Navigate to the Settings page
   - Paste a YouTube video URL
   - The video will be displayed for preview

2. **Create Quiz Questions**
   - In the Settings page, use the data editor to add quiz questions
   - Specify timestamps (e.g., "0:10", "1:30") for when questions should appear
   - Add question text and multiple choice options
   - Mark the correct answer

3. **Start Learning**
   - Navigate to the Test page
   - Watch the video - questions will automatically appear at specified timestamps
   - Select your answers and track your progress
   - Review your accuracy and performance

4. **Join the Community**
   - Visit the Forum page
   - Set your display name
   - Create discussion threads or participate in existing ones
   - Save interesting threads for later

### Quiz Format

Quiz questions follow this format:

| Time | Question | Option A | Option B | Option C | Correct Answer |
|------|----------|----------|----------|----------|----------------|
| 0:10 | What topic is being discussed? | AI Applications | Cloud Computing | Cybersecurity | AI Applications |
| 0:25 | What is the keyword? | Alpha | Beta | Gamma | Beta |

### Forum Categories

- **Accounting**: Financial accounting and reporting
- **Corporate Law**: Business legal matters
- **Public Finance**: Government financial management
- **Controlling**: Management accounting and control
- **Acquisition**: Business acquisitions and mergers
- **Education**: Learning and development
- **General**: Open discussions

## Technical Details

### Dependencies

- **streamlit**: Web application framework
- **streamlit-js-eval**: JavaScript evaluation in Streamlit
- **streamlit-autorefresh**: Auto-refresh functionality
- **rich**: Rich text formatting
- **pandas**: Data manipulation and analysis
- **sqlite3**: Database management (built-in)

### Architecture

The application uses a multi-page Streamlit architecture:

- **Main App** (`streamlit_app.py`): Entry point with navigation
- **Settings Page** (`setting.py`): Configuration interface
- **Test Page** (`test.py`): Interactive quiz player
- **Forum Page** (`forum.py`): Community features

### Data Storage

- **Session State**: User preferences and temporary data
- **SQLite Database**: Forum threads, posts, and user saves
- **Local Storage**: Browser-side storage for quiz progress

## Development

### Adding New Features

1. Create a new page in `src/pages/`
2. Add navigation in `src/streamlit_app.py`
3. Update requirements if needed

### Database Schema

The forum uses three main tables:

- **threads**: Discussion topics with title, body, category, and author
- **posts**: Responses to threads
- **saves**: User bookmarks for threads

### Testing

Run the application locally and test:
1. Video playback and quiz functionality
2. Forum creation and interaction
3. Data persistence across sessions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- YouTube integration using [YouTube IFrame API](https://developers.google.com/youtube/iframe_api_reference)
- Created by [Innovation XLab](https://github.com/JungluChen)

## Support

For support and questions:
- Open an issue on [GitHub](https://github.com/JungluChen/Green-Sproutz-Singapore-Demo/issues)
- Contact the development team

---

**Note**: This is a demo application showcasing interactive learning capabilities. For production use, consider adding authentication, data validation, and security measures.
