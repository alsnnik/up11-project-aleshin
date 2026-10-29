USE interior_db;

SELECT 
    p.product_id, 
    p.name, 
    c.name AS category, 
    p.manufacturer, 
    p.price, 
    COALESCE(SUM(si.quantity), 0) AS total_quantity
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id
LEFT JOIN stock_items si ON p.product_id = si.product_id
GROUP BY p.product_id;