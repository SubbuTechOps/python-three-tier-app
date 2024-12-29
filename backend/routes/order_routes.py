from flask import Blueprint, request, jsonify, session  # Added session import
from database.db_config import get_db_connection, close_db_connection
from models.order import Order
import logging

logger = logging.getLogger(__name__)

order_bp = Blueprint('orders', __name__)

@order_bp.route('/', methods=['POST'])
def create_order():
    """
    Create a new order for a user.
    Expects JSON with user_id, total_amount, and items (product_id and quantity).
    """
    connection = None
    try:
        # Check session first
        if 'user_id' not in session:
            logger.warning("Unauthorized order attempt - no session")
            return jsonify({"message": "Please login to place an order"}), 401

        data = request.get_json()
        if not data:
            logger.warning("No data provided in order request")
            return jsonify({"message": "No data provided"}), 400

        user_id = data.get('user_id')
        total_amount = data.get('total_amount')
        items = data.get('items')

        # Validate required fields
        if not user_id or not total_amount or not items:
            logger.warning("Missing required fields in order data")
            return jsonify({"message": "user_id, total_amount, and items are required"}), 400

        # Verify user_id matches session
        if int(user_id) != int(session['user_id']):
            logger.warning(f"User ID mismatch: {user_id} vs {session['user_id']}")
            return jsonify({"message": "Invalid user session"}), 401

        connection = get_db_connection()
        if not connection:
            logger.error("Database connection failed")
            return jsonify({"message": "Database connection failed"}), 500

        cursor = connection.cursor()

        # Verify cart has items
        cursor.execute("""
            SELECT COUNT(*) FROM cart_items 
            WHERE user_id = %s
        """, (user_id,))
        cart_count = cursor.fetchone()[0]
        
        if cart_count == 0:
            logger.warning(f"Empty cart for user {user_id}")
            return jsonify({"message": "Cart is empty"}), 400

        # Create the order
        cursor.execute("""
            INSERT INTO orders (user_id, total_amount) 
            VALUES (%s, %s)
        """, (user_id, total_amount))
        order_id = cursor.lastrowid

        # Insert order items
        for item in items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity)
                VALUES (%s, %s, %s)
            """, (order_id, item['product_id'], item['quantity']))

        # Clear the user's cart
        cursor.execute("DELETE FROM cart_items WHERE user_id = %s", (user_id,))

        connection.commit()
        logger.info(f"Order {order_id} created successfully for user {user_id}")
        
        return jsonify({
            "message": "Order created successfully",
            "order_id": order_id
        }), 201

    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        if connection:
            connection.rollback()
        return jsonify({
            "message": "Failed to create order", 
            "error": str(e)
        }), 500
    finally:
        if connection:
            close_db_connection(connection)