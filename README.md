# RFM Customer Segmentation

A Python script that takes raw retail transaction data and sorts customers into segments (Champions, Loyal Customers, At Risk, etc.) using RFM analysis. The output is an Excel report with one row per customer.

Built with pandas on the [Online Retail II](https://www.kaggle.com/datasets/lakshmi25npathi/online-retail-dataset) dataset from the UCI Machine Learning Repository.

## The problem

A retailer with thousands of customers can't treat them all the same. Someone who spent heavily last week and someone who made one small purchase two years ago need very different marketing, but raw transaction logs don't show that. Each row is just one line item on one invoice.

The goal here was to turn that raw log into something a marketing or sales team can act on: a list of customers, each with a clear label saying how recent, how frequent and how valuable they are, so the business knows who to reward, who to win back and who to stop spending effort on.

## The approach

RFM stands for:

- **Recency**: how many days since the customer last bought something
- **Frequency**: how often they buy
- **Monetary**: how much they have spent in total

### 1. Load the data

The data comes from the `Year 2009-2010` sheet of `online_retail_II.xlsx`. Each row is a single product line on an invoice, with quantity, unit price, invoice date and customer ID.

### 2. Clean it

- Dropped rows with no `Customer ID`. Without it a purchase can't be tied to a customer, so it can't be used for customer-level analysis.
- Removed rows where `Quantity <= 0` or `Price <= 0`. In this dataset that mostly means returns, cancellations and adjustments, which would distort spending totals.
- Created a `TotalSum` column (`Quantity x Price`) for the value of each line.

### 3. Calculate the RFM metrics

I grouped the cleaned data by `Customer ID` and calculated:

- **Recency**: days between the customer's last purchase and a reference date, which is the last date in the dataset plus one day.
- **Frequency**: the number of transaction lines for that customer.
- **Monetary**: the sum of `TotalSum` across all their purchases.

The reference date is taken from the data instead of using today's date, because the dataset is historical. Using the real current date would make every customer look inactive.

### 4. Score each metric from 1 to 5

I used fixed business-style thresholds instead of quantiles, so the scores are easy to read and explain.

Recency score (days since last purchase):
- 5: 30 days or less
- 4: 31 to 90 days
- 3: 91 to 180 days
- 2: 181 to 365 days
- 1: more than 365 days

Frequency score (number of transaction lines):
- 5: 100 or more
- 4: 50 to 99
- 3: 20 to 49
- 2: 5 to 19
- 1: fewer than 5

Monetary score (total spend):
- 5: 2000 or more
- 4: 1000 to 1999
- 3: 500 to 999
- 2: 200 to 499
- 1: less than 200

### 5. Assign segments

Segments are based on the Recency and Frequency scores. The rules are checked in this order and the first match wins:

1. **Champions**: R is 4 or 5 and F is 4 or 5
2. **Loyal Customers**: R is 3 or higher and F is 4 or 5
3. **At Risk**: R is 2 or lower and F is 3 or higher
4. **About to Sleep**: R is 3 or lower and F is 2 or lower
5. **Lost**: R is 1 and F is 1
6. **Needs Attention**: everyone else

### 6. Export

The full customer table is saved as an Excel report. The script also prints the first 10 rows and a count of customers per segment to the console.

## Output

After cleaning, the 2009-2010 sheet gives 4,312 customers. Each row in the report contains:

`Customer ID`, `Recency`, `Frequency`, `Monetary`, `R_Score`, `F_Score`, `M_Score`, `Segment`

## Project structure

```
.
├── data/
│   ├── raw/
│   │   └── online_retail_II.xlsx            # not included, see below
│   └── outputs/
│       └── RFM_Customer_Segmentation_Report.xlsx    # Final report
├── rfm_analysis.py
├── .gitignore
└── README.md
```

The Excel files are listed in `.gitignore`, so the `data` folder is not part of the repository. Create it yourself when you run the project.

## How to run

1. Clone the repo.
2. Download the dataset from the [UCI page](https://archive.ics.uci.edu/dataset/502/online+retail+ii) and place `online_retail_II.xlsx` in `data/raw/`.
3. Install the dependencies:
   ```
   pip install pandas openpyxl
   ```
4. Run the script from the project folder:
   ```
   python rfm_analysis.py
   ```

Reading the Excel file takes a little while because of its size.

## Limitations and next steps

- **Frequency counts transaction lines, not invoices.** A customer who buys 10 products in one order is counted as 10. Counting unique invoices would be a better measure of how often someone actually shops.
- **The Monetary score is calculated but not used in the segment rules.** Segments currently depend only on R and F. Bringing M in would separate high-spending and low-spending customers inside the same segment.
- **The "Lost" segment is never assigned.** Customers with R = 1 and F = 1 are caught by the "About to Sleep" rule first, because it is checked earlier. Moving the Lost check above it fixes this.
- **Thresholds are fixed.** They were chosen by hand and may not suit every business. Quantile-based scoring would adapt to the data automatically.
- Only the 2009-2010 sheet is analysed. The 2010-2011 sheet could be added for a longer history.
- Ideas for later: charts of segment sizes and revenue share per segment, and a comparison of segment behaviour over time.

## Tools

Python, pandas
