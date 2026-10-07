# Spring AI 2.1.0-M1 - packages (prefix org.springframework.ai. omitted)

package | #classes | sample classes
---|---|---
anthropic | 18 | AnthropicCacheOptions, AnthropicCacheStrategy, AnthropicCacheTtl, AnthropicChatModel, AnthropicChatOptions, AnthropicCitationDocument
anthropic.http.okhttp | 2 | AnthropicHttpClientBuilderCustomizer, SpringAiAnthropicHttpClient
anthropic.metadata | 1 | AnthropicRateLimit
aot | 3 | AiRuntimeHints, SpringAiCoreRuntimeHints, ToolBeanRegistrationAotProcessor
audio.transcription | 8 | AudioTranscription, AudioTranscriptionMetadata, AudioTranscriptionOptions, AudioTranscriptionPrompt, AudioTranscriptionResponse, AudioTranscriptionResponseMetadata
audio.tts | 9 | DefaultTextToSpeechOptions, Speech, StreamingTextToSpeechModel, TextToSpeechMessage, TextToSpeechModel, TextToSpeechOptions
bedrock | 1 | MessageToPromptConverter
bedrock.aot | 1 | BedrockRuntimeHints
bedrock.api | 1 | AbstractBedrockApi
bedrock.cohere | 2 | BedrockCohereEmbeddingModel, BedrockCohereEmbeddingOptions
bedrock.cohere.api | 1 | CohereEmbeddingBedrockApi
bedrock.converse | 4 | BedrockAssistantMessage, BedrockChatOptions, BedrockProxyChatModel, BedrockReasoningContent
bedrock.converse.api | 9 | BedrockCacheOptions, BedrockCacheStrategy, BedrockCacheTtl, BedrockMediaFormat, ConverseApiUtils, ConverseChatResponseStream
bedrock.titan | 2 | BedrockTitanEmbeddingModel, BedrockTitanEmbeddingOptions
bedrock.titan.api | 1 | TitanEmbeddingBedrockApi
chat.cache.semantic | 2 | SemanticCache, SemanticCacheAdvisor
chat.client | 13 | AdvisorParams, ChatClient, ChatClientAttributes, ChatClientBuilderCustomizer, ChatClientCustomizer, ChatClientExtensionsKt
chat.client.advisor | 12 | AdvisorUtils, ChatModelCallAdvisor, ChatModelStreamAdvisor, DefaultAroundAdvisorChain, LastMaxTokenSizeContentPurger, MessageChatMemoryAdvisor
chat.client.advisor.api | 11 | Advisor, AdvisorChain, BaseAdvisor, BaseAdvisorChain, BaseChatMemoryAdvisor, CallAdvisor
chat.client.advisor.observation | 4 | AdvisorObservationContext, AdvisorObservationConvention, AdvisorObservationDocumentation, DefaultAdvisorObservationConvention
chat.client.advisor.toolsearch | 1 | ToolSearchToolCallingAdvisor
chat.client.advisor.toolsearch.autoconfigure | 2 | ToolSearchAdvisorAutoConfiguration, ToolSearchAdvisorProperties
chat.client.advisor.vectorstore | 2 | QuestionAnswerAdvisor, VectorStoreChatMemoryAdvisor
chat.client.observation | 6 | ChatClientCompletionObservationHandler, ChatClientObservationContext, ChatClientObservationConvention, ChatClientObservationDocumentation, ChatClientPromptContentObservationHandler, DefaultChatClientObservationConvention
chat.evaluation | 2 | FactCheckingEvaluator, RelevancyEvaluator
chat.memory | 4 | ChatMemory, ChatMemoryRepository, InMemoryChatMemoryRepository, MessageWindowChatMemory
chat.memory.repository.cassandra | 3 | CassandraChatMemoryRepository, CassandraChatMemoryRepositoryConfig, SchemaUtil
chat.memory.repository.jdbc | 9 | H2ChatMemoryRepositoryDialect, HsqldbChatMemoryRepositoryDialect, JdbcChatMemoryRepository, JdbcChatMemoryRepositoryDialect, MysqlChatMemoryRepositoryDialect, OracleChatMemoryRepositoryDialect
chat.memory.repository.mongo | 2 | Conversation, MongoChatMemoryRepository
chat.memory.repository.neo4j | 7 | AttributeGetter, MediaAttributes, MessageAttributes, Neo4jChatMemoryRepository, Neo4jChatMemoryRepositoryConfig, ToolCallAttributes
chat.memory.repository.redis | 3 | AdvancedRedisChatMemoryRepository, RedisChatMemoryConfig, RedisChatMemoryRepository
chat.messages | 8 | AbstractMessage, AssistantMessage, Message, MessageType, MessageUtils, SystemMessage
chat.messages.part | 9 | MediaPart, MessagePart, OpaquePayload, ReasoningPart, StreamingParts, TextPart
chat.metadata | 10 | ChatGenerationMetadata, ChatResponseMetadata, DefaultChatGenerationMetadata, DefaultChatGenerationMetadataBuilder, DefaultUsage, EmptyRateLimit
chat.model | 6 | ChatModel, ChatResponse, Generation, MessageAggregator, StreamingChatModel, ToolContext
chat.observation | 7 | ChatModelCompletionObservationHandler, ChatModelMeterObservationHandler, ChatModelObservationContext, ChatModelObservationConvention, ChatModelObservationDocumentation, ChatModelPromptContentObservationHandler
chat.prompt | 12 | AssistantPromptTemplate, ChatOptions, ChatPromptTemplate, DefaultChatOptions, DefaultChatOptionsBuilder, Prompt
chroma.vectorstore | 3 | ChromaApi, ChromaFilterExpressionConverter, ChromaVectorStore
content | 3 | Content, Media, MediaContent
converter | 12 | AbstractConversionServiceOutputConverter, AbstractMessageOutputConverter, BeanOutputConverter, CompositeResponseTextCleaner, FormatProvider, ListOutputConverter
deepseek | 3 | DeepSeekAssistantMessage, DeepSeekChatModel, DeepSeekChatOptions
deepseek.aot | 1 | DeepSeekRuntimeHints
deepseek.api | 3 | DeepSeekApi, DeepSeekStreamFunctionCallingHelper, ResponseFormat
deepseek.api.common | 1 | DeepSeekConstants
docker.compose.service.connection.chroma | 2 | ChromaDockerComposeConnectionDetailsFactory, ChromaEnvironment
docker.compose.service.connection.docker | 1 | DockerMcpGatewayDockerComposeConnectionDetailsFactory
docker.compose.service.connection.milvus | 1 | MilvusDockerComposeConnectionDetailsFactory
docker.compose.service.connection.ollama | 1 | OllamaDockerComposeConnectionDetailsFactory
docker.compose.service.connection.opensearch | 4 | AwsOpenSearchDockerComposeConnectionDetailsFactory, AwsOpenSearchEnvironment, OpenSearchDockerComposeConnectionDetailsFactory, OpenSearchEnvironment
docker.compose.service.connection.qdrant | 2 | QdrantDockerComposeConnectionDetailsFactory, QdrantEnvironment
docker.compose.service.connection.typesense | 2 | TypesenseDockerComposeConnectionDetailsFactory, TypesenseEnvironment
docker.compose.service.connection.weaviate | 1 | WeaviateDockerComposeConnectionDetailsFactory
document | 8 | ContentFormatter, DefaultContentFormatter, Document, DocumentMetadata, DocumentReader, DocumentTransformer
document.id | 3 | IdGenerator, JdkSha256HexIdGenerator, RandomIdGenerator
elevenlabs | 2 | ElevenLabsTextToSpeechModel, ElevenLabsTextToSpeechOptions
elevenlabs.aot | 1 | ElevenLabsRuntimeHints
elevenlabs.api | 2 | ElevenLabsApi, ElevenLabsVoicesApi
embedding | 14 | AbstractEmbeddingModel, BatchingStrategy, DefaultEmbeddingOptions, DefaultEmbeddingOptionsBuilder, DocumentEmbeddingModel, DocumentEmbeddingRequest
embedding.observation | 5 | DefaultEmbeddingModelObservationConvention, EmbeddingModelMeterObservationHandler, EmbeddingModelObservationContext, EmbeddingModelObservationConvention, EmbeddingModelObservationDocumentation
evaluation | 3 | EvaluationRequest, EvaluationResponse, Evaluator
google.genai | 3 | GoogleGenAiChatModel, GoogleGenAiChatOptions, MimeTypeDetector
google.genai.aot | 1 | GoogleGenAiRuntimeHints
google.genai.cache | 4 | CachedContentRequest, CachedContentUpdateRequest, GoogleGenAiCachedContent, GoogleGenAiCachedContentService
google.genai.common | 4 | GoogleGenAiConstants, GoogleGenAiSafetySetting, GoogleGenAiServiceTier, GoogleGenAiThinkingLevel
google.genai.embedding | 1 | GoogleGenAiEmbeddingConnectionDetails
google.genai.image | 5 | GoogleGenAiImageConnectionDetails, GoogleGenAiImageGenerationMetadata, GoogleGenAiImageModel, GoogleGenAiImageModelName, GoogleGenAiImageOptions
google.genai.metadata | 3 | GoogleGenAiModalityTokenCount, GoogleGenAiTrafficType, GoogleGenAiUsage
google.genai.schema | 2 | GoogleGenAiToolCallingManager, JsonSchemaConverter
google.genai.text | 3 | GoogleGenAiTextEmbeddingModel, GoogleGenAiTextEmbeddingModelName, GoogleGenAiTextEmbeddingOptions
image | 10 | Image, ImageGeneration, ImageGenerationMetadata, ImageMessage, ImageModel, ImageOptions
image.observation | 5 | DefaultImageModelObservationConvention, ImageModelObservationContext, ImageModelObservationConvention, ImageModelObservationDocumentation, ImageModelPromptContentObservationHandler
mcp | 11 | AsyncMcpToolCallback, AsyncMcpToolCallbackProvider, DefaultMcpToolNamePrefixGenerator, McpConnectionInfo, McpToolFilter, McpToolNamePrefixGenerator
mcp.annotation | 14 | McpArg, McpComplete, McpElicitation, McpLogging, McpMeta, McpProgress
mcp.annotation.adapter | 3 | CompleteAdapter, PromptAdapter, ResourceAdapter
mcp.annotation.common | 3 | ErrorUtils, McpPredicates, MetaUtils
mcp.annotation.context | 12 | DefaultElicitationSpec, DefaultLoggingSpec, DefaultMcpAsyncRequestContext, DefaultMcpSyncRequestContext, DefaultMetaProvider, DefaultProgressSpec
mcp.annotation.method.changed.prompt | 5 | AbstractMcpPromptListChangedMethodCallback, AsyncMcpPromptListChangedMethodCallback, AsyncPromptListChangedSpecification, SyncMcpPromptListChangedMethodCallback, SyncPromptListChangedSpecification
mcp.annotation.method.changed.resource | 5 | AbstractMcpResourceListChangedMethodCallback, AsyncMcpResourceListChangedMethodCallback, AsyncResourceListChangedSpecification, SyncMcpResourceListChangedMethodCallback, SyncResourceListChangedSpecification
mcp.annotation.method.changed.tool | 5 | AbstractMcpToolListChangedMethodCallback, AsyncMcpToolListChangedMethodCallback, AsyncToolListChangedSpecification, SyncMcpToolListChangedMethodCallback, SyncToolListChangedSpecification
mcp.annotation.method.complete | 5 | AbstractMcpCompleteMethodCallback, AsyncMcpCompleteMethodCallback, AsyncStatelessMcpCompleteMethodCallback, SyncMcpCompleteMethodCallback, SyncStatelessMcpCompleteMethodCallback
mcp.annotation.method.elicitation | 5 | AbstractMcpElicitationMethodCallback, AsyncElicitationSpecification, AsyncMcpElicitationMethodCallback, SyncElicitationSpecification, SyncMcpElicitationMethodCallback
mcp.annotation.method.logging | 5 | AbstractMcpLoggingMethodCallback, AsyncLoggingSpecification, AsyncMcpLoggingMethodCallback, SyncLoggingSpecification, SyncMcpLoggingMethodCallback
mcp.annotation.method.progress | 5 | AbstractMcpProgressMethodCallback, AsyncMcpProgressMethodCallback, AsyncProgressSpecification, SyncMcpProgressMethodCallback, SyncProgressSpecification
mcp.annotation.method.prompt | 5 | AbstractMcpPromptMethodCallback, AsyncMcpPromptMethodCallback, AsyncStatelessMcpPromptMethodCallback, SyncMcpPromptMethodCallback, SyncStatelessMcpPromptMethodCallback
mcp.annotation.method.resource | 7 | AbstractMcpResourceMethodCallback, AsyncMcpResourceMethodCallback, AsyncStatelessMcpResourceMethodCallback, DefaultMcpReadResourceResultConverter, McpReadResourceResultConverter, SyncMcpResourceMethodCallback
mcp.annotation.method.sampling | 5 | AbstractMcpSamplingMethodCallback, AsyncMcpSamplingMethodCallback, AsyncSamplingSpecification, SyncMcpSamplingMethodCallback, SyncSamplingSpecification
mcp.annotation.method.tool | 9 | AbstractAsyncMcpToolMethodCallback, AbstractMcpToolMethodCallback, AbstractSyncMcpToolMethodCallback, AsyncMcpToolMethodCallback, AsyncStatelessMcpToolMethodCallback, ReactiveUtils
mcp.annotation.method.tool.utils | 2 | McpJsonSchemaGenerator, McpSpringAiSchemaModule
mcp.annotation.provider.changed.prompt | 2 | AsyncMcpPromptListChangedProvider, SyncMcpPromptListChangedProvider
mcp.annotation.provider.changed.resource | 2 | AsyncMcpResourceListChangedProvider, SyncMcpResourceListChangedProvider
mcp.annotation.provider.changed.tool | 2 | AsyncMcpToolListChangedProvider, SyncMcpToolListChangedProvider
mcp.annotation.provider.complete | 4 | AsyncMcpCompleteProvider, AsyncStatelessMcpCompleteProvider, SyncMcpCompleteProvider, SyncStatelessMcpCompleteProvider
mcp.annotation.provider.elicitation | 2 | AsyncMcpElicitationProvider, SyncMcpElicitationProvider
mcp.annotation.provider.logging | 3 | AsyncMcpLoggingProvider, SyncMcpLogginProvider, SyncMcpLoggingProvider
mcp.annotation.provider.progress | 2 | AsyncMcpProgressProvider, SyncMcpProgressProvider
mcp.annotation.provider.prompt | 4 | AsyncMcpPromptProvider, AsyncStatelessMcpPromptProvider, SyncMcpPromptProvider, SyncStatelessMcpPromptProvider
mcp.annotation.provider.resource | 4 | AsyncMcpResourceProvider, AsyncStatelessMcpResourceProvider, SyncMcpResourceProvider, SyncStatelessMcpResourceProvider
mcp.annotation.provider.sampling | 2 | AsyncMcpSamplingProvider, SyncMcpSamplingProvider
mcp.annotation.provider.tool | 5 | AbstractMcpToolProvider, AsyncMcpToolProvider, AsyncStatelessMcpToolProvider, SyncMcpToolProvider, SyncStatelessMcpToolProvider
mcp.annotation.spring | 6 | AbstractClientMcpHandlerRegistry, AnnotationProviderUtil, AsyncMcpAnnotationProviders, ClientMcpAsyncHandlersRegistry, ClientMcpSyncHandlersRegistry, SyncMcpAnnotationProviders
mcp.annotation.spring.scan | 4 | AbstractAnnotatedMethodBeanFactoryInitializationAotProcessor, AbstractAnnotatedMethodBeanPostProcessor, AbstractMcpAnnotatedBeans, AnnotatedMethodDiscovery
mcp.aot | 1 | McpHints
mcp.client.common.autoconfigure | 8 | McpAsyncToolsChangeEventEmmiter, McpClientAutoConfiguration, McpSseClientConnectionDetails, McpSyncToolsChangeEventEmmiter, McpToolCallbackAutoConfiguration, NamedClientMcpTransport
mcp.client.common.autoconfigure.annotations | 2 | McpClientAnnotationScannerAutoConfiguration, McpClientAnnotationScannerProperties
mcp.client.common.autoconfigure.aot | 1 | McpClientAutoConfigurationRuntimeHints
mcp.client.common.autoconfigure.configurer | 2 | McpAsyncClientConfigurer, McpSyncClientConfigurer
mcp.client.common.autoconfigure.properties | 4 | McpClientCommonProperties, McpSseClientProperties, McpStdioClientProperties, McpStreamableHttpClientProperties
mcp.client.httpclient.autoconfigure | 2 | SseHttpClientTransportAutoConfiguration, StreamableHttpHttpClientTransportAutoConfiguration
mcp.client.httpclient.autoconfigure.aot | 1 | McpClientAutoConfigurationRuntimeHints
mcp.client.webflux.autoconfigure | 2 | SseWebFluxTransportAutoConfiguration, StreamableHttpWebFluxTransportAutoConfiguration
mcp.client.webflux.autoconfigure.aot | 1 | McpClientAutoConfigurationRuntimeHints
mcp.client.webflux.transport | 2 | WebClientStreamableHttpTransport, WebFluxSseClientTransport
mcp.customizer | 5 | McpAsyncServerCustomizer, McpClientCustomizer, McpStatelessAsyncServerCustomizer, McpStatelessSyncServerCustomizer, McpSyncServerCustomizer
mcp.server.common.autoconfigure | 6 | McpServerAutoConfiguration, McpServerJsonMapperAutoConfiguration, McpServerStatelessAutoConfiguration, StatelessToolCallbackConverterAutoConfiguration, ToolCallbackConverterAutoConfiguration, ToolCallbackUtils
mcp.server.common.autoconfigure.annotations | 4 | McpServerAnnotationScannerAutoConfiguration, McpServerAnnotationScannerProperties, McpServerSpecificationFactoryAutoConfiguration, StatelessServerSpecificationFactoryAutoConfiguration
mcp.server.common.autoconfigure.properties | 4 | McpServerChangeNotificationProperties, McpServerProperties, McpServerSseProperties, McpServerStreamableHttpProperties
mcp.server.webflux.autoconfigure | 3 | McpServerSseWebFluxAutoConfiguration, McpServerStatelessWebFluxAutoConfiguration, McpServerStreamableHttpWebFluxAutoConfiguration
mcp.server.webflux.transport | 4 | HeaderUtils, WebFluxSseServerTransportProvider, WebFluxStatelessServerTransport, WebFluxStreamableServerTransportProvider
mcp.server.webmvc.autoconfigure | 3 | McpServerSseWebMvcAutoConfiguration, McpServerStatelessWebMvcAutoConfiguration, McpServerStreamableHttpWebMvcAutoConfiguration
mcp.server.webmvc.transport | 4 | HeaderUtils, WebMvcSseServerTransportProvider, WebMvcStatelessServerTransport, WebMvcStreamableServerTransportProvider
mistralai | 4 | MistralAiChatModel, MistralAiChatOptions, MistralAiEmbeddingModel, MistralAiEmbeddingOptions
mistralai.aot | 1 | MistralAiRuntimeHints
mistralai.api | 3 | MistralAiApi, MistralAiModerationApi, MistralAiStreamFunctionCallingHelper
mistralai.moderation | 2 | MistralAiModerationModel, MistralAiModerationOptions
mistralai.ocr | 2 | MistralAiOcrOptions, MistralOcrApi
model | 19 | AbstractResponseMetadata, ApiKey, ChatModelDescription, EmbeddingModelDescription, EmbeddingUtils, KotlinModule
model.anthropic.autoconfigure | 4 | AnthropicCacheProperties, AnthropicChatAutoConfiguration, AnthropicChatProperties, AnthropicConnectionProperties
model.bedrock.autoconfigure | 3 | BedrockAwsConnectionConfiguration, BedrockAwsConnectionProperties, ProfileProperties
model.bedrock.cohere.autoconfigure | 2 | BedrockCohereEmbeddingAutoConfiguration, BedrockCohereEmbeddingProperties
model.bedrock.converse.autoconfigure | 3 | BedrockCacheProperties, BedrockConverseProxyChatAutoConfiguration, BedrockConverseProxyChatProperties
model.bedrock.titan.autoconfigure | 2 | BedrockTitanEmbeddingAutoConfiguration, BedrockTitanEmbeddingProperties
model.chat.client.autoconfigure | 3 | ChatClientAutoConfiguration, ChatClientBuilderConfigurer, ChatClientBuilderProperties
model.chat.memory.autoconfigure | 1 | ChatMemoryAutoConfiguration
model.chat.memory.redis.autoconfigure | 2 | RedisChatMemoryAutoConfiguration, RedisChatMemoryProperties
model.chat.memory.repository.cassandra.autoconfigure | 2 | CassandraChatMemoryRepositoryAutoConfiguration, CassandraChatMemoryRepositoryProperties
model.chat.memory.repository.jdbc.autoconfigure | 3 | JdbcChatMemoryRepositoryAutoConfiguration, JdbcChatMemoryRepositoryProperties, JdbcChatMemoryRepositorySchemaInitializer
model.chat.memory.repository.mongo.autoconfigure | 3 | MongoChatMemoryAutoConfiguration, MongoChatMemoryIndexCreatorAutoConfiguration, MongoChatMemoryProperties
model.chat.memory.repository.neo4j.autoconfigure | 2 | Neo4jChatMemoryRepositoryAutoConfiguration, Neo4jChatMemoryRepositoryProperties
model.chat.memory.repository.redis.autoconfigure | 2 | RedisChatMemoryRepositoryAutoConfiguration, RedisChatMemoryRepositoryProperties
model.chat.observation.autoconfigure | 2 | ChatObservationAutoConfiguration, ChatObservationProperties
model.deepseek.autoconfigure | 4 | DeepSeekChatAutoConfiguration, DeepSeekChatProperties, DeepSeekConnectionProperties, DeepSeekParentProperties
model.elevenlabs.autoconfigure | 3 | ElevenLabsAutoConfiguration, ElevenLabsConnectionProperties, ElevenLabsSpeechProperties
model.embedding.observation.autoconfigure | 1 | EmbeddingObservationAutoConfiguration
model.google.genai.autoconfigure.chat | 4 | CachedContentServiceCondition, GoogleGenAiChatAutoConfiguration, GoogleGenAiChatProperties, GoogleGenAiConnectionProperties
model.google.genai.autoconfigure.embedding | 4 | GoogleGenAiEmbeddingConnectionAutoConfiguration, GoogleGenAiEmbeddingConnectionProperties, GoogleGenAiTextEmbeddingAutoConfiguration, GoogleGenAiTextEmbeddingProperties
model.google.genai.autoconfigure.image | 4 | GoogleGenAiImageAutoConfiguration, GoogleGenAiImageConnectionAutoConfiguration, GoogleGenAiImageConnectionProperties, GoogleGenAiImageProperties
model.image.observation.autoconfigure | 2 | ImageObservationAutoConfiguration, ImageObservationProperties
model.mistralai.autoconfigure | 10 | MistralAiChatAutoConfiguration, MistralAiChatProperties, MistralAiCommonProperties, MistralAiEmbeddingAutoConfiguration, MistralAiEmbeddingProperties, MistralAiModerationAutoConfiguration
model.observation | 3 | ErrorLoggingObservationHandler, ModelObservationContext, ModelUsageMetricsGenerator
model.ollama.autoconfigure | 9 | OllamaApiAutoConfiguration, OllamaChatAutoConfiguration, OllamaChatProperties, OllamaConnectionDetails, OllamaConnectionProperties, OllamaEmbeddingAutoConfiguration
model.openai.autoconfigure | 17 | AbstractOpenAiProperties, OpenAiAudioSpeechAutoConfiguration, OpenAiAudioSpeechProperties, OpenAiAudioTranscriptionAutoConfiguration, OpenAiAudioTranscriptionProperties, OpenAiAutoConfigurationUtil
model.postgresml.autoconfigure | 2 | PostgresMlEmbeddingAutoConfiguration, PostgresMlEmbeddingProperties
model.stabilityai.autoconfigure | 4 | StabilityAiConnectionProperties, StabilityAiImageAutoConfiguration, StabilityAiImageProperties, StabilityAiParentProperties
model.tool | 12 | DefaultStructuredOutputChatOptions, DefaultToolCallingChatOptions, DefaultToolCallingManager, DefaultToolExecutionResult, StructuredOutputChatOptions, ToolCallLimitBehavior
model.tool.autoconfigure | 2 | ToolCallingAutoConfiguration, ToolCallingProperties
model.tool.internal | 1 | ToolCallReactiveContextHolder
model.transformer | 2 | KeywordMetadataEnricher, SummaryMetadataEnricher
model.transformers.autoconfigure | 2 | TransformersEmbeddingModelAutoConfiguration, TransformersEmbeddingModelProperties
model.vertexai.autoconfigure.embedding | 6 | VertexAiEmbeddingConnectionAutoConfiguration, VertexAiEmbeddingConnectionProperties, VertexAiMultiModalEmbeddingAutoConfiguration, VertexAiMultimodalEmbeddingProperties, VertexAiTextEmbeddingAutoConfiguration, VertexAiTextEmbeddingProperties
moderation | 13 | Categories, CategoryScores, Generation, Moderation, ModerationGenerationMetadata, ModerationMessage
observation | 3 | AiOperationMetadata, ObservabilityHelper, TracingAwareLoggingObservationHandler
observation.conventions | 10 | AiObservationAttributes, AiObservationMetricAttributes, AiObservationMetricNames, AiOperationType, AiProvider, AiTokenType
ollama | 2 | OllamaChatModel, OllamaEmbeddingModel
ollama.aot | 1 | OllamaRuntimeHints
ollama.api | 6 | OllamaApi, OllamaApiHelper, OllamaChatOptions, OllamaEmbeddingOptions, OllamaModel, ThinkOption
ollama.api.common | 1 | OllamaApiConstants
ollama.management | 3 | ModelManagementOptions, OllamaModelManager, PullModelStrategy
openai | 14 | AbstractOpenAiOptions, DiarizedJsonMisclassificationRecovery, OpenAiAudioSpeechModel, OpenAiAudioSpeechOptions, OpenAiAudioTranscriptionModel, OpenAiAudioTranscriptionOptions
openai.http.okhttp | 2 | OpenAiHttpClientBuilderCustomizer, SpringAiOpenAiHttpClient
openai.metadata | 5 | OpenAiAudioSpeechResponseMetadata, OpenAiAudioTranscriptionResponseMetadata, OpenAiImageGenerationMetadata, OpenAiImageResponseMetadata, OpenAiRateLimit
openai.responses | 7 | HostedTool, OpenAiResponsesChatModel, OpenAiResponsesChatOptions, OpenAiResponsesException, ResponsesItemMapper, ResponsesRequestBuilder
openai.setup | 2 | AzureInternalOpenAiHelper, OpenAiSetup
postgresml | 2 | PostgresMlEmbeddingModel, PostgresMlEmbeddingOptions
rag | 1 | Query
rag.advisor | 1 | RetrievalAugmentationAdvisor
rag.generation.augmentation | 2 | ContextualQueryAugmenter, QueryAugmenter
rag.postretrieval.document | 1 | DocumentPostProcessor
rag.preretrieval.query.expansion | 2 | MultiQueryExpander, QueryExpander
rag.preretrieval.query.transformation | 4 | CompressionQueryTransformer, QueryTransformer, RewriteQueryTransformer, TranslationQueryTransformer
rag.retrieval.join | 2 | ConcatenationDocumentJoiner, DocumentJoiner
rag.retrieval.search | 2 | DocumentRetriever, VectorStoreDocumentRetriever
rag.util | 1 | PromptAssert
reader | 5 | EmptyJsonMetadataGenerator, ExtractedTextFormatter, JsonMetadataGenerator, JsonReader, TextReader
reader.jsoup | 1 | JsoupDocumentReader
reader.jsoup.config | 1 | JsoupDocumentReaderConfig
reader.markdown | 1 | MarkdownDocumentReader
reader.markdown.config | 1 | MarkdownDocumentReaderConfig
reader.pdf | 2 | PagePdfDocumentReader, ParagraphPdfDocumentReader
reader.pdf.config | 2 | ParagraphManager, PdfDocumentReaderConfig
reader.pdf.layout | 5 | Character, CharacterFactory, ForkPDFLayoutTextStripper, PDFLayoutTextStripperByArea, TextLine
reader.tika | 1 | TikaDocumentReader
retry | 3 | NonTransientAiException, RetryUtils, TransientAiException
retry.autoconfigure | 2 | SpringAiRetryAutoConfiguration, SpringAiRetryProperties
stabilityai | 3 | StabilityAiImageGenerationMetadata, StabilityAiImageModel, StyleEnum
stabilityai.api | 2 | StabilityAiApi, StabilityAiImageOptions
support | 2 | ToolCallbacks, UsageCalculator
template | 3 | NoOpTemplateRenderer, TemplateRenderer, ValidationMode
template.st | 2 | CommonsLoggingStErrorListener, StTemplateRenderer
testcontainers.service.connection.chroma | 1 | ChromaContainerConnectionDetailsFactory
testcontainers.service.connection.docker | 1 | DockerMcpGatewayContainerConnectionDetailsFactory
testcontainers.service.connection.milvus | 1 | MilvusContainerConnectionDetailsFactory
testcontainers.service.connection.ollama | 1 | OllamaContainerConnectionDetailsFactory
testcontainers.service.connection.opensearch | 2 | AwsOpenSearchContainerConnectionDetailsFactory, OpenSearchContainerConnectionDetailsFactory
testcontainers.service.connection.qdrant | 1 | QdrantContainerConnectionDetailsFactory
testcontainers.service.connection.typesense | 1 | TypesenseContainerConnectionDetailsFactory
testcontainers.service.connection.weaviate | 1 | WeaviateContainerConnectionDetailsFactory
tokenizer | 2 | JTokkitTokenCountEstimator, TokenCountEstimator
tool | 3 | StaticToolCallbackProvider, ToolCallback, ToolCallbackProvider
tool.annotation | 2 | Tool, ToolParam
tool.augment | 4 | AugmentedArgumentEvent, AugmentedToolCallback, AugmentedToolCallbackProvider, ToolInputSchemaAugmenter
tool.definition | 2 | DefaultToolDefinition, ToolDefinition
tool.execution | 5 | DefaultToolCallResultConverter, DefaultToolExecutionExceptionProcessor, ToolCallResultConverter, ToolExecutionException, ToolExecutionExceptionProcessor
tool.function | 1 | FunctionToolCallback
tool.metadata | 2 | DefaultToolMetadata, ToolMetadata
tool.method | 2 | MethodToolCallback, MethodToolCallbackProvider
tool.observation | 5 | DefaultToolCallingObservationConvention, ToolCallingContentObservationFilter, ToolCallingObservationContext, ToolCallingObservationConvention, ToolCallingObservationDocumentation
tool.resolution | 4 | DelegatingToolCallbackResolver, StaticToolCallbackResolver, ToolCallbackResolver, TypeResolverHelper
tool.support | 2 | ToolDefinitions, ToolUtils
tool.toolsearch | 5 | ToolIndex, ToolReference, ToolSearchRequest, ToolSearchResponse, ToolSearchTool
tool.toolsearch.eviction | 6 | AlwaysEvictStrategy, CompositeEvictionStrategy, LruEvictionStrategy, NeverEvictStrategy, ToolIndexEvictionStrategy, TtlEvictionStrategy
tool.toolsearch.index.lucene | 1 | LuceneToolIndex
tool.toolsearch.index.regex | 1 | RegexToolIndex
tool.toolsearch.index.vectorstore | 1 | VectorToolIndex
transformer | 1 | ContentFormatTransformer
transformer.splitter | 2 | TextSplitter, TokenTextSplitter
transformers | 2 | ResourceCacheService, TransformersEmbeddingModel
util | 3 | JacksonUtils, JsonHelper, ParsingUtils
util.json | 1 | JsonParser
util.json.schema | 5 | AbstractSpringAiSchemaModule, JsonSchemaGenerator, JsonSchemaUtils, SchemaType, SpringAiSchemaModule
vectorstore | 8 | AbstractVectorStoreBuilder, EmbeddedDocument, SearchRequest, SimpleVectorStore, SimpleVectorStoreContent, SimpleVectorStoreFilterExpressionEvaluator
vectorstore.azure | 2 | AzureAiSearchFilterExpressionConverter, AzureVectorStore
vectorstore.azure.autoconfigure | 2 | AzureVectorStoreAutoConfiguration, AzureVectorStoreProperties
vectorstore.bedrockknowledgebase | 2 | BedrockKnowledgeBaseFilterExpressionConverter, BedrockKnowledgeBaseVectorStore
vectorstore.bedrockknowledgebase.autoconfigure | 2 | BedrockKnowledgeBaseVectorStoreAutoConfiguration, BedrockKnowledgeBaseVectorStoreProperties
vectorstore.cassandra | 3 | CassandraFilterExpressionConverter, CassandraVectorStore, SchemaUtil
vectorstore.cassandra.autoconfigure | 2 | CassandraVectorStoreAutoConfiguration, CassandraVectorStoreProperties
vectorstore.chroma.autoconfigure | 4 | ChromaApiProperties, ChromaConnectionDetails, ChromaVectorStoreAutoConfiguration, ChromaVectorStoreProperties
vectorstore.coherence | 2 | CoherenceFilterExpressionConverter, CoherenceVectorStore
vectorstore.couchbase | 4 | CouchbaseAiSearchFilterExpressionConverter, CouchbaseIndexOptimization, CouchbaseSearchVectorStore, CouchbaseSimilarityFunction
vectorstore.couchbase.autoconfigure | 2 | CouchbaseSearchVectorStoreAutoConfiguration, CouchbaseSearchVectorStoreProperties
vectorstore.elasticsearch | 4 | ElasticsearchAiSearchFilterExpressionConverter, ElasticsearchVectorStore, ElasticsearchVectorStoreOptions, SimilarityFunction
vectorstore.elasticsearch.autoconfigure | 2 | ElasticsearchVectorStoreAutoConfiguration, ElasticsearchVectorStoreProperties
vectorstore.filter | 5 | Filter, FilterExpressionBuilder, FilterExpressionConverter, FilterExpressionTextParser, FilterHelper
vectorstore.filter.antlr4 | 6 | FiltersBaseListener, FiltersBaseVisitor, FiltersLexer, FiltersListener, FiltersParser, FiltersVisitor
vectorstore.filter.converter | 3 | AbstractFilterExpressionConverter, PineconeFilterExpressionConverter, PrintFilterExpressionConverter
vectorstore.gemfire | 3 | BearerTokenAuthenticationFilterFunction, GemFireAiSearchFilterExpressionConverter, GemFireVectorStore
vectorstore.gemfire.autoconfigure | 3 | GemFireConnectionDetails, GemFireVectorStoreAutoConfiguration, GemFireVectorStoreProperties
vectorstore.mariadb | 3 | MariaDBFilterExpressionConverter, MariaDBSchemaValidator, MariaDBVectorStore
vectorstore.mariadb.autoconfigure | 2 | MariaDbStoreAutoConfiguration, MariaDbStoreProperties
vectorstore.milvus | 3 | MilvusFilterExpressionConverter, MilvusSearchRequest, MilvusVectorStore
vectorstore.milvus.autoconfigure | 4 | MilvusServiceClientConnectionDetails, MilvusServiceClientProperties, MilvusVectorStoreAutoConfiguration, MilvusVectorStoreProperties
vectorstore.mongodb.atlas | 3 | MongoDBAtlasFilterExpressionConverter, MongoDBAtlasVectorStore, VectorSearchAggregation
vectorstore.mongodb.autoconfigure | 2 | MongoDBAtlasVectorStoreAutoConfiguration, MongoDBAtlasVectorStoreProperties
vectorstore.neo4j | 1 | Neo4jVectorStore
vectorstore.neo4j.autoconfigure | 2 | Neo4jVectorStoreAutoConfiguration, Neo4jVectorStoreProperties
vectorstore.neo4j.filter | 1 | Neo4jVectorFilterExpressionConverter
vectorstore.observation | 6 | AbstractObservationVectorStore, DefaultVectorStoreObservationConvention, VectorStoreObservationContext, VectorStoreObservationConvention, VectorStoreObservationDocumentation, VectorStoreQueryResponseObservationHandler
vectorstore.observation.autoconfigure | 2 | VectorStoreObservationAutoConfiguration, VectorStoreObservationProperties
vectorstore.opensearch | 2 | OpenSearchAiSearchFilterExpressionConverter, OpenSearchVectorStore
vectorstore.opensearch.autoconfigure | 5 | AwsOpenSearchConnectionDetails, OpenSearchConnectionDetails, OpenSearchNonAwsCondition, OpenSearchVectorStoreAutoConfiguration, OpenSearchVectorStoreProperties
vectorstore.oracle | 2 | OracleVectorStore, SqlJsonPathFilterExpressionConverter
vectorstore.oracle.autoconfigure | 2 | OracleVectorStoreAutoConfiguration, OracleVectorStoreProperties
vectorstore.pgvector | 3 | PgVectorFilterExpressionConverter, PgVectorSchemaValidator, PgVectorStore
vectorstore.pgvector.autoconfigure | 2 | PgVectorStoreAutoConfiguration, PgVectorStoreProperties
vectorstore.pinecone | 1 | PineconeVectorStore
vectorstore.pinecone.autoconfigure | 2 | PineconeVectorStoreAutoConfiguration, PineconeVectorStoreProperties
vectorstore.properties | 1 | CommonVectorStoreProperties
vectorstore.qdrant | 4 | QdrantFilterExpressionConverter, QdrantObjectFactory, QdrantValueFactory, QdrantVectorStore
vectorstore.qdrant.autoconfigure | 3 | QdrantConnectionDetails, QdrantVectorStoreAutoConfiguration, QdrantVectorStoreProperties
vectorstore.redis | 2 | RedisFilterExpressionConverter, RedisVectorStore
vectorstore.redis.autoconfigure | 2 | RedisVectorStoreAutoConfiguration, RedisVectorStoreProperties
vectorstore.redis.cache.semantic | 2 | DefaultSemanticCache, RedisVectorStoreHelper
vectorstore.redis.cache.semantic.autoconfigure | 2 | RedisSemanticCacheAutoConfiguration, RedisSemanticCacheProperties
vectorstore.s3 | 5 | DocumentUtils, S3VectorFilterExpressionConverter, S3VectorFilterSearchExpressionConverter, S3VectorStore, S3VectorStoreFilterExpressionEvaluator
vectorstore.s3.autoconfigure | 2 | S3VectorStoreAutoConfiguration, S3VectorStoreProperties
vectorstore.typesense | 2 | TypesenseFilterExpressionConverter, TypesenseVectorStore
vectorstore.typesense.autoconfigure | 4 | TypesenseConnectionDetails, TypesenseServiceClientProperties, TypesenseVectorStoreAutoConfiguration, TypesenseVectorStoreProperties
vectorstore.weaviate | 3 | WeaviateFilterExpressionConverter, WeaviateVectorStore, WeaviateVectorStoreOptions
vectorstore.weaviate.autoconfigure | 3 | WeaviateConnectionDetails, WeaviateVectorStoreAutoConfiguration, WeaviateVectorStoreProperties
vertexai.embedding | 2 | VertexAiEmbeddingConnectionDetails, VertexAiEmbeddingUtils
vertexai.embedding.multimodal | 3 | VertexAiMultimodalEmbeddingModel, VertexAiMultimodalEmbeddingModelName, VertexAiMultimodalEmbeddingOptions
vertexai.embedding.text | 3 | VertexAiTextEmbeddingModel, VertexAiTextEmbeddingModelName, VertexAiTextEmbeddingOptions
writer | 1 | FileDocumentWriter
