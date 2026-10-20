\# Retrieval results log (q01-q07, filtered by company and period, K=5)



| run | change | fixed hit@1/3/5 | section hit@1/3/5 |

|---|---|---|---|

| 1 | baseline: fixed 200 words, section up to 350 words | 3/7, 6/7, 7/7 | 4/7, 4/7, 5/7 |

| 2 | fixed 150 words (overlap 30), section max 150 words | 4/7, 5/7, 7/7 | 4/7, 4/7, 5/7 |



q04 section miss: answer chunk (section\_54, full competitor list) ranks 6th at distance 0.544; top 5 span 0.477-0.529 and are customer/services chunks. Near miss, ranking issue; candidate for hybrid keyword search or reranker.


