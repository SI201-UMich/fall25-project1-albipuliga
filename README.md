## Project 1: Sample Superstore Analysis

### Overview
Python analysis of the Kaggle Sample Superstore dataset using only the standard `csv` module. The project:
- Loads the CSV
- Performs four calculations (as defined in the checkpoint)
- Writes results to CSV files
- Includes unit tests (4 per function)

### Files
- [`utils.py`](src/utils.py): data loading, calculations, CSV writer, and [`run_calculations`](src/utils.py#L223) helper function.
- [`main.py`](src/main.py): main entry point to run all calculations and write outputs.
- [`tests.py`](src/tests.py): unit tests (16 total).
- [`SampleSuperstore.csv`](src/SampleSuperstore.csv): Kaggle dataset.

### Quick start

Run main and write outputs (creates `output/` if it does not exist):
```bash
python3 src/main.py
```

Run tests:
```bash
python3 src/tests.py
```

### Calculations
- **Average Profit Margin by Sub-Category within Each Region**
  - Uses: `Profit`, `Sales`, `Sub-Category`, `Region`
  - Method: margin = sum(Profit)/sum(Sales) guarded for zero sales
  - Output: `output/margin_by_region_subcategory.csv`
  - Columns: `Region, SubCategory, total_sales, total_profit, profit_margin`

- **Loss Rate for High-Discount Lines by State and Segment**
  - Uses: `Discount`, `Profit`, `State`, `Segment`
  - Method: filter `Discount >= 0.20`, loss_pct = count(Profit < 0)/total_lines
  - Output: `output/loss_pct_high_discount_by_state_segment.csv`
  - Columns: `State, Segment, num_lines, num_losses, loss_pct`

- **Regional Performance by Customer Segment**
  - Uses: `Region`, `Segment`, `Sales`, `Quantity`
  - Method: avg_order_value = total_sales/total_quantity (guard zero quantity)
  - Output: `output/avg_order_value_by_region_segment.csv`
  - Columns: `Region, Segment, total_sales, total_quantity, avg_order_value`

- **Discount Impact on Order Size by Category**
  - Uses: `Discount`, `Quantity`, `Category`, `Sales`
  - Method: bucket discount into None/Low/Medium/High, compute averages
  - Output: `output/discount_impact_by_category.csv`
  - Columns: `discount_tier, Category, num_orders, avg_quantity, avg_sales`

### Functions breakdown from [`utils.py`](src/utils.py)
- `load_data(csv_path)`: returns list of row dicts with numeric coercions for `Sales`, `Profit`, `Discount`, `Quantity`
- `write_csv(output_path, rows, fieldnames)`: write dict rows to CSV
- `margin_by_region_subcategory(rows)`
- `loss_pct_high_discount_by_state_segment(rows)`
- `avg_order_value_by_region_segment(rows)`
- `discount_impact_by_category(rows)`
- `run_calculations()`: runs all calcs and writes outputs

### Collaborators and AI usage
- Team: David Vargas & Alberto Puliga
- GenAI usage: Assisted with problem decomposition, and tests. All outputs reviewed.