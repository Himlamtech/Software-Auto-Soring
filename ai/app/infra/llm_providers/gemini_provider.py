"""Google Gemini LLM provider implementation with multi-prompt chain support."""

from typing import List, Optional, Dict, Any
import asyncio
import google.generativeai as genai
from loguru import logger

from app.services.llm.extraction_service import LLMExtractionService
from app.services.llm.feedback_service import LLMFeedbackService
from app.core.models.uml_components import UMLDiagram, Actor, UseCase, Relationship
from app.core.models.input_output import ProblemDescription
from app.core.models.scoring import ComponentScore, OverallScore, FeedbackItem


class GeminiLLMService:
    """Enhanced Gemini service with multi-prompt chain support for 3-phase pipeline."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-lite", temperature: float = 0.1):
        """
        Initialize Gemini service.

        Args:
            api_key: Google Gemini API key
            model: Model to use (default: gemini-2.5-flash-lite for free tier)
            temperature: Temperature for generation
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

        # Configure Gemini
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)

        # Generation config
        self.generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=4096,
            top_p=0.95,
            top_k=40
        )

        # Initialize detailed logging storage
        self.detailed_logs = []

    async def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate response from Gemini with error handling and retries.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated response text
        """
        import time
        start_time = time.time()

        try:
            # Log the prompt for detailed tracking
            step_name = kwargs.get('step_name', 'AI Generation')
            logger.info(f"🤖 {step_name} - Sending prompt to Gemini...")

            # Log prompt details (truncated for readability)
            prompt_preview = prompt[:200] + "..." if len(prompt) > 200 else prompt
            logger.info(f"📝 Prompt preview: {prompt_preview}")

            # Override temperature if provided
            temp = kwargs.get('temperature', self.temperature)
            config = genai.types.GenerationConfig(
                temperature=temp,
                max_output_tokens=kwargs.get('max_tokens', 4096),
                top_p=kwargs.get('top_p', 0.95),
                top_k=kwargs.get('top_k', 40)
            )

            response = await self.client.generate_content_async(
                prompt,
                generation_config=config
            )

            processing_time = time.time() - start_time

            # Log the response for detailed tracking
            response_preview = response.text[:200] + "..." if len(response.text) > 200 else response.text
            logger.info(f"✅ {step_name} - Response received in {processing_time:.2f}s")
            logger.info(f"📄 Response preview: {response_preview}")

            # Store detailed log entry
            log_entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "step_name": step_name,
                "prompt": prompt,
                "response": response.text,
                "processing_time": processing_time,
                "model": self.model,
                "temperature": temp
            }
            self.detailed_logs.append(log_entry)

            return response.text

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Gemini API error after {processing_time:.2f}s: {str(e)}"
            logger.error(f"❌ {step_name} - {error_msg}")

            # Store error log entry
            log_entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "step_name": step_name,
                "prompt": prompt,
                "response": None,
                "error": str(e),
                "processing_time": processing_time,
                "model": self.model
            }
            self.detailed_logs.append(log_entry)

            raise e

    def get_detailed_logs(self) -> List[Dict[str, Any]]:
        """Get all detailed logs from this session."""
        return self.detailed_logs.copy()

    def clear_logs(self):
        """Clear all detailed logs."""
        self.detailed_logs.clear()

    def get_logs_summary(self) -> Dict[str, Any]:
        """Get summary of logs for this session."""
        if not self.detailed_logs:
            return {"total_calls": 0, "total_time": 0, "errors": 0}

        total_time = sum(log.get("processing_time", 0) for log in self.detailed_logs)
        errors = sum(1 for log in self.detailed_logs if "error" in log)

        return {
            "total_calls": len(self.detailed_logs),
            "total_time": total_time,
            "errors": errors,
            "average_time": total_time / len(self.detailed_logs) if self.detailed_logs else 0
        }

    async def multi_prompt_chain(self, prompts: List[str], context: Dict[str, Any] = None) -> List[str]:
        """
        Execute multiple prompts in sequence for Phase 1 normalization chain.

        Args:
            prompts: List of prompts to execute in sequence
            context: Shared context dictionary

        Returns:
            List of responses from each prompt
        """
        results = []
        accumulated_context = context.copy() if context else {}

        for i, prompt in enumerate(prompts):
            try:
                # Add previous results to context
                if results:
                    accumulated_context[f"previous_step_{i-1}"] = results[-1]

                # Add context to prompt if available
                if accumulated_context:
                    context_str = "\n".join([f"{k}: {v}" for k, v in accumulated_context.items()])
                    enhanced_prompt = f"CONTEXT:\n{context_str}\n\nPROMPT:\n{prompt}"
                else:
                    enhanced_prompt = prompt

                response = await self.generate_response(enhanced_prompt)
                results.append(response)

                logger.info(f"Multi-prompt chain step {i+1}/{len(prompts)} completed")

                # Rate limiting for free tier (15 RPM = 4 second intervals)
                if i < len(prompts) - 1:
                    await asyncio.sleep(4)

            except Exception as e:
                logger.error(f"Multi-prompt chain failed at step {i+1}: {str(e)}")
                raise e

        return results


class GeminiExtractionProvider(LLMExtractionService):
    """Google Gemini implementation of LLM extraction service."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-lite"):
        """
        Initialize Gemini provider.

        Args:
            api_key: Google Gemini API key
            model: Model to use for extraction
        """
        self.api_key = api_key
        self.model = model
        self.llm_service = GeminiLLMService(api_key, model)
    
    async def extract_from_plantuml(
        self,
        plantuml_code: str,
        context: Optional[str] = None
    ) -> UMLDiagram:
        """Extract UML components from PlantUML code using Gemini."""
        # Implementation placeholder
        actors = await self.extract_actors(plantuml_code, "plantuml")
        use_cases = await self.extract_use_cases(plantuml_code, "plantuml")
        relationships = await self.extract_relationships(
            plantuml_code, actors, use_cases, "plantuml"
        )
        
        return UMLDiagram(
            actors=actors,
            use_cases=use_cases,
            relationships=relationships
        )
    
    async def extract_from_problem_description(
        self,
        problem: ProblemDescription
    ) -> UMLDiagram:
        """Extract expected components from problem description using Gemini."""
        # Implementation placeholder
        full_text = f"{problem.description}\n{problem.functional_requirements or ''}"
        
        actors = await self.extract_actors(full_text, "problem")
        use_cases = await self.extract_use_cases(full_text, "problem")
        relationships = await self.extract_relationships(
            full_text, actors, use_cases, "problem"
        )
        
        return UMLDiagram(
            actors=actors,
            use_cases=use_cases,
            relationships=relationships
        )
    
    async def extract_actors(
        self,
        text: str,
        extraction_type: str = "plantuml"
    ) -> List[Actor]:
        """Extract actors using Gemini with optimized prompts."""
        # Implementation placeholder - use optimized prompts for actor extraction
        return []
    
    async def extract_use_cases(
        self,
        text: str,
        extraction_type: str = "plantuml"
    ) -> List[UseCase]:
        """Extract use cases using Gemini with optimized prompts."""
        # Implementation placeholder - use optimized prompts for use case extraction
        return []
    
    async def extract_relationships(
        self,
        text: str,
        actors: List[Actor],
        use_cases: List[UseCase],
        extraction_type: str = "plantuml"
    ) -> List[Relationship]:
        """Extract relationships using Gemini with optimized prompts."""
        # Implementation placeholder - use optimized prompts for relationship extraction
        return []
    
    async def validate_extraction(
        self,
        diagram: UMLDiagram,
        original_text: str
    ) -> UMLDiagram:
        """Validate and refine extraction using Gemini."""
        # Implementation placeholder - validation and refinement logic
        return diagram
    
    def _get_actor_extraction_prompt(self, text: str, extraction_type: str) -> str:
        """Get optimized prompt for actor extraction."""
        if extraction_type == "plantuml":
            return f"""
            Extract all actors from this PlantUML code. Focus on identifying:
            - Actor names (entities that interact with the system)
            - Any stereotypes or descriptions
            - Consider Vietnamese names and technical terms
            
            PlantUML Code:
            {text}
            
            Return actors in JSON format with name, description, and stereotype fields.
            Respond in Vietnamese if the input contains Vietnamese text.
            """
        else:
            return f"""
            Extract all potential actors from this problem description. Look for:
            - Users, roles, or external systems that interact with the system
            - Stakeholders mentioned in the requirements
            - Consider Vietnamese context and technical terms
            
            Problem Description:
            {text}
            
            Return actors in JSON format with name and description fields.
            Respond in Vietnamese if the input contains Vietnamese text.
            """
    
    def _get_use_case_extraction_prompt(self, text: str, extraction_type: str) -> str:
        """Get optimized prompt for use case extraction."""
        if extraction_type == "plantuml":
            return f"""
            Extract all use cases from this PlantUML code. Focus on identifying:
            - Use case names and descriptions
            - Primary actors associated with each use case
            - Consider Vietnamese technical terms
            
            PlantUML Code:
            {text}
            
            Return use cases in JSON format with name, description, and primary_actor fields.
            Respond in Vietnamese if the input contains Vietnamese text.
            """
        else:
            return f"""
            Extract all potential use cases from this problem description. Look for:
            - System functionalities and features
            - Actions users can perform
            - Business processes described
            - Consider Vietnamese context and technical terms
            
            Problem Description:
            {text}
            
            Return use cases in JSON format with name and description fields.
            Respond in Vietnamese if the input contains Vietnamese text.
            """
    
    def _get_relationship_extraction_prompt(
        self,
        text: str,
        actors: List[Actor],
        use_cases: List[UseCase],
        extraction_type: str
    ) -> str:
        """Get optimized prompt for relationship extraction."""
        actor_names = [actor.name for actor in actors]
        use_case_names = [uc.name for uc in use_cases]
        
        return f"""
        Extract all relationships from this text given the following actors and use cases:
        
        Actors: {actor_names}
        Use Cases: {use_case_names}
        
        Text:
        {text}
        
        Focus on identifying:
        - Associations between actors and use cases
        - Include relationships between use cases
        - Extend relationships between use cases
        - Generalization relationships
        - Consider Vietnamese technical terms and relationships
        
        Return relationships in JSON format with source, target, and relationship_type fields.
        Respond in Vietnamese if the input contains Vietnamese text.
        """


class GeminiFeedbackProvider(LLMFeedbackService):
    """Google Gemini implementation of LLM feedback service."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-lite"):
        """
        Initialize Gemini feedback provider.

        Args:
            api_key: Google Gemini API key
            model: Model to use for feedback generation
        """
        self.api_key = api_key
        self.model = model
        self.llm_service = GeminiLLMService(api_key, model, temperature=0.3)  # Higher temp for creativity
    
    async def generate_overall_feedback(
        self,
        overall_score: OverallScore,
        expected_diagram: UMLDiagram,
        actual_diagram: UMLDiagram
    ) -> List[FeedbackItem]:
        """Generate overall feedback using Gemini."""
        # Implementation placeholder
        return []
    
    async def generate_component_feedback(
        self,
        component_score: ComponentScore,
        expected_components: List[any],
        actual_components: List[any]
    ) -> List[FeedbackItem]:
        """Generate component-specific feedback using Gemini."""
        # Implementation placeholder
        return []
    
    async def generate_strength_feedback(
        self,
        component_scores: List[ComponentScore]
    ) -> List[FeedbackItem]:
        """Generate strength feedback using Gemini."""
        # Implementation placeholder
        return []
    
    async def generate_improvement_suggestions(
        self,
        component_scores: List[ComponentScore],
        expected_diagram: UMLDiagram,
        actual_diagram: UMLDiagram
    ) -> List[FeedbackItem]:
        """Generate improvement suggestions using Gemini."""
        # Implementation placeholder
        return []
    
    async def generate_missing_components_feedback(
        self,
        component_scores: List[ComponentScore]
    ) -> List[FeedbackItem]:
        """Generate missing components feedback using Gemini."""
        # Implementation placeholder
        return []
    
    async def generate_incorrect_components_feedback(
        self,
        component_scores: List[ComponentScore]
    ) -> List[FeedbackItem]:
        """Generate incorrect components feedback using Gemini."""
        # Implementation placeholder
        return []
    
    def _generate_feedback_prompt(self, context: str, component_type: str) -> str:
        """Generate feedback prompt for Gemini."""
        return f"""
        Bạn là một giáo viên chuyên môn Công Nghệ Phần Mềm, chuyên về UML và Use Case Diagram.
        
        Hãy đưa ra phản hồi chi tiết và mang tính giáo dục cho sinh viên về {component_type} trong diagram UML của họ.
        
        Context: {context}
        
        Yêu cầu:
        1. Sử dụng tiếng Việt
        2. Đưa ra phản hồi tích cực và xây dựng
        3. Giải thích cụ thể các lỗi và cách khắc phục
        4. Đưa ra gợi ý cải thiện
        5. Sử dụng thuật ngữ kỹ thuật chính xác
        
        Định dạng phản hồi: JSON với các trường type, component_type, message, severity
        """

