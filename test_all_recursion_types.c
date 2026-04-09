#include <stdio.h>
#include <string.h>

// ===== LINEAR RECURSION (n levels each O(1) work) =====

// Simple linear: T(n) = T(n-1) + O(1) → O(n)
int sum_recursive(int n) {
    if (n <= 0) return 0;
    return n + sum_recursive(n - 1);
}

// Power function: T(n) = T(n-1) + O(1) → O(n)
int power(int base, int exp) {
    if (exp == 0) return 1;
    return base * power(base, exp - 1);
}

// ===== LOGARITHMIC RECURSION (log n levels each O(1) work) =====

// Power with halving: T(n) = T(n/2) + O(1) → O(log n)
int power_log(int base, int exp) {
    if (exp == 0) return 1;
    if (exp % 2 == 0)
        return power_log(base * base, exp / 2);
    else
        return base * power_log(base, exp - 1);
}

// GCD using Euclidean algorithm: T(n) = T(n/2) + O(1) → O(log n)
int gcd(int a, int b) {
    if (b == 0) return a;
    return gcd(b, a % b);
}

// ===== BRANCHING RECURSION WITH LINEAR WORK =====

// Tree summation: T(n) = 2*T(n/2) + O(n) → O(n log n)
int sum_array_divide_conquer(int arr[], int left, int right) {
    if (left == right) return arr[left];
    int mid = (left + right) / 2;
    return sum_array_divide_conquer(arr, left, mid) + 
           sum_array_divide_conquer(arr, mid + 1, right);
}

// ===== EXPONENTIAL BRANCHING RECURSION =====

// Tribonacci: T(n) = 3*T(n-1) + O(1) → O(3^n)
int tribonacci(int n) {
    if (n <= 0) return 0;
    if (n == 1 || n == 2) return 1;
    return tribonacci(n - 1) + tribonacci(n - 2) + tribonacci(n - 3);
}

// ===== DIVIDE AND CONQUER (known algorithms) =====

// Merge sort helper: already tested separately
// Quick sort helper: already tested separately

// ===== EXPONENTIAL WITH CONTROL FLOW (only one path) =====

// Linear search in tree: T(n) = T(n/2) if found else T(n-1) → O(n) worst case
int tree_search(int arr[], int n, int target) {
    if (n <= 0) return -1;
    if (arr[n - 1] == target) return n - 1;
    if (arr[0] <= target)
        return tree_search(arr + 1, n - 1, target);
    else
        return tree_search(arr, n - 1, target);
}

// ===== MUTUAL RECURSION =====

// isEven/isOdd: T(n) = T(n-1) + O(1) → O(n)
int is_even(int n);
int is_odd(int n);

int is_even(int n) {
    if (n == 0) return 1;
    return is_odd(n - 1);
}

int is_odd(int n) {
    if (n == 0) return 0;
    return is_even(n - 1);
}

int main() {
    printf("Sum: %d\n", sum_recursive(5));
    printf("Power: %d\n", power(2, 3));
    printf("Log Power: %d\n", power_log(2, 8));
    printf("GCD: %d\n", gcd(48, 18));
    printf("Tribonacci: %d\n", tribonacci(5));
    return 0;
}
