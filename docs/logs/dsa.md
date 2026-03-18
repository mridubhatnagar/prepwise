# 📅 DSA Daily Learning Logs (Raw)

## Jan 1, 2026
- Watched RAM and Static Arrays videos.
- Solved Remove Duplicates from Sorted Array using brute force.
- Used extra space (hash map).
- Time Complexity: O(n).

---

## Jan 2, 2026
- Skimmed Static Arrays content.
- Attempted Remove Element from Array.
- Brute force failed.
- Watched solution video multiple times.
- Still struggled with implementation.

---

## Jan 3, 2026
- Did not study.

---

## Jan 4, 2026
- Solved Remove Element on paper.
- Implemented successfully.
- Confused about Neetcode output vs return value.
- Eventually passed submission.

---

## Jan 5, 2026
- Implemented Remove Element using swap logic.
- Implemented Dynamic Array.
- Understood size vs capacity.
- Debugged edge cases.

---

## Jan 6, 2026
- Solved Concatenation of Array.
- Completed Stack video.
- Attempted Valid Parentheses.
- Initial solution failed for edge cases.
- Learned stack empty condition and matching logic.

---

## Jan 7, 2026
- Solved Min Stack without solution.
- Watched Single Linked List video.
- Learned random access in linked list is O(n).

---

## Jan 8, 2026
- Implemented Linked List.
- Issues in remove and insertTail.
- Debugged multiple edge cases.

---

## Jan 9, 2026
- Completed Single Linked List implementation with help.
- Fixed remove and insertTail logic.

---

## Jan 10, 2026
- Solved Reverse Linked List (iterative).
- Attempted Merge Two Sorted Linked Lists but failed.

---

## Jan 11, 2026
- Solved Merge Two Sorted Linked Lists independently.
- Implemented on paper → code → submission passed.

---

## Jan 12, 2026
- Worked on Browser History problem.
- Implemented visit, back, forward.
- Struggled with clearing forward history.

---

## Jan 13, 2026
- Simplified Browser History logic.
- Fixed initialization.
- All test cases passed.

---

## Jan 14, 2026
- Watched Queue video.
- Implemented queue using Python list.
- Solved Students Unable to Eat Lunch.
- Learned to think in terms of DS, not Python lists.

---

## Mid Jan 2026 (Travel Phase)
- Deferred Implement Stack using 2 Queues.
- Watched Recursion videos.
- Implemented recursive linked list traversal and sum.
- Solved Valid Parentheses fully.
- Attempted Climbing Stairs but got TLE.

---
## Jan 21, 2026
- Implemented insertion sort.
- Adapted solution for tuple input.
- Learned importance of copying arrays.
- Solution accepted.

## Jan 22, 2026
- Struggled with recursion and merge logic.
- Fixed index out-of-range issues.
- Implemented pointer-based and slicing-based versions.
- Reimplemented from scratch for clarity.

## Jan 23, 2026
### Merge K Sorted Lists
- Derived solution from Merge Two Lists.
- Implemented iterative merging.
- Used dummy node technique.
- Solved independently after revision.
- Timeboxed reattempt (~30 mins).

## Jan 24, 2026
### Quick Sort
- Implemented partition logic independently.
- Built recursive quicksort.
- Implemented Neetcode-style version.
- Successfully sorted arrays.
- Implemented both index based and subarray based approach.

## Jan 25, 2026
### Bucket Sort
- Implemented counting-based bucket sort.
- Handled non-zero minimum values.
- Derived mapping:
  - index = value - min_value
  - value = index + min_value

---
## 📅 Jan 28, 2026

### Topics
- Binary Search
- Search Range (First & Last Position)
- Guess the Number

### Activities
- Watched NeetCode video on **Search Range**.
- Conceptually understood the idea of finding left and right boundaries using binary search.
- Faced confusion while applying the API / implementation details from the suggested problem.
- Revisited **Guess the Number** problem.
- Successfully solved **Guess the Number** using binary search.

### Learnings
- Binary search boundary problems require careful control of `left` and `right`.
- Understanding the concept does not immediately translate to implementation.
- Revisiting simpler problems helps regain confidence.

---

## 📅 Jan 29, 2026

### Topics
- Binary Search Variants
- First Bad Version

### Activities
- Attempted **First Bad Version** (via LeetCode redirect from NeetCode).
- Initially struggled due to abstraction via `isBadVersion` API.
- Stopped and deferred the problem to avoid forcing progress.

### Learnings
- API-based problems add an extra layer of reasoning.
- Recognized that this problem is about finding the **first true** in a monotonic boolean space.
- Learned the importance of stopping when mental clarity drops.

---

## 📅 Jan 30, 2026

### Topics
- First Bad Version
- Binary Search (Left Boundary Pattern)

### Activities
- Revisited **First Bad Version** using paper-based reasoning.
- Successfully implemented a correct solution using binary search.
- Identified mistake in the first attempt where `mid` was returned directly.
- Corrected approach by storing the candidate answer and continuing search on the left.

### Learnings
- Finding *an* occurrence is different from finding the *first* occurrence.
- Left-boundary binary search requires storing the answer and shrinking the search space.
- Patterns learned in earlier problems can be reused effectively.

---

## 📅 Jan 30, 2026

### Topics
- Trees (Introduction)
- Binary Tree Terminology
- Recursion (Conceptual)

### Activities
- Watched introductory videos on **Binary Trees**.
- Learned basic terminology: root, parent, child, leaf, height, depth.
- Realized discomfort with trees due to weak recursion intuition.
- Decided to postpone coding and focus on conceptual clarity.
- Planned to read recursion chapter from *A Common-Sense Guide to Data Structures* before continuing.

### Learnings
- Trees require a shift from loop-based thinking to recursive thinking.
- Base cases are critical for recursion.
- Mental fatigue is a signal to pause, not push.

---

## 📅 Jan 31, 2026

### Topics
- Recursion
- Binary Tree
- Binary Search Tree (BST)

### Activities
- Completed reading the **Recursion** chapter.
- Applied recursion concepts to solve **Height of Binary Tree**.
- Watched video explaining **Binary Search Tree (BST)** properties.
- Implemented and solved **Search element in Binary Search Tree** using recursion.
- Updated personal knowledge base with learnings.

### Learnings
- Recursion works best when assuming the function is already correct for subproblems.
- Tree height can be computed bottom-up using recursion without passing counters.
- Base case (`node is None`) is sufficient for most tree problems.
- BST search leverages ordering properties to reduce search space.
- Tree problems feel more approachable once recursion mental model is clear.
- Learnt category of recursion. Types of recursion - Bottom up , top down. 
- Implemented top down approach for trees. Bottom up is DP. To be done later.


## 📅 Feb 2, 2026

### Topics
- Binary Search Tree (BST)
- Insert in BST
- Delete in BST

### Activities
- Implemented **insert** operation in Binary Search Tree.
- Implemented **delete** operation in Binary Search Tree.
- Dry-ran multiple examples for BST delete to understand recursion flow.
- Focused especially on deletion scenarios involving nodes with two children.

### Key Learnings
- BST deletion logic depends on the **number of children**, not node position.
- When a node has **two children**, the correct replacement is:
  - the **minimum value from the right subtree** (inorder successor),
  - which preserves global BST ordering.
- Deletion in the two-children case happens in **two phases**:
  1. Replace the node’s value with the successor’s value.
  2. Recursively delete the successor from the right subtree.
- Traversal knowledge is not required to understand successor logic; ordering constraints are sufficient.


## 📅 Feb 3, 2026

### Topics
- Depth First Search (DFS)
- Binary Search Tree (BST)
- Inorder Traversal

### Activities
- Watched NeetCode video explaining **Depth First Search (DFS)**.
- Implemented **inorder traversal** for Binary Search Tree on NeetCode.
- Applied recursion with shared state using wrapper + inner DFS pattern.

### Learnings
- DFS traversal follows a strict execution order within each recursive call.
- Inorder traversal processes nodes as: left subtree → node → right subtree.
- For BSTs, inorder traversal naturally produces values in **sorted order**.
- Shared result state in recursion must be defined outside the recursive function when the function signature is fixed.

### Notes
- Clarified misconception about returning early after printing a node.
- Understood that recursive calls must complete fully before unwinding.
- DFS traversal feels more intuitive after working through BST insert and delete.


## Feb 8, 2026

- Did lot of recursion drills. And, dry run on paper for each. 
- To understand the call flow in recursion
- Dry ran height of binary tree

## Feb 9, 2026

- Implemented traversals inorder, preorder, postorder. 
- Wrote call flow for each of these. 
- solved kth smallest element in binary tree problem

## Feb 11, 2026

- Watched video on Binary Search Tree.
- Got stuck on the level wise output format 

## Feb 12, 2026

- Implemented binary search tree. 
- Learnt why was I unable to print it level wise. 
- Submitted.

## Feb 13, 2026

- Implemented right side view of binary tree. Was
able to solve on own
- Key idea - Right most element in each layer in BFS. Will be present in right side view
of binary tree