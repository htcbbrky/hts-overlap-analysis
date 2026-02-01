
# HTS Overlap Analysis

**Version:** 1.0.0  
**License:** MIT  
**Language:** Python 3.11+  
**Repository:** [htcbbrky/hts-overlap-analysis](https://github.com/htcbbrky/hts-overlap-analysis)

---

## 📋 Overview

This tool analyzes **HTS (Historical Traffic Search)** records to detect whether different individuals were simultaneously present at the same base stations. It is a professional analysis system that can be used for evidence evaluation in forensic cases.

### ✨ Key Features

- ✅ **Multi-format support:** XLSX, PDF, CSV
- ✅ **Smart name matching:** Fuzzy matching tolerates spelling variations
- ✅ **Automatic base code extraction:** Parses codes within parentheses
- ✅ **Simultaneity detection:** 30 min, 1 hour, same day levels
- ✅ **Statistical analysis:** Random overlap probability calculation
- ✅ **Detailed reporting:** Excel, PDF, JSON outputs
- ✅ **High performance:** 200K+ record processing capacity

---

## 🚀 Quick Start

### Requirements

```

Python 3.11 or higher
pip (Python package manager)

```

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/htcbbrky/hts-overlap-analysis.git
cd hts-overlap-analysis
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```


### First Run

```bash
python analyze_hts_overlap.py --input data/ --output results/
```


---

## 📂 Project Structure

```
hts-overlap-analysis/
│
├── analyze_hts_overlap.py    # Main script
├── requirements.txt           # Python dependencies
├── config.yaml               # Configuration file
├── README.md                 # This file
├── LICENSE                   # MIT license
│
├── data/                     # Input files (gitignored - add your HTS files here)
│
├── output/                   # Analysis results (gitignored - auto-generated)
│
├── logs/                     # Application logs (gitignored)
│
├── src/                      # Source code modules
│   ├── analyzer.py          # Overlap analysis logic
│   ├── matcher.py           # Fuzzy name matching
│   ├── parser.py            # HTS file parsing (XLSX/PDF/CSV)
│   ├── reporter.py          # Report generation (Excel/PDF/JSON)
│   └── utils.py             # Helper functions
│
├── tests/                    # Unit tests (coming soon)
│
└── docs/                     # Documentation (coming soon)
```


---

## 🔧 Usage

### Basic Usage

```bash
python analyze_hts_overlap.py
```

Default settings:

- Input folder: `./data/`
- Output folder: `./output/`
- Configuration: `config.yaml`


### Advanced Parameters

```bash
python analyze_hts_overlap.py \
  --input /path/to/hts_files/ \
  --output /path/to/results/ \
  --config my_config.yaml \
  --threshold 85 \
  --time-tolerance 30 \
  --verbose
```


#### Parameters:

| Parameter | Description | Default |
| :-- | :-- | :-- |
| `--input` | Folder containing HTS files | `./data/` |
| `--output` | Folder to save results | `./output/` |
| `--config` | Configuration file path | `config.yaml` |
| `--threshold` | Fuzzy matching threshold (%) | `85` |
| `--time-tolerance` | Simultaneity tolerance (minutes) | `30` |
| `--verbose` | Detailed log output | `False` |
| `--format` | Output format (excel/pdf/json) | `excel` |


---

## 📊 Example Use Cases

### Scenario 1: Two Subjects Overlap Analysis

```bash
# Place these files in data/ folder:
# - subject1_hts.xlsx
# - subject2_hts.xlsx

python analyze_hts_overlap.py
```

**Output:**

- `output/overlap_report.xlsx`: List of common base stations
- `output/detailed_analysis.pdf`: Detailed analysis report
- `output/statistics.json`: Statistical findings


### Scenario 2: Custom Time Tolerance

```bash
# For 1-hour simultaneity:
python analyze_hts_overlap.py --time-tolerance 60
```


### Scenario 3: Lower Similarity Threshold

```bash
# Be more flexible in name matching (75%):
python analyze_hts_overlap.py --threshold 75
```


---

## 📖 Configuration File

You can customize analysis parameters by editing the `config.yaml` file:

```yaml
# Fuzzy Matching Settings
matching:
  threshold: 85  # 85% similarity
  use_phone_validation: true
  use_imei_validation: true

# Overlap Analysis Settings
analysis:
  time_tolerance_level1: 30   # minutes
  time_tolerance_level2: 60   # minutes
  same_day_analysis: true

# Data Processing Settings
processing:
  encoding: 'utf-8'
  date_format: 'dd.mm.yyyy hh:mm:ss'
  skip_invalid_records: true

# Reporting Settings
reporting:
  include_statistics: true
  include_charts: false
  export_formats: ['excel', 'pdf']
```


---

## 🧪 Tests

To run unit tests:

```bash
pytest tests/
```

Specific test file:

```bash
pytest tests/test_analyzer.py -v
```

To view test coverage:

```bash
pytest --cov=src tests/
```


---

## 📈 Performance

**Test Environment:**

- CPU: Intel i7-10700K
- RAM: 16 GB
- Disk: SSD

**Measurements:**


| Record Count | Processing Time | Memory Usage |
| :-- | :-- | :-- |
| 10,000 | ~2 minutes | ~500 MB |
| 50,000 | ~8 minutes | ~1.2 GB |
| 100,000 | ~15 minutes | ~2.1 GB |
| 200,000 | ~28 minutes | ~3.8 GB |


---

## 🛠️ Troubleshooting

### Error: "ModuleNotFoundError: No module named 'pandas'"

**Solution:**

```bash
pip install -r requirements.txt
```


### Error: "Permission denied: 'data/'"

**Solution:**

```bash
chmod +x data/
# or
sudo python analyze_hts_overlap.py
```


### Error: "Memory Error"

**Solution:**

- Test with less data
- Increase `chunk_size` parameter in `config.yaml`
- Increase RAM


### Date format errors

**Solution:**

Check date format in `config.yaml`:

```yaml
processing:
  date_format: 'dd.mm.yyyy hh:mm:ss'  # Turkish format
```
---

### Code Standards

- Write PEP 8 compliant code
- Complete docstrings
- Write tests for new features
- Use type hints

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 👤 Contact

**Developer:** htcbbrky
**GitHub:** [@htcbbrky](https://github.com/htcbbrky)
**Repository:** [hts-overlap-analysis](https://github.com/htcbbrky/hts-overlap-analysis)

---

## 🙏 Acknowledgments

This project uses the following open-source libraries:

- [Pandas](https://pandas.pydata.org/) - Data analysis
- [NumPy](https://numpy.org/) - Numerical computations
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel operations
- [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) - Fuzzy string matching
- [PyPDF2](https://pypdf2.readthedocs.io/) - PDF operations

---

## 📚 Additional Resources

- User Guide (coming soon in `docs/`)
- API Reference (coming soon in `docs/`)
- Example Analyses (coming soon in `docs/`)
- FAQ (coming soon in `docs/`)

---

## ⚖️ Legal Notice

This tool is developed for forensic analysis. Ensure that HTS data is obtained legally. Responsibility for compliance with personal data protection legislation (KVKK/GDPR) belongs to the user.

---

**Version History:**

- **v1.0.0** (01.02.2026): First stable release
    - Basic overlap analysis
    - Excel/PDF report support
    - Fuzzy matching integration

---

## 🚀 Getting Started

Ready to analyze HTS data? Follow these steps:

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure settings in `config.yaml`
4. Place your HTS files in the `data/` folder
5. Run `python analyze_hts_overlap.py`
6. Check results in the `output/` folder

**Note:** The `data/`, `output/`, and `logs/` folders are gitignored for privacy and to keep the repository clean. These folders will be created automatically when you run the script.

---

**Made with ⚖️ for forensic analysis**