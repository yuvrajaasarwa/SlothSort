# CS 401: Advanced Database Systems - Assignment 3 Notes
**Topic: B-Tree & B+ Tree Indexing in Relational Databases**

## Key Concepts
- Balanced tree data structure that maintains sorted data and allows searches, sequential access, insertions, and deletions in logarithmic time.
- In a B+ Tree, leaf nodes are linked sequentially as a doubly-linked list for fast range queries.
- Internal nodes only store keys and child pointers (no data records), maximizing fanout and reducing disk I/O.

## Assignment Problem 2 Analysis
- Given Block Size = 4096 bytes, Pointer Size = 8 bytes, Key Size = 16 bytes:
  Order `p` calculation: `p * 8 + (p - 1) * 16 <= 4096` -> `24p - 16 <= 4096` -> `p <= 171.33` -> Max fanout is 171.
- Query optimization benefits: Secondary indexes dramatically speed up WHERE clauses matching indexed attributes.
