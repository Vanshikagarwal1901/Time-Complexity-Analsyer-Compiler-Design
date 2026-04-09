from compiler_analyzer.complexity import ComplexityAnalyzer
import re

# Test the counting logic
fib_body = '''
if (n <= 1) return n;
return fibonacci(n-1) + fibonacci(n-2);
"'''

pattern = r'\bfibonacci\s*\('
matches = re.findall(pattern, fib_body)
print(f"Fibonacci body matches: {len(matches)}")
print(f"All matches: {matches}")

# The -1 is for the function definition, but there is no function definition in body
total = len(matches) - 1 if 'def ' in fib_body or 'fibonacci(' in fib_body.split('\n')[0] else len(matches)
print(f"Total calls: {total}")
