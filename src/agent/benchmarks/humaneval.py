"""
HumanEval Dataset — Standardized coding benchmarks.
"""

from dataclasses import dataclass


@dataclass
class BenchmarkProblem:
    """A single coding benchmark challenge."""

    task_id: str
    prompt: str
    reference_code: str
    test_code: str
    entry_point: str = ""
    difficulty: str = "medium"


BENCHMARK_PROBLEMS: list[BenchmarkProblem] = [
    BenchmarkProblem(
        task_id="BENCH/001",
        prompt="Write a function `two_sum(nums, target)` that returns indices of two numbers that add up to target.",
        reference_code="""
def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        comp = target - n
        if comp in seen:
            return [seen[comp], i]
        seen[n] = i
    return []
""",
        test_code="""
assert two_sum([2, 7, 11, 15], 9) == [0, 1]
assert two_sum([3, 2, 4], 6) == [1, 2]
assert two_sum([3, 3], 6) == [0, 1]
print("PASS")
""",
        entry_point="two_sum",
        difficulty="easy",
    ),
    BenchmarkProblem(
        task_id="BENCH/002",
        prompt="Write a function `fibonacci(n)` that returns the nth Fibonacci number (0-indexed).",
        reference_code="""
def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
""",
        test_code="""
assert fibonacci(0) == 0
assert fibonacci(1) == 1
assert fibonacci(10) == 55
assert fibonacci(20) == 6765
print("PASS")
""",
        entry_point="fibonacci",
        difficulty="easy",
    ),
    BenchmarkProblem(
        task_id="BENCH/003",
        prompt="Write a function `is_palindrome(s)` that checks if a string is a palindrome, ignoring non-alphanumeric chars.",
        reference_code="""
def is_palindrome(s):
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]
""",
        test_code="""
assert is_palindrome("racecar") == True
assert is_palindrome("A man, a plan, a canal: Panama") == True
assert is_palindrome("hello") == False
assert is_palindrome("") == True
print("PASS")
""",
        entry_point="is_palindrome",
        difficulty="easy",
    ),
    BenchmarkProblem(
        task_id="BENCH/004",
        prompt="Write a function `flatten(lst)` that recursively flattens a nested list.",
        reference_code="""
def flatten(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result
""",
        test_code="""
assert flatten([1, [2, 3], [4, [5, 6]]]) == [1, 2, 3, 4, 5, 6]
assert flatten([]) == []
assert flatten([1, 2, 3]) == [1, 2, 3]
assert flatten([[[[1]]]]) == [1]
print("PASS")
""",
        entry_point="flatten",
        difficulty="easy",
    ),
    BenchmarkProblem(
        task_id="BENCH/005",
        prompt="Write a function `max_subarray_sum(nums)` that finds contiguous subarray with largest sum (Kadane's algorithm).",
        reference_code="""
def max_subarray_sum(nums):
    if not nums:
        return 0
    max_sum = current = nums[0]
    for n in nums[1:]:
        current = max(n, current + n)
        max_sum = max(max_sum, current)
    return max_sum
""",
        test_code="""
assert max_subarray_sum([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
assert max_subarray_sum([1]) == 1
assert max_subarray_sum([-1, -2, -3]) == -1
assert max_subarray_sum([5, 4, -1, 7, 8]) == 23
print("PASS")
""",
        entry_point="max_subarray_sum",
        difficulty="medium",
    ),
    BenchmarkProblem(
        task_id="BENCH/006",
        prompt="Write a function `merge_intervals(intervals)` that merges overlapping intervals.",
        reference_code="""
def merge_intervals(intervals):
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
""",
        test_code="""
assert merge_intervals([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]
assert merge_intervals([[1,4],[4,5]]) == [[1,5]]
assert merge_intervals([]) == []
print("PASS")
""",
        entry_point="merge_intervals",
        difficulty="medium",
    ),
    BenchmarkProblem(
        task_id="BENCH/007",
        prompt="Write a function `longest_common_prefix(strs)` that finds the longest common prefix amongst strings.",
        reference_code="""
def longest_common_prefix(strs):
    if not strs:
        return ""
    prefix = strs[0]
    for s in strs[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix
""",
        test_code="""
assert longest_common_prefix(["flower","flow","flight"]) == "fl"
assert longest_common_prefix(["dog","racecar","car"]) == ""
assert longest_common_prefix(["interspecies","interstellar","interstate"]) == "inters"
assert longest_common_prefix([""]) == ""
print("PASS")
""",
        entry_point="longest_common_prefix",
        difficulty="easy",
    ),
    BenchmarkProblem(
        task_id="BENCH/008",
        prompt="Write a function `roman_to_int(s)` that converts a Roman numeral string to an integer.",
        reference_code="""
def roman_to_int(s):
    values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    total = 0
    for i in range(len(s)):
        if i + 1 < len(s) and values[s[i]] < values[s[i+1]]:
            total -= values[s[i]]
        else:
            total += values[s[i]]
    return total
""",
        test_code="""
assert roman_to_int("III") == 3
assert roman_to_int("IV") == 4
assert roman_to_int("IX") == 9
assert roman_to_int("MCMXCIV") == 1994
print("PASS")
""",
        entry_point="roman_to_int",
        difficulty="medium",
    ),
    BenchmarkProblem(
        task_id="BENCH/009",
        prompt="Write a function `group_anagrams(strs)` that groups anagrams together from a list of strings.",
        reference_code="""
from collections import defaultdict
def group_anagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))
        groups[key].append(s)
    return list(groups.values())
""",
        test_code="""
result = group_anagrams(["eat","tea","tan","ate","nat","bat"])
result_sorted = [sorted(g) for g in result]
result_sorted.sort()
assert result_sorted == [['bat'], ['ate', 'eat', 'tea'], ['nat', 'tan']]
print("PASS")
""",
        entry_point="group_anagrams",
        difficulty="medium",
    ),
    BenchmarkProblem(
        task_id="BENCH/010",
        prompt="Write a function `valid_parentheses(s)` that checks if a string of brackets is valid.",
        reference_code="""
def valid_parentheses(s):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for c in s:
        if c in '([{':
            stack.append(c)
        elif c in ')]}':
            if not stack or stack[-1] != pairs[c]:
                return False
            stack.pop()
    return len(stack) == 0
""",
        test_code="""
assert valid_parentheses("()[]{}") == True
assert valid_parentheses("(]") == False
assert valid_parentheses("([)]") == False
assert valid_parentheses("{[]}") == True
assert valid_parentheses("") == True
print("PASS")
""",
        entry_point="valid_parentheses",
        difficulty="easy",
    ),
    BenchmarkProblem(
        task_id="BENCH/011",
        prompt="Write a function `binary_search(arr, target)` that returns index of target in sorted array, or -1.",
        reference_code="""
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1
""",
        test_code="""
assert binary_search([1, 3, 5, 7, 9], 5) == 2
assert binary_search([1, 3, 5, 7, 9], 6) == -1
assert binary_search([], 1) == -1
assert binary_search([1], 1) == 0
print("PASS")
""",
        entry_point="binary_search",
        difficulty="easy",
    ),
    BenchmarkProblem(
        task_id="BENCH/012",
        prompt="Write a function `matrix_multiply(A, B)` that multiplies two matrices.",
        reference_code="""
def matrix_multiply(A, B):
    rows_a, cols_a = len(A), len(A[0])
    cols_b = len(B[0])
    result = [[0] * cols_b for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += A[i][k] * B[k][j]
    return result
""",
        test_code="""
assert matrix_multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]]) == [[19, 22], [43, 50]]
assert matrix_multiply([[1]], [[1]]) == [[1]]
print("PASS")
""",
        entry_point="matrix_multiply",
        difficulty="medium",
    ),
    BenchmarkProblem(
        task_id="BENCH/013",
        prompt="Write a function `lru_cache_manual(capacity)` implementing an LRU cache.",
        reference_code="""
from collections import OrderedDict
def lru_cache_manual(capacity):
    cache = OrderedDict()
    def get(key):
        if key not in cache: return -1
        cache.move_to_end(key)
        return cache[key]
    def put(key, value):
        if key in cache:
            cache.move_to_end(key)
        cache[key] = value
        if len(cache) > capacity:
            cache.popitem(last=False)
    return get, put
""",
        test_code="""
get, put = lru_cache_manual(2)
put(1, 1)
put(2, 2)
assert get(1) == 1
put(3, 3)
assert get(2) == -1
print("PASS")
""",
        entry_point="lru_cache_manual",
        difficulty="hard",
    ),
    BenchmarkProblem(
        task_id="BENCH/014",
        prompt="Write a function `count_islands(grid)` that counts islands in a 2D binary grid.",
        reference_code="""
def count_islands(grid):
    if not grid: return 0
    count = 0
    rows, cols = len(grid), len(grid[0])
    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1':
            return
        grid[r][c] = '#'
        dfs(r+1, c); dfs(r-1, c); dfs(r, c+1); dfs(r, c-1)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                dfs(r, c)
                count += 1
    return count
""",
        test_code="""
grid = [['1','1','0','0','0'],['1','1','0','0','0'],['0','0','1','0','0'],['0','0','0','1','1']]
assert count_islands(grid) == 3
print("PASS")
""",
        entry_point="count_islands",
        difficulty="medium",
    ),
    BenchmarkProblem(
        task_id="BENCH/015",
        prompt="Write `serialize(root)` and `deserialize(data)` for a binary tree.",
        reference_code="""
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val; self.left = left; self.right = right

def serialize(root):
    if not root: return "null"
    return f"{root.val},{serialize(root.left)},{serialize(root.right)}"

def deserialize(data):
    vals = iter(data.split(","))
    def build():
        v = next(vals)
        if v == "null": return None
        node = TreeNode(int(v))
        node.left = build()
        node.right = build()
        return node
    return build()
""",
        test_code="""
root = TreeNode(1, TreeNode(2), TreeNode(3, TreeNode(4), TreeNode(5)))
s = serialize(root)
root2 = deserialize(s)
assert root2.val == 1
assert root2.left.val == 2
assert root2.right.right.val == 5
print("PASS")
""",
        entry_point="serialize",
        difficulty="hard",
    ),
    BenchmarkProblem(
        task_id="BENCH/016",
        prompt="Write a function `top_k_frequent(nums, k)` that returns the k most frequent elements.",
        reference_code="""
from collections import Counter
def top_k_frequent(nums, k):
    return [x for x, _ in Counter(nums).most_common(k)]
""",
        test_code="""
assert sorted(top_k_frequent([1,1,1,2,2,3], 2)) == [1, 2]
assert top_k_frequent([1], 1) == [1]
print("PASS")
""",
        entry_point="top_k_frequent",
        difficulty="easy",
    ),
    BenchmarkProblem(
        task_id="BENCH/017",
        prompt="Write a function `coin_change(coins, amount)` returning fewest coins needed, or -1.",
        reference_code="""
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
""",
        test_code="""
assert coin_change([1, 5, 10, 25], 63) == 6
assert coin_change([2], 3) == -1
assert coin_change([1], 0) == 0
print("PASS")
""",
        entry_point="coin_change",
        difficulty="medium",
    ),
    BenchmarkProblem(
        task_id="BENCH/018",
        prompt="Write a function `longest_substring_without_repeat(s)` returning length of longest substring without duplicates.",
        reference_code="""
def longest_substring_without_repeat(s):
    seen = {}
    start = max_len = 0
    for i, c in enumerate(s):
        if c in seen and seen[c] >= start:
            start = seen[c] + 1
        seen[c] = i
        max_len = max(max_len, i - start + 1)
    return max_len
""",
        test_code="""
assert longest_substring_without_repeat("abcabcbb") == 3
assert longest_substring_without_repeat("bbbbb") == 1
assert longest_substring_without_repeat("pwwkew") == 3
assert longest_substring_without_repeat("") == 0
print("PASS")
""",
        entry_point="longest_substring_without_repeat",
        difficulty="medium",
    ),
    BenchmarkProblem(
        task_id="BENCH/019",
        prompt="Write a function `min_window_substring(s, t)` returning minimum window in s containing all characters of t.",
        reference_code="""
from collections import Counter
def min_window_substring(s, t):
    if not t or not s: return ""
    need = Counter(t)
    have = {}
    formed = 0
    required = len(need)
    ans = (float('inf'), 0, 0)
    l = 0
    for r, c in enumerate(s):
        have[c] = have.get(c, 0) + 1
        if c in need and have[c] == need[c]:
            formed += 1
        while formed == required:
            if r - l + 1 < ans[0]:
                ans = (r - l + 1, l, r + 1)
            have[s[l]] -= 1
            if s[l] in need and have[s[l]] < need[s[l]]:
                formed -= 1
            l += 1
    return "" if ans[0] == float('inf') else s[ans[1]:ans[2]]
""",
        test_code="""
assert min_window_substring("ADOBECODEBANC", "ABC") == "BANC"
assert min_window_substring("a", "a") == "a"
assert min_window_substring("a", "aa") == ""
print("PASS")
""",
        entry_point="min_window_substring",
        difficulty="hard",
    ),
    BenchmarkProblem(
        task_id="BENCH/020",
        prompt="Write a function `calculate(expression)` that evaluates a basic math expression string (+, -, *, /).",
        reference_code="""
def calculate(expression):
    def helper(tokens, pos):
        stack = []
        num = 0
        sign = '+'
        while pos < len(tokens):
            token = tokens[pos]
            if token.isdigit():
                num = int(token)
            if token == '(':
                num, pos = helper(tokens, pos + 1)
            if (not token.isdigit() and token != ' ' and token != '(') or pos == len(tokens) - 1:
                if sign == '+': stack.append(num)
                elif sign == '-': stack.append(-num)
                elif sign == '*': stack.append(stack.pop() * num)
                elif sign == '/': stack.append(int(stack.pop() / num))
                sign = token
                num = 0
            if token == ')':
                return sum(stack), pos
            pos += 1
        return sum(stack), pos
    import re
    tokens = re.findall(r'\\d+|[+\\-*/()]', expression.replace(' ', ''))
    result, _ = helper(tokens, 0)
    return result
""",
        test_code="""
assert calculate("3+2*2") == 7
assert calculate("3+5 / 2") == 5
assert calculate("(1+(4+5+2)-3)+(6+8)") == 23
print("PASS")
""",
        entry_point="calculate",
        difficulty="hard",
    ),
]
