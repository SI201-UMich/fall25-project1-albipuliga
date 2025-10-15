import unittest

from utils import (
    avg_order_value_by_region_segment,
    discount_impact_by_category,
    loss_pct_high_discount_by_state_segment,
    margin_by_region_subcategory,
)


class TestCalculations(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {
                "Region": "East",
                "SubCategory": "Chairs",
                "Sales": 200.0,
                "Profit": 20.0,
                "Quantity": 4,
                "Discount": 0.1,
                "State": "New York",
                "Segment": "Consumer",
                "Category": "Furniture",
            },
            {
                "Region": "East",
                "SubCategory": "Chairs",
                "Sales": 0.0,
                "Profit": 0.0,
                "Quantity": 2,
                "Discount": 0.0,
                "State": "New York",
                "Segment": "Consumer",
                "Category": "Furniture",
            },
            {
                "Region": "West",
                "SubCategory": "Tables",
                "Sales": 300.0,
                "Profit": -30.0,
                "Quantity": 3,
                "Discount": 0.25,
                "State": "California",
                "Segment": "Corporate",
                "Category": "Furniture",
            },
            {
                "Region": "West",
                "SubCategory": "Tables",
                "Sales": 200.0,
                "Profit": 10.0,
                "Quantity": 1,
                "Discount": 0.5,
                "State": "California",
                "Segment": "Corporate",
                "Category": "Furniture",
            },
            {
                "Region": "South",
                "SubCategory": "Paper",
                "Sales": 100.0,
                "Profit": 50.0,
                "Quantity": 10,
                "Discount": 0.0,
                "State": "Texas",
                "Segment": "Home Office",
                "Category": "Office Supplies",
            },
            {
                "Region": "South",
                "SubCategory": "Paper",
                "Sales": 100.0,
                "Profit": -50.0,
                "Quantity": 10,
                "Discount": 0.2,
                "State": "Texas",
                "Segment": "Home Office",
                "Category": "Office Supplies",
            },
        ]

    # margin_by_region_subcategory: 2 normal, 2 edge
    def test_margin_normal(self):
        result = margin_by_region_subcategory(self.rows)
        east_chairs = next(
            r for r in result if r["Region"] == "East" and r["SubCategory"] == "Chairs"
        )
        self.assertAlmostEqual(east_chairs["profit_margin"], 20.0 / 200.0)

    def test_margin_zero_sales_guard(self):
        # Includes a zero-sales line; guard should keep denominator non-zero by sum, but still check behavior
        rows = [
            {
                "Region": "X",
                "Sub-Category": "Y",
                "Sales": 0.0,
                "Profit": 10.0,
                "Quantity": 1,
                "Discount": 0.0,
            }
        ]
        result = margin_by_region_subcategory(rows)
        self.assertEqual(result[0]["profit_margin"], 0.0)

    def test_margin_multiple_groups(self):
        result = margin_by_region_subcategory(self.rows)
        west_tables = next(
            r for r in result if r["Region"] == "West" and r["SubCategory"] == "Tables"
        )
        # total profit = -30 + 10 = -20; total sales = 300 + 200 = 500 -> -0.04
        self.assertAlmostEqual(west_tables["profit_margin"], -0.04)

    def test_margin_missing_labels(self):
        rows = [
            {"Region": "East", "Sales": 100.0, "Profit": 10.0}
        ]  # missing SubCategory
        result = margin_by_region_subcategory(rows)
        self.assertEqual(result, [])

    # loss_pct_high_discount_by_state_segment: 2 normal, 2 edge
    def test_loss_pct_filters_high_discount(self):
        result = loss_pct_high_discount_by_state_segment(self.rows)
        ca_corp = next(
            r
            for r in result
            if r["State"] == "California" and r["Segment"] == "Corporate"
        )
        # two lines, one loss
        self.assertEqual(ca_corp["num_lines"], 2)
        self.assertEqual(ca_corp["num_losses"], 1)
        self.assertAlmostEqual(ca_corp["loss_pct"], 0.5)

    def test_loss_pct_ignores_low_discount(self):
        rows = [{"State": "X", "Segment": "Y", "Discount": 0.1, "Profit": -1.0}]
        result = loss_pct_high_discount_by_state_segment(rows)
        self.assertEqual(result, [])

    def test_loss_pct_missing_labels(self):
        rows = [{"Discount": 0.5, "Profit": -1.0}]  # missing State/Segment
        result = loss_pct_high_discount_by_state_segment(rows)
        self.assertEqual(result, [])

    def test_loss_pct_zero_division_guard(self):
        rows = [{"State": "A", "Segment": "B", "Discount": 0.2, "Profit": 1.0}]
        result = loss_pct_high_discount_by_state_segment(rows)
        self.assertAlmostEqual(result[0]["loss_pct"], 0.0)

    # avg_order_value_by_region_segment: 2 normal, 2 edge
    def test_aov_basic(self):
        result = avg_order_value_by_region_segment(self.rows)
        east_consumer = next(
            r for r in result if r["Region"] == "East" and r["Segment"] == "Consumer"
        )
        self.assertAlmostEqual(east_consumer["avg_order_value"], 200.0 / (4 + 2))

    def test_aov_zero_quantity_guard(self):
        rows = [{"Region": "R", "Segment": "S", "Sales": 100.0, "Quantity": 0}]
        result = avg_order_value_by_region_segment(rows)
        self.assertEqual(result[0]["avg_order_value"], 0.0)

    def test_aov_multiple_groups(self):
        result = avg_order_value_by_region_segment(self.rows)
        south_home = next(
            r
            for r in result
            if r["Region"] == "South" and r["Segment"] == "Home Office"
        )
        # total sales = 200, total quantity = 20 -> 10
        self.assertAlmostEqual(south_home["avg_order_value"], 10.0)

    def test_aov_missing_labels(self):
        rows = [{"Region": "R", "Sales": 10.0, "Quantity": 1}]  # missing Segment
        result = avg_order_value_by_region_segment(rows)
        self.assertEqual(result, [])

    # discount_impact_by_category: 2 normal, 2 edge
    def test_discount_tiers_and_averages(self):
        result = discount_impact_by_category(self.rows)
        medium_office = next(
            r
            for r in result
            if r["discount_tier"] == "Medium" and r["Category"] == "Office Supplies"
        )
        self.assertEqual(medium_office["num_orders"], 1)
        self.assertAlmostEqual(medium_office["avg_quantity"], 10)
        self.assertAlmostEqual(medium_office["avg_sales"], 100.0)

    def test_discount_none_tier(self):
        rows = [{"Category": "Tech", "Discount": 0.0, "Quantity": 2, "Sales": 50.0}]
        result = discount_impact_by_category(rows)
        self.assertEqual(result[0]["discount_tier"], "None")

    def test_discount_low_tier(self):
        rows = [{"Category": "Tech", "Discount": 0.19, "Quantity": 2, "Sales": 50.0}]
        result = discount_impact_by_category(rows)
        self.assertEqual(result[0]["discount_tier"], "Low")

    def test_discount_high_tier(self):
        rows = [{"Category": "Tech", "Discount": 0.41, "Quantity": 2, "Sales": 50.0}]
        result = discount_impact_by_category(rows)
        self.assertEqual(result[0]["discount_tier"], "High")


if __name__ == "__main__":
    unittest.main()
