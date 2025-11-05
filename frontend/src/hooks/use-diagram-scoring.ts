/**
 * React hook for diagram scoring functionality
 */

import { useState, useCallback } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { 
  diagramAPI, 
  DiagramSubmissionRequest, 
  DiagramScoringResponse,
  PipelineStatusResponse,
  SupportedDiagramsResponse,
  handleAPIError
} from '@/services/api';
import { useToast } from '@/hooks/use-toast';

export interface ScoringState {
  isLoading: boolean;
  error: string | null;
  result: DiagramScoringResponse | null;
}

export interface DiagramScoringHook {
  // Scoring state
  scoringState: ScoringState;
  
  // Actions
  scoreDiagram: (request: DiagramSubmissionRequest) => Promise<void>;
  clearResult: () => void;
  
  // Pipeline info
  pipelineStatus: PipelineStatusResponse | undefined;
  supportedDiagrams: SupportedDiagramsResponse | undefined;
  isConnected: boolean;
  
  // Loading states
  isLoadingStatus: boolean;
  isLoadingDiagrams: boolean;
}

export const useDiagramScoring = (): DiagramScoringHook => {
  const { toast } = useToast();
  const [scoringState, setScoringState] = useState<ScoringState>({
    isLoading: false,
    error: null,
    result: null,
  });

  // Query for pipeline status
  const {
    data: pipelineStatus,
    isLoading: isLoadingStatus,
    error: statusError,
  } = useQuery({
    queryKey: ['pipeline-status'],
    queryFn: () => diagramAPI.getPipelineStatus(),
    retry: 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Query for supported diagrams
  const {
    data: supportedDiagrams,
    isLoading: isLoadingDiagrams,
    error: diagramsError,
  } = useQuery({
    queryKey: ['supported-diagrams'],
    queryFn: () => diagramAPI.getSupportedDiagrams(),
    retry: 2,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });

  // Connection status
  const isConnected = !statusError && !diagramsError && !!pipelineStatus;

  // Mutation for scoring diagrams
  const scoringMutation = useMutation({
    mutationFn: (request: DiagramSubmissionRequest) => diagramAPI.scoreDiagram(request),
    onMutate: () => {
      setScoringState({
        isLoading: true,
        error: null,
        result: null,
      });
    },
    onSuccess: (data: DiagramScoringResponse) => {
      setScoringState({
        isLoading: false,
        error: null,
        result: data,
      });

      // Show success toast
      toast({
        title: "Analysis Complete!",
        description: `Your diagram scored ${data.final_score.toFixed(2)}/10 (Grade ${data.grade_letter})`,
        duration: 5000,
      });
    },
    onError: (error: unknown) => {
      const errorMessage = handleAPIError(error);
      setScoringState({
        isLoading: false,
        error: errorMessage,
        result: null,
      });

      // Show error toast
      toast({
        title: "Analysis Failed",
        description: errorMessage,
        variant: "destructive",
        duration: 8000,
      });
    },
  });

  // Score diagram function
  const scoreDiagram = useCallback(async (request: DiagramSubmissionRequest) => {
    try {
      await scoringMutation.mutateAsync(request);
    } catch (error) {
      // Error is already handled in onError
      console.error('Scoring failed:', error);
    }
  }, [scoringMutation]);

  // Clear result function
  const clearResult = useCallback(() => {
    setScoringState({
      isLoading: false,
      error: null,
      result: null,
    });
  }, []);

  return {
    scoringState,
    scoreDiagram,
    clearResult,
    pipelineStatus,
    supportedDiagrams,
    isConnected,
    isLoadingStatus,
    isLoadingDiagrams,
  };
};

// Additional utility hooks

/**
 * Hook for testing API connection
 */
export const useAPIConnection = () => {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState(false);

  const checkConnection = useCallback(async () => {
    setIsChecking(true);
    try {
      const connected = await diagramAPI.testConnection();
      setIsConnected(connected);
      return connected;
    } catch (error) {
      setIsConnected(false);
      return false;
    } finally {
      setIsChecking(false);
    }
  }, []);

  return {
    isConnected,
    isChecking,
    checkConnection,
  };
};

/**
 * Hook for batch scoring (future feature)
 */
export const useBatchScoring = () => {
  const { toast } = useToast();
  const [results, setResults] = useState<DiagramScoringResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const scoreBatch = useCallback(async (requests: DiagramSubmissionRequest[]) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const batchResults = await diagramAPI.scoreDiagramsBatch(requests);
      setResults(batchResults);
      
      toast({
        title: "Batch Analysis Complete!",
        description: `Successfully analyzed ${batchResults.length} diagrams`,
        duration: 5000,
      });
    } catch (error) {
      const errorMessage = handleAPIError(error);
      setError(errorMessage);
      
      toast({
        title: "Batch Analysis Failed",
        description: errorMessage,
        variant: "destructive",
        duration: 8000,
      });
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  const clearResults = useCallback(() => {
    setResults([]);
    setError(null);
  }, []);

  return {
    results,
    isLoading,
    error,
    scoreBatch,
    clearResults,
  };
};
