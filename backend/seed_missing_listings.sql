-- ─────────────────────────────────────────────────────────────────
--  SEED: Missing listings for 8 products with 0 sellers
--  Matches the style of existing data in seller_trust_db
-- ─────────────────────────────────────────────────────────────────

-- ── 1. Insert new sellers (if they don't already exist) ──────────
INSERT IGNORE INTO sellers (seller_name, location, joined_date, total_sales, seller_email) VALUES
('FitZone Store',       'Pune',      '2021-03-12', 8420,  'fitzone@verdant.in'),
('HealthHub India',     'Hyderabad', '2020-07-04', 12300, 'healthhub@verdant.in'),
('SportsMart Pro',      'Chennai',   '2022-01-18', 5670,  'sportsmart@verdant.in'),
('NatureCare Co',       'Bengaluru', '2019-11-25', 19800, 'naturecare@verdant.in'),
('GlowUp Essentials',   'Mumbai',    '2021-06-09', 7350,  'glowup@verdant.in'),
('KitchenKing India',   'Delhi',     '2020-04-17', 15200, 'kitchenking@verdant.in'),
('HomeNeeds Express',   'Ahmedabad', '2022-08-30', 4890,  'homeneeds@verdant.in'),
('TechDeal Hub',        'Kolkata',   '2021-12-05', 9100,  'techdeal@verdant.in'),
('QuickShip Retail',    'Jaipur',    '2020-09-14', 11400, 'quickship@verdant.in'),
('ValueBuy Online',     'Surat',     '2023-02-20', 3200,  'valuebuy@verdant.in');

-- ─────────────────────────────────────────────────────────────────
--  Helper: get product_ids for the 8 missing products
--  We use subqueries so this works regardless of actual IDs
-- ─────────────────────────────────────────────────────────────────

-- ── 2. Boldfit Yoga Mat ──────────────────────────────────────────
INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 949.00,  4.6, 0.04, 80,  '2023-02-10'
FROM products p, sellers s WHERE p.name = 'Boldfit Yoga Mat' AND s.seller_name = 'FitZone Store' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 899.00,  4.3, 0.08, 120, '2023-04-15'
FROM products p, sellers s WHERE p.name = 'Boldfit Yoga Mat' AND s.seller_name = 'SportsMart Pro' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 979.00,  3.9, 0.13, 45,  '2023-06-01'
FROM products p, sellers s WHERE p.name = 'Boldfit Yoga Mat' AND s.seller_name = 'ValueBuy Online' LIMIT 1;

-- ── 3. Nivia Storm Football ──────────────────────────────────────
INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 1349.00, 4.7, 0.03, 60,  '2022-11-05'
FROM products p, sellers s WHERE p.name = 'Nivia Storm Football' AND s.seller_name = 'SportsMart Pro' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 1299.00, 4.4, 0.06, 95,  '2023-01-20'
FROM products p, sellers s WHERE p.name = 'Nivia Storm Football' AND s.seller_name = 'FitZone Store' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 1399.00, 3.7, 0.17, 30,  '2023-03-11'
FROM products p, sellers s WHERE p.name = 'Nivia Storm Football' AND s.seller_name = 'QuickShip Retail' LIMIT 1;

-- ── 4. Minimalist 10% Niacinamide Serum ─────────────────────────
INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 649.00,  4.8, 0.02, 200, '2022-09-14'
FROM products p, sellers s WHERE p.name = 'Minimalist 10% Niacinamide Serum' AND s.seller_name = 'GlowUp Essentials' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 699.00,  4.5, 0.05, 150, '2022-12-01'
FROM products p, sellers s WHERE p.name = 'Minimalist 10% Niacinamide Serum' AND s.seller_name = 'NatureCare Co' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 619.00,  3.8, 0.14, 75,  '2023-02-28'
FROM products p, sellers s WHERE p.name = 'Minimalist 10% Niacinamide Serum' AND s.seller_name = 'ValueBuy Online' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 729.00,  4.2, 0.09, 60,  '2023-05-10'
FROM products p, sellers s WHERE p.name = 'Minimalist 10% Niacinamide Serum' AND s.seller_name = 'QuickShip Retail' LIMIT 1;

-- ── 5. Forest Essentials Sandalwood Cream ───────────────────────
INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 1850.00, 4.9, 0.02, 40,  '2022-08-20'
FROM products p, sellers s WHERE p.name = 'Forest Essentials Sandalwood Cream' AND s.seller_name = 'NatureCare Co' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 1950.00, 4.6, 0.05, 25,  '2022-10-15'
FROM products p, sellers s WHERE p.name = 'Forest Essentials Sandalwood Cream' AND s.seller_name = 'GlowUp Essentials' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 1799.00, 3.5, 0.19, 15,  '2023-01-07'
FROM products p, sellers s WHERE p.name = 'Forest Essentials Sandalwood Cream' AND s.seller_name = 'HomeNeeds Express' LIMIT 1;

-- ── 6. Prestige Svachh Deep Kadai ───────────────────────────────
INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 1299.00, 4.7, 0.03, 110, '2022-07-18'
FROM products p, sellers s WHERE p.name = 'Prestige Svachh Deep Kadai' AND s.seller_name = 'KitchenKing India' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 1349.00, 4.4, 0.07, 80,  '2022-09-22'
FROM products p, sellers s WHERE p.name = 'Prestige Svachh Deep Kadai' AND s.seller_name = 'HomeNeeds Express' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 1249.00, 4.1, 0.11, 55,  '2023-01-30'
FROM products p, sellers s WHERE p.name = 'Prestige Svachh Deep Kadai' AND s.seller_name = 'QuickShip Retail' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 1399.00, 3.6, 0.18, 20,  '2023-04-05'
FROM products p, sellers s WHERE p.name = 'Prestige Svachh Deep Kadai' AND s.seller_name = 'ValueBuy Online' LIMIT 1;

-- ── 7. Philips HL7756 Mixer Grinder ─────────────────────────────
INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 3199.00, 4.6, 0.04, 70,  '2022-06-10'
FROM products p, sellers s WHERE p.name = 'Philips HL7756 Mixer Grinder' AND s.seller_name = 'KitchenKing India' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 3349.00, 4.4, 0.06, 45,  '2022-09-05'
FROM products p, sellers s WHERE p.name = 'Philips HL7756 Mixer Grinder' AND s.seller_name = 'TechDeal Hub' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 2999.00, 3.8, 0.15, 30,  '2023-02-14'
FROM products p, sellers s WHERE p.name = 'Philips HL7756 Mixer Grinder' AND s.seller_name = 'HomeNeeds Express' LIMIT 1;

-- ── 8. Milton Thermosteel Flask 1L ──────────────────────────────
INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 849.00,  4.8, 0.02, 180, '2022-05-22'
FROM products p, sellers s WHERE p.name = 'Milton Thermosteel Flask 1L' AND s.seller_name = 'KitchenKing India' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 899.00,  4.5, 0.05, 120, '2022-08-11'
FROM products p, sellers s WHERE p.name = 'Milton Thermosteel Flask 1L' AND s.seller_name = 'HomeNeeds Express' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 819.00,  4.0, 0.10, 90,  '2023-01-03'
FROM products p, sellers s WHERE p.name = 'Milton Thermosteel Flask 1L' AND s.seller_name = 'QuickShip Retail' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 929.00,  3.4, 0.21, 25,  '2023-05-19'
FROM products p, sellers s WHERE p.name = 'Milton Thermosteel Flask 1L' AND s.seller_name = 'ValueBuy Online' LIMIT 1;

-- ── 9. boAt Airdopes 141 ─────────────────────────────────────────
INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 1299.00, 4.5, 0.05, 150, '2022-04-08'
FROM products p, sellers s WHERE p.name = 'boAt Airdopes 141' AND s.seller_name = 'TechDeal Hub' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 1349.00, 4.3, 0.08, 100, '2022-07-25'
FROM products p, sellers s WHERE p.name = 'boAt Airdopes 141' AND s.seller_name = 'QuickShip Retail' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 1249.00, 4.0, 0.12, 80,  '2022-10-14'
FROM products p, sellers s WHERE p.name = 'boAt Airdopes 141' AND s.seller_name = 'ValueBuy Online' LIMIT 1;

INSERT INTO listings (product_id, seller_id, price, rating, return_rate, stock, listed_date)
SELECT p.product_id, s.seller_id, 1399.00, 3.6, 0.20, 35,  '2023-03-02'
FROM products p, sellers s WHERE p.name = 'boAt Airdopes 141' AND s.seller_name = 'HomeNeeds Express' LIMIT 1;

-- ── Verify ───────────────────────────────────────────────────────
SELECT p.name, COUNT(l.listing_id) AS seller_count
FROM products p
LEFT JOIN listings l ON p.product_id = l.product_id
GROUP BY p.name
ORDER BY seller_count ASC;
