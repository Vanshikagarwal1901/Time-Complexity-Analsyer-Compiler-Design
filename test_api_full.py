import json
import urllib.request

test_files = [
    ('test_merge_sort.c', 'O(n log n)'),
    ('test_quick_sort.c', 'O(n log n)'),
    ('test_jump_search.c', 'O(√n)'),
]

# Also test recursion patterns through samples
recursion_tests = [
    ('samples/fibonacci.c', 'O(2^n)', 'Fibonacci - branching rec'),
    ('samples/binary_search.c', 'O(log n)', 'Binary Search - log rec'),
]

print('=== SORTING/SEARCHING ALGORITHMS ===')
for filename, expected in test_files:
    try:
        with open(filename, 'r') as f:
            code = f.read()
        
        payload = {'source': code}
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request('http://localhost:8000/api/analyze', data=data, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            got = result['complexity']
            status = '✓ PASS' if got == expected else '✗ FAIL'
            print(f'{filename:20} Expected: {expected:15} Got: {got:15} {status}')
    except Exception as e:
        print(f'{filename:20} ERROR: {str(e)[:40]}')

print()
print('=== RECURSION PATTERNS ===')
for filename, expected, desc in recursion_tests:
    try:
        with open(filename, 'r') as f:
            code = f.read()
        
        payload = {'source': code}
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request('http://localhost:8000/api/analyze', data=data, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            got = result['complexity']
            status = '✓ PASS' if got == expected else '✗ FAIL'
            print(f'{desc:30} Expected: {expected:10} Got: {got:10} {status}')
    except Exception as e:
        print(f'{desc:30} ERROR: {str(e)[:40]}')
