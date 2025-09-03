# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project that generates a BCG (Boston Consulting Group) matrix visualization from product sales data. The BCG matrix is a business tool that plots products on a 2D grid based on their market growth rate (Y-axis) and relative market share (X-axis).

## Key Files

- `scripts/make_bcg.py`: Main script that processes CSV data and generates BCG matrix visualization
- `data/bcg_raw.csv`: Sample input data with product information
- `pyproject.toml`: Project dependencies and configuration

## Common Commands

### Running the BCG Matrix Generator

```bash
uv run python scripts/make_bcg.py --in data/bcg_raw.csv --out out
```

This command will:
1. Process the input CSV file containing product data
2. Calculate unit profit and sales volume metrics
3. Generate a BCG matrix with four quadrants:
   - Star (High profit × High sales)
   - Cash Cow (Low profit × High sales)
   - Question Mark (High profit × Low sales)
   - Dog (Low profit × Low sales)
4. Output results to the `out` directory:
   - `bcg_with_indices.csv`: Processed data with coordinates and quadrant classifications
   - `bcg_plot.png`: Visualization of the BCG matrix

### Dependencies

The project uses:
- Python >= 3.11
- pandas: Data processing
- matplotlib: Visualization
- numpy: Numerical computations

Dependencies are managed with `uv` (https://github.com/astral-sh/uv), a fast Python package installer and resolver.

## Code Architecture

The main script (`scripts/make_bcg.py`) follows this workflow:

1. **Data Input**: Reads CSV with columns [商品ID, 商品名, 月销量, 平均价格, 毛利率]
2. **Metric Calculation**:
   - Unit Profit = Average Price × Gross Margin
   - Sales Revenue = Monthly Sales × Average Price
   - X coordinate = 1 - minmax(Unit Profit) [inverted so high profit is on the left]
   - Y coordinate = minmax(Monthly Sales) [normalized so high sales is at the top]
3. **Quadrant Classification**: Products are classified into four quadrants based on median X/Y values
4. **Visualization**: Creates a bubble chart with:
   - Quadrant background colors
   - Product bubbles sized by sales revenue
   - Labels for each product
   - Legend explaining quadrant meanings

The minmax function normalizes values to a 0-1 range, with special handling for cases where all values are identical.