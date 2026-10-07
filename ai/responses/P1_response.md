# P1 response (zero context)

> Caveat from the assistant: I have no access to the 2.1.0-M1 sources in this
> conversation; the answer is based on my general knowledge of the Spring AI
> 1.x/2.x code base and may contain modules that were renamed or removed.

## 1. Components

| # | Component | Responsibility | Key types |
|---|-----------|----------------|-----------|
| 1 | **Commons / Core model API** (`spring-ai-commons`, `spring-ai-model`; historically `spring-ai-core`) | Provider-independent abstractions: generic `Model<Req,Res>`, `ModelRequest`, `ModelResponse`, `ModelOptions`; `Document`, `Media`, `Content` | `Model`, `StreamingModel`, `Document`, `ModelOptionsUtils` |
| 2 | **Chat model API** | Messages, prompts, chat options, response metadata, streaming | `ChatModel`, `StreamingChatModel`, `Prompt`, `Message` (`UserMessage`, `SystemMessage`, `AssistantMessage`, `ToolResponseMessage`), `ChatOptions`, `ChatResponse` |
| 3 | **Other model types** | Embeddings, image generation, audio (transcription & TTS), moderation | `EmbeddingModel`, `ImageModel`, `AudioTranscriptionModel`, `TextToSpeechModel`, `ModerationModel` |
| 4 | **ChatClient & Advisors** (`spring-ai-client-chat`) | Fluent client API à la `WebClient`; an interceptor chain (advisors) that implements cross-cutting AI patterns: memory, RAG, logging, safeguard | `ChatClient`, `Advisor`, `CallAdvisor`, `StreamAdvisor`, `MessageChatMemoryAdvisor`, `SimpleLoggerAdvisor`, `SafeGuardAdvisor` |
| 5 | **Structured output** | Converting LLM text into POJOs/lists/maps via JSON schema | `StructuredOutputConverter`, `BeanOutputConverter`, `MapOutputConverter` |
| 6 | **Tool calling** | Describe Java methods/functions as tools, resolve and execute them | `ToolCallback`, `@Tool`, `ToolCallingManager`, `ToolDefinition`, `MethodToolCallback` |
| 7 | **Chat memory** | Conversation history and repositories | `ChatMemory`, `MessageWindowChatMemory`, `ChatMemoryRepository` (JDBC, Cassandra, Neo4j, ...) |
| 8 | **RAG & ETL** | Document readers (PDF, Tika, Markdown, JSoup), transformers (token splitter, keyword/summary enrichers), writers; modular RAG (query transformers, retrievers, augmenters) | `DocumentReader`, `DocumentTransformer`, `TokenTextSplitter`, `RetrievalAugmentationAdvisor`, `VectorStoreDocumentRetriever` |
| 9 | **Vector store abstraction** | Portable similarity search API and the SQL-like metadata filter language | `VectorStore`, `SearchRequest`, `Filter.Expression`, `FilterExpressionBuilder` |
| 10 | **Vector store implementations** | PGVector, Chroma, Milvus, Neo4j, Redis, Elasticsearch, OpenSearch, Qdrant, Weaviate, Pinecone, MongoDB Atlas, Cassandra, Azure AI Search, Oracle, ... | `PgVectorStore`, `ChromaVectorStore`, ... |
| 11 | **Model provider integrations** | Adapters from the portable API to vendor APIs: OpenAI, Azure OpenAI, Anthropic, Ollama, Bedrock, Vertex AI Gemini, Mistral, DeepSeek, Hugging Face, Stability AI, ... Usually a low-level REST client `XxxApi` + `XxxChatModel` + `XxxChatOptions` | `OpenAiChatModel`, `OpenAiApi`, `AnthropicChatModel`, `OllamaChatModel` |
| 12 | **MCP** | Model Context Protocol client/server integration, MCP tools as `ToolCallback`s, annotations | `McpToolUtils`, `SyncMcpToolCallback` |
| 13 | **Observability** | Micrometer observations and semantic conventions for model, client, vector-store and tool calls | `ChatModelObservationContext`, `DefaultChatModelObservationConvention` |
| 14 | **Spring Boot auto-configuration & starters** | Auto-configures beans from properties; starters only aggregate dependencies | `OpenAiChatAutoConfiguration`, `ChatClientAutoConfiguration` |

## 2. Dependencies

* Provider integrations and vector-store implementations depend **downward** on
  the abstractions (Chat/Embedding/... API, `VectorStore`) – Ports & Adapters.
* `ChatClient` depends on `ChatModel`, tool calling, chat memory and structured
  output; RAG advisors depend on `VectorStore`.
* Vector stores depend on `EmbeddingModel` (to embed documents).
* Auto-configuration depends on everything it configures; nothing depends on it.
* Observability and commons are used by almost all components.

## 3. Diagram

```
+-------------------------------------------------------------------------+
|        Spring Boot auto-configuration  /  starters  /  MCP boot          |
+-------------------------------------------------------------------------+
|  ChatClient + Advisors   |  RAG / ETL pipeline  |  MCP client/server     |
+--------------------------+----------------------+------------------------+
| Tool calling | Chat memory | Structured output | Vector store API+filter |
+-------------------------------------------------------------------------+
| Model API: Chat | Embedding | Image | Audio | Moderation  (+ options)    |
+-------------------------------------------------------------------------+
| Commons: Document, Media, Content, ModelOptionsUtils, observation, retry |
+-------------------------------------------------------------------------+
  ^ implemented by: Model providers (OpenAI, Anthropic, Ollama, Bedrock,
    Azure OpenAI, Vertex AI, Mistral, ...) and Vector stores (PGVector, ...)
```

## 4. Styles and patterns

Layered architecture + **Ports and Adapters/Hexagonal** (portable API = ports,
providers/stores = adapters), **plugin** architecture through Spring Boot
auto-configuration, **Chain of Responsibility/Interceptor** (advisors),
**Strategy** (options, converters, splitters), **Builder** (prompts, options,
clients), **Template Method** (`AbstractEmbeddingModel`), **Pipes & Filters**
(ETL pipeline), **Observer** (Micrometer observations).

Unsure: whether `spring-ai-core` still exists in 2.1 (it was split in 1.0.0-M7),
the exact provider list (Azure OpenAI, Vertex AI Gemini, Hugging Face, Watsonx
and others have been moved out or into the community organisation at some
point), and how the MCP support is packaged.
