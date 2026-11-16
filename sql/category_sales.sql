select COALESCE(p.product_category_name, 'Unknown')           AS category,
       strftime('%Y', o.order_purchase_timestamp)             AS sales_year,
       ROUND(SUM(oi.price), 2)                                AS total_sales,
       COUNT(distinct o.order_id)                             AS Distinct_Orders,
       ROUND((SUM(oi.price) / COUNT(distinct o.order_id)), 2) AS AOV
from orders as o
         INNER JOIN order_items as oi on o.order_id = oi.order_id
         INNER JOIN products as p ON oi.product_id = p.product_id
WHERE o.order_status = 'delivered'
  AND o.order_purchase_timestamp >= '2017-01-01'
  AND o.order_purchase_timestamp < '2018-09-01'
GROUP BY category, sales_year
ORDER BY 3 DESC