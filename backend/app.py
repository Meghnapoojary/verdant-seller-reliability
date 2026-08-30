from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
from google import genai
from datetime import datetime, date
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────
#  DB CONFIG  – update credentials as needed
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "seller_trust_db"),
}

DB_SSL_CA = os.getenv("DB_SSL_CA", "")

if DB_SSL_CA:
    DB_CONFIG["ssl"] = {
        "ca": DB_SSL_CA
    }

def get_db():
    return pymysql.connect(
        **DB_CONFIG,
        cursorclass=DictCursor,
        autocommit=False
    )
def serial(v):
    """Make a value JSON-safe."""
    if isinstance(v, (datetime, date)):
        return str(v)
    if hasattr(v, "__float__") and v is not None:
        return float(v)
    return v

def clean(row):
    return {k: serial(v) for k, v in row.items()}


# ──────────────────────────────────────────────
#  TRUST SCORE ENGINE
# ──────────────────────────────────────────────
def compute_trust(rating, return_rate, complaint_count, is_earliest):
    rating_component   = rating / 5.0
    return_performance = 1.0 - return_rate
    complaint_component = 1.0 / (1.0 + complaint_count)
    base_score = (rating_component * 0.4) + (return_performance * 0.4) + (complaint_component * 0.2)
    if is_earliest:
        base_score = min(1.0, base_score + 0.03)
    trust_score = round(base_score, 4)

    if trust_score > 0.70:
        risk_level, risk_class, recommended, recommendation = "Low Risk", "low", True, "Recommended"
    elif trust_score > 0.40:
        risk_level, risk_class, recommended, recommendation = "Medium Risk", "medium", False, "Not Recommended"
    else:
        risk_level, risk_class, recommended, recommendation = "High Risk", "high", False, "Not Recommended"

    reasons = []
    if rating >= 4.5:   reasons.append("excellent customer ratings")
    elif rating >= 3.5: reasons.append("decent customer ratings")
    else:               reasons.append("poor customer ratings")

    if return_rate <= 0.05:   reasons.append("very low return rate")
    elif return_rate <= 0.15: reasons.append("moderate return rate")
    else:                     reasons.append("high return rate — caution advised")

    if complaint_count == 0:       reasons.append("zero complaints on record")
    elif complaint_count <= 2:     reasons.append(f"{complaint_count} complaint(s) on record")
    else:                          reasons.append(f"{complaint_count} complaints — high risk")

    if is_earliest:
        reasons.append("earliest listing (original seller)")

    return {
        "trust_score":    trust_score,
        "risk_level":     risk_level,
        "risk_class":     risk_class,
        "recommended":    recommended,
        "recommendation": recommendation,
        "explanation":    "This seller has " + ", ".join(reasons) + "."
    }


# ──────────────────────────────────────────────
#  HELPER: get canonical product_ids for a name
# ──────────────────────────────────────────────
def get_all_pids_for_name(cursor, product_name):
    """Return all product_ids that share the same name (duplicate rows)."""
    cursor.execute("SELECT product_id FROM products WHERE name = %s", (product_name,))
    return [r["product_id"] for r in cursor.fetchall()]


# ──────────────────────────────────────────────
#  ROUTES
# ──────────────────────────────────────────────

@app.route("/")
def index():
    return jsonify({"message": "Seller Reliability Analysis API", "version": "1.1"})


@app.route("/products", methods=["GET"])
def get_products():
    """
    Return one row per unique product name.
    seller_count / min_price / max_price / avg_rating aggregate across
    ALL duplicate product_id rows that share the same name, so the
    marketplace card shows correct data regardless of how many times
    the seed SQL was run.
    """
    db = get_db()
    cursor = db.cursor() 
    cursor.execute("""
        SELECT
            MIN(p.product_id)           AS product_id,
            p.name,
            p.category,
            p.description,
            p.image_url,
            p.base_price,
            COUNT(DISTINCT l.seller_id) AS seller_count,
            MIN(CASE
                WHEN l.price BETWEEN p.base_price * 0.80 AND p.base_price * 1.20
                THEN l.price
                ELSE NULL
            END)                        AS min_price,
            MAX(CASE
                WHEN l.price BETWEEN p.base_price * 0.80 AND p.base_price * 1.20
                THEN l.price
                ELSE NULL
            END)                        AS max_price,
            AVG(l.rating)               AS avg_rating
        FROM products p
        LEFT JOIN listings l ON l.product_id = p.product_id
        GROUP BY p.name, p.category, p.description, p.image_url, p.base_price
        ORDER BY MIN(p.product_id)
    """)
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify([clean(r) for r in rows])


@app.route("/product/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Return product details. Accepts any of the duplicate product_ids."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    row = cursor.fetchone()
    cursor.close()
    db.close()
    if not row:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(clean(row))


@app.route("/trust-data/<int:product_id>", methods=["GET"])
def get_trust_data(product_id):
    """
    Return one entry per unique seller for this product.

    Because the seed SQL may have been run multiple times the products
    table can contain several rows with the same name but different
    product_ids, each with their own listings rows.  We:
      1. Find the product name for the requested id.
      2. Collect ALL product_ids that share that name.
      3. Pull ONE listing row per seller across all those product_ids
         (earliest listing_id wins).
      4. Clamp the displayed price to a realistic multiple of base_price
         so the price spread shown to buyers is never absurd.
    """
    db = get_db()
    cursor = db.cursor()

    # 1. Product name
    cursor.execute("SELECT name, base_price FROM products WHERE product_id = %s", (product_id,))
    prow = cursor.fetchone()
    if not prow:
        cursor.close(); db.close()
        return jsonify({"error": "Product not found"}), 404

    product_name = prow["name"]
    base_price   = float(prow["base_price"]) if prow["base_price"] else None

    # 2. All duplicate product_ids for this name
    cursor.execute("SELECT product_id FROM products WHERE name = %s", (product_name,))
    all_pids = [r["product_id"] for r in cursor.fetchall()]
    ph = ",".join(["%s"] * len(all_pids))   # placeholders: %s,%s,...

    # 3. One row per seller (earliest listing_id across all duplicate pids)
    cursor.execute(f"""
        SELECT l.*, s.seller_name, s.location, s.joined_date,
               s.total_sales, s.profile_image, s.seller_email
        FROM listings l
        JOIN sellers s ON l.seller_id = s.seller_id
        JOIN (
            SELECT seller_id, MIN(listing_id) AS min_lid
            FROM   listings
            WHERE  product_id IN ({ph})
            GROUP  BY seller_id
        ) dedup ON l.listing_id = dedup.min_lid
        ORDER BY l.listed_date ASC
    """, all_pids)
    listings = cursor.fetchall()

    if not listings:
        cursor.close(); db.close()
        return jsonify({"error": "No listings found for this product"}), 404

    # 4. Complaints across all duplicate pids
    cursor.execute(f"""
        SELECT seller_id, COUNT(*) AS complaint_count
        FROM   complaints
        WHERE  product_id IN ({ph})
        GROUP  BY seller_id
    """, all_pids)
    complaint_map = {r["seller_id"]: r["complaint_count"] for r in cursor.fetchall()}

    cursor.close(); db.close()

    earliest_sid = listings[0]["seller_id"]
    results = []

    for l in listings:
        sid   = l["seller_id"]
        price = float(l["price"])

        # ── Price sanity clamp ──────────────────────────────────────────
        # Only show prices within ±20% of base_price so the range on
        # the product card never shows absurd outliers (e.g. ₹2,499
        # for a ₹24,999 product). Prices outside this band are replaced
        # with the nearest boundary so the seller still appears but with
        # a sensible price.
        if base_price and base_price > 0:
            lo = base_price * 0.80
            hi = base_price * 1.20
            price = max(lo, min(price, hi))
        # ────────────────────────────────────────────────────────────────

        rating          = float(l["rating"])
        return_rate     = float(l["return_rate"])
        complaint_count = complaint_map.get(sid, 0)
        is_earliest     = (sid == earliest_sid)

        results.append({
            "listing_id":      l["listing_id"],
            "seller_id":       sid,
            "seller_name":     l["seller_name"],
            "location":        l["location"],
            "joined_date":     str(l["joined_date"]) if l["joined_date"] else None,
            "total_sales":     l["total_sales"],
            "price":           round(price, 2),
            "rating":          rating,
            "return_rate":     return_rate,
            "listed_date":     str(l["listed_date"]) if l["listed_date"] else None,
            "stock":           l["stock"],
            "complaint_count": complaint_count,
            "is_earliest":     is_earliest,
            **compute_trust(rating, return_rate, complaint_count, is_earliest)
        })

    # Python-level seller dedup (safety net)
    seen, deduped = set(), []
    for r in results:
        if r["seller_id"] not in seen:
            seen.add(r["seller_id"])
            deduped.append(r)
    results = deduped

    # Sort: recommended first, then trust score desc
    results.sort(key=lambda x: (-int(x["recommended"]), -x["trust_score"]))

    if results:
        results[0]["is_best"] = True
        for r in results[1:]:
            r["is_best"] = False

    return jsonify({"product_id": product_id, "sellers": results, "total": len(results)})


@app.route("/place-order", methods=["POST"])
def place_order():
    data   = request.get_json()
    db     = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO orders (product_id, seller_id, customer_name, quantity, total_price)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        data.get("product_id"),
        data.get("seller_id"),
        data.get("customer_name", "Guest"),
        data.get("quantity", 1),
        data.get("total_price")
    ))
    db.commit()
    order_id = cursor.lastrowid
    cursor.close(); db.close()
    return jsonify({"success": True, "order_id": order_id, "message": "Order placed successfully!"})


@app.route("/sellers", methods=["GET"])
def get_sellers():
    db     = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM sellers ORDER BY total_sales DESC")
    rows = cursor.fetchall()
    cursor.close(); db.close()
    return jsonify([clean(r) for r in rows])


@app.route("/file-complaint", methods=["POST"])
def file_complaint():
    data = request.get_json()
    product_id   = data.get("product_id")
    seller_id    = data.get("seller_id")
    customer_name = data.get("customer_name", "Guest")
    description  = data.get("description", "")

    if not product_id or not seller_id:
        return jsonify({"error": "product_id and seller_id are required"}), 400

    db     = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO complaints (product_id, seller_id, customer_name, description)
        VALUES (%s, %s, %s, %s)
    """, (product_id, seller_id, customer_name, description))
    db.commit()
    complaint_id = cursor.lastrowid
    cursor.close(); db.close()
    return jsonify({"success": True, "complaint_id": complaint_id,
                    "message": "Complaint filed. Thank you — this helps keep our marketplace safe."})



@app.route("/review-trust-analysis", methods=["POST"])
def review_trust_analysis():
    """AI-assisted review authenticity signal. It is a risk heuristic, not proof of fake reviews."""
    data = request.get_json(silent=True) or {}
    reviews = (data.get("reviews") or "").strip()
    if len(reviews) < 80:
        return jsonify({"error": "Please provide at least a few sentences of review text."}), 400
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"error": "GEMINI_API_KEY is not configured on the server."}), 500

    client = genai.Client(api_key=api_key)
    rating = data.get("rating")
    review_count = data.get("review_count")
    prompt = f"""
You are an e-commerce review integrity analyst.
Analyze the supplied review text and seller rating as a SIGNAL of possible review manipulation.
Do NOT claim that a review is fake with certainty. Look for patterns such as repetitive phrasing,
unnaturally uniform sentiment, generic non-specific wording, suspiciously similar structure,
contradiction between rating and text, excessive promotional language, or unusually clustered claims.
Give a cautious assessment and explain the evidence. This is a heuristic, not forensic proof.

Product: {data.get('product_name','Unknown')}
Seller: {data.get('seller_name','Unknown')}
Overall rating: {rating}
Reported review count: {review_count}

REVIEWS:
{reviews}
"""
    schema = {
        "type":"object",
        "properties":{
            "authenticityRisk":{"type":"string","enum":["Low","Medium","High"]},
            "confidence":{"type":"integer"},
            "ratingConsistency":{"type":"string"},
            "signals":{"type":"array","items":{"type":"string"}},
            "positiveSignals":{"type":"array","items":{"type":"string"}},
            "summary":{"type":"string"},
            "recommendation":{"type":"string"}
        },
        "required":["authenticityRisk","confidence","ratingConsistency","signals","positiveSignals","summary","recommendation"]
    }
    try:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
            contents=prompt,
            config={"response_mime_type":"application/json","response_schema":schema}
        )
        result = response.parsed if getattr(response, "parsed", None) else __import__("json").loads(response.text)
        result["confidence"] = max(0, min(100, int(result.get("confidence", 0))))
        return jsonify({"success": True, "analysis": result})
    except Exception as exc:
        print("Review AI error:", exc)
        return jsonify({"error": "Review analysis failed. Check the Gemini key and server logs."}), 500

@app.route("/orders/<customer_name>", methods=["GET"])
def get_orders(customer_name):
    db     = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT o.order_id, o.product_id, o.seller_id, o.quantity,
               o.total_price, o.order_date,
               p.name AS product_name, p.image_url, p.category,
               s.seller_name, s.location,
               l.rating, l.return_rate, l.price AS listing_price
        FROM orders o
        LEFT JOIN products  p ON o.product_id = p.product_id
        LEFT JOIN sellers   s ON o.seller_id   = s.seller_id
        LEFT JOIN listings  l ON l.product_id  = o.product_id
                               AND l.seller_id = o.seller_id
        WHERE o.customer_name = %s
        ORDER BY o.order_date DESC
    """, (customer_name,))
    rows = cursor.fetchall()

    # Get complaints per order (product+seller pair) filed by this customer
    cursor.execute("""
        SELECT product_id, seller_id, COUNT(*) AS cnt
        FROM complaints
        WHERE customer_name = %s
        GROUP BY product_id, seller_id
    """, (customer_name,))
    complaint_map = {(r["product_id"], r["seller_id"]): r["cnt"] for r in cursor.fetchall()}
    cursor.close(); db.close()

    results = []
    for r in rows:
        cr = clean(r)
        rating         = float(r["rating"])  if r["rating"]       else 3.5
        return_rate    = float(r["return_rate"]) if r["return_rate"] else 0.1
        complaint_count = complaint_map.get((r["product_id"], r["seller_id"]), 0)
        trust = compute_trust(rating, return_rate, complaint_count, False)
        cr.update(trust)
        results.append(cr)

    return jsonify(results)


@app.route("/trust-trend/<int:product_id>/<int:seller_id>", methods=["GET"])
def get_trust_trend(product_id, seller_id):
    """
    Return simulated monthly trust-score snapshots for a seller on a product.
    We derive past months by slightly varying the current metrics to produce
    a realistic trend without needing a separate history table.
    """
    db     = get_db()
    cursor = db.cursor()

    # Get current metrics
    cursor.execute("SELECT name FROM products WHERE product_id = %s", (product_id,))
    prow = cursor.fetchone()
    if not prow:
        cursor.close(); db.close()
        return jsonify({"error": "Product not found"}), 404

    cursor.execute("SELECT name FROM products WHERE name = %s", (prow["name"],))
    all_pids = [r["name"] for r in cursor.fetchall()]

    cursor.execute("""
        SELECT l.rating, l.return_rate, l.listed_date
        FROM listings l
        WHERE l.product_id = %s AND l.seller_id = %s
        LIMIT 1
    """, (product_id, seller_id))
    listing = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) AS cnt FROM complaints
        WHERE product_id = %s AND seller_id = %s
    """, (product_id, seller_id))
    cc = cursor.fetchone()["cnt"]
    cursor.close(); db.close()

    if not listing:
        return jsonify({"error": "Listing not found"}), 404

    import random, math
    random.seed(seller_id * 7 + product_id * 13)  # stable randomness per seller/product

    rating       = float(listing["rating"])
    return_rate  = float(listing["return_rate"])
    base_trust   = compute_trust(rating, return_rate, cc, False)["trust_score"]

    # Build 6-month trend ending at current score
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    from datetime import date
    today = date.today()
    trend = []
    for i in range(5, -1, -1):
        # Go back i months
        mo = (today.month - 1 - i) % 12
        yr = today.year - ((today.month - 1 - i) // 12 + (1 if (today.month - 1 - i) < 0 else 0))
        label = f"{months[mo]} {str(yr)[2:]}"
        # Slightly jitter older scores; current month = exact
        if i == 0:
            score = base_trust
        else:
            jitter = random.uniform(-0.07, 0.04)
            score  = round(max(0.1, min(1.0, base_trust + jitter * (i / 3))), 4)
        trend.append({"month": label, "trust_score": score, "pct": round(score * 100, 1)})

    return jsonify({"seller_id": seller_id, "product_id": product_id, "trend": trend})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
