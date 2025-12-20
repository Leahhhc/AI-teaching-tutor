# AI Teaching Tutor

An intelligent, adaptive learning system designed to help students efficiently prepare for final exams through personalized quiz generation, real-time evaluation, and dynamic difficulty adjustment.

**Final Project for Columbia COMS4995_032 Applied Machine Learning**

## 🌟 Overview

This project implements an AI-powered adaptive learning tutor that combines modern language models with sophisticated evaluation algorithms to create a personalized learning experience. The system analyzes student performance in real-time and adapts quiz difficulty to optimize learning outcomes.

### Key Features

- **🤖 AI-Powered Quiz Generation**: Leverages Phi-3 language model to generate contextual questions from course materials
- **📊 Adaptive Difficulty System**: Dynamically adjusts question complexity based on student performance using EMA (Exponential Moving Average) algorithms
- **🎯 RAG-Based Grounding**: Retrieval-Augmented Generation ensures answers are grounded in actual course content
- **📈 Progress Tracking**: Real-time mastery level computation and performance analytics
- **💾 Vector Storage**: ChromaDB integration for efficient similarity search and content retrieval
- **🔄 Iterative Learning Loop**: Continuous feedback cycle between quiz generation, evaluation, and adaptation

## 🏗️ Architecture

The system is built with a modular architecture consisting of four main components:

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     System Integration                       │
│                  (Team A - Architecture)                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌───────▼────────┐   ┌───────▼────────┐
│ Content        │   │  Evaluation &  │   │   Frontend &   │
│ Processing     │   │  Adaptive      │   │ Visualization  │
│ (Team B)       │   │  Logic         │   │  (Team D)      │
│                │   │  (Team C)      │   │                │
│ • LLM Pipeline │   │ • Answer Eval  │   │ • UI/UX        │
│ • RAG System   │   │ • EMA Tracking │   │ • Data Display │
│ • Vector DB    │   │ • Difficulty   │   │ • Progress     │
└────────────────┘   └────────────────┘   └────────────────┘
```

### Technical Stack

- **Language Model**: Phi-3 (4-bit quantization for efficiency)
- **Vector Database**: ChromaDB for semantic search
- **LLM Provider**: Hugging Face (Meta-Llama models via router.huggingface.co)
- **Evaluation**: Custom EMA-based mastery tracking algorithms
- **Interface**: Command-line interface with planned web UI

## 📁 Project Structure

```
AI-teaching-tutor/
├── agents/            # Agent implementations for quiz generation
├── core/              # Core data types and essential system components
├── data/              # Course materials and training data
├── evaluation/        # Answer evaluation and scoring logic
├── memory/            # ChromaDB integration and vector storage
├── parsers/           # Data parsing and preprocessing utilities
├── prompts/           # LLM prompt templates
├── tests/             # Unit tests
├── main.py            # Command-line interface entry point
├── app.py             # Web application entry point
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variable template
└── INTERFACES.md      # Component interface specifications
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip package manager
- Hugging Face account and API token

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Leahhhc/AI-teaching-tutor.git
   cd AI-teaching-tutor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Hugging Face API token
   ```

4. **Set up your Hugging Face token**
   
   Get your token from [Hugging Face Settings](https://huggingface.co/settings/tokens) and add to `.env`:
   ```
   HF_TOKEN=your_token_here
   ```

## 💻 Usage

### Command-Line Interface

Run the interactive tutor:

```bash
python main.py
```

The system will guide you through:
1. Topic selection from available course materials
2. Initial difficulty calibration
3. Quiz generation and question presentation
4. Answer submission and evaluation
5. Adaptive difficulty adjustment based on performance
6. Progress tracking and mastery level updates

### Web Interface (Optional)

Launch the web application:

```bash
python app.py
```

Then navigate to `http://localhost:5000` in your browser.

## 🔬 Technical Details

### RAG (Retrieval-Augmented Generation)

The system uses RAG to ground quiz questions and answers in actual course materials:

1. Course content is embedded and stored in ChromaDB
2. For each question, relevant context is retrieved via similarity search
3. The LLM generates questions/evaluates answers using retrieved context
4. This ensures factual accuracy and alignment with course materials

### Adaptive Learning Algorithm

The system employs Exponential Moving Average (EMA) for mastery tracking:

```python
# Simplified EMA update
mastery_new = α × score_current + (1 - α) × mastery_old
```

Difficulty adjustment follows threshold-based policies:
- **High performance** (mastery > threshold_high) → Increase difficulty
- **Low performance** (mastery < threshold_low) → Decrease difficulty
- **Moderate performance** → Maintain current difficulty

### Evaluation System

The evaluation component uses an adapter pattern for schema isolation:

1. **Input Adapter**: Converts quiz output to evaluation-compatible format
2. **Evaluator**: Scores answers using LLM-based rubrics
3. **Output Adapter**: Transforms evaluation results to progress tracking format
4. **Progress Tracker**: Updates mastery levels using EMA algorithms

## 👥 Team

This project is a collaborative effort by four team members:

- **Team A** (System Architecture & Integration): System design, component integration, overall workflow orchestration
- **Team B** (Content Processing & LLM Pipeline): RAG implementation, vector storage, quiz generation
- **Team C** (Evaluation & Adaptive Logic): Answer evaluation, EMA algorithms, difficulty adaptation
- **Team D** (Frontend & Visualization): User interface, data visualization, user experience

## 📊 Evaluation & Results

The system demonstrates:
- Successful integration of independent codebases into unified workflow
- Complete learning cycle from quiz generation to adaptive difficulty adjustment
- Structured data flow between components using adapter patterns
- Real-time mastery tracking with EMA-based progress computation

## 🔮 Future Work

Potential enhancements include:

- **Multi-modal learning**: Support for images, diagrams, and video content
- **Collaborative learning**: Group study sessions and peer comparison
- **Advanced analytics**: Detailed performance insights and learning pattern analysis
- **Mobile application**: Native iOS/Android apps for on-the-go learning
- **Content expansion**: Support for multiple courses and subject areas
- **Spaced repetition**: Integration of scientifically-proven retention techniques

## 📝 Documentation

For detailed component interfaces and integration specifications, see [INTERFACES.md](INTERFACES.md).

## ⚠️ Important Notes

- **Security**: Never commit your `.env` file or expose API tokens
- **Model Usage**: Phi-3 with 4-bit quantization reduces memory footprint
- **Rate Limits**: Be mindful of Hugging Face API rate limits during testing
- **Data Privacy**: Course materials should not contain sensitive information

## 🙏 Acknowledgments

- Columbia University COMS4995_032 Applied Machine Learning course
- Anthropic's Claude for development assistance
- Hugging Face for model hosting and API infrastructure
- ChromaDB team for vector database tools

## 📄 License

This project is developed as academic coursework for Columbia University.

---

**Course**: COMS4995_032 Applied Machine Learning  
**Institution**: Columbia University  
**Year**: 2025.12