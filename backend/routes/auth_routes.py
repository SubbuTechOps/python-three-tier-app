from flask import Blueprint, request, jsonify, session, make_response, redirect, url_for
from models.user import User
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

# Add check auth status route
@auth_bp.route('/status', methods=['GET'])
def check_auth_status():
    """Check if user is authenticated"""
    logger.debug(f"Current session: {session}")
    if 'user_id' in session:
        return jsonify({
            "authenticated": True,
            "user": {
                "username": session.get('username'),
                "user_id": session.get('user_id')
            }
        }), 200
    return jsonify({"authenticated": False}), 401

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        if not request.is_json:
            return jsonify({"message": "Invalid request format. JSON required."}), 400
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"message": "Username and password are required."}), 400
        
        if User.get_user_by_username(username):
            return jsonify({"message": "Username already exists."}), 400
        
        user = User.create_user(username, password)
        
        # Set session
        session.clear()  # Clear any existing session first
        session['username'] = username
        session['user_id'] = user.user_id
        session.permanent = True
        
        logger.debug(f"Session after signup: {session}")
        
        response = jsonify({
            "message": "User registered successfully.", 
            "user": user.to_dict()
        })
        return response, 201
    
    except Exception as e:
        logger.error(f"Error in signup: {str(e)}", exc_info=True)
        return jsonify({
            "message": "An error occurred during signup.", 
            "error": str(e)
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        logger.debug(f"Login attempt - Session before: {session}")
        
        if not request.is_json:
            return jsonify({"message": "Invalid request format. JSON required."}), 400
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"message": "Username and password are required."}), 400
        
        user = User.authenticate(username, password)
        if user:
            # Clear any existing session first
            session.clear()
            
            # Set new session
            session['username'] = username
            session['user_id'] = user.user_id
            session.permanent = True
            
            logger.debug(f"Login successful - Session after: {session}")
            
            response = jsonify({
                "message": "Login successful.", 
                "user": user.to_dict()
            })
            return response, 200
        
        logger.warning(f"Login failed for username: {username}")
        return jsonify({"message": "Invalid credentials."}), 401
    
    except Exception as e:
        logger.error(f"Error in login: {str(e)}", exc_info=True)
        return jsonify({
            "message": "An error occurred during login.", 
            "error": str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        logger.debug(f"Logout attempt - Session before: {session}")
        session.clear()
        logger.debug(f"Logout successful - Session after: {session}")
        
        response = make_response(jsonify({"message": "Logout successful."}))
        response.delete_cookie('session')  # Delete the session cookie
        return response, 200
    
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}", exc_info=True)
        return jsonify({
            "message": "An error occurred during logout.", 
            "error": str(e)
        }), 500

# Add authentication middleware
def login_required(view_function):
    def wrapper(*args, **kwargs):
        logger.debug(f"Checking authentication - Current session: {session}")
        if 'user_id' not in session:
            return jsonify({"message": "Authentication required"}), 401
        return view_function(*args, **kwargs)
    wrapper.__name__ = view_function.__name__
    return wrapper