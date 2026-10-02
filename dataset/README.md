# SIH26099 Dataset Organization & Data Provenance Policy

## Strict Data Provenance Rules

1. **Benchmark Data (`dataset/benchmark/kaggle/`):**
   - The dataset in this folder (`train.csv`, 27,188 records) originates from the public Kaggle Multimodal Product Matching Challenge.
   - **MANDATORY POLICY:** This data is used **ONLY as an algorithmic development and evaluation benchmark**. It must **NEVER** be described as official CPSE data, Indian government procurement data, ONGC data, or BHEL data.

2. **Demonstration CPSE Records (`dataset/sample_cpse_data/`):**
   - Contains demonstration files for testing cross-enterprise harmonization:
     - `synthetic_ongc/cpse_a_ongc.csv`: 8 demonstration records labeled ONGC.
     - `synthetic_bhel/cpse_b_bhel.xlsx`: 5 demonstration records labeled BHEL.
   - **MANDATORY POLICY:** These are manually constructed synthetic demonstration records. They must **ALWAYS** be labeled in documentation and UI as:
     `"Demonstration CPSE Data (Synthetic)"` or `"ONGC — Demonstration Data (Synthetic)"` / `"BHEL — Demonstration Data (Synthetic)"`.

3. **Production CPSE Data:**
   - Real CPSE material master records will be ingested securely from participating CPSE ERP/SAP systems via the Spring Boot ingestion pipeline upon official onboarding.

---

## Directory Structure

```
dataset/
├── benchmark/
│   └── kaggle/
│       └── train.csv                      # Algorithmic benchmark (27,188 records)
│
├── sample_cpse_data/
│   ├── synthetic_ongc/
│   │   └── cpse_a_ongc.csv                # Demonstration ONGC records (Synthetic)
│   └── synthetic_bhel/
│       └── cpse_b_bhel.xlsx               # Demonstration BHEL records (Synthetic)
│
└── README.md
```
