---
title: "Architecture Evolution of Spring AI"
subtitle: "EPL484 Software Evolution – Project 1 – Team X"
author: "‹Member 1 (ID)›, ‹Member 2 (ID)›"
date: "October 2026"
---

> Code and data: GitHub repository `epl484.fall26.project1.teamX`
> (pipeline in `scripts/`, data in `data/`, all computed results in `results/`).
> Every number in the tables of this report is generated from the result
> files by `scripts/report_tables.py`.

# 1. Project choice and characteristics

## 1.1 What is Spring AI?

[Spring AI](https://github.com/spring-projects/spring-ai) is the Spring
ecosystem's application framework for AI engineering. Its goal is to bring
Spring's principles (portability, modularity, POJOs, dependency injection)
to applications that use generative AI models. It offers:

* **Portable model APIs** for chat, embedding, image generation, audio
  (transcription, text-to-speech) and moderation (`ChatModel`,
  `EmbeddingModel`, `ImageModel`, ...), with synchronous and streaming calls;
* **adapters to ~12 AI providers** (OpenAI, Anthropic, Amazon Bedrock,
  Google GenAI/Vertex AI, Ollama, Mistral AI, DeepSeek, ElevenLabs, Stability AI, ...);
* the fluent **`ChatClient`** API with an **advisor** (interceptor) chain for
  chat memory, RAG, logging and guard-rails;
* **structured output** (LLM text → POJOs), **tool/function calling** and
  **MCP** (Model Context Protocol) client/server support;
* **Retrieval-Augmented Generation**: an ETL pipeline (document readers,
  splitters), a portable **`VectorStore`** API with a SQL-like metadata filter
  language and ~20 vector-database adapters;
* **observability** (Micrometer) and **Spring Boot auto-configuration/starters**
  for everything above.

The project lives in the `spring-projects` GitHub organisation (Apache 2.0).
Its first commit was made on 2023-07-24. It has 4,249 commits, 4,007 of them
after 1/1/2024, and it is very actively developed.

## 1.2 Eligibility (Phase 1)

| Criterion | Spring AI |
|---|---|
| ≥ 10 major/minor versions | 48 tags: 4 GA (0.8.0, 1.0.0, 1.1.0, 2.0.0), 21 feature milestones, 4 RCs, 19 patches. Strictly 5 major.minor lines (0.8, 1.0, 1.1, 2.0, 2.1); **25 feature releases** if milestones are counted (see note) |
| Repository on GitHub | `spring-projects/spring-ai` |
| Latest version ≥ 10K LOC | 2.1.0-M1: 1,341 production `.java` files, **95,546 non-comment, non-blank LOC** |
| Not archived / not a fork | ✔ / ✔ (original repository) |
| ≥ 50 commits since 1/1/2024 | **4,007** |
| Created before 2024 | 2023-07-24 |

*Note on versions.* Spring projects deliver all features of a line through
public **milestones** (M1…M8), followed by a release candidate and a GA. For
example, the 1.0 line grew from 489 to 828 classes during its eight
milestones. We therefore treat milestones as feature releases (agreed with
the instructor in the approval e-mail ‹to be confirmed›).

## 1.3 Number and size of versions

We analyse the **continuous sequence of all 25 feature releases** from 0.8.0
(Feb 2024) to 2.1.0-M1 (Sep 2026), i.e. every milestone and GA with no gaps.
Table 1 gives the size of each version. *Modules* are the Maven modules
that contain code. *Class files* include inner and anonymous classes.
*Top-level classes* are compilation units. *Dependencies* are distinct
class-to-class dependencies between top-level classes.

Table 1 – Size of the analysed versions.

{{TABLE_SIZE}}

## 1.4 Is the architecture documented?

Partly. The [reference documentation](https://docs.spring.io/spring-ai/reference/)
describes the concepts (models, prompts, embeddings, tools, RAG, advisors,
vector stores, MCP) and contains a high-level integration diagram ("connect
your *Data* and *APIs* with the *AI Models*"). The repository has a `design/`
folder with short design records. *Design 02 – Spring Boot Modularity* is
the only document that states an architectural rule: the core must not
depend on Spring Boot, auto-configuration modules depend on the core, and
starters contain no code. The Maven build enforces this rule
(`maven-enforcer-plugin`). There is **no documented component/connector view
and no documented decomposition**. The module structure and the package
naming (`*.autoconfigure`, `vectorstore.<vendor>`, `<provider>.api`) are the
only other architectural evidence.

# 2. Methodology

Figure 1 summarises the pipeline. All steps are scripts in the repository and
can be re-run with the commands in `README.md`.

```
GitHub tags ─► version selection ─► Maven BOM ─► module jars ─► 1 merged jar / version
                                                                  │
                         ┌────────────────────────────────────────┤
                         ▼                                        ▼
            DependencyExtractor.jar                           JNode.jar
            class dependencies (csv)                    noise classes (csv)
                         │                                        │
                         └──────────► top-level class graph ◄─────┘
                                     │                     │
                                full graph           graph without noise
                                │      │               │        │
                             ACDC(A1) k-means(A3)   ACDC(A2) k-means(A4)
                                └──────┴─── metrics ───┴────────┘
                         cohesion · coupling · MQ · MoJoFM · stability
```
*Figure 1 – Analysis pipeline.*

## 2.1 Data collection

1. **Releases.** All 48 tags were listed with `git ls-remote --tags`
   (`data/tags.csv`). Creation dates and the Phase 1 statistics come from a
   blob-less clone (`scripts/project_stats.sh`).
2. **Binaries.** Spring AI is a multi-module Maven project (21 modules in
   0.8.0, 116 in 2.1.0-M1), and its module structure changes often (e.g. the
   1.0.0-M7 split of `spring-ai-core`). To analyse the *whole system*
   consistently, `scripts/collect_versions.py` reads each release's **BOM**
   (`spring-ai-bom`, the official list of the release's artifacts). It
   downloads every listed module jar from Maven Central or, for old
   milestones, from `repo.spring.io/milestone`. It then merges all
   `org/springframework/ai/**.class` files into **one jar per version**
   (`data/workspace/<v>/bin/`). This is the input format of the course tools.

## 2.2 Data cleaning

* **Excluded releases.** 19 *patch* releases (bug fixes on maintenance
  branches, published in parallel with newer lines, e.g. 1.0.9 and 2.0.0 on
  the same day) and 4 *release candidates* (feature-frozen, practically
  identical to the following GA). This left **25 of 48** releases.
* **Excluded artifacts.** *Starters* (no code), `spring-ai-test` (test
  utilities), the BOM and docs. `module-info`/`package-info` classes and
  third-party classes were also dropped. Classes that appear in two modules
  (split packages) were kept once.
* **Inner classes.** DependencyExtractor and JNode work on class files. For
  architecture recovery we fold inner/anonymous classes (`A$B`, `A$1`) into
  their top-level class and drop the resulting self-dependencies. A
  top-level class is noise if any of its class files is flagged by JNode.
* **Isolated classes.** 2–15 classes per version have no dependency to or
  from another Spring AI class. They cannot be clustered from dependencies and
  are left out of A1–A4 (column *Isolated* in Table 3).

## 2.3 Tools and libraries

| Step | Tool / library |
|---|---|
| Class dependencies (3.2) | Course **DependencyExtractor.jar** (bytecode; EXTENDS, IMPLEMENTS, METHOD_CALL, METHOD_PARAMETER, FIELD_REFERENCE, TYPE_USAGE, ...) |
| Noise classes (3.3) | Course **JNode.jar**, with two documented fixes (below) |
| ACDC (A1, A2) | ACDC (Tzerpos & Holt) – Java port from USC **ARCADE** (`tools/acdc/`, BSD licence). The York wiki link was not reachable from our environment |
| Clustering (A3, A4) | **scikit-learn** `KMeans`, `TruncatedSVD`; `kneed` (elbow) |
| Metrics, tables, plots | Python 3.13, numpy, scipy, matplotlib |
| PDF | pandoc + headless Chromium |

**Fixes to JNode.** JNode needed more than 2 hours per 2,000-class version
and broke down on the largest versions. We decompiled it (CFR) and recompiled
three methods; `tools/jnode-patch/` documents the patch:

1. *Performance* – a class-name lookup that scanned the whole class list on
   every step of the subgraph extraction, and a set-membership test written
   as an iteration, were replaced by hash lookups. The output is
   **byte-identical** to the original on 0.8.0, 1.0.0-M1 and 1.0.0-M2. The
   run time dropped from ~9 min to ~1.3 min for 1.0.0-M1.
2. *Precision* – JNode's CR model rounds weights to 3 decimals and initialises
   every weight to `round(1/n, 3)`. For **n > 2,000 class files** this rounds
   to **0**. The shortest-path weights then become 0, `1/0 = ∞`, every SIG is
   normalised to 0, and no noise is found. This happened for exactly the four
   versions with more than 2,000 class files (2.0.0-M2/M3/M4, 2.1.0-M1).
   We re-ran all versions with 4-decimal rounding. On the 20 versions where
   the original worked, the noise sets agree with Jaccard 0.88–1.00 (Table 3).
3. *Threshold fallback* (in our scripts, not in JNode) – JNode flags a class
   if its normalised SIG ≥ mean + 1σ. For 0.8.0 this limit (1.004) is above
   the maximum (1.0), so nothing is flagged. Only for that case we clamp the
   limit to the maximum SIG, i.e. the classes with the highest SIG are noise.

**Changes to ACDC.** (a) Optional parameters `maxClusterSize` (default 20)
and pattern set (`b` BodyHeader, `s` SubGraph, `o` OrphanAdoption), so that
we can run the experiment suggested in the tutorial. (b) A hash map for node
lookup when reading the RSF file (same output, linear instead of quadratic
time). (c) **Subsystem naming.** ACDC was written for C file names and names
each subsystem after the *base name* of its dominator (the text before the
last dot, `foo.c` → `foo`) + `.ss`. For a Java class name this base name is
the *package*, so all subsystems whose dominators share a package received
the same name and were merged when the output was read. We therefore pass
file-style names (`pkg.Class.java`) to ACDC and strip the suffix from the
output; each subsystem is then named after its dominator class (e.g.
`openai.OpenAiChatModel.ss`). Input: `data/rsf/<v>_full.rsf` / `_nonoise.rsf` with one
`depends A B` line per distinct dependency.

## 2.4 Implementation steps

1. `collect_versions.py` → merged jars, `data/versions.csv`, `data/modules/`.
2. `run_tools.sh` / `run_jnode_pool.sh` → `data/dependencies/<v>.csv`,
   `data/noise/<v>.csv`.
3. `recover.py`, for each version: build the top-level class graph; write the
   two RSF files; **A1/A2** ACDC on the full graph and on the graph without
   noise classes (noise nodes and all their edges removed); **A3/A4** k-means
   on the same two graphs; **PKG** – the developers' Java package
   decomposition as a reference; evaluate all of them with `metrics.py`.
4. `acdc_params.py` (ACDC experiment), `ai_inputs.py` / `ai_eval.py` (Phase 4),
   `noise_fanin.py`, `compare_noise.py`, `module_changes.py`, `plots.py`,
   `report_tables.py` + `build_report.sh` (this report).

**Feature vectors for k-means.** k-means needs points in a vector space, so
each class is represented by its *dependency profile*: its row of the
symmetric adjacency matrix *A + Aᵀ + I* (the classes it uses, the classes
that use it, and itself). Rows are L2-normalised and reduced to 64
dimensions with truncated SVD (LSA). On the normalised vectors, Euclidean
k-means approximates clustering by cosine similarity of dependency profiles.
Classes with similar neighbourhoods end up together. We used
`n_init = 10` and `random_state = 42`.

## 2.5 Choosing the number of clusters k

For every version and both graphs we ran k-means for k = 4 … n/3 and recorded
the **inertia** (within-cluster sum of squares) and the **silhouette**
coefficient (cosine). k was chosen with the **elbow method**, located
automatically with the *Kneedle* algorithm. Figure 2 shows both curves for
2.1.0-M1. The silhouette rises steeply up to the elbow and then flattens. Its
maximum lies at clusters of only 4–11 classes on average (e.g. k = 76 for the
284 classes of 0.8.0), which is too fine to be an architecture: such a
"component" is little more than a class with its helpers. The elbow gives
clusters of 6–12 classes on average, slightly coarser than ACDC (5–6 classes
per cluster). At the
elbow the silhouette has already reached 91–98 % of its maximum (77–79 % only
for the small 0.8.0). The resulting k grows from 36 (0.8.0) to 84 (A3) /
76 (A4) in 2.1.0-M1 (Table 5).

![Figure 2 – k selection for 2.1.0-M1: elbow on the inertia (left) and silhouette (right); dotted lines = chosen k.](../results/figures/kselection_latest.png)

## 2.6 Quality metrics (3.5)

For a clustering into k clusters, with μᵢ the dependencies inside cluster i
(Nᵢ classes) and εᵢⱼ the dependencies between clusters i and j (directed,
unweighted class graph), we use the definitions of the course (Lecture 6–7,
"Ποια θεωρείται καλή διάτμηση"):

* **Cohesion** (intra-connectivity) Aᵢ = μᵢ / Nᵢ². The lecture allows
  μᵢ/Nᵢ² or μᵢ/(Nᵢ(Nᵢ−1)). We use Nᵢ² because it is defined for one-class
  clusters (packages and ACDC produce some). We report the mean over clusters.
* **Coupling** (inter-connectivity) Eᵢⱼ = εᵢⱼ / (2·Nᵢ·Nⱼ), averaged over all
  cluster pairs.
* **MQ – Modularization Quality** (course definition, Mancoridis et al. 1998):
  MQ = (1/k)·ΣAᵢ − (2/(k(k−1)))·ΣEᵢⱼ, in [−1, 1]. This is the **main quality
  measure** of the assignment. Because Aᵢ divides by Nᵢ², MQ favours many
  small, dense clusters, so it is only comparable between architectures
  with a similar number of clusters.
* Supplementary measures, independent of k: **TurboMQ/k**, the mean cluster
  factor 2μᵢ/(2μᵢ+εᵢ) of the later Bunch MQ (Mitchell & Mancoridis 2006), where
  εᵢ counts all dependencies crossing the border of cluster i; and **intra
  deps**, the share of all dependencies that stay inside a cluster.
  TurboMQ (the sum, which grows with k) is given in the appendix.

## 2.7 Additional analyses from the lectures

* **MoJoFM** (Lecture 6–7): MoJoFM(A, R) = (1 − mno(A,R) / max mno(·,R)) · 100 %,
  where mno is the minimum number of *Move* and *Join* operations that turn
  architecture A into reference R (100 % = identical). It is computed with the
  original MoJo 2.0 implementation (`tools/mojo.jar`). The system has no
  expert ("ground-truth") architecture, so we use the developers' **package
  structure** as the reference for every version and, for the latest version,
  also the **AI architecture** of Phase 4. MoJoFM between the architectures
  of consecutive versions measures **architectural stability**; we also report
  the adjusted Rand index (ARI).
* **Omnipresent classes with the Bunch rule** (Lecture 6–7): in-degree
  > 3 × average in-degree. We compare it with JNode (Constantinou et al. 2015),
  and, as in the lecture's comparison of "System", "Noise" and "Bunch", we
  measure how close ACDC gets to the reference architecture without each set.
* **Architectural smells and their evolution** (Lecture 5; Fontana et al.
  2016, Sas et al. 2019), each normalised by the number of classes or packages:
  *cyclic dependency* (packages/classes in a dependency cycle, i.e. a
  strongly connected component of size > 1, found by depth-first search);
  *hub-like dependency* (classes with fan-in and fan-out above the system
  medians and |fan-in − fan-out| < 0.25·(fan-in + fan-out)); *unstable
  dependency* (packages, instability I = Ce/(Ca+Ce), of which more than 30 %
  of the package dependencies point to less stable packages – the Arcan
  threshold); *god component* (packages with more classes than mean + 2σ of
  the package sizes, since the lecture leaves the threshold open).
* **Lehman's laws** (Lecture 1–2): besides size and dependency growth, we count
  the **dependencies added and removed** per version (as in the lecture's
  Eclipse example for law II) and the **commits per month** between the
  analysed releases (law IV, conservation of organisational stability).

# 3. Results and discussion

## 3.1 Size and its evolution

![Figure 3 – Number of classes per version (GA releases in bold).](../results/figures/size_classes.png)

![Figure 4 – Packages and Maven modules per version.](../results/figures/size_packages_modules.png)

The system grew from **290 to 1,039 top-level classes (×3.6)** and from 543
to 2,015 class files in 31 months (Table 1, Figures 3–4). The growth is
**not uniform**:

* **0.8.0 → 1.0.0-M2 (×2.3 in 6 months):** the young framework adds model
  providers (Anthropic, Mistral, ZhiPu, MiniMax, Vertex Gemini, Watsonx, ...),
  vector stores (Cassandra, Elasticsearch, Qdrant, Redis, ...) and the
  `ChatClient`/advisor API (+198 classes in `spring-ai-core` in M2 alone).
* **1.0.0-M3 → 1.1.0 (slower, −4 % to +8 % per release):** consolidation
  before and after the first GA. **1.0.0-M8 → 1.0.0 even shrinks (−3.6 %)**: the
  RAG and chat-memory APIs were reworked and the Watsonx adapter removed for
  the GA.
* **2.0.0-M3 (+11.8 %):** the MCP annotation framework (+190 classes) is moved
  into Spring AI, and the Anthropic adapter is rewritten on the official SDK.
* **2.0.0-M5 (−9.5 %):** clean-up for the 2.0 GA. The OpenAI adapter is
  rewritten (−92 classes), and Azure OpenAI, Vertex AI Gemini and ZhiPu AI are
  removed (moved to the community organisation).

The **number of modules** shows a structural event the class count does
not. In **1.0.0-M7** the monolithic `spring-ai-core` (542 class files) and
`spring-ai-spring-boot-autoconfigure` (185) were split into `spring-ai-model`,
`-client-chat`, `-vector-store`, `-commons`, `-rag` and **one auto-configuration
module per provider/store**. The module count jumped from 51 to 104
(+57/−4 modules, Table 9), but the class count changed by only +7 %. It was a
**re-modularisation**, not a growth step.

**Lehman's laws.** *Continuing change (I)* and *continuing growth (VI)* are
clearly visible: 25 releases in 31 months, and every release adds or removes
modules (Table 9). Growth is fast in the first months and then slows down
to a few percent per release. This is the "inverse-square" shape that
Turski's model associates with the growing effort needed to understand an
ever-larger system, and it is consistent with *conservation of familiarity
(V)*: after 1.0 no release changes more than ~12 % of the system. The
size curve also shows *self-regulation (III)*: phases of expansion
(M1–M2, 1.1-M1–M2, 2.0-M2–M3) are followed by releases that shrink or
restructure the system (1.0.0, 2.0.0-M5…M7).

## 3.2 Class dependencies

![Figure 5 – Class-to-class dependencies (left) and dependencies per class (right).](../results/figures/dependencies.png)

Dependencies grew from **827 to 3,725 (×4.5)**, faster than the classes
(×3.6). Density rose from 2.9 to **4.1 dependencies per class at 1.0.0-M6**,
the version just before the module split (Figure 5). From 1.0.0-M7 onwards
it **falls** to 3.6–4.0 and stays there, even though the system keeps
growing. This is *increasing complexity (II)* together with the
counter-measure the law predicts: complexity grows "unless work is done to
maintain or reduce it". The 1.0.0-M7 re-modularisation and the 2.0 clean-up
are exactly such *anti-regressive* work.

## 3.3 Widely-used (noise) classes

Table 3 – Noise classes (JNode) per version. *JNode-3/4 noise files* = class
files flagged by the original (3-decimal) and fixed (4-decimal) JNode;
*Top-30 fan-in flagged* = how many of the 30 most-used classes are noise.

{{TABLE_NOISE}}

![Figure 6 – Noise classes per version (absolute and % of connected classes).](../results/figures/noise.png)

JNode flags **21–147 top-level classes (7–20 %)** per version. The noise
classes have a fan-in 3–9 times higher than the other classes (13.1 vs 2.4
on average, `results/noise_vs_fanin.csv`). In 0.8.0–1.0.0-M6 they are exactly
the classes one would call omnipresent: `Document`, `ModelRequest`,
`ModelResponse`, `ChatOptions`, `ModelOptionsUtils`, `Message`, `Filter`,
`EmbeddingModel`, `FunctionCallback` (29–30 of the 30 classes with the
highest fan-in).

Two observations need care:

1. **The share drops abruptly from 19 % to 9 % at 1.0.0-M7.** The core API
   classes are still widely used, but the module split changed the shape
   of the graph. JNode computes SIG only *inside the subgraph reachable from
   each class* and then normalises globally with mean + 1σ. After the split,
   the per-module auto-configuration classes reach long chains of classes;
   this presumably raises the mean SIG, so fewer classes exceed the
   threshold.
2. **In 2.x JNode drifts away from fan-in.** In 2.1.0-M1 only 16 of the 30
   most-used classes are flagged. `Document` (fan-in 71), `Filter` (61) and
   `EmbeddingModel` (47) are *not* flagged, while MCP transports (56 of the
   116 noise classes are in `mcp.*`) and Anthropic adapter classes are.
   JNode's notion of "noise" is a *reachability/significance* measure, not a
   usage count. It depends on how the classes are connected, and the 2.x MCP
   framework forms a large, densely connected subgraph. Removing these
   classes still helps the clustering (3.4), but the noise set of 2.x
   versions should not be read as "the utility classes of Spring AI".

## 3.4 Recovered architectures (A1–A4)

Table 4 – Mean over the 25 versions.

{{TABLE_MEANS}}

![Figure 7 – Normalised TurboMQ (TurboMQ/k) per version and architecture.](../results/figures/mq_turbo_norm.png)

![Figure 8 – Number of clusters per version.](../results/figures/clusters.png)

**Size of the recovered architectures.** ACDC produces 54 (0.8.0) to 185
(2.1.0-M1) clusters, k-means 36 to 84 (A3) / 76 (A4). ACDC's clusters are
less balanced: its largest cluster has 34–76 classes (50 in 2.1.0-M1),
whereas k-means clusters never exceed 35 classes. ACDC leaves almost no
singletons (1.7 per version on average; OrphanAdoption assigns orphans to
the subsystem they depend on most). The package decomposition has ~240
packages, 54 of them with a single class (Table 4).

**Quality by the course MQ.** ACDC has by far the highest MQ in every
version (0.22–0.24; mean 0.231 for A1 and 0.232 for A2). k-means (0.135 /
0.155) and the package structure (0.139) score much lower. MQ is dominated by
its cohesion term (0.23 for ACDC vs 0.14–0.16), while all coupling terms are
≈ 0.002. ACDC's many small, dense subgraph clusters (5–6 classes on average)
are exactly what MQ rewards. By MQ, k-means is not better than the packages.

**Quality by the k-independent measures.** On TurboMQ/k and on the share of
internal dependencies, all algorithmic architectures are **far more modular
than the package structure**. On average 38 % (A1) and 33 % (A3) of the
dependencies stay inside a cluster, against 21 % inside a package, and
TurboMQ/k is 0.41–0.70 vs 0.20. Spring AI's
packages are organised by *feature* (`chat.prompt`, `chat.messages`,
`chat.model`, ...) and by *vendor* (`openai`, `openai.api`, ...), and
features are used across packages. The recovery algorithms group classes
by *collaboration*.

* **ACDC vs k-means.** ACDC has the higher cohesion and MQ (0.23 vs
  0.13–0.15) because its many small subgraph clusters are dense. k-means has
  the higher TurboMQ/k (0.53 vs 0.41 on the full graph) and fewer, more
  balanced clusters. ACDC keeps slightly more dependencies inside clusters on
  the full graph (38 % vs 33 %); without noise k-means is ahead (57 % vs 53 %).
* **Effect of noise removal (A1→A2, A3→A4).** Removing the noise classes
  raises TurboMQ/k by **+0.12 (ACDC) and +0.18 (k-means)**, the intra-cluster
  share from 38 → 53 % and 33 → 57 %, and lowers coupling by a third (ACDC)
  to a half (k-means). The course MQ hardly changes (A1 0.231 → A2 0.232;
  A3 0.135 → A4 0.155), because removing classes does not change how dense
  the small clusters are. The benefit shows in the k-independent measures and
  in the distance to the package structure (MoJoFM, 3.6). It also
  makes the clusterings more stable over time (3.5). Hub classes such as
  `Document` or `ChatOptions` connect almost every cluster to every other one;
  without them the true subsystems separate. The effect is strongest for
  1.0.0-M1…M6 (TurboMQ/k up to 0.63 for A2 and 0.86 for A4), where JNode removed ~19 % of the
  classes, and smaller after 1.0.0-M7 (fewer noise classes, see 3.3).

**ACDC parameters (tutorial suggestion).** Table 6 shows the experiment on
2.1.0-M1. (i) **BodyHeader has no effect**: `bso` and `so` give identical
results. (ii) **OrphanAdoption is essential**: without it, ACDC's last step
(ClusterLast) puts all unclustered classes into one cluster of 406 classes,
and TurboMQ/k drops from 0.41 to 0.34. (iii) The **maximum cluster size**
matters only below 20: 5 gives 213 smaller clusters with lower TurboMQ/k
(0.39), 10 gives 192 (0.40), and 20, 40 or 80 give practically the same
result (184–185 clusters, 0.411–0.412). We therefore kept the default (20, `bso`).

![Figure 9 – ACDC parameter experiment (2.1.0-M1, full graph); the `bso` line lies exactly under `so`.](../results/figures/acdc_params.png)

Table 6 – ACDC parameter experiment (2.1.0-M1).

{{TABLE_ACDC}}

## 3.5 Quality of the architecture over time

![Figure 10 – Cohesion (mean intra-connectivity).](../results/figures/cohesion.png)

![Figure 11 – Coupling (mean inter-connectivity).](../results/figures/coupling.png)

![Figure 12 – Share of dependencies inside clusters.](../results/figures/intra_ratio.png)

![Figure 13 – Stability: ARI between the architectures of consecutive versions.](../results/figures/stability.png)

The evolution of the metrics (Tables 5, 7, 8; Figures 7, 10–13) tells a
consistent story in three phases:

1. **0.8.0 → 1.0.0-M6 – erosion during fast growth.** The modularity of the
   full system decreases: ACDC TurboMQ/k falls from 0.46 to 0.40, the
   package decomposition from 0.25 to 0.19, and the intra-cluster share of
   A1 from 0.47 to 0.37. More and more classes depend on a growing set of
   core abstractions, which is *declining quality (VII)* while new features
   are added quickly. The architectures are also unstable between releases
   (A1 ARI 0.62–0.88 for M1–M5): new features are not only added but
   re-wired.
2. **1.0.0-M7 → 1.0.0 – restructuring.** The module split is the largest
   architectural change in the history (A1 ARI 0.61 vs 1.0.0-M6). After it,
   the noise-free architectures (A2, A4) lose quality (A2 0.58 → 0.51)
   because fewer hub classes are removed (3.3). The full-graph architectures
   stay at their level.
3. **1.1.0-M1 → 2.1.0-M1 – stable.** ACDC TurboMQ/k stays at 0.40–0.42
   while its intra-cluster share rises from 0.36 to 0.40; k-means rises from
   0.53 to 0.57, and coupling falls (A1 0.0030 in 1.0.0 → 0.0017). ACDC
   architectures are **very stable** between releases (ARI 0.94–1.00 for A2
   between 1.0.0 and 2.0.0-M4). The visible dips are 2.0.0-M3 (MCP
   annotations) and 2.0.0-M5 (provider removals). The exception is A2, which
   falls from 0.55 to 0.46 in 2.0.0/2.1.0-M1: JNode's noise set drifts towards
   the MCP classes and leaves real hubs such as `Document` in the graph (3.3).
   Despite +33 % classes since 1.0.0, the quality of the full system did not
   decline. The clean-up releases kept the architecture in shape.

Overall, Lehman's *declining quality* law holds only for the early,
fast-growing phase. After 1.0 the project counteracts it with explicit
restructuring, enforced module rules (design doc 02) and removal of
adapters, so quality stays stable.

**Stability of the methods.** ACDC is clearly more stable than k-means (mean
ARI 0.88/0.94 for A1/A2 vs 0.77/0.81 for A3/A4). ACDC's patterns are
deterministic and local, so a release changes only the clusters it touches.
k-means re-partitions the whole space whenever k or the embedding changes.
For evolution studies ACDC therefore gives more interpretable diffs.

## 3.6 Distance to the reference architecture (MoJoFM)

![Figure 14 – MoJoFM of A1–A4 to the package structure.](../results/figures/mojofm_pkg.png)

![Figure 15 – MoJoFM between consecutive versions.](../results/figures/mojofm_stability.png)

Spring AI has no expert-validated architecture, so, following the lecture's
methodology, we measure how far each recovered architecture is from a
reference architecture: the developers' package structure (all versions)
and the AI architecture (latest version).

* **To the packages** (Table 13): ACDC is closer than k-means (mean MoJoFM
  45.7 % for A1 vs 38.6 % for A3), and **removing the noise classes brings
  both closer** (A2 50.9 %, A4 41.8 %). This is the effect the lecture reports
  for the noise-removal technique (slide 49). The gain is largest in
  1.0.0-M1…M6 (A2 up to 61 %), where JNode's noise set contained the real
  hubs. Over time k-means drifts away from the packages (≈ 50 % → 36–40 %)
  while ACDC stays at 43–48 %. As the system grows, connectivity-based
  clusters cut across Spring AI's feature/vendor packages more and more.
* **To the AI architecture** (latest version, Table 14): the package
  structure is closest (73 %), then k-means (65 %), then ACDC (54–55 %).
  k-means' fewer, larger clusters are easier to merge into the AI's 12
  components than ACDC's 185 small ones. (MoJoFM is asymmetric: in the
  other direction, turning the 12 AI components into 282 packages needs many
  moves, and MoJoFM(AI → packages) is only 12 %.)
* **Stability** (Table 15): consecutive ACDC architectures are almost the same
  (mean MoJoFM 95.5 % for A1, 96.5 % for A2; lowest 83 % at 1.0.0-M7, the
  module split). k-means changes much more (84–87 %). This confirms the ARI
  result of 3.5.

Table 13 – MoJoFM (%) of the recovered architectures to the package structure.

{{TABLE_MOJO}}

Table 14 – MoJoFM (%) to the AI architecture (latest version).

{{TABLE_MOJO_AI}}

Table 15 – MoJoFM (%) between consecutive versions.

{{TABLE_MOJO_STAB}}

## 3.7 Omnipresent classes: JNode vs Bunch

![Figure 16 – Omnipresent classes found by JNode and by the Bunch rule (left); MoJoFM of ACDC to the packages for the full system, without JNode noise and without Bunch omnipresent classes (right).](../results/figures/bunch_vs_jnode.png)

The Bunch rule (in-degree > 3 × average, Lecture 6–7) flags **24–86 classes**
per version, JNode 21–147. The two sets **overlap only partly** (Jaccard
0.17–0.46), and the overlap shrinks over time (0.17 in 2.0.0 and 2.1.0-M1).
Bunch flags the classes with the highest fan-in by definition (`Document`,
`Filter`, `EmbeddingModel`, ...). JNode's SIG also flags less used classes
that lie on many paths (e.g. the MCP transports, 3.3).

Removing the omnipresent classes before ACDC (Table 16) gives the lecture's
picture: both variants are closer to the package structure than the full
system (MoJoFM 47–55 % and 47–61 % vs 43–48 %). **JNode helps more in
1.0.0-M1…M6** (its noise set then contained the real hubs), and **Bunch helps
more from 1.0.0-M7 on** (49–53 % vs 47–50 %), when JNode's set drifts away from
the most-used classes. The course MQ is practically the same for all three
variants (0.22–0.24). The choice of omnipresent classes changes *which*
classes end up together, not how dense the clusters are.

Table 16 – JNode vs Bunch omnipresent classes and their effect on ACDC.

{{TABLE_BUNCH}}

## 3.8 Architectural smells and their evolution

![Figure 17 – Evolution of the architectural smells (normalised by #packages or #classes).](../results/figures/smells.png)

Following Lecture 5 (Sas et al.), we track four smells over the 25 versions
(Table 17, Figure 17):

* **Cyclic dependency** shows the clearest trend. The share of packages in a
  dependency cycle rises from 4.9 % (0.8.0) to **14.6 % in 1.0.0-M6**, stays
  high in M7/M8, and **drops to 7.2 % in 1.0.0** and ≈ 5–7 % afterwards. The
  release that cleaned up the RAG and chat-memory APIs for the GA removed many
  package cycles, the same anti-regressive work seen in 3.2. Class-level
  cycles grow from 4 % to 9 % (1.0.0) and then stay at 7–9 %.
* **Hub-like dependency** stays at 4–6 % of the classes and decreases slightly
  after 1.1 (5.5 % → 4.6 %). No class is getting worse as a hub.
* **Unstable dependency** affects only 1.5–4.7 % of the packages. Spring AI's
  packages mostly depend on more stable ones (the model API, `document`,
  `util`), as a ports-and-adapters design should.
* **God component.** Spring AI's packages are small (mean ≈ 4 classes), so
  the mean + 2σ threshold is only 9–10 classes and 4 → 19–21 packages exceed it
  (`chat.client`, `chat.prompt`, `model`, `openai`, ...). None of them is a
  "god" package in absolute terms. The growth reflects more feature packages
  of normal size, not a degrading package.

Table 17 – Architectural smells per version.

{{TABLE_SMELLS}}

## 3.9 Lehman's laws: dependency changes and work rate

![Figure 18 – Dependencies added and removed per version.](../results/figures/dependency_changes.png)

![Figure 19 – Commits per month between the analysed releases.](../results/figures/activity.png)

* **Law II – increasing complexity.** As in the lecture's Eclipse example,
  Figure 18 separates added from removed dependencies. Growth phases add
  hundreds of dependencies (1,154 in 1.0.0-M1, 916 in M2, 532 in 2.0.0-M3),
  and **large removals mark the restructuring releases**: 1.0.0-M7 (−678, the
  module split), 1.0.0-M8 and 1.0.0 (−375, −411, the GA clean-up) and
  2.0.0-M5 (−674, removed providers). These are exactly the points where
  "work is done to reduce complexity". After each of them the dependency
  density stays lower (3.2).
* **Law IV – conservation of organisational stability.** The work rate between
  releases varies from 73 to 447 commits per month (median 123) without a
  long-term trend; the peaks are the weeks before a GA (1.0.0: 293, 2.0.0:
  447). This is consistent with an invariant average work rate.
* **Law VIII – feedback system.** Spring AI's process has the multi-level
  feedback loops the law describes: public milestones every 1–2 months with
  user feedback, parallel maintenance lines (1.0.x, 1.1.x, 2.0.x), and
  design records that turn feedback into enforced rules (design doc 02).
* Spring AI is an **E-type** system: it must keep adapting to new AI
  providers and protocols (MCP), so all laws apply.

Table 18 – Dependencies added and removed between versions.

{{TABLE_DEPCHANGES}}

# 4. Architecture recovery with AI (latest version, 2.1.0-M1)

**Tool and protocol.** We used **Claude (Anthropic)** through Claude Code.
We wrote four prompts with increasing context (all prompts, inputs and
verbatim responses are in `ai/`):

| Prompt | Information given |
|---|---|
| P1 | Only the name/version and the GitHub URL |
| P2 | README of 2.1.0-M1 + list of the 116 Maven modules with their number of classes (`ai/inputs/modules.md`) |
| P3 | P2 + all 283 packages with class counts and sample classes (`packages.md`) + the package dependency graph from DependencyExtractor (1,047 weighted edges, `package_deps.md`); the answer had to map **every package to exactly one component** as ordered regex rules in JSON |
| P4 | Follow-up: the metrics of the P3 architecture compared with ACDC/k-means, asking for an explanation and possible improvements |

Limitation: the same assistant also helped to build the pipeline and had
therefore seen the analysis data. The P1 answer is thus not a fully
"cold" answer. Re-running the prompts in ChatGPT or another tool would give
an independent comparison.

**What the AI produced.**

* **P1 (no context)**: a plausible 14-component layered architecture
  (commons, chat/other model APIs, ChatClient & advisors, structured output,
  tools, memory, RAG/ETL, vector store API and implementations, providers,
  MCP, observability, Boot auto-configuration) with the right styles
  (*Ports & Adapters*, plug-in auto-configuration, *Chain of Responsibility*
  for advisors). But it is generic and partly **outdated**: it lists Azure
  OpenAI, Vertex AI Gemini, Hugging Face and `spring-ai-core`, all of which no
  longer exist in 2.1.0-M1 (removed in 1.0.0-M7, 2.0.0-M3 and 2.0.0-M5). It
  says it is unsure about exactly these points.
* **P2 (README + modules)**: 13 components in 5 layers (Foundation → Core
  abstractions → Application services → Adapters → Spring Boot integration)
  with an exact module-to-component mapping. It also identified real smells:
  `spring-ai-model` as a large "kernel" (346 class files), MCP annotations as
  a second large subsystem (224), and 57 auto-configuration modules.
* **P3 (packages + dependency graph)**: 12 components with an explicit
  package mapping (`ai/ai_architecture_P3.json`), a layered diagram derived
  from the measured dependencies, the strongest component dependencies
  (Model providers → Model API: 516; Vector stores → Vector store API: 190),
  three small cycles (Model API ⇄ Commons ⇄ Tool calling) and the hub
  packages (`document`, `embedding`, `vectorstore`, `model`, observation
  conventions).

Table 10 – Components of the AI architecture (P3) – classes with at least one dependency.

{{TABLE_AI_COMP}}

Table 11 – AI (P3) architecture vs algorithmic architectures (2.1.0-M1).

{{TABLE_AI}}

Table 12 – Agreement (ARI) of the AI architecture with the other architectures.

{{TABLE_AI_ARI}}

# 5. Reflection

## 5.1 Comparing the architectures of the latest version

* **Granularity.** The AI architecture has **12 components**, ACDC 185
  clusters, k-means 84, the package structure 282 packages. Only the AI
  architecture is at the level of abstraction an architect would draw on a
  whiteboard. The algorithmic architectures are closer to "modules of
  collaborating classes" and would need a second, hierarchical step to be read
  as components.
* **Quality metrics – the verdict depends on the measure.** By the
  **course MQ**, ACDC is clearly best (0.229), k-means (0.133/0.145) and the
  packages (0.140) follow, and the AI architecture is the *worst* (0.026).
  MQ's cohesion term divides by Nᵢ², so 12 components of up to 214 classes
  can never be dense. On the **k-independent measures** the picture
  reverses: with 15× fewer components the AI architecture keeps **a higher
  share of dependencies inside components than ACDC (47.2 % vs 40.4 %)**, and
  its TurboMQ/k is also higher (0.457 vs 0.411). Only k-means is better
  (0.567; without noise 0.648). The course MQ is therefore suitable for
  comparing architectures with a similar number of clusters (A1–A4), not
  for comparing a 12-component view with 185 clusters.
* **Agreement.** The AI architecture agrees very little with all algorithmic
  architectures (ARI ≈ 0.05–0.11) and even with the packages (0.07; ARI is
  low when the numbers of groups differ so much). ACDC and k-means agree with
  each other only moderately (ARI 0.29 for A1 vs A3, 0.32 for A2 vs A4), and
  each agrees with the packages at ARI ≈ 0.24–0.30. With the lecture's
  MoJoFM and the AI architecture as reference, the packages are closest
  (73 %), then k-means (65 %) and ACDC (54–55 %) (3.6).
* **Different principles.** The AI groups by **responsibility and
  architectural role**. All provider adapters form one component, all
  vector-store adapters another, all auto-configuration a third. The
  algorithms group by **connectivity**: each adapter ends up next to the
  ports it uses most (an OpenAI cluster with its options, API client and
  auto-configuration). The AI's decomposition makes the *Ports & Adapters*
  style visible: the strongest inter-component dependencies are adapter → port
  by design. The algorithmic decompositions show *vertical slices* (feature
  or vendor) that are easier to change in isolation. Both are valid views:
  the AI's answers "what are the parts and their roles?", the algorithms
  answer "what changes together / depends together?".

**Our assessment.** For understanding and documenting the system, the AI
architecture (P3) is the most useful. It is correct with respect to the
code (every package is mapped, the dependency directions are measured), it
matches the documented intent (design doc 02), and it names its own weak
points. ACDC is the best fully automatic method for *tracking evolution*:
it has the highest course MQ, it is stable and deterministic (MoJoFM ≈ 96 %
between consecutive versions), and with noise removal it is the closest to
the package structure (MoJoFM 51 %). k-means gives the best modularity
numbers but depends on k and on the embedding, and its clusters change most
between versions.

## 5.2 Does the AI tool help? How do information and prompts influence the result?

* **It helps a lot, but only when given facts.** P1 is a fluent but generic
  answer that mixes the 1.x and 2.x code bases and names removed modules: a
  typical *hallucination by outdated training data*. Adding the module list
  (P2) fixed the component inventory. Adding packages and the measured
  dependency graph (P3) made the answer **verifiable and quantitative**:
  a complete package mapping, real dependency weights, real cycles.
* **The prompt shapes the result.** Asking for "8–15 components" fixed the
  granularity. Asking for a mapping in machine-readable form (ordered regex
  rules) forced completeness and let us evaluate the AI architecture with the
  same metrics as ACDC/k-means. Feeding the metrics back (P4) produced a
  reasoned answer: it explained the effect of granularity on the metrics and
  proposed refinements (split MCP into annotations vs transports, split
  auto-configuration by target, move observability into its own component)
  without giving up the port/adapter boundary.
* **Risks.** The AI does not compute anything on its own; it reasons over
  what it is given. Without the extracted facts, the result cannot be checked,
  and even with them, a claim like "small cycles" must be verified (we did,
  `results/ai_component_deps.csv`). The output also depends on the model
  version and on the conversation, so it is not reproducible in a strict
  sense.

## 5.3 Which method for other systems?

For other systems and many versions we would **combine** the methods: run
the deterministic pipeline (DependencyExtractor → noise removal → ACDC) on
every version for *evolution* and *metrics*, and use an AI tool on the
**latest** version, *given the extracted facts* (modules, packages, the
dependency graph and the ACDC clusters), to produce a named, layered
component view and to explain the algorithmic clusters. AI alone is
fast but unverifiable and possibly outdated. Algorithms alone are
reproducible but produce clusters that still need a human (or an AI) to name
and abstract them. Noise removal should always be applied, but the noise
set should be sanity-checked (e.g. against fan-in, as in 3.3), because
JNode's SIG measure depends on the graph's shape.

# 6. Threats to validity

* **Binary vs source.** We analyse published jars, so only compiled
  dependencies are seen (no reflection, Spring wiring by configuration,
  service loading or annotations processed at run time).
* **System boundary.** The BOM defines the system. Modules not in the BOM
  (e.g. integration tests, docs) are not analysed. Duplicated split-package
  classes are kept once.
* **Tool changes.** JNode had to be patched (performance, identical output;
  precision, Jaccard ≥ 0.88 with the original where it worked), and 0.8.0 needed
  a threshold fallback. ACDC is a third-party port, not the York original,
  and needed file-style class names to name its subsystems correctly (2.3).
* **k-means.** The results depend on the feature representation (dependency
  profiles + SVD) and on the elbow choice of k. The silhouette would pick
  much finer clusterings (Figure 2).
* **Metrics.** Cohesion, the course MQ and TurboMQ depend strongly on k; we report
  the course MQ as the main measure for architectures of similar size (A1–A4)
  and TurboMQ/k, the intra-cluster share and MoJoFM to compare across very
  different k.
* **Milestones as versions** (see 1.2).

# References

* Mancoridis S., Mitchell B. S., Rorres C., Chen Y., Gansner E. R. (1998). *Using Automatic Clustering to Produce High-Level System Organizations of Source Code.* IWPC.
* Mitchell B. S., Mancoridis S. (2006). *On the automatic modularization of software systems using the Bunch tool.* IEEE TSE 32(3).
* Tzerpos V., Holt R. C. (2000). *ACDC: An Algorithm for Comprehension-Driven Clustering.* WCRE.
* Lehman M. M. (1980/1996). *Laws of Software Evolution Revisited.* EWSPT.
* Turski W. M. (1996). *Reference model for smooth growth of software systems.* IEEE TSE 22(8).
* Satopää V. et al. (2011). *Finding a "Kneedle" in a Haystack.* ICDCSW.
* Spring AI reference documentation and `design/02-boot-modularity.adoc`, v2.1.0-M1.

# Appendix A – Full metric tables

Table 5 – Number of clusters (k).

{{TABLE_K}}

Table 7 – TurboMQ/k (normalised TurboMQ).

{{TABLE_TMQN}}

Table 7b – TurboMQ.

{{TABLE_TMQ}}

Table 7c – MQ (course definition).

{{TABLE_BASICMQ}}

Table 8a – Cohesion (mean intra-connectivity).

{{TABLE_COH}}

Table 8b – Coupling (mean inter-connectivity).

{{TABLE_COUP}}

Table 8c – Share of dependencies inside clusters.

{{TABLE_INTRA}}

Table 8d – Stability (ARI with the previous version).

{{TABLE_STAB}}

Table 9 – Module changes per release.

{{TABLE_MODCHANGES}}

![Figure A1 – TurboMQ.](../results/figures/mq_turbo.png)

![Figure A2 – MQ (course definition).](../results/figures/mq_basic.png)
