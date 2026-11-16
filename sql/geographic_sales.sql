select strftime('%Y', o.order_purchase_timestamp)             as sales_year,
       c.customer_state                                       as customer_state,
       ROUND(SUM(oi.price), 2)                                AS total_sales,
       COUNT(DISTINCT o.order_id)                             AS total_orders,
       ROUND((SUM(oi.price) / COUNT(DISTINCT o.order_id)), 2) AS AOV
FROM orders as o
         INNER JOIN order_items as oi ON o.order_id = oi.order_id
         INNER JOIN customers as c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
  AND o.order_purchase_timestamp >= '2017-01-01'
  AND o.order_purchase_timestamp < '2018-09-01'
GROUP BY 1, 2
ORDER BY 3 DESC