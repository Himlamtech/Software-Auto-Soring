import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send, BarChart3, User, Bot, History, Settings, FileText, HelpCircle, Github, ExternalLink, Menu, X } from "lucide-react";

interface ScoreMetrics {
  accuracy: number;
  precision: number;
  f1: number;
  recall: number;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  plantUML?: string;
  description?: string;
  scores?: ScoreMetrics;
  review?: string;
  timestamp: Date;
}

export const ChatInterface = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [plantUML, setPlantUML] = useState("");
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true); // Keep sidebar open by default

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
    if (!plantUML.trim() || !description.trim()) return;

    setIsLoading(true);

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      plantUML: plantUML.trim(),
      description: description.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);

    // Simulate AI processing
    setTimeout(() => {
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        scores: generateScores(),
        review: generateReview(),
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 3000);

    setPlantUML("");
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
                    Submit your PlantUML diagram and technical description to receive comprehensive AI-powered scoring and detailed review feedback.
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
                              <div>
                                <h3 className="font-medium text-gray-900 mb-2">PlantUML Code</h3>
                                <pre 
                                  className="bg-gray-100 p-4 rounded-lg text-sm border overflow-x-auto"
                                  style={{ fontFamily: '"JetBrains Mono", "SF Mono", Consolas, monospace', fontSize: '14px', lineHeight: '1.5' }}
                                >
                                  {message.plantUML}
                                </pre>
                              </div>
                              <div>
                                <h3 className="font-medium text-gray-900 mb-2">Description</h3>
                                <p className="text-gray-700 bg-white p-4 rounded-lg border">
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
                                    <h4 className="font-semibold text-gray-900">Expert Review</h4>
                                  </div>
                                  <p className="text-gray-700 leading-relaxed">
                                    {message.review}
                                  </p>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}

                  {isLoading && (
                    <div className="bg-red-50 rounded-xl p-6 shadow-sm border border-red-100">
                      <div className="flex items-center gap-4">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse"></div>
                          <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                          <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
                        </div>
                        <span className="text-gray-700">AI is analyzing your code...</span>
                      </div>
                    </div>
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
              </div>
              
              <div className="grid lg:grid-cols-2 gap-8 mb-8">
                <div className="space-y-3">
                  <label htmlFor="plantuml" className="block text-base font-bold text-gray-800 mb-3 flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-red-500" />
                    PlantUML Code
                  </label>
                  <Textarea
                    id="plantuml"
                    placeholder="@startuml&#10;class UserService {&#10;  +authenticate(credentials)&#10;}&#10;class DatabaseAdapter {&#10;  +connect()&#10;}&#10;UserService --> DatabaseAdapter&#10;@enduml"
                    value={plantUML}
                    onChange={(e) => setPlantUML(e.target.value)}
                    className="h-40 w-full resize-none border-2 border-gray-300 rounded-xl px-4 py-4 bg-gray-50 focus:bg-white focus:ring-3 focus:ring-red-300 focus:border-red-500 transition-all duration-200 shadow-md hover:shadow-lg"
                    style={{ fontFamily: '"JetBrains Mono", "SF Mono", Consolas, monospace', fontSize: '14px', lineHeight: '1.5' }}
                  />
                  <p className="text-xs text-gray-500 mt-2">Enter your PlantUML diagram code here</p>
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
                    className="h-40 w-full resize-none border-2 border-gray-300 rounded-xl px-4 py-4 bg-gray-50 focus:bg-white focus:ring-3 focus:ring-red-300 focus:border-red-500 transition-all duration-200 shadow-md hover:shadow-lg"
                  />
                  <p className="text-xs text-gray-500 mt-2">Provide context about your design and implementation</p>
                </div>
              </div>
              
              <div className="flex justify-center pt-4">
                <Button
                  onClick={handleSubmit}
                  disabled={!plantUML.trim() || !description.trim() || isLoading}
                  className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white px-12 py-5 rounded-xl font-bold text-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3 shadow-xl hover:shadow-2xl transition-all duration-200 min-w-[250px] transform hover:scale-105"
                >
                  {isLoading ? (
                    <>
                      <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Analyzing your code...</span>
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