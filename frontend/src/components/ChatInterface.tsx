import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send, BarChart3, User, Bot, History, Settings, FileText, HelpCircle, Github, ExternalLink, Menu, X, AlertCircle, CheckCircle, Clock, Zap, Play, Pause, RotateCcw, Target, Brain, MessageSquare } from "lucide-react";
import { useDiagramScoring } from "@/hooks/use-diagram-scoring";
import { DiagramSubmissionRequest } from "@/services/api";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface ScoreMetrics {
  accuracy: number;
  precision: number;
  f1: number;
  recall: number;
}

interface AIGenerationLog {
  timestamp: string;
  step_name: string;
  prompt: string;
  response: string | null;
  processing_time: number;
  model: string;
  temperature?: number;
  error?: string;
}

interface LogsSummary {
  total_calls: number;
  total_time: number;
  errors: number;
  average_time: number;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  studentPlantUML?: string;
  teacherPlantUML?: string;
  description?: string;
  scores?: ScoreMetrics;
  review?: string;
  aiLogs?: AIGenerationLog[];
  logsSummary?: LogsSummary;
  timestamp: Date;
}

export const ChatInterface = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [studentPlantUML, setStudentPlantUML] = useState("");
  const [teacherPlantUML, setTeacherPlantUML] = useState("");
  const [description, setDescription] = useState("");

  // Sample data for quick testing
  const loadSampleData = () => {
    setStudentPlantUML(`@startuml
actor user as "User"
actor admin as "Administrator"

usecase login as "login"
usecase manage as "user management"

user --> login
admin --> login
admin --> manage
@enduml`);
    setTeacherPlantUML(`@startuml
actor User
actor Administrator

usecase Login
usecase "User Management"
usecase "View Reports"

User --> Login
Administrator --> Login
Administrator --> "User Management"
Administrator --> "View Reports"
@enduml`);
    setDescription("This is a use case diagram for a user management system. The system has two main actors: User and Administrator. The User can login to the system, while the Administrator can login and manage users. The diagram shows the relationships between actors and use cases.");
  };
  const [sidebarOpen, setSidebarOpen] = useState(true); // Keep sidebar open by default
  const [processingPhase, setProcessingPhase] = useState<number>(0);
  const [processingLogs, setProcessingLogs] = useState<string[]>([]);
  const [phaseStartTime, setPhaseStartTime] = useState<number>(0);

  // Use the real API hook
  const {
    scoringState,
    scoreDiagram,
    clearResult,
    pipelineStatus,
    supportedDiagrams,
    isConnected,
    isLoadingStatus
  } = useDiagramScoring();

  // Handle API response and add to messages
  useEffect(() => {
    if (scoringState.result && !scoringState.isLoading) {
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        scores: {
          accuracy: scoringState.result.metrics.overall_metrics.accuracy,
          precision: scoringState.result.metrics.overall_metrics.precision,
          f1: scoringState.result.metrics.overall_metrics.f1_score,
          recall: scoringState.result.metrics.overall_metrics.recall,
        },
        review: scoringState.result.feedback_summary,
        aiLogs: scoringState.result.ai_generation_logs,
        logsSummary: scoringState.result.logs_summary,
        timestamp: new Date(),
      };

      // Find the current user message and replace messages with user + assistant
      const currentUserMessage = messages.find(msg => msg.type === 'user');
      if (currentUserMessage) {
        setMessages([currentUserMessage, assistantMessage]);
      } else {
        setMessages([assistantMessage]);
      }
      clearResult(); // Clear the result to prevent duplicate messages
    }
  }, [scoringState.result, scoringState.isLoading, clearResult]);

  // Simulate processing phases with realistic timing
  const simulateProcessing = () => {
    setProcessingPhase(0);
    setProcessingLogs([]);
    setPhaseStartTime(Date.now());

    const phases = [
      {
        phase: 1,
        name: "Convention Normalization",
        duration: 20000, // 20 seconds
        logs: [
          "🔍 Analyzing teacher diagram conventions...",
          "📊 Detecting naming patterns and style guidelines...",
          "🔄 Comparing student vs teacher conventions...",
          "✏️  Generating normalized PlantUML code...",
          "✅ Validating normalized diagram syntax...",
          "🎯 Convention normalization completed!"
        ]
      },
      {
        phase: 2,
        name: "Code-based Extraction & Metrics",
        duration: 1000, // 1 second
        logs: [
          "⚡ Parsing PlantUML components...",
          "🧮 Calculating precision, recall, F1-score...",
          "📈 Computing accuracy metrics...",
          "✅ Metrics calculation completed!"
        ]
      },
      {
        phase: 3,
        name: "AI Feedback Generation",
        duration: 6000, // 6 seconds
        logs: [
          "🤖 Analyzing diagram errors and patterns...",
          "💡 Generating improvement suggestions...",
          "📝 Creating detailed feedback report...",
          "🎯 Calculating final score and grade...",
          "✅ AI feedback generation completed!"
        ]
      }
    ];

    let currentPhase = 0;
    let currentLogIndex = 0;

    const processPhase = () => {
      if (currentPhase >= phases.length) return;

      const phase = phases[currentPhase];
      setProcessingPhase(currentPhase + 1);

      const logInterval = phase.duration / phase.logs.length;

      const addLog = () => {
        if (currentLogIndex < phase.logs.length) {
          setProcessingLogs(prev => [...prev, phase.logs[currentLogIndex]]);
          currentLogIndex++;
          setTimeout(addLog, logInterval);
        } else {
          currentPhase++;
          currentLogIndex = 0;
          if (currentPhase < phases.length) {
            setTimeout(processPhase, 500);
          }
        }
      };

      addLog();
    };

    processPhase();
  };

  const generateScores = (): ScoreMetrics => {
    // Simulate AI scoring
    return {
      accuracy: Math.random() * 0.3 + 0.7, // 70-100%
      precision: Math.random() * 0.25 + 0.75, // 75-100%
      f1: Math.random() * 0.2 + 0.8, // 80-100%
      recall: Math.random() * 0.25 + 0.75, // 75-100%
    };
  };

  const generateReview = (): string => {
    const reviews = [
      "Your PlantUML diagram demonstrates a solid understanding of object-oriented design principles. The class structure is well-organized with clear separation of concerns. Consider implementing interface segregation for better modularity.",
      "Excellent use of composition over inheritance in your design. The relationships between classes are clearly defined. To improve further, consider adding error handling patterns and implementing the Observer pattern for better event management.",
      "Good architectural design with proper layering. The service classes are well-abstracted. For enhancement, consider implementing dependency injection and adding validation layers for improved robustness.",
    ];
    return reviews[Math.floor(Math.random() * reviews.length)];
  };

  const getScoreIcon = (score: number) => {
    return BarChart3;
  };

  const handleSubmit = async () => {
    if (!studentPlantUML.trim() || !teacherPlantUML.trim() || !description.trim()) return;

    // Clear previous messages for new session
    setMessages([]);

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      studentPlantUML: studentPlantUML.trim(),
      teacherPlantUML: teacherPlantUML.trim(),
      description: description.trim(),
      timestamp: new Date(),
    };

    setMessages([userMessage]);

    // Prepare API request
    const request: DiagramSubmissionRequest = {
      student_plantuml: studentPlantUML.trim(),
      teacher_plantuml: teacherPlantUML.trim(),
      problem_description: description.trim(),
    };

    try {
      // Start processing simulation
      simulateProcessing();

      // Call real API
      await scoreDiagram(request);
    } catch (error) {
      console.error('Failed to score diagram:', error);
      // Reset processing state on error
      setProcessingPhase(0);
      setProcessingLogs([]);
    }

    setStudentPlantUML("");
    setTeacherPlantUML("");
    setDescription("");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex min-h-screen">
        {/* Left Sidebar */}
        <div className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-white border-r border-gray-200 transition-all duration-300 flex flex-col h-screen sticky top-0`}>
          {/* Sidebar Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-white border-2 border-red-200 shadow-lg">
                <img
                  src="/assets/logo.png"
                  alt="PTIT Logo"
                  className="w-6 h-6 object-contain"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                    target.nextElementSibling?.classList.remove('hidden');
                  }}
                />
                <BarChart3 className="h-5 w-5 text-red-500 hidden" />
              </div>
              {sidebarOpen && (
                <div>
                  <h2 className="font-bold text-gray-900">AnD Auto Scoring</h2>
                  <p className="text-xs text-gray-500">PTIT Research</p>
                </div>
              )}
            </div>
          </div>

          {/* Navigation */}
          <div className="flex-1 p-4">
            <nav className="space-y-2">
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left text-red-600 bg-red-50 rounded-lg font-medium">
                <BarChart3 className="h-5 w-5" />
                {sidebarOpen && <span>Code Analysis</span>}
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left text-gray-600 hover:bg-gray-50 rounded-lg">
                <History className="h-5 w-5" />
                {sidebarOpen && <span>History</span>}
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left text-gray-600 hover:bg-gray-50 rounded-lg">
                <FileText className="h-5 w-5" />
                {sidebarOpen && <span>Templates</span>}
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 text-left text-gray-600 hover:bg-gray-50 rounded-lg">
                <Settings className="h-5 w-5" />
                {sidebarOpen && <span>Settings</span>}
              </button>
            </nav>
          </div>

          {/* Sidebar Footer */}
          <div className="p-4 border-t border-gray-200">
            <button className="w-full flex items-center gap-3 px-3 py-2 text-left text-gray-600 hover:bg-gray-50 rounded-lg">
              <HelpCircle className="h-5 w-5" />
              {sidebarOpen && <span>Help & Support</span>}
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-h-screen">
          {/* Top Header */}
          <div className="border-b border-gray-200 bg-white">
            <div className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSidebarOpen(!sidebarOpen)}
                    className="text-gray-600 hover:text-gray-900"
                  >
                    {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                  </Button>
                  <div>
                    <h1 className="text-xl font-bold text-gray-900">
                      PlantUML Code Analyzer
                    </h1>
                    <p className="text-sm text-gray-600">
                      Submit your code for AI-powered analysis and scoring
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {/* Connection Status */}
                  <div className="flex items-center gap-2 px-3 py-1 rounded-full text-sm">
                    {isConnected ? (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <span className="text-green-700">AI Connected</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="h-4 w-4 text-red-500" />
                        <span className="text-red-700">AI Disconnected</span>
                      </>
                    )}
                  </div>
                  <Button variant="outline" size="sm" className="text-gray-600 border-gray-300">
                    <Github className="h-4 w-4 mr-2" />
                    View on GitHub
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Messages Container */}
          <div className="flex-1 bg-gray-50">
            <div className="max-w-4xl mx-auto px-6 py-6">
              {messages.length === 0 ? (
                <div className="text-center py-20">
                  <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-red-50 mb-8 border border-red-100">
                    <BarChart3 className="h-10 w-10 text-red-500" />
                  </div>
                  <h2 className="text-2xl font-semibold mb-4 text-gray-900">Ready to analyze your code</h2>
                  <p className="text-gray-600 max-w-lg mx-auto leading-relaxed">

                  </p>
                  <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
                    <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-sm">
                      <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center mb-3 mx-auto">
                        <BarChart3 className="h-4 w-4 text-red-600" />
                      </div>
                      <h3 className="font-medium text-gray-900 mb-2">Accurate Scoring</h3>
                      <p className="text-sm text-gray-600">Get precise metrics for accuracy, precision, F1, and recall</p>
                    </div>
                    <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-sm">
                      <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center mb-3 mx-auto">
                        <FileText className="h-4 w-4 text-red-600" />
                      </div>
                      <h3 className="font-medium text-gray-900 mb-2">Expert Review</h3>
                      <p className="text-sm text-gray-600">Receive detailed feedback and improvement suggestions</p>
                    </div>
                    <div className="p-4 bg-white rounded-xl border border-gray-200 shadow-sm">
                      <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center mb-3 mx-auto">
                        <ExternalLink className="h-4 w-4 text-red-600" />
                      </div>
                      <h3 className="font-medium text-gray-900 mb-2">Best Practices</h3>
                      <p className="text-sm text-gray-600">Learn industry standards and coding conventions</p>
                    </div>
                  </div>

                  {/* Scroll down arrow */}
                  <div className="mt-12 text-center">
                    <p className="text-sm text-gray-500 mb-2">Scroll down to submit your code</p>
                    <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-red-100 animate-bounce">
                      <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                      </svg>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="py-8">
                  {messages.map((message, index) => (
                    <div key={message.id} className="animate-fade-in mb-8">
                      {message.type === 'user' && (
                        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                          <div className="flex items-start gap-4">
                            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                              <User className="w-4 h-4 text-gray-600" />
                            </div>
                            <div className="flex-1 space-y-4">
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                  <h3 className="font-medium text-blue-700 mb-2 flex items-center">
                                    <span className="mr-2">🔵</span>
                                    Student PlantUML Code
                                  </h3>
                                  <pre
                                    className="bg-blue-50 p-4 rounded-lg text-sm border border-blue-200 overflow-x-auto"
                                    style={{ fontFamily: '"JetBrains Mono", "SF Mono", Consolas, monospace', fontSize: '14px', lineHeight: '1.5' }}
                                  >
                                    {message.studentPlantUML}
                                  </pre>
                                </div>
                                <div>
                                  <h3 className="font-medium text-green-700 mb-2 flex items-center">
                                    <span className="mr-2">🟢</span>
                                    Reference PlantUML Code
                                  </h3>
                                  <pre
                                    className="bg-green-50 p-4 rounded-lg text-sm border border-green-200 overflow-x-auto"
                                    style={{ fontFamily: '"JetBrains Mono", "SF Mono", Consolas, monospace', fontSize: '14px', lineHeight: '1.5' }}
                                  >
                                    {message.teacherPlantUML}
                                  </pre>
                                </div>
                              </div>
                              <div>
                                <h3 className="font-medium text-purple-700 mb-2 flex items-center">
                                  <span className="mr-2">🟣</span>
                                  Technical Description
                                </h3>
                                <p className="text-gray-700 bg-purple-50 p-4 rounded-lg border border-purple-200">
                                  {message.description}
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {message.type === 'assistant' && (
                        <div className="bg-red-50 rounded-xl p-6 shadow-sm border border-red-100">
                          <div className="flex items-start gap-4">
                            <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                              <Bot className="w-4 h-4 text-red-600" />
                            </div>
                            <div className="flex-1 space-y-6">
                              <div>
                                <h3 className="font-bold text-lg text-gray-900 mb-4">AI Analysis Results</h3>

                                {/* Scores */}
                                <div className="mb-6">
                                  <h4 className="font-semibold mb-4 text-gray-900">Performance Metrics</h4>
                                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                                    {message.scores && Object.entries(message.scores).map(([key, value]) => (
                                      <div key={key} className="bg-white p-4 rounded-lg border border-gray-200">
                                        <div className="flex items-center gap-2 mb-2">
                                          <BarChart3 className="h-4 w-4 text-red-500" />
                                          <h5 className="font-medium text-gray-900 capitalize">{key}</h5>
                                        </div>
                                        <p className="text-2xl font-bold text-red-600">
                                          {(value * 100).toFixed(1)}%
                                        </p>
                                      </div>
                                    ))}
                                  </div>
                                </div>

                                {/* Review */}
                                <div className="bg-white p-5 rounded-lg border border-gray-200">
                                  <div className="flex items-center gap-2 mb-3">
                                    <FileText className="h-4 w-4 text-red-500" />
                                    <h4 className="font-semibold text-gray-900">Expert Review & Suggestions</h4>
                                  </div>
                                  <div className="text-gray-700 leading-relaxed">
                                    {message.review && message.review.split('\n').map((line, index) => {
                                      // Check if line is a suggestion/error point
                                      if (line.trim().startsWith('•') || line.trim().startsWith('-') || line.trim().startsWith('*')) {
                                        return (
                                          <div key={index} className="flex items-start gap-2 mb-2 p-2 bg-red-50 rounded border-l-4 border-red-300">
                                            <span className="text-red-500 font-bold">⚠️</span>
                                            <span className="text-red-700">{line.trim().substring(1).trim()}</span>
                                          </div>
                                        );
                                      }
                                      // Check if line contains improvement suggestions
                                      else if (line.toLowerCase().includes('suggest') || line.toLowerCase().includes('improve') || line.toLowerCase().includes('should')) {
                                        return (
                                          <div key={index} className="flex items-start gap-2 mb-2 p-2 bg-blue-50 rounded border-l-4 border-blue-300">
                                            <span className="text-blue-500 font-bold">💡</span>
                                            <span className="text-blue-700">{line.trim()}</span>
                                          </div>
                                        );
                                      }
                                      // Regular text
                                      else if (line.trim()) {
                                        return (
                                          <p key={index} className="mb-2">{line}</p>
                                        );
                                      }
                                      return null;
                                    })}
                                  </div>
                                </div>

                                {/* AI Generation Logs for Evidence */}
                                {message.aiLogs && message.aiLogs.length > 0 && (
                                  <div className="bg-white p-5 rounded-lg border border-gray-200 mt-4">
                                    <div className="flex items-center justify-between mb-3">
                                      <div className="flex items-center gap-2">
                                        <span className="text-blue-500">🤖</span>
                                        <h4 className="font-semibold text-gray-900">AI Generation Evidence & Logs</h4>
                                        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                                          {message.logsSummary?.total_calls} AI calls in {message.logsSummary?.total_time.toFixed(2)}s
                                        </span>
                                      </div>
                                      <button
                                        onClick={() => {
                                          const evidenceData = {
                                            timestamp: new Date().toISOString(),
                                            student_submission: {
                                              student_plantuml: message.studentPlantUML,
                                              teacher_plantuml: message.teacherPlantUML,
                                              description: message.description
                                            },
                                            scoring_results: {
                                              final_score: message.scores?.overall,
                                              grade_letter: message.scores?.grade,
                                              metrics: message.scores
                                            },
                                            ai_evidence: {
                                              logs_summary: message.logsSummary,
                                              detailed_logs: message.aiLogs,
                                              review: message.review
                                            }
                                          };

                                          const blob = new Blob([JSON.stringify(evidenceData, null, 2)], {
                                            type: 'application/json'
                                          });
                                          const url = URL.createObjectURL(blob);
                                          const a = document.createElement('a');
                                          a.href = url;
                                          a.download = `ai-scoring-evidence-${Date.now()}.json`;
                                          document.body.appendChild(a);
                                          a.click();
                                          document.body.removeChild(a);
                                          URL.revokeObjectURL(url);
                                        }}
                                        className="inline-flex items-center gap-1 px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                                      >
                                        📄 Export Evidence
                                      </button>
                                    </div>

                                    <div className="space-y-3 max-h-96 overflow-y-auto">
                                      {message.aiLogs.map((log, index) => (
                                        <div key={index} className="border border-gray-200 rounded-lg p-3 bg-gradient-to-r from-gray-50 to-blue-50">
                                          <div className="flex items-center justify-between mb-2">
                                            <div className="flex items-center gap-2">
                                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                {log.step_name}
                                              </span>
                                              <span className="text-xs text-gray-500">{log.timestamp}</span>
                                            </div>
                                            <div className="flex items-center gap-3 text-xs">
                                              <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded">
                                                ⏱️ {log.processing_time.toFixed(2)}s
                                              </span>
                                              <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-100 text-purple-700 rounded">
                                                🧠 {log.model}
                                              </span>
                                              {log.temperature && (
                                                <span className="inline-flex items-center gap-1 px-2 py-1 bg-orange-100 text-orange-700 rounded">
                                                  🌡️ {log.temperature}
                                                </span>
                                              )}
                                            </div>
                                          </div>

                                          {log.error ? (
                                            <div className="bg-red-50 border-l-4 border-red-400 p-3 rounded">
                                              <div className="flex items-center">
                                                <span className="text-red-500 mr-2">❌</span>
                                                <span className="text-red-700 font-medium">Error occurred during AI processing</span>
                                              </div>
                                              <p className="text-red-600 text-sm mt-1">{log.error}</p>
                                            </div>
                                          ) : (
                                            <div className="space-y-3">
                                              <details className="group border border-blue-200 rounded-lg">
                                                <summary className="cursor-pointer p-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors">
                                                  <div className="flex items-center justify-between">
                                                    <span className="text-sm font-medium text-blue-800 flex items-center gap-2">
                                                      📝 AI Prompt
                                                    </span>
                                                    <span className="text-xs text-blue-600 bg-blue-200 px-2 py-1 rounded">
                                                      {log.prompt.length.toLocaleString()} characters
                                                    </span>
                                                  </div>
                                                </summary>
                                                <div className="p-3 bg-white border-t border-blue-200">
                                                  <div className="bg-blue-50 border border-blue-200 rounded p-3 text-xs font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
                                                    {log.prompt}
                                                  </div>
                                                </div>
                                              </details>

                                              <details className="group border border-green-200 rounded-lg">
                                                <summary className="cursor-pointer p-3 bg-green-50 hover:bg-green-100 rounded-lg transition-colors">
                                                  <div className="flex items-center justify-between">
                                                    <span className="text-sm font-medium text-green-800 flex items-center gap-2">
                                                      🤖 AI Response
                                                    </span>
                                                    <span className="text-xs text-green-600 bg-green-200 px-2 py-1 rounded">
                                                      {(log.response?.length || 0).toLocaleString()} characters
                                                    </span>
                                                  </div>
                                                </summary>
                                                <div className="p-3 bg-white border-t border-green-200">
                                                  <div className="bg-green-50 border border-green-200 rounded p-3 text-xs font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
                                                    {log.response}
                                                  </div>
                                                </div>
                                              </details>
                                            </div>
                                          )}
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}

                  {scoringState.isLoading && (
                    <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-xl p-6 shadow-lg border border-red-200">
                      {/* Phase Progress Header */}
                      <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                            <Brain className="w-5 h-5 text-red-600 animate-pulse" />
                          </div>
                          <div>
                            <h3 className="font-bold text-lg text-gray-900">3-Phase AI Analysis Pipeline</h3>
                            <p className="text-sm text-gray-600">Processing your diagram with advanced AI...</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-red-600">
                            {Math.floor((Date.now() - phaseStartTime) / 1000)}s
                          </div>
                          <div className="text-xs text-gray-500">Elapsed</div>
                        </div>
                      </div>

                      {/* Phase Progress Indicators */}
                      <div className="grid grid-cols-3 gap-4 mb-6">
                        {[
                          { name: "Convention Normalization", icon: RotateCcw, color: "red", duration: "~20s" },
                          { name: "Metrics Calculation", icon: Target, color: "blue", duration: "~1s" },
                          { name: "Feedback Generation", icon: MessageSquare, color: "green", duration: "~6s" }
                        ].map((phase, index) => {
                          const isActive = processingPhase === index + 1;
                          const isCompleted = processingPhase > index + 1;
                          const Icon = phase.icon;

                          return (
                            <div key={index} className={`p-4 rounded-lg border-2 transition-all duration-300 ${isActive
                              ? `border-${phase.color}-300 bg-${phase.color}-50 shadow-md`
                              : isCompleted
                                ? `border-green-300 bg-green-50`
                                : 'border-gray-200 bg-gray-50'
                              }`}>
                              <div className="flex items-center gap-2 mb-2">
                                <Icon className={`w-4 h-4 ${isActive
                                  ? `text-${phase.color}-600 animate-spin`
                                  : isCompleted
                                    ? 'text-green-600'
                                    : 'text-gray-400'
                                  }`} />
                                <span className={`text-sm font-medium ${isActive || isCompleted ? 'text-gray-900' : 'text-gray-500'
                                  }`}>
                                  Phase {index + 1}
                                </span>
                              </div>
                              <div className={`text-xs ${isActive || isCompleted ? 'text-gray-700' : 'text-gray-500'
                                }`}>
                                {phase.name}
                              </div>
                              <div className={`text-xs mt-1 ${isActive ? `text-${phase.color}-600 font-medium` : 'text-gray-400'
                                }`}>
                                {phase.duration}
                              </div>
                            </div>
                          );
                        })}
                      </div>

                      {/* Real-time Processing Logs */}
                      <div className="bg-gray-900 rounded-lg p-4 max-h-48 overflow-y-auto">
                        <div className="flex items-center gap-2 mb-3">
                          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                          <span className="text-green-400 text-sm font-mono">Processing Logs</span>
                        </div>
                        <div className="space-y-1">
                          {processingLogs.map((log, index) => (
                            <div key={index} className="text-gray-300 text-sm font-mono animate-fade-in">
                              <span className="text-gray-500">[{new Date().toLocaleTimeString()}]</span> {log}
                            </div>
                          ))}
                          {processingLogs.length > 0 && (
                            <div className="text-green-400 text-sm font-mono animate-pulse">
                              <span className="text-gray-500">[{new Date().toLocaleTimeString()}]</span> ▋
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="mt-4">
                        <div className="flex justify-between text-sm text-gray-600 mb-2">
                          <span>Overall Progress</span>
                          <span>{Math.round((processingPhase / 3) * 100)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-red-500 to-orange-500 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${(processingPhase / 3) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  )}

                  {scoringState.error && (
                    <Alert className="border-red-200 bg-red-50">
                      <AlertCircle className="h-4 w-4 text-red-600" />
                      <AlertDescription className="text-red-700">
                        <strong>Analysis Failed:</strong> {scoringState.error}
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Enhanced Input Form */}
          <div className="border-t-2 border-red-200 bg-white shadow-lg">
            <div className="max-w-4xl mx-auto p-8">
              <div className="mb-8 text-center">
                <h3 className="text-2xl font-bold text-gray-900 mb-3">Submit Your Code for Analysis</h3>
                <p className="text-base text-gray-600">Provide your PlantUML diagram and technical context for comprehensive AI evaluation</p>
                <div className="mt-4 flex gap-2 justify-center">
                  <Button
                    onClick={loadSampleData}
                    variant="outline"
                    size="sm"
                    className="text-red-600 border-red-300 hover:bg-red-50"
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    Load Sample Data
                  </Button>
                  {messages.length > 0 && (
                    <Button
                      onClick={() => {
                        setMessages([]);
                        setStudentPlantUML('');
                        setTeacherPlantUML('');
                        setDescription('');
                      }}
                      variant="outline"
                      size="sm"
                      className="text-gray-600 border-gray-300 hover:bg-gray-50"
                    >
                      <span className="mr-2">🗑️</span>
                      Clear All
                    </Button>
                  )}
                </div>
              </div>

              <div className="grid lg:grid-cols-3 gap-6 mb-8">
                <div className="space-y-3">
                  <label htmlFor="student-plantuml" className="block text-base font-bold text-gray-800 mb-3 flex items-center gap-2">
                    <User className="h-5 w-5 text-blue-500" />
                    Student PlantUML Code
                  </label>
                  <Textarea
                    id="student-plantuml"
                    placeholder="@startuml&#10;actor user as &quot;User&quot;&#10;usecase login as &quot;login&quot;&#10;user --> login&#10;@enduml"
                    value={studentPlantUML}
                    onChange={(e) => setStudentPlantUML(e.target.value)}
                    className="h-40 w-full resize-none border-2 border-gray-300 rounded-xl px-4 py-4 bg-gray-50 focus:bg-white focus:ring-3 focus:ring-blue-300 focus:border-blue-500 transition-all duration-200 shadow-md hover:shadow-lg"
                    style={{ fontFamily: '"JetBrains Mono", "SF Mono", Consolas, monospace', fontSize: '14px', lineHeight: '1.5' }}
                  />
                  <p className="text-xs text-gray-500 mt-2">Enter the student's PlantUML diagram code</p>
                </div>
                <div className="space-y-3">
                  <label htmlFor="teacher-plantuml" className="block text-base font-bold text-gray-800 mb-3 flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-green-500" />
                    Reference PlantUML Code
                  </label>
                  <Textarea
                    id="teacher-plantuml"
                    placeholder="@startuml&#10;actor User&#10;usecase Login&#10;User --> Login&#10;@enduml"
                    value={teacherPlantUML}
                    onChange={(e) => setTeacherPlantUML(e.target.value)}
                    className="h-40 w-full resize-none border-2 border-gray-300 rounded-xl px-4 py-4 bg-gray-50 focus:bg-white focus:ring-3 focus:ring-green-300 focus:border-green-500 transition-all duration-200 shadow-md hover:shadow-lg"
                    style={{ fontFamily: '"JetBrains Mono", "SF Mono", Consolas, monospace', fontSize: '14px', lineHeight: '1.5' }}
                  />
                  <p className="text-xs text-gray-500 mt-2">Enter the reference/correct PlantUML diagram code</p>
                </div>
                <div className="space-y-3">
                  <label htmlFor="description" className="block text-base font-bold text-gray-800 mb-3 flex items-center gap-2">
                    <FileText className="h-5 w-5 text-red-500" />
                    Technical Description
                  </label>
                  <Textarea
                    id="description"
                    placeholder="Describe your software architecture design decisions, implementation approach, design patterns used, and any specific technical challenges..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="h-40 w-full resize-none border-2 border-gray-300 rounded-xl px-4 py-4 bg-gray-50 focus:bg-white focus:ring-3 focus:ring-purple-300 focus:border-purple-500 transition-all duration-200 shadow-md hover:shadow-lg"
                  />
                  <p className="text-xs text-gray-500 mt-2">Provide context about your design and implementation</p>
                </div>
              </div>

              <div className="flex justify-center pt-4">
                <Button
                  onClick={handleSubmit}
                  disabled={!studentPlantUML.trim() || !teacherPlantUML.trim() || !description.trim() || scoringState.isLoading || !isConnected}
                  className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white px-12 py-5 rounded-xl font-bold text-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3 shadow-xl hover:shadow-2xl transition-all duration-200 min-w-[250px] transform hover:scale-105"
                >
                  {scoringState.isLoading ? (
                    <>
                      <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Analyzing your code...</span>
                    </>
                  ) : !isConnected ? (
                    <>
                      <AlertCircle className="w-6 h-6" />
                      <span>AI Disconnected</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-6 h-6" />
                      <span>Submit for AI Review</span>
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Professional Footer - Now at bottom of page */}
      <div className="border-t border-gray-200 bg-gray-50 w-full">
        <div className="max-w-4xl mx-auto px-6 py-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-white border border-red-200 shadow-sm">
                  <img
                    src="/assets/logo.png"
                    alt="PTIT Logo"
                    className="w-5 h-5 object-contain"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      target.nextElementSibling?.classList.remove('hidden');
                    }}
                  />
                  <BarChart3 className="h-4 w-4 text-red-500 hidden" />
                </div>
                <h3 className="font-bold text-gray-900">AnD Auto Scoring</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                Advanced AI-powered PlantUML analysis and code review system developed by PTIT Research team for comprehensive software evaluation.
              </p>
              <div className="flex gap-4">
                <Button variant="ghost" size="sm" className="text-gray-600 hover:text-red-600">
                  <Github className="h-4 w-4 mr-2" />
                  GitHub
                </Button>
                <Button variant="ghost" size="sm" className="text-gray-600 hover:text-red-600">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Documentation
                </Button>
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Features</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>AI Code Analysis</li>
                <li>Performance Metrics</li>
                <li>Expert Reviews</li>
                <li>Best Practices</li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-gray-900 mb-4">Support</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>Documentation</li>
                <li>API Reference</li>
                <li>Community</li>
                <li>Contact Us</li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-200 mt-8 pt-6 flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-gray-500">
              © 2024 PTIT Research. All rights reserved.
            </p>
            <div className="flex gap-6 mt-4 md:mt-0">
              <a href="#" className="text-sm text-gray-500 hover:text-red-600 transition-colors">Privacy Policy</a>
              <a href="#" className="text-sm text-gray-500 hover:text-red-600 transition-colors">Terms of Service</a>
              <a href="#" className="text-sm text-gray-500 hover:text-red-600 transition-colors">Contact</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};