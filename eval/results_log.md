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

