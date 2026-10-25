\# Retrieval results log (q01-q07, filtered by company and period, K=5)



| run | change | fixed hit@1/3/5 | section hit@1/3/5 |

|---|---|---|---|

| 1 | baseline: fixed 200 words, section up to 350 words | 3/7, 6/7, 7/7 | 4/7, 4/7, 5/7 |

| 2 | fixed 150 words (overlap 30), section max 150 words | 4/7, 5/7, 7/7 | 4/7, 4/7, 5/7 |



q04 section miss: answer chunk (section\_54, full competitor list) ranks 6th at distance 0.544; top 5 span 0.477-0.529 and are customer/services chunks. Near miss, ranking issue; candidate for hybrid keyword search or reranker.



\## Run 3: expanded harness (q01-q15; 11 scored, 4 unanswerable; strict cross-year)



| mode | collection | hit@1/3/5 |

|---|---|---|

| filtered | fixed | 5/11, 6/11, 9/11 |

| filtered | section | 4/11, 5/11, 7/11 |

| unfiltered | fixed | 1/11, 1/11, 3/11 |

| unfiltered | section | 1/11, 3/11, 4/11 |



Findings: removing the company and period filter dropped single-filing hit@5 from 7/7 to 2/7 (fixed) and from 5/7 to 3/7 (section). Unanswerable best distances (0.245 to 0.504) overlap fully with answerable hits (0.238 to 0.504), so a distance cutoff cannot drive refusal. q08 and q09 miss in all configurations; q09 evidence strings were verified in the source text, so those are retrieval misses.



q09 diagnosis: the 2025 evidence sentence ("virtual team of AI agents") is in section\_1, while section\_0 (rank 5) holds the start of the same overview; chunk boundaries split the overview and the multi-topic question retrieves neither chunk well.



\## Run 4: query routing added



| mode | collection | hit@1/3/5 (all 11) |

|---|---|---|

| filtered | fixed | 5/11, 6/11, 9/11 |

| filtered | section | 4/11, 5/11, 7/11 |

| routed | fixed | 4/11, 5/11, 6/11 |

| routed | section | 3/11, 4/11, 7/11 |

| unfiltered | fixed | 1/11, 1/11, 3/11 |

| unfiltered | section | 1/11, 3/11, 4/11 |



Findings: company routing found the right company on 15 of 15 questions and roughly doubled hit@5 versus unfiltered. It stayed below filtered because questions without a year search all three years.



\## Run 5: routing defaults to the latest filing when no year is named



| mode | collection | hit@1/3/5 (all 11) |

|---|---|---|

| routed | fixed | 5/11, 5/11, 8/11 |

| routed | section | 4/11, 5/11, 7/11 |



Change: one edit in route.py. Run 4 routed was fixed 4/11, 5/11, 6/11 and section 3/11, 4/11, 7/11. Routed now sits within one question of filtered. Caveat: most questions target the newest filing, so the default favors this test set. A first attempt at the edit routed every question to PANW because of a stale bytecode cache; clearing src/\_\_pycache\_\_ fixed it.



\## Run 6: answer step (routed retrieval, fixed chunks, prompt with REFUSE rule)



| model | unanswerable refused | answerable wrongly refused | errors |

|---|---|---|---|

| gemini-flash-lite-latest (alias) | 4/4 | 2/11 (q08, q14, cross-year) | 0 |



Caveats: n=4 unanswerable; answer quality and faithfulness not yet scored; alias model, not pinned.

## Run 7: answer step with 10 unanswerable questions (q10-q13, q16-q21)



| model | unanswerable refused | answerable wrongly refused | errors |

|---|---|---|---|

| gemini-flash-lite-latest (alias) | 10/10 | 2/11 (q08, q14, cross-year) | 0 |



Caveats: n=10 unanswerable, mostly specific-figure-not-disclosed cases; faithfulness of answered questions not yet scored; alias model, not pinned.

## Run 8: per-period retrieval for questions naming two years (3 chunks per period)



| model | unanswerable refused | answerable wrongly refused | errors |

|---|---|---|---|

| gemini-flash-lite-latest (alias) | 10/10 | 1/11 (q14) | 0 |



Change: one edit in answer.py retrieve(). Run 7 was 10/10 and 2/11. q05 now correct; q06, q08 partial; q09 off-target; q14 refused. Refusal score does not measure answer correctness. Caveat: the change targeted questions in this set.
## Run 9: index cleaning no longer deletes short numeric table lines



| model | unanswerable refused | answerable wrongly refused | errors |

|---|---|---|---|

| gemini-flash-lite-latest (alias) | 10/10 | 2/11 (q06, q14) | 0 |



Change: clean() in index.py. Chunks: fixed 6272 to 6290, section 5653 to 5660. Chunk check confirms the 11% now survives in four ADBE chunks. q06 still refused in the answer run; cause under investigation (retrieval vs model variance). Router gap found: q19 names no company (TurboTax), routed to None.

