from compiler_analyzer.complexity import ComplexityAnalyzer

# Test 1: Fibonacci (branching recursion, linear reduction)
fibonacci_code = '''
int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}
'''

analyzer = ComplexityAnalyzer()
result = analyzer.analyze(fibonacci_code)
print('=== FIBONACCI (branching, linear reduction) ===')
print(f'Complexity: {result.complexity}')
print('Analysis:')
for step in result.steps:
    print(f'  {step}')
print()

# Test 2: Factorial (single recursion, linear reduction)
factorial_code = '''
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n-1);
}
'''

result = analyzer.analyze(factorial_code)
print('=== FACTORIAL (single, linear reduction) ===')
print(f'Complexity: {result.complexity}')
print('Analysis:')
for step in result.steps:
    print(f'  {step}')
print()

# Test 3: Binary Search (single recursion, logarithmic)
binary_search_code = '''
int binarySearch(int arr[], int left, int right, int x) {
    if (left > right) return -1;
    int mid = (left + right) / 2;
    if (arr[mid] == x) return mid;
    if (arr[mid] > x)
        return binarySearch(arr, left, mid - 1, x);
    else
        return binarySearch(arr, mid + 1, right, x);
}
'''

result = analyzer.analyze(binary_search_code)
print('=== BINARY SEARCH (single, logarithmic reduction) ===')
print(f'Complexity: {result.complexity}')
print('Analysis:')
for step in result.steps:
    print(f'  {step}')
