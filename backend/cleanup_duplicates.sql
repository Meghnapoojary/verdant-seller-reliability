-- ═══════════════════════════════════════════════════════════════
--  Verdant — One-time duplicate cleanup (v2)
--  Picks up from where the previous run left off.
--  listings and complaints are already fixed — this script
--  handles the orders table then deletes duplicate products.
-- ═══════════════════════════════════════════════════════════════

USE seller_trust_db;
SET SQL_SAFE_UPDATES = 0;

-- ── STEP 1: Re-point orders to canonical product_id ────────────
UPDATE orders o
JOIN   products p  ON o.product_id = p.product_id
JOIN (
    SELECT name, MIN(product_id) AS canonical_pid
    FROM   products
    GROUP  BY name
) canon ON p.name = canon.name
SET o.product_id = canon.canonical_pid
WHERE o.product_id <> canon.canonical_pid;

-- ── STEP 2: Delete the duplicate product rows ───────────────────
DELETE FROM products
WHERE product_id NOT IN (
    SELECT canonical_pid FROM (
        SELECT MIN(product_id) AS canonical_pid
        FROM   products
        GROUP  BY name
    ) AS keep
);

-- ── STEP 3: Re-enable safe updates ─────────────────────────────
SET SQL_SAFE_UPDATES = 1;

-- ── STEP 4: Verify ──────────────────────────────────────────────
SELECT name, COUNT(*) AS cnt
FROM   products
GROUP  BY name
HAVING cnt > 1;
-- Should return 0 rows if cleanup was successful.
