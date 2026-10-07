# P2 response (README + module list)

## 1. Components (module groups)

| Component | Modules (class files) | Responsibility |
|-----------|----------------------|----------------|
| **C1 Commons** | `spring-ai-commons` (57), `spring-ai-template-st` (3), `spring-ai-retry` (6) | Document/Media model, observation conventions, template rendering (StringTemplate), retry support |
| **C2 Model API** | `spring-ai-model` (346) | Portable model abstractions (chat, embedding, image, audio, moderation), messages & prompts, tool-calling SPI, structured-output converters, chat memory SPI. The biggest module – the “kernel” |
| **C3 Chat Client & Advisors** | `spring-ai-client-chat` (98) | Fluent `ChatClient`, advisor chain, structured output at client level |
| **C4 RAG & Advisors on data** | `spring-ai-rag` (24), `spring-ai-vector-store-advisor` (4), `spring-ai-redis-semantic-cache` (8) | Modular RAG, `QuestionAnswerAdvisor`, semantic cache |
| **C5 Tool search** | `spring-ai-tool-search-tool` (22), `spring-ai-tool-search-advisor` (3) | Dynamic discovery of tools (index over tool definitions) |
| **C6 ETL – document readers** | `spring-ai-pdf-document-reader` (12), `-tika-` (1), `-markdown-` (4), `-jsoup-` (3) | Ingestion of documents |
| **C7 Vector store API** | `spring-ai-vector-store` (88) | `VectorStore`, metadata filter language (ANTLR), observation |
| **C8 Vector store adapters** | 21 `*-store` modules (azure, cassandra, chroma, coherence, couchbase, elasticsearch, gemfire, mariadb, milvus, mongodb-atlas, neo4j, opensearch, oracle, pgvector, pinecone, qdrant, redis, s3, typesense, weaviate, bedrock-knowledgebase) | Adapters to vector databases |
| **C9 Chat memory repositories** | `spring-ai-model-chat-memory-repository-{cassandra,jdbc,mongodb,neo4j,redis}` | Persistent conversation memory |
| **C10 Model provider adapters** | `anthropic` (50), `openai` (81), `mistral-ai` (79), `ollama` (46), `deepseek` (40), `elevenlabs` (36), `google-genai` (+embedding, image: 53), `bedrock` (25), `bedrock-converse` (22), `stability-ai` (11), `vertex-ai-embedding` (18), `postgresml` (4), `transformers` (2) | Adapters to AI providers |
| **C11 MCP** | `spring-ai-mcp` (25), `spring-ai-mcp-annotations` (224), `mcp-spring-webflux` (16), `mcp-spring-webmvc` (10) | Model Context Protocol: tool bridging, annotation-based servers/clients, transports |
| **C12 Boot auto-configuration** | 57 `spring-ai-autoconfigure-*` modules | Spring Boot wiring for every model, store, memory, MCP, observation |
| **C13 Dev services** | `spring-ai-spring-boot-docker-compose` (23), `spring-ai-spring-boot-testcontainers` (18) | Service connections for Docker Compose / Testcontainers |

## 2. Layers and allowed dependencies

1. **L1 Foundation** – C1.
2. **L2 Core abstractions** – C2, C7 (depends on L1).
3. **L3 Application services** – C3, C4, C5, C6, C11 (depend on L1–L2; C4 also on C7).
4. **L4 Adapters (plugins)** – C8, C9, C10 (implement L2 SPIs; must not depend on each other).
5. **L5 Spring Boot integration** – C12, C13 (may depend on everything below; nothing depends on them).

Dependencies should only point downwards; adapters should be leaves.

## 3. Diagram

```
 L5  [ C12 Boot auto-configuration (57 modules) ]   [ C13 Dev services ]
          |  wires everything below
 L4  [ C10 Model providers ] [ C8 Vector stores ] [ C9 Memory repositories ]
          |  implement SPIs of
 L3  [ C3 ChatClient+Advisors ] [ C4 RAG ] [ C5 Tool search ] [ C6 Readers ] [ C11 MCP ]
          |
 L2  [ C2 Model API (chat, embedding, image, audio, moderation, tool, memory, converter) ]
     [ C7 Vector store API + filter language ]
          |
 L1  [ C1 Commons: Document, observation, template, retry ]
```

## 4. Observations / smells

* `spring-ai-model` (346 classes) is a **large kernel** that mixes several
  concerns (all model types, tool calling, memory SPI, converters) – a
  candidate “god module”.
* `spring-ai-mcp-annotations` (224 classes) is the second largest module;
  MCP has become a subsystem of its own size.
* The **auto-configuration layer** has ~1 module per adapter (57 modules) –
  clean plugin structure but a very large surface.
* `chat-memory-redis` exists both as an auto-configuration and as a repository
  auto-configuration (`...-chat-memory-redis` and `...-chat-memory-repository-redis`),
  which looks like a duplicated/legacy path.
* Tool search is split across a tool module and an advisor module – good
  separation, but it depends on vector stores and on the client layer.
