# Travel Chat Agent with Microsoft Agent Framework and Azure Managed Redis

## Project Overview

Build a simple Travel Chat Agent using Microsoft Agent Framework in Python that demonstrates integration with Azure Managed Redis for both short-term and long-term memory management. This sample will serve as a starting point for developers to understand how to use Azure Managed Redis with the Agent Framework. 

## Requirements

### Core Features
1. **Travel Chat Agent**: An AI-powered conversational agent that can help users with travel-related queries such as:
   - Destination recommendations
   - Travel planning assistance
   - Big sports events in or around the destination
   - Booking information
   - Weather updates
   - Local attractions and activities

2. **Memory Management with Azure Managed Redis**:
   - **Short-term Memory**: Use Azure Manged Redis as backend for Thread management with associated ChatMessageStore
   - **Long-term Memory**: Implement durable memory through ContextProviders using Azure Manged Redis

3. **Development UI**: Integrate with the Agent Framework dev UI for easy testing and interaction

## Technical Architecture

### Backend Storage
- **Azure Managed Redis**: Primary storage for both thread management and context providers
- **Thread Management**: Store conversation threads and chat messages in Azure Manged Redis
- **Context Providers**: Implement durable memory for user preferences in Azure Manged Redis, travel history, and personalized recommendations Azure Manged Redis

### Framework Components
- **Microsoft Agent Framework**: Core framework for building the conversational agent
- **Dev UI**: Use the built-in development interface for testing and interaction

## Implementation Guidelines

### 1. Project Structure
Create a simple, well-organized project structure that follows Python best practices and Agent Framework conventions.

### 2. Redis Integration
Implement the following Redis-based components:

#### Thread Management
- Use Redis as the backend for storing conversation threads
- Implement ChatMessageStore to persist chat history
- Ensure thread isolation for concurrent users

#### Context Providers
Reference and adapt the following patterns from the Agent Framework samples:
- `https://github.com/microsoft/agent-framework/blob/main/python/samples/getting_started/context_providers/redis/redis_basics.py` - Basic Redis operations
- `https://github.com/microsoft/agent-framework/blob/main/python/samples/getting_started/context_providers/redis/redis_conversation.py` - Conversation context management
- `phttps://github.com/microsoft/agent-framework/blob/main/python/samples/getting_started/context_providers/redis/redis_threads.py` - Thread-based context handling

### 3. Agent Implementation
- Create a travel-focused agent with relevant capabilities
- Implement conversation flow that leverages both short-term and long-term memory
- Use context from previous conversations to provide personalized recommendations

### 4. Development UI Integration
- Integrate with the Agent Framework dev UI: https://github.com/microsoft/agent-framework/tree/main/python/packages/devui
- Ensure the UI can properly display conversation history and agent responses
- Configure the UI to work seamlessly with Redis backend

## Implementation requirments
### Conversation Management
- Initialize and manage conversation threads in Redis
- Store and retrieve chat message history
- Handle concurrent user sessions

### Context Awareness
- Remember user travel preferences across sessions
- Store and recall previous travel queries and destinations
- Maintain user profile information for personalized responses

### Travel Agent Capabilities
- Destination recommendation based on user preferences
- Travel planning assistance with memory of previous plans
- Weather information for planned destinations
- Local attractions and activity suggestions

### Redis Operations
- Basic Redis connectivity and configuration
- Thread creation and management
- Message persistence and retrieval
- Context data storage and management
- Proper error handling and connection management

## Configuration Requirements

### Azure Managed Redis
- Connection string configuration in the .env file as REDIS_URL
- Simle authentication setup via authentication token in the URL
- Security best practices

### Azure Open AI
- Connection string configuration in the .env file as AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME

### Agent Framework
- Agent configuration with Redis backends
- Context provider registration
- Dev UI setup and configuration

## Success Criteria

1. **Functional Agent**: A working travel chat agent that can engage in meaningful conversations about travel
2. **Persistent Memory**: Conversations and context are properly stored and retrieved from Redis
3. **Developer-Friendly**: Code is simple, well-documented, and easy to understand
4. **Scalable Foundation**: Architecture that can be easily extended for more complex scenarios
5. **Working Dev UI**: Fully functional development interface for testing

## Sample Scenarios to Support

1. **First-time User**: Agent introduces itself and learns user travel preferences
2. **Returning User**: Agent remembers previous conversations and preferences
3. **Trip Planning**: Agent helps plan a trip using remembered preferences and past interactions
4. **Follow-up Questions**: Agent maintains context throughout extended conversations

## Documentation Requirements

- Clear setup instructions for Azure Managed Redis
- Step-by-step deployment guide
- Code comments explaining Redis integration patterns
- Examples of extending the agent for additional travel features
- Troubleshooting guide for common Redis connectivity issues

## Deliverables

1. **Source Code**: Complete Python implementation with proper project structure
2. **Configuration Files**: All necessary configuration templates
3. **Documentation**: README with setup and usage instructions
4. **Sample Data**: Example conversations and context data for testing
5. **Deployment Guide**: Instructions for deploying to different environments

This sample should serve as a comprehensive starting point for developers wanting to build conversational agents with Microsoft Agent Framework and Azure Managed Redis, focusing on simplicity while demonstrating key architectural patterns.