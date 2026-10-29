USE interior_db;

SELECT 
    p.product_id, 
    p.name, 
    p.category, 
    p.manufacturer, 
    p.composition, 
    p.price, 
    p.image_path,
    COALESCE(SUM(si.quantity), 0) AS total_quantity
FROM products p
LEFT JOIN stock_items si ON p.product_id = si.product_id
GROUP BY p.product_id;
