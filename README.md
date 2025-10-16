# OpenWrite

OpenWrite provides a lightweight, rule-based grammar checker that surfaces
common issues such as repeated words, missing capitalization, missing terminal
punctuation, double spaces and potentially run-on sentences.

## Installation

The project can be installed in editable mode for local development:

```bash
pip install -e .
```

## Usage

You can run the grammar checker against a file or standard input:

```bash
openwrite path/to/document.txt
```

To view contextual snippets for each issue, add `--show-context`:

```bash
openwrite --show-context path/to/document.txt
```

Alternatively, pipe text directly:

```bash
echo "this sentence lacks punctuation" | openwrite
```

## Development

Run the automated tests with:

```bash
pytest
```
