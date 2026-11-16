import sqlite3
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "olist.db"

with sqlite3.connect(DB_PATH) as conn:
    sales_df = pd.read_sql_query(
        """
        WITH monthly_sales AS (SELECT strftime('%Y-%m', order_purchase_timestamp) AS time_period,
                                      ROUND(SUM(oi.price), 2)                     AS total_sales,
                                      COUNT(DISTINCT oi.order_id)                 AS total_orders,
                                      ROUND(
                                              SUM(oi.price) / COUNT(DISTINCT oi.order_id),
                                              2
                                      )                                           AS average_order_value
                               FROM orders as o
                                        INNER JOIN order_items as oi ON o.order_id = oi.order_id
                               WHERE o.order_status = 'delivered'
                               GROUP BY 1
                               ORDER BY 1),
             sales_comparison AS (SELECT time_period,
                                         total_sales,
                                         LAG(total_sales) OVER (
                                             ORDER BY time_period
                                             ) AS previous_month_sales
                                  FROM monthly_sales)
        SELECT time_period,
               total_sales,
               previous_month_sales,
               ROUND(
                       (total_sales - previous_month_sales) * 100.0
                           / NULLIF(previous_month_sales, 0),
                       2
               ) AS growth_per_month
        FROM sales_comparison
        WHERE time_period BETWEEN '2017-03' AND '2018-08'
        ORDER BY time_period;
        """,
        conn
    )

# print(sales_df.dtypes)
sales_df['time_period'] = pd.to_datetime(sales_df['time_period'], format="%Y-%m")

print(sales_df.head())

plt.figure(figsize=(10, 6))
plt.plot(sales_df['time_period'], sales_df['growth_per_month'])
plt.axhline(y=0, color="gray", linestyle="--")
plt.title("Olist — Monthly Sales Growth (2017–2018)")
plt.xlabel("Month")
plt.ylabel("Month-over-Month Growth (%)")
# plt.xticks()
plt.grid()

fig, ax = plt.subplots(figsize=(11, 6))

ax.plot(
    sales_df["time_period"],
    sales_df["total_sales"],
    marker="o",
    linewidth=2
)

ax.set_title("Olist — Monthly Delivered-Order Sales")
ax.set_xlabel("Month")
ax.set_ylabel("Sales Value (R$)")

ax.xaxis.set_major_locator(
    mdates.MonthLocator(interval=2)
)
ax.xaxis.set_major_formatter(
    mdates.DateFormatter("%b. %Y")
)

ax.yaxis.set_major_formatter(
    FuncFormatter(lambda x, pos: f"R${x / 1_000_000:.1f}M")
)

ax.set_ylim(bottom=0)
ax.grid(alpha=0.3)

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
