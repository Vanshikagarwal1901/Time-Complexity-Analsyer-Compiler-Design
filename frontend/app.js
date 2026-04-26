const sourceInput = document.getElementById("sourceInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const clearBtn = document.getElementById("clearBtn");
const sampleSelect = document.getElementById("sampleSelect");
const summaryCards = document.getElementById("summaryCards");
const statusText = document.getElementById("statusText");
const statusDot = document.getElementById("statusDot");
const expandAllBtn = document.getElementById("expandAllBtn");
const collapseAllBtn = document.getElementById("collapseAllBtn");
const dependencyViz = document.getElementById("dependencyViz");
const recursionViz = document.getElementById("recursionViz");
const complexityViz = document.getElementById("complexityViz");
const exportButtons = document.querySelectorAll(".export-btn");

const panels = {
  lexicalOut: document.getElementById("lexicalOut"),
  syntaxOut: document.getElementById("syntaxOut"),
  parseTreeOut: document.getElementById("parseTreeOut"),
  semanticOut: document.getElementById("semanticOut"),
  suggestionOut: document.getElementById("suggestionOut"),
  irOut: document.getElementById("irOut"),
  optOut: document.getElementById("optOut"),
  codegenOut: document.getElementById("codegenOut"),
  complexityOut: document.getElementById("complexityOut"),
};

const vizState = {
  dependency: null,
  recursion: null,
  complexity: null,
};

const SAMPLES = {
  // ===== SEARCHING =====
  linear: `#include <stdio.h>\n\nint linearSearch(int arr[], int n, int key) {\n  for (int i = 0; i < n; i++) {\n    if (arr[i] == key) return i;\n  }\n  return -1;\n}\n\nint main() {\n  int arr[] = {10, 20, 30, 40, 50};\n  int n = 5;\n  int idx = linearSearch(arr, n, 30);\n  printf("%d\\n", idx);\n  return 0;\n}`,
  binary: `#include <stdio.h>\n\nint binarySearch(int arr[], int n, int target) {\n  int low = 0, high = n - 1;\n  while (low <= high) {\n    int mid = low + (high - low) / 2;\n    if (arr[mid] == target) return mid;\n    if (arr[mid] < target) low = mid + 1;\n    else high = mid - 1;\n  }\n  return -1;\n}\n\nint main() {\n  int arr[] = {2, 5, 8, 12, 16, 23, 38, 56};\n  int n = 8;\n  int idx = binarySearch(arr, n, 23);\n  printf("%d\\n", idx);\n  return 0;\n}`,
  jump: `#include <stdio.h>\n#include <math.h>\n\nint jumpSearch(int arr[], int n, int target) {\n  int step = (int)sqrt((double)n);\n  int prev = 0;\n\n  while (prev < n && arr[(step < n ? step : n) - 1] < target) {\n    prev = step;\n    step += (int)sqrt((double)n);\n    if (prev >= n) return -1;\n  }\n\n  while (prev < n && arr[prev] < target) {\n    prev++;\n    if (prev == (step < n ? step : n)) return -1;\n  }\n\n  if (prev < n && arr[prev] == target) return prev;\n  return -1;\n}\n\nint main() {\n  int arr[] = {1, 3, 5, 7, 9, 11, 13, 15, 17};\n  int n = 9;\n  int idx = jumpSearch(arr, n, 11);\n  printf("%d\\n", idx);\n  return 0;\n}`,

  // ===== SORTING =====
  bubble: `#include <stdio.h>\n\nvoid bubbleSort(int arr[], int n) {\n  for (int i = 0; i < n - 1; i++) {\n    for (int j = 0; j < n - i - 1; j++) {\n      if (arr[j] > arr[j + 1]) {\n        int t = arr[j];\n        arr[j] = arr[j + 1];\n        arr[j + 1] = t;\n      }\n    }\n  }\n}\n\nint main() {\n  int arr[] = {64, 34, 25, 12, 22, 11, 90};\n  int n = 7;\n  bubbleSort(arr, n);\n  for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n  printf("\\n");\n  return 0;\n}`,
  selection: `#include <stdio.h>\n\nvoid selectionSort(int arr[], int n) {\n  for (int i = 0; i < n - 1; i++) {\n    int minIdx = i;\n    for (int j = i + 1; j < n; j++) {\n      if (arr[j] < arr[minIdx]) minIdx = j;\n    }\n    int t = arr[i];\n    arr[i] = arr[minIdx];\n    arr[minIdx] = t;\n  }\n}\n\nint main() {\n  int arr[] = {29, 10, 14, 37, 13};\n  int n = 5;\n  selectionSort(arr, n);\n  for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n  printf("\\n");\n  return 0;\n}`,
  insertion: `#include <stdio.h>\n\nvoid insertionSort(int arr[], int n) {\n  for (int i = 1; i < n; i++) {\n    int key = arr[i];\n    int j = i - 1;\n    while (j >= 0 && arr[j] > key) {\n      arr[j + 1] = arr[j];\n      j--;\n    }\n    arr[j + 1] = key;\n  }\n}\n\nint main() {\n  int arr[] = {12, 11, 13, 5, 6};\n  int n = 5;\n  insertionSort(arr, n);\n  for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n  printf("\\n");\n  return 0;\n}`,
  merge: `#include <stdio.h>\n\nvoid merge(int arr[], int l, int m, int r) {\n  int n1 = m - l + 1;\n  int n2 = r - m;\n  int L[100], R[100];\n  for (int i = 0; i < n1; i++) L[i] = arr[l + i];\n  for (int j = 0; j < n2; j++) R[j] = arr[m + 1 + j];\n  int i = 0, j = 0, k = l;\n  while (i < n1 && j < n2) {\n    if (L[i] <= R[j]) arr[k++] = L[i++];\n    else arr[k++] = R[j++];\n  }\n  while (i < n1) arr[k++] = L[i++];\n  while (j < n2) arr[k++] = R[j++];\n}\n\nvoid mergeSort(int arr[], int l, int r) {\n  if (l < r) {\n    int m = l + (r - l) / 2;\n    mergeSort(arr, l, m);\n    mergeSort(arr, m + 1, r);\n    merge(arr, l, m, r);\n  }\n}\n\nint main() {\n  int arr[] = {38, 27, 43, 3, 9, 82, 10};\n  int n = 7;\n  mergeSort(arr, 0, n - 1);\n  for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n  printf("\\n");\n  return 0;\n}`,
  quick: `#include <stdio.h>\n\nint partition(int arr[], int low, int high) {\n  int pivot = arr[high];\n  int i = low - 1;\n  for (int j = low; j < high; j++) {\n    if (arr[j] <= pivot) {\n      i++;\n      int t = arr[i]; arr[i] = arr[j]; arr[j] = t;\n    }\n  }\n  int t = arr[i + 1]; arr[i + 1] = arr[high]; arr[high] = t;\n  return i + 1;\n}\n\nvoid quickSort(int arr[], int low, int high) {\n  if (low < high) {\n    int pi = partition(arr, low, high);\n    quickSort(arr, low, pi - 1);\n    quickSort(arr, pi + 1, high);\n  }\n}\n\nint main() {\n  int arr[] = {10, 7, 8, 9, 1, 5};\n  int n = 6;\n  quickSort(arr, 0, n - 1);\n  for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n  printf("\\n");\n  return 0;\n}`,

  // ===== RECURSION - LINEAR =====
  factorial: `#include <stdio.h>\n\nint factorial(int n) {\n  if (n <= 1) return 1;\n  return n * factorial(n - 1);\n}\n\nint main() {\n  int n = 6;\n  printf("6! = %d\\n", factorial(n));\n  return 0;\n}`,
  sum_recursive: `#include <stdio.h>\n\nint sum_recursive(int n) {\n  if (n <= 0) return 0;\n  return n + sum_recursive(n - 1);\n}\n\nint main() {\n  int n = 10;\n  printf("Sum 1 to %d = %d\\n", n, sum_recursive(n));\n  return 0;\n}`,
  power: `#include <stdio.h>\n\nint power(int base, int exp) {\n  if (exp == 0) return 1;\n  return base * power(base, exp - 1);\n}\n\nint main() {\n  printf("2^8 = %d\\n", power(2, 8));\n  return 0;\n}`,

  // ===== RECURSION - LOGARITHMIC =====
  power_log: `#include <stdio.h>\n\nint power_log(int base, int exp) {\n  if (exp == 0) return 1;\n  if (exp % 2 == 0) {\n    int half = power_log(base, exp / 2);\n    return half * half;\n  } else {\n    return base * power_log(base, exp - 1);\n  }\n}\n\nint main() {\n  printf("2^16 = %d\\n", power_log(2, 16));\n  return 0;\n}`,
  gcd: `#include <stdio.h>\n\nint gcd(int a, int b) {\n  if (b == 0) return a;\n  return gcd(b, a % b);\n}\n\nint main() {\n  printf("GCD(48, 18) = %d\\n", gcd(48, 18));\n  printf("GCD(100, 35) = %d\\n", gcd(100, 35));\n  return 0;\n}`,

  // ===== RECURSION - BRANCHING =====
  fibrec: `#include <stdio.h>\n\nint fibonacci(int n) {\n  if (n <= 1) return n;\n  return fibonacci(n - 1) + fibonacci(n - 2);\n}\n\nint main() {\n  printf("Fibonacci sequence:\\n");\n  for (int i = 0; i < 10; i++) printf("%d ", fibonacci(i));\n  printf("\\n");\n  return 0;\n}`,
  tribonacci: `#include <stdio.h>\n\nint tribonacci(int n) {\n  if (n <= 0) return 0;\n  if (n == 1 || n == 2) return 1;\n  return tribonacci(n - 1) + tribonacci(n - 2) + tribonacci(n - 3);\n}\n\nint main() {\n  printf("Tribonacci sequence:\\n");\n  for (int i = 0; i < 8; i++) printf("%d ", tribonacci(i));\n  printf("\\n");\n  return 0;\n}`,

  // ===== COMPLEXITY PATTERNS =====
  nested: `#include <stdio.h>\n\nint main() {\n  int n = 1000;\n  int sum = 0;\n  for (int i = 0; i < n; i++) {\n    for (int j = 1; j < n; j *= 2) {\n      sum += i + j;\n    }\n  }\n  printf("Result: %d\\n", sum);\n  return 0;\n}`,
  triangular: `#include <stdio.h>\n\nint main() {\n  int n = 1000;\n  int sum = 0;\n  for (int i = 0; i < n; i++) {\n    for (int j = 0; j < i; j++) {\n      sum += j;\n    }\n  }\n  printf("Result: %d\\n", sum);\n  return 0;\n}`,

  // ===== CONSTANT TIME =====
  const_simple: `#include <stdio.h>\n\nint main() {\n  int x = 5;\n  int y = 10;\n  int sum = x + y;\n  printf("Sum: %d\\n", sum);\n  return 0;\n}`,
  const_fixed_loop: `#include <stdio.h>\n\nint main() {\n  int arr[] = {1, 2, 3, 4, 5};\n  int sum = 0;\n  for (int i = 0; i < 5; i++) {\n    sum += arr[i];\n  }\n  printf("Sum of fixed 5 elements: %d\\n", sum);\n  return 0;\n}`,
  const_three_ops: `#include <stdio.h>\n\nint main() {\n  for (int i = 0; i < 10; i++) {\n    int tmp = i * 2;\n  }\n  printf("Done\\n");\n  return 0;\n}`,

  // ===== OPTIMIZATION DEMO =====
  optimization_demo: `#include <stdio.h>\n\nint compute(int n) {\n  int a = 5 + 3;\n  int b = 5 + 3;\n  int c = a + b;\n  int dead = 100;\n\n  if (0) {\n    c = c + 999;\n  }\n\n  int x = 10 * 2;\n  int y = x - 4;\n  int z = y + 0;\n  int w = z * 1;\n\n  return w + c;\n}\n\nint main() {\n  int result = compute(10);\n  printf("Result: %d\\n", result);\n  return 0;\n}`,

  // ===== NESTED LOOPS (3 loops) =====
  triple_nested: `#include <stdio.h>\n\nint main() {\n  int n = 100;\n  int count = 0;\n  for (int i = 0; i < n; i++) {\n    for (int j = 0; j < n; j++) {\n      for (int k = 0; k < n; k++) {\n        count++;\n      }\n    }\n  }\n  printf("Total iterations: %d\\n", count);\n  return 0;\n}`,
  triple_mixed: `#include <stdio.h>\n\nint main() {\n  int n = 100;\n  int sum = 0;\n  for (int i = 0; i < n; i++) {\n    for (int j = 0; j < n; j += 2) {\n      for (int k = 1; k < n; k *= 2) {\n        sum += i + j + k;\n      }\n    }\n  }\n  printf("Result: %d\\n", sum);\n  return 0;\n}`,
  triple_triangular: `#include <stdio.h>\n\nint main() {\n  int n = 100;\n  int sum = 0;\n  for (int i = 0; i < n; i++) {\n    for (int j = 0; j < i; j++) {\n      for (int k = 0; k < j; k++) {\n        sum++;\n      }\n    }\n  }\n  printf("Nested triangular sum: %d\\n", sum);\n  return 0;\n}`,
};

sampleSelect.addEventListener("change", () => {
  if (SAMPLES[sampleSelect.value]) {
    sourceInput.value = SAMPLES[sampleSelect.value];
  }
});

clearBtn.addEventListener("click", () => {
  sourceInput.value = "";
  sampleSelect.value = "";
  renderVisualAnalytics("", null);
  setStatus("Editor cleared.", true);
  sourceInput.focus();
});

async function runAnalysis() {
  const src = sourceInput.value.trim();
  if (!src) {
    setStatus("Please paste C/C++ code first.", false);
    return;
  }

  setBusy(true);

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: src }),
    });

    if (!response.ok) {
      throw new Error("Backend endpoint not available yet. Add /api/analyze server route next.");
    }

    const result = await response.json();
    renderResult(result);
    renderVisualAnalytics(src, result);
    setStatus("Analysis completed.", true);
  } catch (err) {
    renderFallback(src, String(err.message || err));
    renderVisualAnalytics(src, null);
    setStatus("Frontend ready. Waiting for backend API wiring.", false);
  } finally {
    setBusy(false);
  }
}

analyzeBtn.addEventListener("click", runAnalysis);

sourceInput.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    event.preventDefault();
    runAnalysis();
  }
});

expandAllBtn.addEventListener("click", () => setAllPanelsCollapsed(false));
collapseAllBtn.addEventListener("click", () => setAllPanelsCollapsed(true));

function setBusy(isBusy) {
  if (isBusy) {
    statusDot.classList.add("busy");
    statusText.textContent = "Analyzing...";
  } else {
    statusDot.classList.remove("busy");
  }
}

function setStatus(text, ok) {
  statusText.textContent = text;
  statusDot.style.background = ok ? "var(--ok)" : "var(--danger)";
}

function renderResult(result) {
  summaryCards.innerHTML = "";
  const cards = [
    ["Tokens", String(result.tokens_count || "-")],
    ["Syntax Errors", String(result.syntax_error_count || 0)],
    ["Semantic Errors", String(result.semantic_error_count || 0)],
    ["Semantic Warnings", String(result.semantic_warning_count || 0)],
    ["Complexity", String(result.complexity || "-")],
  ];

  cards.forEach(([label, value]) => {
    const el = document.createElement("div");
    el.className = "summary-card";
    el.innerHTML = `<span>${label}</span><strong>${value}</strong>`;
    summaryCards.appendChild(el);
  });

  panels.lexicalOut.textContent = result.lexical || "No lexical output.";
  panels.syntaxOut.textContent = result.syntax || "No syntax output.";
  renderParseTree3D(result.parse_tree || "No parse tree output.");
  panels.semanticOut.textContent = result.semantic || "No semantic output.";
  panels.suggestionOut.textContent = buildSuggestionOutput(result);
  panels.irOut.textContent = result.ir || "No IR output.";
  panels.optOut.textContent = result.optimization || "No optimization output.";
  panels.codegenOut.textContent = result.codegen || "No code generation output.";
  panels.complexityOut.textContent = result.complexity_detail || result.complexity || "No complexity output.";
}

function buildSuggestionOutput(result) {
  const suggestedCode = String(result.suggested_code || "").trim();
  const suggestedKind = String(result.suggested_code_kind || "none");
  const optimizationText = String(result.optimization || "");
  const hasOptimization = optimizationText && optimizationText !== "No optimizations." && optimizationText !== "No optimization rule was applicable.";
  const hasSemanticIssues = Number(result.semantic_error_count || 0) > 0 || Number(result.semantic_warning_count || 0) > 0 || Number(result.syntax_error_count || 0) > 0;

  if (suggestedCode) {
    if (suggestedKind === "source-fix") {
      return [
        "Corrected Source (from semantic/syntax guidance):",
        suggestedCode,
      ].join("\n\n");
    }

    if (suggestedKind === "optimized-code") {
      return [
        "Suggested Optimized Code:",
        suggestedCode,
      ].join("\n\n");
    }

    return suggestedCode;
  }

  const legacyExtract = extractSuggestedCodeFromGuidedFeedback(result.guided_feedback || "");
  if (legacyExtract) {
    return [
      "Corrected Source (from semantic/syntax guidance):",
      legacyExtract,
    ].join("\n\n");
  }

  if (hasOptimization) {
    return [
      "Optimization is present, but no direct source rewrite is available.",
      "See Optimization and Code Generation panels for transformed output.",
    ].join("\n");
  }

  if (hasSemanticIssues) {
    return "Semantic/syntax issues found, but no automatic code rewrite was generated.";
  }

  return "No suggestion needed: code is already valid and no optimization rewrite is available.";
}

function extractSuggestedCodeFromGuidedFeedback(feedback) {
  const marker = "Suggested Corrected Version:";
  const idx = feedback.indexOf(marker);
  if (idx < 0) return "";
  const block = feedback.slice(idx + marker.length).trim();
  return block;
}

function renderFallback(source, errorText) {
  const lineCount = source.split(/\r?\n/).length;
  const tokenApprox = source.split(/\s+/).filter(Boolean).length;

  summaryCards.innerHTML = `
    <div class="summary-card"><span>Source Lines</span><strong>${lineCount}</strong></div>
    <div class="summary-card"><span>Token Estimate</span><strong>${tokenApprox}</strong></div>
    <div class="summary-card"><span>Status</span><strong>Frontend Ready</strong></div>
    <div class="summary-card"><span>Backend</span><strong>Pending API</strong></div>
  `;

  panels.lexicalOut.textContent = "Frontend built. Awaiting /api/analyze response.";
  panels.syntaxOut.textContent = "Error: " + errorText;
  panels.parseTreeOut.textContent = "Parse tree panel is connected and ready for backend payload.";
  panels.semanticOut.textContent = "Next step: expose Python analyzer through an HTTP endpoint.";
  panels.suggestionOut.textContent = "Suggested corrected code will appear here when semantic fixes or optimization suggestions are available.";
  panels.irOut.textContent = "IR panel is connected and ready for backend payload.";
  panels.optOut.textContent = "Optimization panel is connected and ready for backend payload.";
  panels.codegenOut.textContent = "Codegen panel is connected and ready for backend payload.";
  panels.complexityOut.textContent = "Complexity panel is connected and ready for backend payload.";
}

function renderParseTree3D(treeText) {
  const records = parseTreeRecords(treeText);
  if (!records.length) {
    panels.parseTreeOut.textContent = treeText || "No parse tree output.";
    return;
  }

  const root = document.createElement("div");
  root.className = "tree-root";

  records.forEach((record) => {
    const card = document.createElement("section");
    card.className = "tree-record";

    const title = document.createElement("div");
    title.className = "tree-record-title";
    title.textContent = record.title;
    card.appendChild(title);

    const nodesWrap = document.createElement("div");
    nodesWrap.className = "tree-nodes";

    record.nodes.forEach((node) => {
      const row = document.createElement("div");
      row.className = "tree-node";
      row.style.setProperty("--depth", String(node.depth));

      const chip = document.createElement("span");
      chip.className = "tree-chip";
      chip.style.setProperty("--tilt", node.depth % 2 === 0 ? "-1.4deg" : "1.4deg");
      chip.textContent = node.label;
      row.appendChild(chip);
      nodesWrap.appendChild(row);
    });

    card.appendChild(nodesWrap);
    root.appendChild(card);
  });

  panels.parseTreeOut.innerHTML = "";
  panels.parseTreeOut.appendChild(root);
}

function initPhasePanels() {
  const phasePanels = document.querySelectorAll(".phase-panel");
  phasePanels.forEach((panel) => {
    if (panel.dataset.enhanced === "1") return;

    const heading = panel.querySelector("h3");
    const output = panel.querySelector(".output-box");
    if (!heading || !output) return;

    const title = heading.textContent.trim();
    const head = document.createElement("div");
    head.className = "phase-head";

    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "phase-toggle";
    toggle.dataset.label = title;
    toggle.setAttribute("aria-expanded", "true");

    const copy = document.createElement("button");
    copy.type = "button";
    copy.className = "panel-copy";
    copy.textContent = "Copy";

    head.appendChild(toggle);
    head.appendChild(copy);
    heading.replaceWith(head);

    setToggleLabel(toggle, true);

    toggle.addEventListener("click", () => {
      const expanded = !panel.classList.contains("collapsed");
      panel.classList.toggle("collapsed", expanded);
      setToggleLabel(toggle, !expanded);
      toggle.setAttribute("aria-expanded", String(!expanded));
    });

    copy.addEventListener("click", async () => {
      const text = output.innerText || output.textContent || "";
      try {
        await navigator.clipboard.writeText(text.trim());
        setStatus(`${title} copied.`, true);
      } catch {
        setStatus("Copy failed in this browser context.", false);
      }
    });

    panel.dataset.enhanced = "1";
  });
}

function setToggleLabel(toggleBtn, expanded) {
  const marker = expanded ? "▾" : "▸";
  toggleBtn.textContent = `${marker} ${toggleBtn.dataset.label}`;
}

function setAllPanelsCollapsed(collapsed) {
  const phasePanels = document.querySelectorAll(".phase-panel");
  phasePanels.forEach((panel) => {
    panel.classList.toggle("collapsed", collapsed);
    const toggle = panel.querySelector(".phase-toggle");
    if (toggle) {
      setToggleLabel(toggle, !collapsed);
      toggle.setAttribute("aria-expanded", String(!collapsed));
    }
  });
}

function parseTreeRecords(treeText) {
  if (!treeText || typeof treeText !== "string") return [];

  const lines = treeText.split(/\r?\n/);
  const records = [];
  let current = null;

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();
    if (!line.trim()) continue;

    if (line.startsWith("[")) {
      if (current && current.nodes.length) {
        records.push(current);
      }
      current = { title: line.trim(), nodes: [] };
      continue;
    }

    const markerIdx = Math.max(line.indexOf("├──"), line.indexOf("└──"));
    if (markerIdx === -1 || !current) continue;

    const prefix = line.slice(0, markerIdx);
    const depth = Math.max(0, Math.floor(prefix.length / 4));
    const label = line.slice(markerIdx + 3).replace(/^\s+/, "");
    current.nodes.push({ depth, label });
  }

  if (current && current.nodes.length) {
    records.push(current);
  }

  return records;
}

function renderVisualAnalytics(source, result) {
  const dependencyData = buildDependencyData(source);
  const recursionData = buildRecursionData(dependencyData);
  const complexityData = buildComplexityData(result);

  vizState.dependency = dependencyData;
  vizState.recursion = recursionData;
  vizState.complexity = complexityData;

  renderDependencySvg(dependencyViz, dependencyData);
  renderRecursionSvg(recursionViz, recursionData);
  renderComplexitySvg(complexityViz, complexityData);
}

function buildDependencyData(source) {
  const functions = extractFunctionBodies(source);
  const nodeNames = Object.keys(functions);
  const nodeSet = new Set(nodeNames);
  const edgeCountByPair = new Map();
  const recursiveCallCounts = {};

  for (const [name, info] of Object.entries(functions)) {
    const calls = info.body.match(/\b([A-Za-z_][A-Za-z0-9_]*)\s*\(/g) || [];
    recursiveCallCounts[name] = 0;
    for (const call of calls) {
      const callee = call.replace(/\s*\($/, "").trim();
      if (isControlKeyword(callee)) continue;
      if (!nodeSet.has(callee)) continue;
      if (callee === name) recursiveCallCounts[name] += 1;
      const id = `${name}->${callee}`;
      edgeCountByPair.set(id, (edgeCountByPair.get(id) || 0) + 1);
    }
  }

  const edges = Array.from(edgeCountByPair.entries()).map(([id, count]) => {
    const split = id.split("->");
    return {
      from: split[0],
      to: split[1],
      count,
    };
  });

  const sccGroups = computeSccGroups(nodeNames, edges);
  const groupByNode = {};
  sccGroups.forEach((group, idx) => {
    group.forEach((name) => {
      groupByNode[name] = idx;
    });
  });

  const recursiveGroups = sccGroups.filter((group) => {
    if (group.length > 1) return true;
    const only = group[0];
    return (recursiveCallCounts[only] || 0) > 0;
  });

  const cycleNodeSet = new Set(recursiveGroups.flat());

  const edgesWithCycle = edges.map((edge) => {
    const fromGroup = groupByNode[edge.from];
    const toGroup = groupByNode[edge.to];
    return {
      ...edge,
      inCycle: fromGroup === toGroup && cycleNodeSet.has(edge.from) && cycleNodeSet.has(edge.to),
    };
  });

  return {
    nodes: nodeNames.map((id) => ({ id })),
    edges: edgesWithCycle,
    recursiveCallCounts,
    recursiveGroups,
    groupByNode,
  };
}

function computeSccGroups(nodes, edges) {
  const adjacency = {};
  const reversed = {};
  nodes.forEach((name) => {
    adjacency[name] = [];
    reversed[name] = [];
  });

  edges.forEach((edge) => {
    if (!adjacency[edge.from]) adjacency[edge.from] = [];
    if (!reversed[edge.to]) reversed[edge.to] = [];
    adjacency[edge.from].push(edge.to);
    reversed[edge.to].push(edge.from);
  });

  const visited = new Set();
  const order = [];

  function dfsFill(node) {
    if (visited.has(node)) return;
    visited.add(node);
    (adjacency[node] || []).forEach((next) => dfsFill(next));
    order.push(node);
  }

  nodes.forEach((node) => dfsFill(node));

  const reversedVisited = new Set();
  const groups = [];

  function dfsCollect(node, group) {
    if (reversedVisited.has(node)) return;
    reversedVisited.add(node);
    group.push(node);
    (reversed[node] || []).forEach((next) => dfsCollect(next, group));
  }

  for (let i = order.length - 1; i >= 0; i--) {
    const node = order[i];
    if (reversedVisited.has(node)) continue;
    const group = [];
    dfsCollect(node, group);
    if (group.length) groups.push(group.sort());
  }

  return groups;
}

function extractFunctionBodies(source) {
  const map = {};
  const defRegex = /(?:^|\n)\s*(?:[A-Za-z_][A-Za-z0-9_\s\*]*?)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^;{}]*\)\s*\{/g;
  let match;

  while ((match = defRegex.exec(source)) !== null) {
    const name = match[1];
    const openIndex = source.indexOf("{", match.index);
    const closeIndex = findMatchingBrace(source, openIndex);
    if (openIndex === -1 || closeIndex === -1) continue;
    const body = source.slice(openIndex + 1, closeIndex);
    map[name] = {
      start: openIndex,
      end: closeIndex,
      body,
    };
  }

  return map;
}

function findMatchingBrace(source, openIndex) {
  if (openIndex < 0 || source[openIndex] !== "{") return -1;
  let depth = 0;
  for (let i = openIndex; i < source.length; i++) {
    const ch = source[i];
    if (ch === "{") depth += 1;
    if (ch === "}") {
      depth -= 1;
      if (depth === 0) return i;
    }
  }
  return -1;
}

function isControlKeyword(name) {
  return ["if", "for", "while", "switch", "return", "sizeof"].includes(name);
}

function buildRecursionData(dependencyData) {
  const directSelf = dependencyData.edges.find((edge) => edge.from === edge.to);
  const cycleGroup = dependencyData.recursiveGroups.find((group) => group.length > 1);
  const primary = directSelf ? directSelf.from : (cycleGroup ? cycleGroup[0] : null);

  if (!primary) {
    return {
      mode: "none",
      functionName: null,
      cycleMembers: [],
      levels: [],
      branching: 0,
      estimatedNodes: 0,
    };
  }

  const mode = directSelf ? "direct" : "indirect";
  const cycleMembers = cycleGroup || [primary];

  let callCount = dependencyData.recursiveCallCounts[primary] || 0;
  if (mode === "indirect") {
    const groupSet = new Set(cycleMembers);
    const internalEdges = dependencyData.edges.filter((edge) => groupSet.has(edge.from) && groupSet.has(edge.to));
    const outByNode = new Map();
    for (const edge of internalEdges) {
      const prev = outByNode.get(edge.from) || 0;
      outByNode.set(edge.from, prev + 1);
    }
    callCount = Math.max(1, ...outByNode.values());
  }

  const branching = Math.max(1, Math.min(4, callCount || 1));
  const maxDepth = branching === 1 ? 9 : branching === 2 ? 7 : branching === 3 ? 6 : 5;
  const levels = [];

  for (let depth = 0; depth <= maxDepth; depth++) {
    const count = branching === 1 ? 1 : Math.pow(branching, depth);
    const shownCount = Math.min(36, count);
    levels.push({ depth, count, shownCount });
  }

  const estimatedNodes = branching === 1
    ? levels.length
    : Math.round((Math.pow(branching, levels.length) - 1) / (branching - 1));

  return {
    mode,
    functionName: primary,
    cycleMembers,
    levels,
    branching,
    estimatedNodes,
  };
}

function buildComplexityData(result) {
  const complexity = (result && result.complexity) || "Unknown";
  const stepsText = (result && result.complexity_detail) || "";
  const steps = stepsText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .slice(0, 8);

  const terms = splitComplexityTerms(complexity);
  const bars = terms.map((term) => ({
    term,
    weight: complexityWeight(term),
  }));

  return {
    complexity,
    steps,
    bars,
  };
}

function splitComplexityTerms(complexity) {
  const clean = complexity.replace(/^O\(/i, "").replace(/\)$/i, "").trim();
  if (!clean || clean === "Unknown") return ["Unknown"];

  const plusTerms = clean.split("+").map((part) => part.trim()).filter(Boolean);
  const factors = [];

  plusTerms.forEach((term) => {
    term.split(/\*/).map((part) => part.trim()).filter(Boolean).forEach((part) => factors.push(part));
  });

  return factors.length ? factors : [clean];
}

function complexityWeight(term) {
  const normalized = term.toLowerCase().replace(/\s+/g, "");
  if (normalized === "1") return 1;
  if (normalized.includes("logn")) return 3;
  if (normalized.includes("sqrtn")) return 4;
  if (normalized === "n") return 5;
  if (normalized.includes("nlogn")) return 7;
  if (normalized.includes("n^2") || normalized.includes("n2")) return 9;
  if (normalized.includes("n^3") || normalized.includes("n3")) return 11;
  if (normalized.includes("2^n")) return 13;
  if (normalized.includes("3^n")) return 15;
  if (normalized.includes("^n")) return 14;
  return 6;
}

function renderDependencySvg(container, data) {
  if (!data.nodes.length) {
    container.textContent = "No functions found in source.";
    return;
  }

  const width = 980;
  const height = 460;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) / 2 - 84;
  const nodeRadius = data.nodes.length > 12 ? 20 : 24;

  const cycleNodes = new Set(data.recursiveGroups.flat());
  const cycleArray = data.nodes.filter((node) => cycleNodes.has(node.id));
  const nonCycleArray = data.nodes.filter((node) => !cycleNodes.has(node.id));

  const positions = {};
  nonCycleArray.forEach((node, idx) => {
    const angle = (Math.PI * 2 * idx) / Math.max(nonCycleArray.length, 1) - Math.PI / 2;
    positions[node.id] = {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
    };
  });

  cycleArray.forEach((node, idx) => {
    const angle = (Math.PI * 2 * idx) / Math.max(cycleArray.length, 1) - Math.PI / 2;
    const cycleRadius = Math.max(64, radius * 0.56);
    positions[node.id] = {
      x: centerX + cycleRadius * Math.cos(angle),
      y: centerY + cycleRadius * Math.sin(angle),
    };
  });

  const maxEdgeCount = Math.max(...data.edges.map((edge) => edge.count || 1), 1);

  const edgeSvg = data.edges
    .map((edge, idx) => {
      const a = positions[edge.from];
      const b = positions[edge.to];
      if (!a || !b) return "";
      const edgeClass = edge.inCycle ? "dep-edge dep-edge-cycle" : "dep-edge";
      const edgeWidth = 1.6 + ((edge.count || 1) / maxEdgeCount) * 1.6;

      if (edge.from === edge.to) {
        return `<path d="M ${a.x - 16} ${a.y - 18} C ${a.x + 25} ${a.y - 55}, ${a.x + 60} ${a.y - 10}, ${a.x + 20} ${a.y + 10}" class="dep-loop dep-edge-cycle" style="stroke-width:${edgeWidth}" marker-end="url(#arrow-${idx})"/>`;
      }

      return `<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" class="${edgeClass}" style="stroke-width:${edgeWidth}" marker-end="url(#arrow-${idx})"/>`;
    })
    .join("");

  const edgeLabels = data.edges
    .map((edge) => {
      if ((edge.count || 1) <= 1) return "";
      const a = positions[edge.from];
      const b = positions[edge.to];
      if (!a || !b) return "";

      if (edge.from === edge.to) {
        return `<text x="${a.x + 52}" y="${a.y - 26}" class="dep-edge-label">x${edge.count}</text>`;
      }

      const midX = (a.x + b.x) / 2;
      const midY = (a.y + b.y) / 2;
      return `<text x="${midX}" y="${midY - 6}" text-anchor="middle" class="dep-edge-label">x${edge.count}</text>`;
    })
    .join("");

  const defs = data.edges
    .map((_, idx) => `<marker id="arrow-${idx}" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#74e0ca"></path></marker>`)
    .join("");

  const nodeSvg = data.nodes
    .map((node) => {
      const pos = positions[node.id];
      const nodeClass = cycleNodes.has(node.id) ? "dep-node dep-node-cycle" : "dep-node";
      return [
        `<g class="${nodeClass}">`,
        `<circle cx="${pos.x}" cy="${pos.y}" r="${nodeRadius}"></circle>`,
        `<text x="${pos.x}" y="${pos.y + 4}" text-anchor="middle">${escapeXml(node.id)}</text>`,
        `</g>`,
      ].join("");
    })
    .join("");

  const cycleSummary = data.recursiveGroups.length
    ? `, ${data.recursiveGroups.length} recursive cluster${data.recursiveGroups.length > 1 ? "s" : ""}`
    : "";
  const totalCallSites = data.edges.reduce((sum, edge) => sum + (edge.count || 1), 0);

  container.innerHTML = `
    <svg class="viz-svg" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Dependency graph">
      <defs>${defs}</defs>
      ${edgeSvg}
      ${edgeLabels}
      ${nodeSvg}
    </svg>
    <div class="viz-caption">${data.nodes.length} functions, ${data.edges.length} unique call edges, ${totalCallSites} call sites${cycleSummary}.</div>
  `;
}

function renderRecursionSvg(container, data) {
  if (!data.functionName || !data.levels.length) {
    container.textContent = "No recursion cycle detected in current source.";
    return;
  }

  const width = 980;
  const height = 460;
  const levels = data.levels;
  const levelNodes = [];
  const lines = [];
  const depthLabels = [];

  levels.forEach((level) => {
    const y = 40 + (level.depth * (height - 92)) / Math.max(levels.length - 1, 1);
    depthLabels.push(`<text x="14" y="${y + 4}" class="rec-level-label">d=${level.depth} (${formatCount(level.count)})</text>`);
    const row = [];
    for (let i = 0; i < level.shownCount; i++) {
      const x = 108 + ((i + 1) * (width - 140)) / (level.shownCount + 1);
      row.push({ depth: level.depth, x, y, index: i });
    }
    levelNodes.push(row);
  });

  for (let depth = 0; depth < levelNodes.length - 1; depth++) {
    const parents = levelNodes[depth];
    const children = levelNodes[depth + 1];
    if (!parents.length || !children.length) continue;

    for (let i = 0; i < parents.length; i++) {
      const parent = parents[i];
      const start = Math.floor((i * children.length) / parents.length);
      const end = Math.floor(((i + 1) * children.length) / parents.length) - 1;
      const first = Math.max(0, Math.min(children.length - 1, start));
      const last = Math.max(first, Math.min(children.length - 1, end));
      let drawn = 0;

      for (let childIdx = first; childIdx <= last && drawn < data.branching; childIdx++) {
        const child = children[childIdx];
        lines.push(`<line x1="${parent.x}" y1="${parent.y}" x2="${child.x}" y2="${child.y}" class="rec-edge"/>`);
        drawn += 1;
      }

      if (drawn === 0) {
        const child = children[first];
        lines.push(`<line x1="${parent.x}" y1="${parent.y}" x2="${child.x}" y2="${child.y}" class="rec-edge"/>`);
      }
    }
  }

  const nodes = levelNodes.flat();

  const circles = nodes
    .map((node) => `<circle cx="${node.x}" cy="${node.y}" r="6" class="rec-node rec-d${node.depth % 4}"></circle>`)
    .join("");

  const descriptor = data.mode === "indirect"
    ? `Indirect recursion cluster: ${data.cycleMembers.map((item) => escapeXml(item)).join(" -> ")}`
    : `${escapeXml(data.functionName)} direct recursion`;

  const shownNodes = nodes.length;
  const deepest = levels[levels.length - 1] || { depth: 0, count: 1 };
  const levelRows = levels
    .slice(0, 8)
    .map((level) => `<li>Depth ${level.depth}: ${formatCount(level.count)} call${level.count === 1 ? "" : "s"}</li>`)
    .join("");

  const levelDetail = levelRows
    ? `<ul class="rec-steps">${levelRows}</ul>`
    : "";

  container.innerHTML = `
    <svg class="viz-svg" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Recursion tree">
      ${depthLabels.join("")}
      ${lines.join("")}
      ${circles}
    </svg>
    <div class="viz-caption">${descriptor}, branching factor ${data.branching}, depth ${deepest.depth}, approx ${formatCount(data.estimatedNodes)} calls (${formatCount(shownNodes)} nodes shown).</div>
    ${levelDetail}
  `;
}

function formatCount(value) {
  return Number(value || 0).toLocaleString();
}

function renderComplexitySvg(container, data) {
  const width = 740;
  const height = 270;
  const bars = data.bars.slice(0, 6);
  const maxWeight = Math.max(...bars.map((b) => b.weight), 1);

  const barHeight = 26;
  const gap = 12;
  const chartTop = 28;
  const labelWidth = 130;
  const chartWidth = width - labelWidth - 40;

  const barSvg = bars
    .map((bar, idx) => {
      const y = chartTop + idx * (barHeight + gap);
      const w = (bar.weight / maxWeight) * chartWidth;
      return [
        `<text x="14" y="${y + 17}" class="cmp-label">${escapeXml(bar.term)}</text>`,
        `<rect x="${labelWidth}" y="${y}" width="${w}" height="${barHeight}" rx="8" class="cmp-bar"></rect>`,
        `<text x="${labelWidth + w + 8}" y="${y + 17}" class="cmp-value">${bar.weight}</text>`,
      ].join("");
    })
    .join("");

  const stepList = data.steps.length
    ? `<ul class="cmp-steps">${data.steps.map((step) => `<li>${escapeXml(step)}</li>`).join("")}</ul>`
    : '<div class="viz-caption">No detailed complexity derivation steps returned by backend.</div>';

  container.innerHTML = `
    <svg class="viz-svg" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Complexity profile">
      <defs>
        <linearGradient id="cmpGradient" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stop-color="#ff8f3f"></stop>
          <stop offset="100%" stop-color="#46d1b7"></stop>
        </linearGradient>
      </defs>
      <text x="14" y="16" class="cmp-title">Overall: ${escapeXml(data.complexity)}</text>
      ${barSvg}
    </svg>
    ${stepList}
  `;
}

function escapeXml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

async function exportViz(vizName, format) {
  const container = document.getElementById(`${vizName}Viz`);
  const svg = container ? container.querySelector("svg") : null;
  const jsonData = vizState[vizName];
  const stamp = new Date().toISOString().replaceAll(":", "-").slice(0, 19);

  if (format === "json") {
    if (!jsonData) {
      setStatus("No visualization data available to export.", false);
      return;
    }
    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: "application/json" });
    triggerDownload(blob, `${vizName}-${stamp}.json`);
    setStatus(`${vizName} JSON exported.`, true);
    return;
  }

  if (!svg) {
    setStatus("No SVG available to export.", false);
    return;
  }

  const svgMarkup = new XMLSerializer().serializeToString(svg);
  if (format === "svg") {
    const blob = new Blob([svgMarkup], { type: "image/svg+xml;charset=utf-8" });
    triggerDownload(blob, `${vizName}-${stamp}.svg`);
    setStatus(`${vizName} SVG exported.`, true);
    return;
  }

  if (format === "png") {
    const pngBlob = await svgToPngBlob(svg, svgMarkup, 2);
    if (!pngBlob) {
      setStatus("PNG export failed.", false);
      return;
    }
    triggerDownload(pngBlob, `${vizName}-${stamp}.png`);
    setStatus(`${vizName} PNG exported.`, true);
  }
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

async function svgToPngBlob(svgElement, svgMarkup, scale) {
  return new Promise((resolve) => {
    const img = new Image();
    const blob = new Blob([svgMarkup], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);

    img.onload = () => {
      const canvas = document.createElement("canvas");
      const vb = svgElement.viewBox && svgElement.viewBox.baseVal;
      const baseWidth = (vb && vb.width) || svgElement.clientWidth || img.width || 740;
      const baseHeight = (vb && vb.height) || svgElement.clientHeight || img.height || 300;
      canvas.width = Math.max(1, Math.round(baseWidth * scale));
      canvas.height = Math.max(1, Math.round(baseHeight * scale));

      const ctx = canvas.getContext("2d");
      if (!ctx) {
        URL.revokeObjectURL(url);
        resolve(null);
        return;
      }

      ctx.fillStyle = "#081319";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((pngBlob) => {
        URL.revokeObjectURL(url);
        resolve(pngBlob || null);
      }, "image/png");
    };

    img.onerror = () => {
      URL.revokeObjectURL(url);
      resolve(null);
    };

    img.src = url;
  });
}

exportButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    exportViz(btn.dataset.viz, btn.dataset.format);
  });
});

initPhasePanels();
sourceInput.value = SAMPLES.linear;
renderVisualAnalytics(sourceInput.value, null);
