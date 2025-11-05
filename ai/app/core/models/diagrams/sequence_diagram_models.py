"""Domain models for UML Sequence Diagrams."""

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class MessageType(str, Enum):
    """Types of messages in sequence diagrams."""
    SYNCHRONOUS = "synchronous"      # ->
    ASYNCHRONOUS = "asynchronous"    # ->>
    RETURN = "return"                # <--
    CREATE = "create"                # -> with <<create>>
    DESTROY = "destroy"              # -> with <<destroy>>
    SELF = "self"                    # -> to self


class Participant(BaseModel):
    """Represents a participant (actor/object) in a sequence diagram."""
    
    name: str = Field(..., description="Name of the participant")
    type: Optional[str] = Field(None, description="Type of participant (actor, boundary, control, entity)")
    stereotype: Optional[str] = Field(None, description="Participant stereotype")
    alias: Optional[str] = Field(None, description="Alias used in the diagram")
    
    def get_display_name(self) -> str:
        """Get the display name for the participant."""
        return self.alias if self.alias else self.name


class Message(BaseModel):
    """Represents a message between participants in a sequence diagram."""
    
    source: str = Field(..., description="Source participant name")
    target: str = Field(..., description="Target participant name")
    message_type: MessageType = Field(..., description="Type of message")
    label: str = Field(..., description="Message label/description")
    sequence_number: Optional[int] = Field(None, description="Sequence number for ordering")
    return_message: Optional[str] = Field(None, description="Return message if any")
    
    def __str__(self) -> str:
        """String representation for PlantUML generation."""
        message_symbols = {
            MessageType.SYNCHRONOUS: "->",
            MessageType.ASYNCHRONOUS: "->>",
            MessageType.RETURN: "<--",
            MessageType.CREATE: "->",
            MessageType.DESTROY: "->",
            MessageType.SELF: "->"
        }
        
        symbol = message_symbols[self.message_type]
        target = self.target if self.message_type != MessageType.SELF else self.source
        
        return f"{self.source} {symbol} {target} : {self.label}"


class Activation(BaseModel):
    """Represents an activation (lifeline) in a sequence diagram."""
    
    participant: str = Field(..., description="Participant name")
    start_message: Optional[str] = Field(None, description="Message that starts the activation")
    end_message: Optional[str] = Field(None, description="Message that ends the activation")
    duration: Optional[int] = Field(None, description="Duration of activation")


class Fragment(BaseModel):
    """Represents a combined fragment (alt, opt, loop, etc.) in sequence diagrams."""
    
    fragment_type: str = Field(..., description="Type of fragment (alt, opt, loop, par, etc.)")
    condition: Optional[str] = Field(None, description="Fragment condition")
    participants: List[str] = Field(default_factory=list, description="Participants involved")
    messages: List[Message] = Field(default_factory=list, description="Messages within the fragment")


class SequenceDiagram(BaseModel):
    """Complete UML Sequence Diagram representation."""
    
    participants: List[Participant] = Field(default_factory=list, description="List of participants")
    messages: List[Message] = Field(default_factory=list, description="List of messages")
    activations: List[Activation] = Field(default_factory=list, description="List of activations")
    fragments: List[Fragment] = Field(default_factory=list, description="List of combined fragments")
    title: Optional[str] = Field(None, description="Diagram title")
    
    def get_participant_names(self) -> List[str]:
        """Get list of all participant names."""
        return [p.name for p in self.participants]
    
    def get_message_labels(self) -> List[str]:
        """Get list of all message labels."""
        return [m.label for m in self.messages]
    
    def find_participant_by_name(self, name: str) -> Optional[Participant]:
        """Find a participant by name."""
        for participant in self.participants:
            if participant.name == name or participant.alias == name:
                return participant
        return None
    
    def get_messages_from_participant(self, participant_name: str) -> List[Message]:
        """Get all messages sent from a specific participant."""
        return [m for m in self.messages if m.source == participant_name]
    
    def get_messages_to_participant(self, participant_name: str) -> List[Message]:
        """Get all messages sent to a specific participant."""
        return [m for m in self.messages if m.target == participant_name]
    
    def get_ordered_messages(self) -> List[Message]:
        """Get messages ordered by sequence number."""
        return sorted(
            [m for m in self.messages if m.sequence_number is not None],
            key=lambda x: x.sequence_number
        ) + [m for m in self.messages if m.sequence_number is None]
