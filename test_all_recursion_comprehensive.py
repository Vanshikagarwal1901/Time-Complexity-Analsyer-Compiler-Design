from compiler_analyzer.complexity import ComplexityAnalyzer

analyzer = ComplexityAnalyzer()

# Read all recursive patterns from the test file
with open('test_all_recursion_types.c', 'r') as f:
    all_code = f.read()

# Extract each function
test_cases = [
    # Linear recursion patterns
    ('sum_recursive', 'O(n)', 'Linear: T(n)=T(n-1)+O(1)'),
    ('power', 'O(n)', 'Linear: T(n)=T(n-1)+O(1)'),
    
    # Logarithmic patterns
    ('power_log', 'O(log n)', 'Logarithmic: T(n)=T(n/2)+O(1)'),
    ('gcd', 'O(log n)', 'Logarithmic: T(n)=T(n/2)+O(1)'),
    
    # Divide and conquer (without merge work it's O(n), not O(n log n))
    ('sum_array_divide_conquer', 'O(n)', 'Divide-Conquer: T(n)=2T(n/2)+O(1) = O(n)'),
    
    # Exponential branching
    ('tribonacci', 'O(3^n)', 'Exponential: T(n)=3T(n-1)+O(1)'),
    
    # If/else branching (single path)
    ('tree_search', 'O(n)', 'Control flow (one path): T(n)=T(n/2) or T(n-1)'),
    
    # Mutual recursion
    ('is_even', 'O(n)', 'Mutual recursion: T(n)=T(n-1)+O(1)'),
    ('is_odd', 'O(n)', 'Mutual recursion: T(n)=T(n-1)+O(1)'),
]

print("=" * 90)
print("RECURSION TREE ANALYSIS - COMPREHENSIVE TEST")
print("=" * 90)
print()

results = []
for func_name, expected, description in test_cases:
    try:
        # Extract just the function we're testing
        func_start = all_code.find(f'int {func_name}(')
        if func_start == -1:
            func_start = all_code.find(f'{func_name}(')
        
        if func_start == -1:
            print(f"[FAIL] {func_name:30} NOT FOUND")
            continue
        
        # Find end of function body
        brace_count = 0
        func_end = func_start
        started = False
        for i in range(func_start, len(all_code)):
            if all_code[i] == '{':
                started = True
                brace_count += 1
            elif all_code[i] == '}':
                brace_count -= 1
                if started and brace_count == 0:
                    func_end = i + 1
                    break
        
        if func_end == func_start:
            print(f"[FAIL] {func_name:30} PARSE ERROR")
            continue
        
        func_code = all_code[func_start:func_end]
        
        # For mutual recursion, include both functions
        if func_name == 'is_odd':
            func_code = all_code  # Include both is_even and is_odd
        elif func_name == 'is_even':
            func_code = all_code  # Include both functions
        
        result = analyzer.analyze(func_code)
        got = result.complexity
        
        status = "PASS" if got == expected else "FAIL"
        results.append((func_name, expected, got, status, description))
        
        print(f"[{status}] {func_name:25} | Expected: {expected:12} | Got: {got:12}")
        
    except Exception as e:
        print(f"[ERR ] {func_name:30} ERROR: {str(e)[:50]}")
        results.append((func_name, expected, "ERROR", "FAIL", description))

print()
print("=" * 90)
print("SUMMARY")
print("=" * 90)

passed = sum(1 for r in results if r[3] == "PASS")
total = len(results)

print(f"Tests Passed: {passed}/{total}")

if passed == total:
    print("[OK] All recursion patterns correctly identified!")
else:
    print("\n[FAILED] Tests that failed:")
    for name, expected, got, status, desc in results:
        if status != "PASS":
            print(f"  {name:25} Expected: {expected:12} Got: {got:12}")
            print(f"    Pattern: {desc}")

print()
print("=" * 90)
