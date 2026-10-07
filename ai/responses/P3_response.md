# P3 response (README + modules + packages + package dependency graph)

## 1. Components and package mapping

Twelve components. Ordered rules, first match wins (also stored as
`ai/ai_architecture_P3.json`):

```json
[
  ["Boot auto-configuration", ".*\\.autoconfigure(\\..*)?$|^aot$|.*\\.aot$"],
  ["Dev services (Docker Compose / Testcontainers)", "^(docker|testcontainers)\\..*"],
  ["Chat memory repositories", "^chat\\.memory\\.repository\\..*"],
  ["MCP", "^mcp(\\..*)?$"],
  ["Vector store implementations", "^vectorstore\\.(?!filter|observation|properties$).*|^chroma\\.vectorstore$|^chat\\.cache\\.semantic$"],
  ["Vector store API & filter language", "^vectorstore(\\.filter(\\..*)?|\\.observation|\\.properties)?$"],
  ["Model providers", "^(anthropic|bedrock|deepseek|elevenlabs|google\\.genai|mistralai|ollama|openai|postgresml|stabilityai|transformers|vertexai)(\\..*)?$"],
  ["ChatClient & Advisors", "^chat\\.client(\\..*)?$|^chat\\.memory$|^chat\\.evaluation$"],
  ["RAG & ETL", "^rag(\\..*)?$|^reader(\\..*)?$|^transformer(\\..*)?$|^writer$"],
  ["Tool calling & tool search", "^tool(\\..*)?$|^model\\.tool(\\..*)?$"],
  ["Model API (chat, embedding, image, audio, moderation)", "^(model|model\\.observation|model\\.transformer|chat\\.model|chat\\.messages(\\..*)?|chat\\.prompt|chat\\.metadata|chat\\.observation|embedding(\\..*)?|image(\\..*)?|audio\\..*|moderation|converter|evaluation|tokenizer)$"],
  ["Commons & infrastructure", ".*"]
]
```

Rationale for the ordering: the `autoconfigure`/`aot` suffix is the strongest
architectural signal (Spring Boot wiring lives in its own modules, design doc
02), so it is matched first; `chat.memory.repository.*` and
`chat.cache.semantic` are adapters even though they live under `chat`;
`vectorstore.<vendor>` packages are adapters while `vectorstore`,
`vectorstore.filter.*` and `vectorstore.observation` are the port.

## 2. Responsibilities and key classes

| Component | Responsibility | Key classes (from the package list) |
|-----------|----------------|-------------------------------------|
| Commons & infrastructure | Data model shared by everything, observability conventions, JSON-schema utilities, templating, retry | `Document`, `Media`, `Content`, `ObservabilityHelper`, `JsonSchemaGenerator`, `StTemplateRenderer`, `RetryUtils` |
| Model API | Portable, provider-independent model SPI for chat, embedding, image, audio (TTS/transcription), moderation, plus prompts/messages, metadata and structured-output converters | `ChatModel`, `Prompt`, `UserMessage`, `ChatResponse`, `EmbeddingModel`, `ImageModel`, `BeanOutputConverter`, `ModelOptionsUtils` |
| Tool calling & tool search | Tool definitions/callbacks, `@Tool` annotation, resolution and execution, tool-search index (Lucene/regex/vector store) | `ToolCallback`, `ToolCallingManager`, `MethodToolCallback`, `ToolSearcher` |
| ChatClient & Advisors | Fluent client, advisor chain (memory, logging, safeguard, tool search, vector store QA), chat memory, evaluation | `ChatClient`, `DefaultChatClient`, `Advisor`, `MessageChatMemoryAdvisor`, `ChatMemory` |
| RAG & ETL | Modular RAG pipeline (query transformation/expansion, retrieval, join, augmentation) and ETL (readers, splitters, writers) | `RetrievalAugmentationAdvisor`, `VectorStoreDocumentRetriever`, `PagePdfDocumentReader`, `TokenTextSplitter` |
| Vector store API & filter language | `VectorStore` port, `SearchRequest`, portable metadata filter language (ANTLR parser + converters), observation | `VectorStore`, `SearchRequest`, `Filter`, `FilterExpressionBuilder` |
| Vector store implementations | 21 vector database adapters + Redis semantic cache | `PgVectorStore`, `MilvusVectorStore`, `QdrantVectorStore`, ... |
| Chat memory repositories | Persistent `ChatMemoryRepository` adapters | `JdbcChatMemoryRepository`, `CassandraChatMemoryRepository`, ... |
| Model providers | Adapters to 12 AI providers (low-level `*Api` clients + `*ChatModel`, `*EmbeddingModel`, options) | `OpenAiChatModel`, `AnthropicChatModel`, `OllamaChatModel`, `GoogleGenAiChatModel` |
| MCP | Model Context Protocol: annotation-based server/client methods and providers, tool bridging, WebFlux/WebMVC transports | `McpToolUtils`, `SyncMcpToolCallback`, `@McpTool`, `SyncMcpToolProvider` |
| Boot auto-configuration | Spring Boot `@AutoConfiguration` + `@ConfigurationProperties` for every component above; AOT runtime hints | `OpenAiChatAutoConfiguration`, `ChatClientAutoConfiguration`, `McpServerAutoConfiguration` |
| Dev services | Docker Compose / Testcontainers service connections for vector stores and Ollama | `ChromaDockerComposeConnectionDetailsFactory` |

## 3. Dependencies between components

Aggregating the package graph to the components gives (class-level
dependencies, strongest first):

| From → To | # |
|-----------|---|
| Model providers → Model API | 516 |
| Vector store impl. → Vector store API | 190 |
| Boot auto-config → Model providers | 148 |
| ChatClient & Advisors → Model API | 104 |
| Boot auto-config → Model API | 90 |
| Model providers → Commons | 80 |
| Vector store impl. → Commons | 77 |
| Vector store impl. → Model API (embedding) | 77 |
| Model providers → Tool calling | 69 |
| Boot auto-config → Vector store API / MCP / Tool calling | 53 / 51 / 41 |

Small cycles: Model API ⇄ Commons (48 vs 8), Model API ⇄ Tool calling (37 vs
3) and Commons ⇄ Tool calling (18 vs 4). They come from a handful of classes
(e.g. `model.tool` ↔ `chat.messages`, converters using JSON-schema utilities in
`util.json.schema` and vice-versa). Everything else is acyclic.

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │ L5  Boot auto-configuration (221)        Dev services (23)          │
 └───────────────┬──────────────────────────────────┬──────────────────┘
 ┌───────────────▼──────────────────────────────────▼──────────────────┐
 │ L4  Model providers (148) │ Vector store impl. (62) │ Memory repos (24)│ ← adapters
 └───────────────┬──────────────────────────────────┬──────────────────┘
 ┌───────────────▼──────────────────────────────────▼──────────────────┐
 │ L3  ChatClient & Advisors (55) │ RAG & ETL (39) │ MCP (163)          │
 └───────────────┬──────────────────────────────────┬──────────────────┘
 ┌───────────────▼──────────────────────────────────▼──────────────────┐
 │ L2  Model API (157) ⇄ Tool calling (59)    Vector store API (29)     │ ← ports
 └───────────────┬──────────────────────────────────┬──────────────────┘
 ┌───────────────▼──────────────────────────────────▼──────────────────┐
 │ L1  Commons & infrastructure (46): Document, observation, util, retry│
 └─────────────────────────────────────────────────────────────────────┘
```
(numbers = top-level classes that take part in at least one dependency)

## 4. Hub packages (omnipresent candidates)

By number of distinct packages depending on them: `document` (57 packages),
`embedding` (55), `vectorstore` (45), `model` (43),
`observation.conventions` (41), `vectorstore.observation` (39), `util` (37),
`chat.messages` (34), `chat.prompt` (33), `vectorstore.filter` (29),
`chat.model` (28), `chat.metadata` (27), `model.tool` (25), `retry` (24).
Classes like `Document`, `EmbeddingModel`, `VectorStore`, `ModelOptionsUtils`,
`ChatResponse` and the observation conventions are therefore expected to be
detected as omnipresent ("noise") classes.

## 5. Modularity assessment

* **Strong points.** A textbook Ports & Adapters structure: the two strongest
  component dependencies are adapters → ports (providers → Model API, stores →
  Vector store API); adapters never depend on each other; Boot wiring is
  isolated in its own layer and nothing below depends on it (enforced by
  Maven enforcer rules, design doc 02).
* **Weak points.** (i) The Model API is a large kernel that every other
  component uses – a change there ripples everywhere; (ii) small cycles between
  Model API, Tool calling and Commons; (iii) MCP has grown into the
  second-largest component (163 classes, mostly the annotation framework with
  one package per MCP method type) and is almost a framework of its own;
  (iv) auto-configuration is the largest component by class count –
  configuration code outweighs some of the functional code.
