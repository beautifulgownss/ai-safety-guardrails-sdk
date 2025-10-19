# AI Safety Guardrails SDK - Benchmark Results

This document contains benchmark results for all guards in the AI Safety Guardrails SDK. The benchmarks measure accuracy (F1 score) and latency (P50/P95/P99) to ensure production-ready performance.

## Test Environment

- **Python Version**: 3.13
- **Device**: CPU (device=-1)
- **Date**: 2025-10-17
- **Platform**: macOS

## Summary

| Guard | Type | Accuracy (F1) | Latency (P50) | Status |
|-------|------|---------------|---------------|--------|
| MLPromptInjectionGuard | ML-Classifier | TBD | TBD | ⚠️ Not yet benchmarked |
| MLPIIDetectorGuard | ML-NER | TBD | TBD | ⚠️ Not yet benchmarked |
| InjectionDetectorGuard | Regex | N/A | TBD | ⚠️ Not yet benchmarked |
| PIIDetectorGuard | Regex | N/A | TBD | ⚠️ Not yet benchmarked |
| RBACGuard | Rule-based | N/A | TBD | ⚠️ Not yet benchmarked |

## 1. Prompt Injection Detection Accuracy

**Guard**: `MLPromptInjectionGuard`
**Model**: `protectai/deberta-v3-base-prompt-injection`
**Threshold**: 0.8

### Classification Metrics

To run the benchmark:
```bash
cd benchmarks
python test_injection_accuracy.py
```

Expected results will be populated here after running the benchmark.

**Metrics:**
- Accuracy: TBD
- Precision: TBD
- Recall: TBD
- F1 Score: TBD
- False Positive Rate: TBD
- False Negative Rate: TBD

**Confusion Matrix:**
- True Positives: TBD
- False Positives: TBD
- True Negatives: TBD
- False Negatives: TBD

### Threshold Sensitivity Analysis

| Threshold | Accuracy | Precision | Recall | F1 |
|-----------|----------|-----------|--------|-----|
| 0.50 | TBD | TBD | TBD | TBD |
| 0.70 | TBD | TBD | TBD | TBD |
| 0.80 | TBD | TBD | TBD | TBD |
| 0.90 | TBD | TBD | TBD | TBD |
| 0.95 | TBD | TBD | TBD | TBD |

**Recommendation**: Use threshold 0.8 for balanced precision/recall.

---

## 2. PII Detection Accuracy

**Guard**: `MLPIIDetectorGuard`
**Model**: `dslim/bert-base-NER`
**Threshold**: 0.75

### Overall Metrics

To run the benchmark:
```bash
cd benchmarks
python test_pii_accuracy.py
```

Expected results will be populated here after running the benchmark.

**Overall:**
- Precision: TBD
- Recall: TBD
- F1 Score: TBD
- True Positives: TBD
- False Positives: TBD
- False Negatives: TBD

### Per-Entity Metrics

| Entity Type | Precision | Recall | F1 |
|-------------|-----------|--------|-----|
| PERSON | TBD | TBD | TBD |
| ORGANIZATION | TBD | TBD | TBD |
| LOCATION | TBD | TBD | TBD |
| EMAIL | TBD | TBD | TBD |
| PHONE | TBD | TBD | TBD |

---

## 3. Latency Benchmarks

All guards tested with short (19 chars), medium (142 chars), and long (500+ chars) prompts.
Measurements: 50 warm iterations after cold start.

To run the benchmark:
```bash
cd benchmarks
python test_latency.py
```

### Summary Table

| Guard | Length | P50 (ms) | P95 (ms) | P99 (ms) | RPS |
|-------|--------|----------|----------|----------|-----|
| **Regex-Based Guards** | | | | | |
| PIIDetectorGuard | short | TBD | TBD | TBD | TBD |
| PIIDetectorGuard | medium | TBD | TBD | TBD | TBD |
| PIIDetectorGuard | long | TBD | TBD | TBD | TBD |
| InjectionDetectorGuard | short | TBD | TBD | TBD | TBD |
| InjectionDetectorGuard | medium | TBD | TBD | TBD | TBD |
| InjectionDetectorGuard | long | TBD | TBD | TBD | TBD |
| RBACGuard | short | TBD | TBD | TBD | TBD |
| RBACGuard | medium | TBD | TBD | TBD | TBD |
| RBACGuard | long | TBD | TBD | TBD | TBD |
| **ML-Based Guards** | | | | | |
| MLPIIDetectorGuard | short | TBD | TBD | TBD | TBD |
| MLPIIDetectorGuard | medium | TBD | TBD | TBD | TBD |
| MLPIIDetectorGuard | long | TBD | TBD | TBD | TBD |
| MLPromptInjectionGuard | short | TBD | TBD | TBD | TBD |
| MLPromptInjectionGuard | medium | TBD | TBD | TBD | TBD |
| MLPromptInjectionGuard | long | TBD | TBD | TBD | TBD |

### Performance Tiers

**Ultra-Fast (<10ms P95):**
- TBD

**Fast (10-100ms P95):**
- TBD

**Moderate (100-500ms P95):**
- TBD

**Slow (>500ms P95):**
- TBD

---

## 4. Production Readiness Assessment

### Regex-Based Guards
**Status**: ✅ Production Ready
- **Latency**: Expected <5ms P95
- **Accuracy**: Rule-based (100% precision for defined patterns, limited recall)
- **Use Case**: Fast screening, high-throughput scenarios
- **Recommendation**: Use as first-line defense in guard chains

### ML-Based Guards
**Status**: ⚠️ Pending Benchmark Results
- **Latency**: Expected 50-200ms P95 (CPU), 10-50ms (GPU)
- **Accuracy**: Expected F1 > 0.85 for both guards
- **Use Case**: High-accuracy detection, security-critical applications
- **Recommendation**: Use for thorough analysis after regex screening

---

## 5. Recommendations

### Guard Chain Strategy
For optimal production performance, use a two-stage guard chain:

```python
from safety_sdk.guards import (
    InjectionDetectorGuard,      # Stage 1: Fast regex
    MLPromptInjectionGuard,       # Stage 2: Accurate ML
    PIIDetectorGuard,             # Stage 1: Fast regex
    MLPIIDetectorGuard,           # Stage 2: Accurate ML
)

# Fast screening first
fast_guards = [
    InjectionDetectorGuard({"action": "block"}),
    PIIDetectorGuard({"action": "warn"}),
]

# Thorough ML-based analysis
ml_guards = [
    MLPromptInjectionGuard({"threshold": 0.8, "action": "block"}),
    MLPIIDetectorGuard({"threshold": 0.75, "action": "warn"}),
]
```

### Threshold Tuning
- **Lower threshold (0.7)**: More sensitive, catches more threats but more false positives
- **Higher threshold (0.9)**: More conservative, fewer false positives but may miss some threats
- **Recommended (0.8)**: Balanced precision/recall for production use

### GPU Acceleration
For high-throughput production environments, use GPU acceleration:
```python
config = {
    "device": 0,  # Use first GPU
    "model_name_or_path": "protectai/deberta-v3-base-prompt-injection",
}
guard = MLPromptInjectionGuard(config)
```

Expected speedup: 3-5x faster than CPU inference.

---

## Running the Benchmarks

To reproduce these results:

```bash
# Install dependencies
pip install transformers torch

# Run all benchmarks
cd benchmarks

# Accuracy benchmarks
python test_pii_accuracy.py > pii_accuracy.log
python test_injection_accuracy.py > injection_accuracy.log

# Latency benchmarks
python test_latency.py > latency.log

# Examples/tests
cd ../examples
python test_injection_detection.py > injection_detection.log
```

---

## Changelog

- **2025-10-17**: Initial benchmark framework created
- **TBD**: First benchmark run results to be added

---

## Future Work

1. **GPU Benchmarks**: Measure latency on GPU (CUDA)
2. **Batch Processing**: Test throughput with batch sizes 8, 16, 32
3. **Model Comparison**: Compare multiple injection detection models
4. **Real-World Dataset**: Test on production-like data
5. **Adversarial Testing**: Red team evaluation with novel injection techniques
