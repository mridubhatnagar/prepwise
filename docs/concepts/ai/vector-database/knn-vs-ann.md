# KNN vs ANN

## KNN (k-Nearest Neighbors)

KNN refers to the k-nearest neighbors algorithm.

In vector search, KNN computes similarity between the query vector and **all stored vectors** in the embedding space.

For example:

- Compute cosine similarity (or dot product) with every vector.
- Sort results.
- Return top-k closest vectors.

Since similarity is computed against every stored vector, the time complexity grows linearly with dataset size (O(N)).

Due to this, brute-force KNN becomes slow and difficult to scale for large datasets.

---

## ANN (Approximate Nearest Neighbors)

ANN refers to Approximate Nearest Neighbor search.

Instead of comparing the query vector with every stored vector, ANN uses an indexing structure (such as HNSW) to reduce the number of similarity computations.

HNSW builds a proximity graph over stored vectors. During search:

- The algorithm starts from an entry node.
- It navigates through neighboring nodes that are closer to the query.
- Similarity is computed only with selected candidate vectors.
- The search progressively moves toward closer vectors.

ANN does not guarantee perfectly exact nearest neighbors like brute-force KNN, but it provides results that are very close to optimal while being significantly faster and more scalable.

---

## Summary

### First Principles View

- KNN = exact search, high computation cost.
- ANN = approximate search, lower computation cost.
- HNSW is one commonly used ANN algorithm in vector databases.
- ANN trades perfect accuracy for significant speed improvements.

### Tradeoffs

- KNN provides exact results but scales poorly.
- ANN provides approximate results but scales efficiently.

### Interview Summary

- KNN performs brute-force similarity search.
- ANN reduces similarity computations using indexing.
- HNSW is a common ANN algorithm.
- ANN trades exactness for speed.
