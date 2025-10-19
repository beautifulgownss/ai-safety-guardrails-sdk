# Benchmarks

This directory contains comprehensive benchmarks for the AI Safety Guardrails SDK, measuring both accuracy and performance of all guards.

## Overview

The benchmark suite consists of three main components:

1. **Accuracy Benchmarks** - Measure precision, recall, and F1 scores
2. **Latency Benchmarks** - Measure P50/P95/P99 latency and throughput
3. **Results Documentation** - Track performance metrics over time

## Benchmark Files

### Accuracy Tests

#### `test_pii_accuracy.py`
Measures PII detection accuracy for `MLPIIDetectorGuard`:
- Overall F1 score across all entity types
- Per-entity metrics (PERSON, ORGANIZATION, LOCATION, EMAIL, PHONE, etc.)
- Precision/recall tradeoffs
- Threshold sensitivity analysis

**Usage:**
```bash
python test_pii_accuracy.py
```

**Test Dataset:** 25+ synthetic test cases with ground truth labels

#### `test_injection_accuracy.py`
Measures prompt injection detection accuracy for `MLPromptInjectionGuard`:
- Classification metrics (accuracy, precision, recall, F1)
- False positive/negative analysis
- Detection of jailbreak attempts, instruction overrides, context injection
- Threshold comparison

**Usage:**
```bash
python test_injection_accuracy.py
```

**Test Dataset:** 50+ labeled examples including:
- Known injection patterns (DAN, jailbreaks, overrides)
- Safe prompts that should not be flagged
- Edge cases (legitimate security discussions)

### Performance Tests

#### `test_latency.py`
Comprehensive latency benchmark for all guards:
- P50, P95, P99 latency percentiles
- Throughput (requests per second)
- Cold start vs warm inference
- Performance across different prompt lengths
- Performance tier classification

**Usage:**
```bash
python test_latency.py
```

**Metrics:**
- 50 warm iterations per test
- Tests with short, medium, and long prompts
- Both regex-based and ML-based guards

### Results

#### `results.md`
Living document tracking benchmark results:
- Latest benchmark metrics
- Performance trends over time
- Production readiness assessments
- Recommendations for deployment

## Quick Start

### Install Dependencies

```bash
# From project root
pip install transformers torch

# Or with the package
pip install -e .
```

### Run All Benchmarks

```bash
cd benchmarks

# Run accuracy benchmarks
python test_pii_accuracy.py
python test_injection_accuracy.py

# Run latency benchmarks
python test_latency.py
```

### Run Individual Tests

```bash
# Just PII accuracy
python test_pii_accuracy.py

# Just injection detection with custom threshold
python -c "
from test_injection_accuracy import evaluate_injection_detection, print_results
results = evaluate_injection_detection(threshold=0.85)
print_results(results)
"
```

## Understanding the Metrics

### Accuracy Metrics

**Precision**: Of all items detected as PII/injection, what % were correct?
- High precision = few false positives
- Important for: Avoiding user frustration from incorrectly blocked content

**Recall**: Of all actual PII/injections, what % were detected?
- High recall = few false negatives
- Important for: Security (catching all threats)

**F1 Score**: Harmonic mean of precision and recall
- Balances both metrics
- F1 > 0.85 is considered good for production

### Latency Metrics

**P50 (Median)**: 50% of requests are faster than this
- Typical user experience

**P95**: 95% of requests are faster than this
- Worst-case for most users
- Key metric for SLAs

**P99**: 99% of requests are faster than this
- Tail latency
- Important for large-scale deployments

**Throughput (RPS)**: Requests per second
- System capacity
- Important for resource planning

## Performance Targets

Based on FAANG best practices:

### Regex-Based Guards
- **Target P95**: <5ms
- **Target F1**: N/A (rule-based, 100% precision for defined patterns)
- **Status**: Production-ready for high-throughput scenarios

### ML-Based Guards
- **Target P95**:
  - CPU: <200ms
  - GPU: <50ms
- **Target F1**: >0.85
- **Status**: Production-ready with proper infrastructure

## Interpreting Results

### Accuracy Assessment

| F1 Score | Status | Recommendation |
|----------|--------|----------------|
| ≥0.90 | Excellent | Deploy with confidence |
| ≥0.85 | Good | Production-ready |
| ≥0.75 | Acceptable | Consider threshold tuning |
| <0.75 | Needs work | Review model/patterns |

### Latency Assessment

| P95 Latency | Status | Use Case |
|-------------|--------|----------|
| <10ms | Ultra-fast | Real-time, high-volume |
| <100ms | Fast | Interactive applications |
| <500ms | Moderate | Background processing |
| >500ms | Slow | Batch/offline only |

## Troubleshooting

### ImportError: No module named 'transformers'

```bash
pip install transformers torch
```

### Slow Performance

1. **Use GPU** if available:
   ```python
   config = {"device": 0}  # Use first GPU
   ```

2. **Reduce batch size** if running out of memory

3. **Cache models** to avoid redownloading:
   ```python
   # Models are cached in ~/.cache/huggingface/
   ```

### Inconsistent Results

- ML models have some variance due to floating-point operations
- Run benchmarks multiple times and average results
- Ensure no other processes are competing for resources

## Continuous Benchmarking

For production deployments, consider:

1. **Automated CI/CD benchmarks** on each release
2. **Performance regression alerts** if metrics degrade
3. **A/B testing** of new models/thresholds
4. **Real-world data** collection for more accurate benchmarks

## Contributing

To add new benchmarks:

1. Create a new `test_*.py` file in this directory
2. Follow the existing structure (setup, run, report)
3. Update `results.md` with a new section
4. Document in this README

## References

- [Transformers Library](https://huggingface.co/docs/transformers)
- [ProtectAI Models](https://huggingface.co/protectai)
- [dslim/bert-base-NER](https://huggingface.co/dslim/bert-base-NER)
- [Performance Best Practices](https://huggingface.co/docs/transformers/performance)
