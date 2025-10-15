"""
SI 201 Project 1: Data Analysis (Sample Superstore)

Team: David Vargas & Alberto Puliga
Repo: fall25-project1-albipuliga
GenAI usage: Assisted with problem decomposition, and tests. All outputs reviewed.

This module provides:
- CSV load using Python csv module
- Four calculations defined in the checkpoint
- Generic CSV writer
"""

import csv
from collections import defaultdict


def load_data(csv_path):
    """Load Sample Superstore CSV and coerce common columns to numbers.

    Returns a list of row dicts with keys matching the CSV headers.
    """
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Normalize whitespace-only values to empty strings
            normalized = {
                k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()
            }

            # Numeric coercions with safe fallbacks
            for key in ["Sales", "Profit", "Discount"]:
                value = normalized.get(key, "")
                try:
                    normalized[key] = float(value)
                except Exception:
                    normalized[key] = 0.0

            value = normalized.get("Quantity", "")
            try:
                normalized["Quantity"] = int(float(value))
            except Exception:
                normalized["Quantity"] = 0

            rows.append(normalized)
    return rows


def write_csv(output_path, rows, fieldnames):
    """Write list of dict rows to CSV.

    Fieldnames controls column order in output.
    """
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})


def margin_by_region_subcategory(rows):
    """Average profit margin by (Region, Sub-Category).

    For each pair, compute total_sales, total_profit, profit_margin = total_profit / total_sales.
    Guards divide-by-zero by returning 0.0 margin when total_sales is 0.
    """
    totals = defaultdict(lambda: {"total_sales": 0.0, "total_profit": 0.0})

    for r in rows:
        region = r.get("Region", "")
        subcat = r.get("Sub-Category", r.get("SubCategory", ""))
        sales = r.get("Sales", 0.0)
        profit = r.get("Profit", 0.0)
        if not region or not subcat:
            continue
        totals[(region, subcat)]["total_sales"] += sales
        totals[(region, subcat)]["total_profit"] += profit

    output = []
    for (region, subcat), agg in totals.items():
        total_sales = agg["total_sales"]
        total_profit = agg["total_profit"]
        margin = (total_profit / total_sales) if total_sales != 0 else 0.0
        output.append(
            {
                "Region": region,
                "SubCategory": subcat,
                "total_sales": round(total_sales, 2),
                "total_profit": round(total_profit, 2),
                "profit_margin": round(margin, 6),
            }
        )
    # Stable order for deterministic tests
    output.sort(key=lambda x: (x["Region"], x["SubCategory"]))
    return output


def loss_pct_high_discount_by_state_segment(rows):
    """Loss rate for high-discount (>= 0.20) lines grouped by (State, Segment).

    Returns rows with: State, Segment, num_lines, num_losses, loss_pct
    """
    counts = defaultdict(lambda: {"num_lines": 0, "num_losses": 0})

    for r in rows:
        discount = r.get("Discount", 0.0)
        if discount < 0.20:
            continue
        state = r.get("State", "")
        segment = r.get("Segment", "")
        if not state or not segment:
            continue
        is_loss = 1 if r.get("Profit", 0.0) < 0 else 0
        counts[(state, segment)]["num_lines"] += 1
        counts[(state, segment)]["num_losses"] += is_loss

    output = []
    for (state, segment), agg in counts.items():
        num_lines = agg["num_lines"]
        num_losses = agg["num_losses"]
        loss_pct = (num_losses / num_lines) if num_lines != 0 else 0.0
        output.append(
            {
                "State": state,
                "Segment": segment,
                "num_lines": num_lines,
                "num_losses": num_losses,
                "loss_pct": round(loss_pct, 6),
            }
        )
    output.sort(key=lambda x: (x["State"], x["Segment"]))
    return output


def avg_order_value_by_region_segment(rows):
    """Average order value proxy by (Region, Segment): total_sales / total_quantity.

    Uses line-level quantity as denominator; guards divide-by-zero.
    """
    totals = defaultdict(lambda: {"total_sales": 0.0, "total_quantity": 0})

    for r in rows:
        region = r.get("Region", "")
        segment = r.get("Segment", "")
        if not region or not segment:
            continue
        totals[(region, segment)]["total_sales"] += r.get("Sales", 0.0)
        totals[(region, segment)]["total_quantity"] += r.get("Quantity", 0)

    output = []
    for (region, segment), agg in totals.items():
        total_sales = agg["total_sales"]
        total_quantity = agg["total_quantity"]
        aov = (total_sales / total_quantity) if total_quantity != 0 else 0.0
        output.append(
            {
                "Region": region,
                "Segment": segment,
                "total_sales": round(total_sales, 2),
                "total_quantity": total_quantity,
                "avg_order_value": aov,
            }
        )
    output.sort(key=lambda x: (x["Region"], x["Segment"]))
    return output


def _discount_tier(value):
    if value is None:
        return "None"
    if value <= 0:
        return "None"
    if 0 < value < 0.20:
        return "Low"
    if 0.20 <= value < 0.40:
        return "Medium"
    return "High"


def discount_impact_by_category(rows):
    """Discount tier impact by Category.

    Groups by (discount_tier, Category) and computes:
    - num_orders (lines)
    - avg_quantity (mean of Quantity)
    - avg_sales (mean of Sales)
    """
    totals = defaultdict(lambda: {"num_orders": 0, "sum_quantity": 0, "sum_sales": 0.0})

    for r in rows:
        category = r.get("Category", "")
        if not category:
            continue
        tier = _discount_tier(r.get("Discount", 0.0))
        key = (tier, category)
        totals[key]["num_orders"] += 1
        totals[key]["sum_quantity"] += r.get("Quantity", 0)
        totals[key]["sum_sales"] += r.get("Sales", 0.0)

    output = []
    for (tier, category), agg in totals.items():
        num_orders = agg["num_orders"]
        if num_orders == 0:
            avg_q = 0.0
            avg_s = 0.0
        else:
            avg_q = agg["sum_quantity"] / num_orders
            avg_s = agg["sum_sales"] / num_orders
        output.append(
            {
                "discount_tier": tier,
                "Category": category,
                "num_orders": num_orders,
                "avg_quantity": round(avg_q, 6),
                "avg_sales": round(avg_s, 6),
            }
        )
    output.sort(key=lambda x: (x["discount_tier"], x["Category"]))
    return output


def run_calculations():
    """Run all calculations and write outputs as CSV files in the output directory."""
    input_csv_path = "../SampleSuperstore.csv"
    output_dir_path = "../output"

    data = load_data(input_csv_path)

    margin_rows = margin_by_region_subcategory(data)
    write_csv(
        f"{output_dir_path}/margin_by_region_subcategory.csv",
        margin_rows,
        ["Region", "SubCategory", "total_sales", "total_profit", "profit_margin"],
    )

    loss_rows = loss_pct_high_discount_by_state_segment(data)
    write_csv(
        f"{output_dir_path}/loss_pct_high_discount_by_state_segment.csv",
        loss_rows,
        ["State", "Segment", "num_lines", "num_losses", "loss_pct"],
    )

    aov_rows = avg_order_value_by_region_segment(data)
    write_csv(
        f"{output_dir_path}/avg_order_value_by_region_segment.csv",
        aov_rows,
        ["Region", "Segment", "total_sales", "total_quantity", "avg_order_value"],
    )

    discount_rows = discount_impact_by_category(data)
    write_csv(
        f"{output_dir_path}/discount_impact_by_category.csv",
        discount_rows,
        ["discount_tier", "Category", "num_orders", "avg_quantity", "avg_sales"],
    )

    return {
        "margin": margin_rows,
        "loss": loss_rows,
        "aov": aov_rows,
        "discount": discount_rows,
    }
