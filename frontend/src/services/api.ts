/**
 * API service for communicating with the 3-Phase AI backend
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Types for API requests and responses
export interface DiagramSubmissionRequest {
  student_plantuml: string;
  teacher_plantuml: string;
  problem_description: string;
  diagram_type?: 'use_case' | 'class' | 'sequence';
  custom_weights?: Record<string, number>;
}

export interface ComponentMetrics {
  true_positives: number;
  false_positives: number;
  false_negatives: number;
  precision: number;
  recall: number;
  f1_score: number;
  accuracy: number;
}

export interface DiagramMetrics {
  diagram_type: string;
  component_metrics: Record<string, ComponentMetrics>;
  overall_metrics: ComponentMetrics;
  similarity_score: number;
  total_expected: number;
  total_actual: number;
  total_matched: number;
}

export interface FeedbackItem {
  type: 'error' | 'suggestion' | 'praise' | 'warning';
  category: string;
  message: string;
  severity: 'low' | 'medium' | 'high';
  actionable: boolean;
  examples: string[];
}

export interface DetailedFeedback {
  strengths: string[];
  areas_for_improvement: string[];
  detailed_items: FeedbackItem[];
}

export interface ErrorAnalysis {
  total_errors: number;
  primary_issues: string[];
  severity_breakdown: Record<string, number>;
}

export interface ScoringDetails {
  base_score: number;
  penalties: Record<string, number>;
  bonuses: Record<string, number>;
  explanation: string;
}

export interface AIGenerationLog {
  timestamp: string;
  step_name: string;
  prompt: string;
  response: string | null;
  processing_time: number;
  model: string;
  temperature?: number;
  error?: string;
}

export interface LogsSummary {
  total_calls: number;
  total_time: number;
  errors: number;
  average_time: number;
}

export interface DiagramScoringResponse {
  success: boolean;
  diagram_type: string;
  final_score: number;
  grade_letter: string;
  feedback_summary: string;
  processing_time: number;
  confidence: number;
  detailed_feedback: DetailedFeedback;
  metrics: DiagramMetrics;
  phase_results: {
    phase_one: any;
    phase_two: any;
    phase_three: any;
    phase_timings: Record<string, number>;
  };
  ai_generation_logs: AIGenerationLog[];
  logs_summary: LogsSummary;
  warnings: string[];
  errors: string[];
}

export interface PipelineStatusResponse {
  pipeline: string;
  phases: Record<string, any>;
  supported_diagrams: string[];
  llm_model: string;
  rate_limit: string;
  scoring_scale: string;
}

export interface SupportedDiagramsResponse {
  supported_types: Array<{
    type: string;
    name: string;
    description: string;
  }>;
  auto_detection: boolean;
  description: string;
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  service?: string;
  model?: string;
  version?: string;
  reason?: string;
}

// API Client Class
export class DiagramScoringAPI {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Score a single diagram using the 3-phase pipeline
   */
  async scoreDiagram(request: DiagramSubmissionRequest): Promise<DiagramScoringResponse> {
    const response = await fetch(`${this.baseURL}/three-phase/score-diagram`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Score multiple diagrams in batch
   */
  async scoreDiagramsBatch(requests: DiagramSubmissionRequest[]): Promise<DiagramScoringResponse[]> {
    const response = await fetch(`${this.baseURL}/three-phase/score-batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requests),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get pipeline status and capabilities
   */
  async getPipelineStatus(): Promise<PipelineStatusResponse> {
    const response = await fetch(`${this.baseURL}/three-phase/status`);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get supported diagram types
   */
  async getSupportedDiagrams(): Promise<SupportedDiagramsResponse> {
    const response = await fetch(`${this.baseURL}/three-phase/supported-diagrams`);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await fetch(`${this.baseURL}/three-phase/health`);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Test connection to the API
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch (error) {
      console.error('API connection test failed:', error);
      return false;
    }
  }
}

// Default API instance
export const diagramAPI = new DiagramScoringAPI();

// Utility functions
export const formatScore = (score: number): string => {
  return `${score.toFixed(2)}/10`;
};

export const formatPercentage = (value: number): string => {
  return `${(value * 100).toFixed(1)}%`;
};

export const getScoreColor = (score: number): string => {
  if (score >= 9) return 'text-green-600';
  if (score >= 8) return 'text-blue-600';
  if (score >= 7) return 'text-yellow-600';
  if (score >= 6) return 'text-orange-600';
  return 'text-red-600';
};

export const getGradeColor = (grade: string): string => {
  switch (grade) {
    case 'A': return 'text-green-600 bg-green-50 border-green-200';
    case 'B': return 'text-blue-600 bg-blue-50 border-blue-200';
    case 'C': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'D': return 'text-orange-600 bg-orange-50 border-orange-200';
    case 'F': return 'text-red-600 bg-red-50 border-red-200';
    default: return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

export const getSeverityColor = (severity: string): string => {
  switch (severity) {
    case 'high': return 'text-red-600 bg-red-50';
    case 'medium': return 'text-yellow-600 bg-yellow-50';
    case 'low': return 'text-green-600 bg-green-50';
    default: return 'text-gray-600 bg-gray-50';
  }
};

// Error handling utilities
export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export const handleAPIError = (error: unknown): string => {
  if (error instanceof APIError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected error occurred';
};
