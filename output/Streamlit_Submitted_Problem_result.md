# 🧩 DSA Problem Solution: Streamlit Submitted Problem

---

## 📝 Problem Analysis & Explanation

**Approach:** ```json

````
Given a binary string `s`, the goal is to count the total number of substrings that consist solely of '1's. Since the answer can be very large, it must be returned modulo `10^9 + 7`.

**Approach and Intuition**

The core idea behind solving this problem efficiently is to understand how substrings of '1's are formed. A substring consisting of all '1's can only exist within a continuous block of '1's. A '0' character acts as a separator, meaning any substring of all '1's cannot cross a '0'.

Consider a block of `k` consecutive '1's, for example, "111" (where `k=3`).
The substrings of all '1's within this block are:
- "1" (3 times: at index 0, index 1, index 2)
- "11" (2 times: starting at index 0, starting at index 1)
- "111" (1 time: starting at index 0)
The total count for "111" is `3 + 2 + 1 = 6`.

In general, for a block of `k` consecutive '1's, the number of substrings with all '1's is the sum of integers from 1 to `k`, which is given by the arithmetic series formula: `k * (k + 1) / 2`.

This observation leads to a straightforward single-pass algorithm:
1.  Iterate through the input string `s`.
2.  Maintain a `current_consecutive_ones` counter to track the length of the current block of '1's.
3.  Maintain a `total_count` to accumulate the results, applying the modulo operation at each step.

Let's refine the approach based on the `1+2+...+k` sum.
When we encounter a '1':
-   We increment `current_consecutive_ones`.
-   This new '1' extends all `current_consecutive_ones - 1` substrings that ended at the previous position by one, and also forms a new single '1' substring by itself. Thus, it effectively adds `current_consecutive_ones` new substrings that end at the current position. For example, if we have "11" (`current_consecutive_ones = 2`) and encounter another '1' to make "111" (`current_consecutive_ones = 3`):
    -   The first '1' contributed 1 ("1"). Total: 1.
    -   The second '1' contributed 2 ("1", "11"). Total: 1+2 = 3.
    -   The third '1' contributed 3 ("1", "11", "111"). Total: 3+3 = 6.
This pattern of adding the `current_consecutive_ones` value to the `total_count` each time a '1' is encountered naturally sums up `1+2+...+k` for any block of `k` ones.

When we encounter a '0':
-   The current block of '1's is broken. We reset `current_consecutive_ones` to `0`, effectively starting a fresh count for any subsequent '1's.

**Detailed Algorithm**

1.  Initialize `total_count = 0`. This will store our final result.
2.  Initialize `current_consecutive_ones = 0`. This counter will keep track of the length of the current sequence of '1's.
3.  Define `MOD = 10^9 + 7`. This is the modulus for the answer.
4.  Iterate through each character `c` in the input string `s`:
    a.  If `c == '1'`:
        i.  Increment `current_consecutive_ones` by 1.
        ii. Add the new `current_consecutive_ones` value to `total_count`. This is where the sum `1+2+...+k` is incrementally built.
        iii. Apply the modulo operation: `total_count = (total_count + current_consecutive_ones) % MOD`.
    b.  If `c == '0'`:
        i.  Reset `current_consecutive_ones` to `0`, as the streak of '1's has been broken.
5.  After iterating through the entire string, `total_count` will hold the final sum of substrings with all '1's, modulo `10^9 + 7`. Return `total_count`.

**Example Walkthrough: `s = "0110111"`**

-   `total_count = 0`, `current_consecutive_ones = 0`
-   `MOD = 10^9 + 7`

1.  `c = '0'` (at index 0): `current_consecutive_ones` remains `0`.
2.  `c = '1'` (at index 1):
    -   `current_consecutive_ones` becomes `1`.
    -   `total_count = (0 + 1) % MOD = 1`.
3.  `c = '1'` (at index 2):
    -   `current_consecutive_ones` becomes `2`.
    -   `total_count = (1 + 2) % MOD = 3`.
4.  `c = '0'` (at index 3): `current_consecutive_ones` resets to `0`.
5.  `c = '1'` (at index 4):
    -   `current_consecutive_ones` becomes `1`.
    -   `total_count = (3 + 1) % MOD = 4`.
6.  `c = '1'` (at index 5):
    -   `current_consecutive_ones` becomes `2`.
    -   `total_count = (4 + 2) % MOD = 6`.
7.  `c = '1'` (at index 6):
    -   `current_consecutive_ones` becomes `3`.
    -   `total_count = (6 + 3) % MOD = 9`.

End of string. Return `total_count = 9`. This matches Example 1.

**Why It Works**

The algorithm works because it correctly identifies and sums the contributions of all contiguous blocks of '1's.
-   Each time a '1' is encountered, `current_consecutive_ones` tells us the length of the sequence of '1's ending at the current position.
-   Adding `current_consecutive_ones` to `total_count` ensures that we are summing `1 + 2 + ... + k` for each block of `k` ones. For instance, if `current_consecutive_ones` is `j`, it means we have `j` consecutive '1's ending at the current position. These `j` ones form `j` valid substrings: the single '1' itself, the '11' ending here, and so on, up to the full `j`-length sequence of '1's.
-   The '0's correctly break the counting streak, ensuring that substrings do not span across '0's, which is a fundamental requirement of the problem.
-   The modulo operation `(total_count + current_consecutive_ones) % MOD` is applied at each addition to prevent integer overflow for large string lengths while maintaining the correct result modulo `10^9 + 7`. The maximum `current_consecutive_ones` is `10^5`, and `total_count` is at most `MOD-1`, so `total_count + current_consecutive_ones` will fit within a standard 64-bit integer before the modulo.

**Edge Cases**

1.  **String with all '0's (e.g., "000")**: `current_consecutive_ones` will always be `0`, `total_count` will remain `0`. Correct.
2.  **String with all '1's (e.g., "111111")**:
    -   `i=0, s[0]='1'`: `cur=1`, `total=(0+1)%MOD=1`
    -   `i=1, s[1]='1'`: `cur=2`, `total=(1+2)%MOD=3`
    -   `i=2, s[2]='1'`: `cur=3`, `total=(3+3)%MOD=6`
    -   ...
    -   `i=5, s[5]='1'`: `cur=6`, `total=(15+6)%MOD=21`. Correct, `6 * (6+1) / 2 = 21`.
3.  **String with a single '1' (e.g., "1")**: `current_consecutive_ones` becomes `1`, `total_count` becomes `1`. Correct.
4.  **String with alternating '1's and '0's (e.g., "10101")**: `total_count` will be 3 (one '1' from index 0, one '1' from index 2, one '1' from index 4). The algorithm handles this by resetting `current_consecutive_ones` to `0` after each '0'. Correct.
5.  **Constraints**: `1 <= s.length <= 10^5`. The algorithm processes each character once, making it efficient enough for this constraint.

**Time and Space Complexity**

-   **Time Complexity:** The algorithm iterates through the string `s` exactly once. For each character, it performs constant time operations (increment, addition, modulo, comparison). Therefore, the time complexity is **O(N)**, where N is the length of the string `s`.
-   **Space Complexity:** The algorithm uses a fixed number of variables (`total_count`, `current_consecutive_ones`, `MOD`) regardless of the input string's length. Hence, the space complexity is **O(1)**.


### Approach Validation

**Complexity & Test Pass Rate:** [LLM] Single Pass Iteration / Sliding Window. The algorithm iterates through the input string 's' (passed as 'nums1') exactly once. For each character, it performs constant time operations (comparison, arithmetic, modulo). The total time taken is directly proportional to the length of the string, 'n'. The space complexity is constant because it only uses a fixed number of variables (total_count, current_consecutive_ones, MOD) regardless of the input string's length.\nPassed 0 / 1 tests.

**Time Complexity:** `O(n)`

**Space Complexity:** `O(1)`

**Optimization Tips:** Consider appropriate DS (hashmap/heap) and pruning.


## 💻 Generated Code


```python

import sys, json, math

class Solution:
    # This method signature is provided by the problem prompt.
    # It is typically for the "Median of Two Sorted Arrays" problem.
    # For this specific problem (counting substrings with all 1s),
    # we assume 's' (the binary string) is passed as the 'nums1' argument,
    # and 'nums2' is ignored. The return type is an integer (count),
    # which the driver code will then format as a float.
    def findMedianSortedArrays(self, nums1: list[int], nums2: list[int]) -> float:
        # We treat nums1 as the input binary string 's'.
        s: str = nums1

        MOD = 10**9 + 7
        total_count = 0
        current_consecutive_ones = 0

        for char in s:
            if char == '1':
                current_consecutive_ones += 1
            else: # char == '0'
                # If a block of '1's just ended, calculate its contribution.
                # A block of 'k' ones ("1...1", k times) has k * (k + 1) / 2 substrings.
                if current_consecutive_ones > 0:
                    contribution = current_consecutive_ones * (current_consecutive_ones + 1) // 2
                    total_count = (total_count + contribution) % MOD
                current_consecutive_ones = 0 # Reset count for '1's, as a '0' breaks the sequence

        # After the loop, check if there's a trailing block of '1's at the end of the string.
        # This handles cases like "111" or "011".
        if current_consecutive_ones > 0:
            contribution = current_consecutive_ones * (current_consecutive_ones + 1) // 2
            total_count = (total_count + contribution) % MOD

        # The problem asks for an integer count. The driver code will implicitly
        # convert this integer to a float (e.g., 9 -> 9.00000) for printing.
        return total_count

# --- Execution Driver ---
import sys, json, math
try:
    input_lines = sys.stdin.read().strip().split('\n')
    if len(input_lines) >= 2:
        # Assume input lines are JSON strings representing arrays
        nums1 = json.loads(input_lines[0])
        nums2 = json.loads(input_lines[1])
    elif len(input_lines) == 1 and input_lines[0]:
        # Handle single array input (if problem was different)
        nums1 = json.loads(input_lines[0])
        nums2 = []
    else:
        # Empty input case
        nums1 = []
        nums2 = []

    # Instantiate and call the solution method
    result = Solution().findMedianSortedArrays(nums1, nums2)
    # Print result formatted to match test expectations
    print(f'{result:.5f}')
except Exception:
    # Suppress errors, let the empty output fail the test
    pass

````

## 🧪 Test Execution

| Test # | Status | Input (Snippet) | Expected | Actual | Error Snippet |

|---|---|---|---|---|---|

| 0 (auto) | **❌ FAIL** | `|` | `0.00000` | `None` |

## 🔗 Similar Problems

- Count Binary Substrings - https://leetcode.com/problems/count-binary-substrings/

- Count of substrings of a given Binary string with all ... - https://www.geeksforgeeks.org/dsa/count-of-substrings-of-a-given-binary-string-with-all-characters-same/

- Count of sub-strings with equal consecutive 0's and 1's - https://www.geeksforgeeks.org/dsa/count-of-sub-strings-with-equal-consecutive-0s-and-1s/

---

### Execution Metadata

- **Problem Title:** Streamlit Submitted Problem

- **Timestamp:** 2025-11-16 17:02:32
