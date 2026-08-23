from fastmcp import FastMCP
from db import get_connection
mcp = FastMCP("Ecommerce Database MCP")
@mcp.tool()
def hello() -> str:
    """Test whether the MCP server is working."""
    return "MCP server is working!"
@mcp.tool()
def test_database()->str:
    """Test connection with postgresql databasr"""
    conn=get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result=cursor.fetchone()
        return f"Database connection seccuseeful :{result}"
    finally:
        conn.close()
@mcp.tool()
def get_products()->list:
    """Get allthe products from the ecommerece database"""
    conn=get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
SELECT id,name,category,price 
FROM products 
ORDER by id;

""")
            rows=cursor.fetchall()
            products=[]
            for row in rows:
                products.append({
                    "id":row[0],
                    "name":row[1],
                    "category":row[2],
                    "price":row[3]
                })
            return products

    finally:
        conn.close()

@mcp.tool()
def get_users()->list:
    """Get all the users from the ecommerece database"""
    conn=get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
SELECT id,name,email,signup_date
FROM users
order by id;
""")
            rows=cursor.fetchall()
            users=[]
            for row in rows:
                users.append({
                    "id":row[0],
                    "name":row[1],
                    "email":row[2],
                    "signup_date":str(row[3])
                })

            return users
    finally:
        conn.close()

@mcp.tool()
def get_orders()->list:
    """Get all the orders with the user name"""
    conn=get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
SELECT orders.id,users.name,orders,order_date 
from orders 
JOIN users
on orders.user_id=users.id
ORDER BY orders.id
""")
            rows=cursor.fetchall()
            orders=[]
            for row in rows:
                orders.append({
                    "order_id":row[0],
                    "user_name":row[1],
                    "order_date":str(row[2])

                })
            return orders
    finally:
        conn.close()
@mcp.tool()
def get_order_details()->list:
    """Get detailed information about all orders"""
    conn=get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
SELECT 
orders.id AS order_id,
users.name AS user_name,
products.name AS product_name,
order_items.quantity,
products.price
FROM orders
JOIN users
    ON orders.user_id=users.id
JOIN order_items
    ON orders.id = order_items.order_id
JOIN products
    ON order_items.product_id=products.id
ORDER BY orders.id;

""")
            rows=cursor.fetchall()
            products=[]
            for row in rows:
                products.append({
                "order_id":row[0],
                "user_name":row[1],
                "product_name":row[2],
                "quantity":row[3],
                "price":float(row[4])
            })
            return products
    finally:
        conn.close()
@mcp.tool()
def get_sales_summary()->list:
    """Get the total quantity sold and revenue fro each products"""
    conn=get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
SELECT 
products.id,
products.name,
SUM(order_items.quantity) AS total_quantity,
SUM(order_items.quantity * products.price) AS total_revenue
FROM order_items
JOIN products
ON order_items.product_id=products.id
GROUP BY products.id,products.name
ORDER BY total_revenue DESC;
""")
            rows=cursor.fetchall()
            revenue=[]
            for row in rows:
                revenue.append({
                    "product_id":row[0],
                    "product_name":row[1],
                    "total_quantity":row[2],
                    "Total _revenue":float(row[3])
                })
            return revenue
    finally:
        conn.close()
@mcp.tool()
def get_top_customers()->list[dict]:
    """Get customers ranked by total spending"""
    conn=get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
SELECT 
users.id,
users.name,
COUNT(DISTINCT orders.id) as total_orders,
SUM(order_items.quantity*products.price) AS total_spent
FROM users
JOIN orders
    ON users.id =orders.user_id
JOIN order_items
    ON orders.id=order_items.order_id
JOIN products
    ON order_items.product_id=products.id
GROUP BY users.id,users.name
ORDER BY total_spent DESC

""")
            rows=cursor.fetchall()
            customer=[]
            for row in rows:
                customer.append({
                    "user_id":row[0],
                    "user_name":row[1],
                    "total_orders":row[2],
                    "total_spent":float(row[3])
                })
                return customer
    finally:
        conn.close()

@mcp.tool()
def get_customer_orders(user_id:int)->list:
    """Get all orders placed by this customers"""
    conn=get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
SELECT 
orders.id as order_id,
users.name as user_name,
orders.order_date
FROM orders
JOIN users
ON orders.user_id=users.id
WHere users.id=%s
ORDER BY orders.id;
""",(user_id,))
            rows=cur.fetchall()
            person=[]
            for row in rows:
                person.append({
                    "user_name":row[1],
                    "order_id":row[0],
                    "order_date":str(row[2])
                })
            return person
    finally:
        conn.close()
@mcp.tool()
def search_products(search_term: str) -> list[dict]:
    """Search products by name or category."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id,
                    name,
                    category,
                    price
                FROM products
                WHERE name ILIKE %s
                   OR category ILIKE %s
                ORDER BY id;
            """, (f"%{search_term}%", f"%{search_term}%"))

            rows = cur.fetchall()

            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "category": row[2],
                    "price": float(row[3])
                }
                for row in rows
            ]

    finally:
        conn.close()
@mcp.tool()
def get_customer_summary(user_id: int) -> dict:
    """Get a summary of a customer's orders and total spending."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    users.id,
                    users.name,
                    COUNT(DISTINCT orders.id) AS total_orders,
                    COALESCE(SUM(order_items.quantity), 0) AS total_items,
                    COALESCE(
                        SUM(order_items.quantity * products.price),
                        0
                    ) AS total_spent
                FROM users
                LEFT JOIN orders
                    ON users.id = orders.user_id
                LEFT JOIN order_items
                    ON orders.id = order_items.order_id
                LEFT JOIN products
                    ON order_items.product_id = products.id
                WHERE users.id = %s
                GROUP BY users.id, users.name;
            """, (user_id,))

            row = cur.fetchone()

            if row is None:
                return {
                    "error": f"User with id {user_id} not found."
                }

            return {
                "user_id": row[0],
                "user_name": row[1],
                "total_orders": row[2],
                "total_items": row[3],
                "total_spent": float(row[4])
            }

    finally:
        conn.close()
@mcp.tool()
def get_order_total(order_id: int) -> dict:
    """Get the total amount of a specific order."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    orders.id,
                    users.name,
                    COALESCE(
                        SUM(order_items.quantity * products.price),
                        0
                    ) AS order_total
                FROM orders
                JOIN users
                    ON orders.user_id = users.id
                LEFT JOIN order_items
                    ON orders.id = order_items.order_id
                LEFT JOIN products
                    ON order_items.product_id = products.id
                WHERE orders.id = %s
                GROUP BY orders.id, users.name;
            """, (order_id,))

            row = cur.fetchone()

            if row is None:
                return {
                    "error": f"Order with id {order_id} not found."
                }

            return {
                "order_id": row[0],
                "customer": row[1],
                "total": float(row[2])
            }

    finally:
        conn.close()
@mcp.tool()
def run_read_query(query: str) -> list[dict]:
    """Execute a read-only SQL query."""

    query = query.strip()

    if not query:
        raise ValueError("Query cannot be empty.")

    forbidden_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create",
        "grant",
        "revoke"
    ]

    query_lower = query.lower()

    if not query_lower.startswith(("select", "with")):
        raise ValueError("Only SELECT or WITH queries are allowed.")

    for keyword in forbidden_keywords:
        if keyword in query_lower:
            raise ValueError(
                f"Forbidden SQL operation: {keyword}"
            )

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(query)

            rows = cur.fetchall()

            columns = [desc.name for desc in cur.description]

            return [
                dict(zip(columns, row))
                for row in rows
            ]

    finally:
        conn.close()
if __name__ == "__main__":
    mcp.run()