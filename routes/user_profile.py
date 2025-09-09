from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import uuid
import os

# Configure upload folder
UPLOAD_FOLDER = 'user'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

user_profile = Blueprint('user_profile', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_profile.route('/api/user_profile', methods=['POST'])
def update_user_profile():
    """Update user profile data"""
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        
        if not telegram_id:
            return jsonify({'success': False, 'error': 'No telegram_id provided'}), 400

        # Remove telegram_id from data to avoid updating it
        update_data = {k: v for k, v in data.items() if k != 'telegram_id'}
        
        if not update_data:
            # If no update data, just return current profile
            result = supabase.table('users').select('*').eq('telegram_id', telegram_id).execute()
            if result.data:
                return jsonify({'success': True, 'profile': result.data[0]})
            return jsonify({'success': False, 'error': 'User not found'}), 404

        # Update user data
        result = supabase.table('users').update(update_data).eq('telegram_id', telegram_id).execute()
        
        if result.data:
            return jsonify({'success': True, 'profile': result.data[0]})
        return jsonify({'success': False, 'error': 'Failed to update profile'}), 500

    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@user_profile.route('/api/upload_avatar', methods=['POST'])
def upload_avatar():
    """Handle avatar upload"""
    try:
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['avatar']
        telegram_id = request.form.get('telegram_id')
        
        if not telegram_id:
            return jsonify({'success': False, 'error': 'No telegram_id provided'}), 400
        
        if not file or not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400

        # Create user directory if it doesn't exist
        user_dir = os.path.join(UPLOAD_FOLDER, str(telegram_id))
        os.makedirs(user_dir, exist_ok=True)

        # Generate unique filename
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(user_dir, unique_filename)

        # Save file
        file.save(file_path)

        # Update user record in database
        avatar_url = f"/user/{telegram_id}/{unique_filename}"
        supabase.table('users').update({
            'avatar_path': avatar_url
        }).eq('telegram_id', telegram_id).execute()

        return jsonify({
            'success': True,
            'avatar_path': avatar_url
        })

    except Exception as e:
        print(f"Error uploading avatar: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@user_profile.route('/user/<path:filename>')
def serve_user_file(filename):
    """Serve user uploaded files"""
    return send_from_directory(UPLOAD_FOLDER, filename)
