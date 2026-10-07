# Phase 1 – System selection: Spring AI

Repository: <https://github.com/spring-projects/spring-ai> (Apache-2.0)

Spring AI is the Spring ecosystem's application framework for AI engineering. It
offers portable, provider-independent APIs (`ChatModel`, `EmbeddingModel`,
`ImageModel`, `AudioModel`, `ModerationModel`), a fluent `ChatClient`,
structured output conversion, tool/function calling, chat memory, an advisor
(interceptor) chain, Retrieval-Augmented Generation (document readers,
transformers/splitters, `VectorStore` abstraction with ~20 back-ends), MCP
(Model Context Protocol) client/server support, observability (Micrometer) and
Spring Boot auto-configuration/starters for ~20 model providers (OpenAI,
Anthropic, Azure OpenAI, Ollama, Bedrock, Vertex AI/Gemini, Mistral, ...).

## Eligibility check (verified on 2026-10-07)

| # | Criterion | Evidence | OK |
|---|-----------|----------|----|
| 1 | ≥ 10 major/minor versions | 48 release tags. Feature lines 0.8, 1.0, 1.1, 2.0, 2.1 plus 22 feature milestones (`-Mx`) that each introduce new API/modules. 25 feature releases are analysed (see below). | ✔ (with milestones, see note) |
| 2 | Repository on GitHub | `spring-projects/spring-ai` | ✔ |
| 3 | Latest version ≥ 10,000 LOC | v2.1.0-M1: 1,341 production `.java` files, 179,743 physical lines, **95,546 non-comment non-blank LOC** (`src/main/java` only) | ✔ |
| 4 | Not archived | Actively developed, last commit 2026-10-07 | ✔ |
| 5 | ≥ 50 commits since 1/1/2024 | **4,007** of 4,249 commits are after 2024-01-01 | ✔ |
| 6 | Not a fork | Original repository of the `spring-projects` organisation | ✔ |
| 7 | Created before 2024 | First commit 2023-07-24 | ✔ |

Commands used (see also `scripts/project_stats.sh`):
`git rev-list --count --since=2024-01-01 HEAD`, `git log --reverse`, and an
NCLOC count over `**/src/main/java/**/*.java` of tag `v2.1.0-M1`.

**Note on criterion 1.** Spring AI follows the Spring release model: every
major/minor line is developed through a series of public *milestones*
(`M1…M8`), which are where all features land, followed by an RC and a GA.
Strictly counting GA lines gives 0.8, 1.0, 1.1, 2.0 (+2.1 in milestones); counting
feature releases (milestones + GA) gives 25. This should be explicitly
confirmed with the instructor in the approval e-mail (draft below).

## Version selection and cleaning

All 48 tags were retrieved (`data/tags.csv`: 4 GA, 21 milestones, 4 RCs, 19 patches) (`git ls-remote --tags`). Cleaning rules:

* **Excluded – patch releases** (`x.y.z`, z > 0: 0.8.1, 1.0.1–1.0.9, 1.1.1–1.1.8,
  2.0.1; 19 tags): bug-fix-only maintenance branches that are released in
  parallel with newer lines and would break the chronological order.
* **Excluded – release candidates** (1.0.0-RC1, 1.1.0-RC1, 2.0.0-RC1, 2.0.0-RC2;
  4 tags): feature-frozen and practically identical to the following GA.
* **Kept – 25 feature releases**: 0.8.0, 1.0.0-M1…M8, 1.0.0, 1.1.0-M1…M4, 1.1.0,
  2.0.0-M1…M8, 2.0.0, 2.1.0-M1 (Feb 2024 – Sep 2026).

## Draft approval e-mail to the instructor

> Subject: EPL484 Project 1 – Team X – system proposal
>
> Dear Dr. Constantinou,
>
> Our team (GitHub usernames: `<member1>`, `<member2>`) would like to propose
> the following systems, in order of preference:
>
> 1. **Spring AI** – https://github.com/spring-projects/spring-ai
>    (created 07/2023, 4,007 commits since 1/2024, ~95K NCLOC, 48 releases; we
>    plan to analyse its 25 feature releases 0.8.0 → 2.1.0-M1 including the
>    public milestones, since all features of a Spring line are delivered in
>    milestones – please let us know if milestones are acceptable as versions)
> 2. `<alternative 2>`
> 3. `<alternative 3>`
>
> We would prefer the team repository to be private.
>
> Kind regards,
> `<names>`
