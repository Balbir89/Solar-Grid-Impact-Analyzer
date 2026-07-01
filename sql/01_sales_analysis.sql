CREATE TABLE sales (
  id INT,
  product TEXT,
  amount INT
);

INSERT INTO sales VALUES
(1, 'Shoes', 120),
(2, 'Bag', 80),
(3, 'Shoes', 150);

SELECT product, SUM(amount) AS total_sales
FROM sales
GROUP BY product
ORDER BY total_sales DESC;
