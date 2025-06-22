# Lazy Swap Shuffler

Generating a minimal sequence of lazy pair swaps to cover all N! combinations of a list of N-elements.

## 🔀 Problem

Given a sequence of `N` **distinct integers**, find the **shortest sequence of lazy pair swaps** `(i, j)` — where `i < j` — such that, when each swap is applied **probabilistically** (with a 50% chance), the set of all possible outcomes **covers all `N!` permutations**.

A *lazy swap* means:

- You **attempt** to swap elements at positions `i` and `j`.
- With **50% probability**, the swap is applied; otherwise, it is skipped.

The challenge is to find a minimal-length sequence of such swaps that, **when executed once per run with randomized decisions**, can produce *any* of the `N!` permutations — **uniformly and completely**.

---

## 📁 Data

I have generated pair sequences for `N < 6` so far and analyzed the co-occurrences within each combination. I plan to use this analysis to build a set generator that will greatly constrain the explosive search space so I can find pair combinations for `N > 10`.
