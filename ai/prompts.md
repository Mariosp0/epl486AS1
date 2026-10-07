# Phase 4 – Prompts given to the AI tool

AI tool: **Claude (Anthropic)**, used through Claude Code. Each prompt was given
in a fresh conversation together with the listed inputs (files in
`ai/inputs/`). Target: the latest version, **Spring AI 2.1.0-M1**.
The responses are stored verbatim in `ai/responses/`.

To reproduce with another tool (e.g. ChatGPT), paste the prompt text and attach
the listed input files.

---

## P1 – zero context (name only)

Inputs: none.

```text
You are an experienced software architect. Recover the software architecture
of the open-source framework Spring AI, version 2.1.0-M1
(https://github.com/spring-projects/spring-ai).
1. Identify the main architectural components (layers / subsystems), their
   responsibilities and the most important classes or interfaces of each.
2. Describe the dependencies between the components.
3. Give the architecture as a layered component diagram (text/ASCII).
4. State the architectural styles and design patterns you recognise.
Be explicit about what you are unsure of.
```

## P2 – project documentation + module structure

Inputs: `ai/inputs/README.md` (project README of v2.1.0-M1),
`ai/inputs/modules.md` (the 116 Maven modules of the release with their number
of class files, extracted from the binaries by `scripts/ai_inputs.py`).

```text
You are an experienced software architect. I attach (a) the README of Spring AI
2.1.0-M1 and (b) the complete list of Maven modules of this release with the
number of compiled classes each one contains.
Using ONLY this information:
1. Group the modules into architectural components (subsystems) and give each
   component a name and a responsibility.
2. Organise the components in layers and describe the allowed dependencies
   between layers.
3. Draw the architecture as a layered component diagram (text/ASCII).
4. Point out anything in the module structure that looks like an architectural
   smell or a deviation from a clean layering.
```

## P3 – code-level facts: packages and package dependency graph

Inputs: P2 inputs + `ai/inputs/packages.md` (283 packages, number of classes and
sample class names) + `ai/inputs/package_deps.md` (1,047 package-to-package
dependencies, weighted by number of class-level dependencies, extracted with
DependencyExtractor).

```text
You are an experienced software architect performing architecture recovery.
I attach for Spring AI 2.1.0-M1: the README, the Maven modules, the list of
all Java packages (prefix org.springframework.ai omitted) with their number of
classes and sample class names, and the package dependency graph extracted
from the bytecode ("a -> b : n" means n class-level dependencies from package
a to package b).
1. Recover the architecture: define between 8 and 15 components. Every package
   must belong to exactly one component. Give the mapping as an ORDERED list of
   (component, Java regular expression over the package name) rules where the
   first matching rule wins, in JSON.
2. For each component give its responsibility and key classes.
3. Using the package dependency graph, describe the dependencies between your
   components (which are strongest, are there cycles?) and draw a layered
   component diagram.
4. Which packages are "hubs" used almost everywhere (candidates for
   omnipresent/utility classes)?
5. Assess the modularity of the system: where is it well modularised and
   where are the weak points?
```

## P4 – follow-up on P3 (refinement with feedback from the metrics)

Inputs: P3 conversation + the quality metrics of the P3 architecture computed by
`scripts/ai_eval.py` (see `results/ai_metrics.csv`).

```text
I mapped every class to your components and computed the metrics below
(cohesion = mean intra-connectivity, coupling = mean inter-connectivity,
TurboMQ, share of dependencies that stay inside components), next to the
ACDC and k-means architectures of the same version.
<metrics table: see the top of ai/responses/P4_response.md>
Explain the difference. Would you change your decomposition, and if so how,
without losing its meaning for a developer?
```
