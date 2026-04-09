# Frontend (Connected)

This folder contains the first frontend implementation for the Compiler + Time Complexity Analyzer.

## Included

- `index.html`: UI layout and section structure for all compiler phases.
- `styles.css`: Responsive styling, custom typography, animated background, and phase panels.
- `app.js`: Frontend logic for sample loading, Analyze action, and output rendering.

## Backend Contract (next step)

The Analyze button calls:

- `POST /api/analyze`
- JSON body: `{ "source": "<C/C++ code>" }`

Expected JSON response fields:

- `tokens_count`
- `syntax_error_count`
- `semantic_error_count`
- `complexity`
- `lexical`
- `syntax`
- `semantic`
- `ir`
- `optimization`
- `codegen`
- `complexity_detail`

## Run Connected App

From the project root:

```bash
python server.py
```

Then open:

- `http://127.0.0.1:8000`

The frontend and backend are now wired. Clicking Analyze sends code to `/api/analyze` and renders real phase outputs.
