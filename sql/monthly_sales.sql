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
                                     ) AS previous_month_sales,
                                 average_order_value,
                                 total_orders
                          FROM monthly_sales)
SELECT time_period,
       total_sales,
       previous_month_sales,
       ROUND(
               (total_sales - previous_month_sales) * 100.0
                   / NULLIF(previous_month_sales, 0),
               2
       ) AS growth_per_month,
       average_order_value,
       total_orders
FROM sales_comparison
WHERE time_period BETWEEN '2017-01' AND '2018-08'
ORDER BY time_period;