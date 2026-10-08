# Phase 1 – System selection: Google Guava

Repository: <https://github.com/google/guava> (Apache-2.0)

Guava is Google's core Java library. It provides immutable and new collection
types (`ImmutableList`, `Multimap`, `Multiset`, `BiMap`, `Table`, `RangeSet`),
a graph library (`common.graph`), caching (`common.cache`), concurrency
utilities (`ListenableFuture`, `Futures`, `RateLimiter`, `Service`), hashing,
I/O (`ByteSource`, `CharSink`, `Files`), math, primitives, reflection,
string processing and escaping (`Joiner`, `Splitter`, `CharMatcher`,
`Escaper`), an event bus and networking helpers (`InternetDomainName`,
`HostAndPort`, `MediaType`).

## Eligibility check (verified on 2026-10-07)

| # | Criterion | Evidence | OK |
|---|-----------|----------|----|
| 1 | ≥ 10 major/minor versions | 109 version tags (`v*`); **54 major/minor releases** (33 major v1.0–v33.0, 21 minor such as 23.1, 28.2, 33.7.0) plus 28 patch releases (e.g. 33.7.2) and 25 release candidates | ✔ |
| 2 | Repository on GitHub | `google/guava` | ✔ |
| 3 | Latest version ≥ 10,000 LOC | v33.7.2: 611 production `.java` files in `guava/src`, **96,646 non-comment non-blank LOC** | ✔ |
| 4 | Not archived | Last commit 2026-10-07 | ✔ |
| 5 | ≥ 50 commits since 1/1/2024 | **1,261** of 7,546 commits | ✔ |
| 6 | Not a fork | Original repository of the `google` organisation | ✔ |
| 7 | Created before 2024 | History starts 2009-06-18 (moved to GitHub in 2014) | ✔ |

Commands: `git rev-list --count --since=2024-01-01 HEAD`, `git log --reverse`,
NCLOC count over `guava/src/**/*.java` at tag `v33.7.2`
(the same procedure as `scripts/project_stats.sh`).

## Version selection (sparse sampling)

All tags are listed in `guava/data/tags.csv` with their date and kind.

* **Population:** the major/minor releases from 10.0 on (Guava's numbering
  before 10.0 was `r01…r09`; the first tagged `10.0` is from Sept. 2011).
* **Excluded:** patch releases (x.y.z with z > 0, e.g. 23.6.1, 31.0.1),
  release candidates (`-rc`) and two special tags (`13.0-final`,
  `15.0-cdi1.0`).
* **Sparse sample:** every **second major release** from 10.0 to 32.0
  (10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32.0.0) plus the **latest
  release at the time of the analysis, 33.7.2** (29 Sep 2026), i.e. **13
  versions over 15 years**, no two of them consecutive. Phase 4 (AI) uses
  only the latest, 33.7.2. 33.7.2 is a patch release of the 33.7 feature
  release (33.7.0, Aug 2026). We take it because the assignment asks for the
  latest release; at bytecode level it is identical in structure to 33.7.0
  (same 1,948 class files and exactly the same DependencyExtractor output).

| Version | Date | Gap |
|---|---|---|
| 10.0 | 2011-09-27 | – |
| 12.0 | 2012-04-30 | 7 months |
| 14.0 | 2013-02-25 | 10 months |
| 16.0 | 2014-01-17 | 11 months |
| 18.0 | 2014-08-25 | 7 months |
| 20.0 | 2016-10-28 | 26 months |
| 22.0 | 2017-05-22 | 7 months |
| 24.0 | 2018-02-01 | 8 months |
| 26.0 | 2018-08-01 | 6 months |
| 28.0 | 2019-06-11 | 10 months |
| 30.0 | 2020-10-16 | 16 months |
| 32.0.0 | 2023-05-26 | 31 months |
| 33.7.2 | 2026-09-29 | 40 months |

From 23.1 on Guava is published in two flavours (`-jre` and `-android`);
we analyse the `-jre` flavour (the main line).

## Draft approval e-mail to the instructor

> Subject: EPL484 Project 1 – Team X – system proposal
>
> Dear Dr. Constantinou,
>
> Our team (GitHub usernames: `Mariosp0`, `<member2>`) would like to propose,
> in order of preference:
>
> 1. **Google Guava** – https://github.com/google/guava (54 major/minor
>    releases, ~97K NCLOC in 33.7.2, 1,261 commits since 1/2024). We plan to
>    analyse 13 versions: every second major release 10.0–32.0 and the latest
>    release 33.7.2.
> 2. `<alternative 2>`
> 3. `<alternative 3>`
>
> We would prefer the team repository to be private.
>
> Kind regards,
> `<names>`
