import os
import hashlib
import secrets
import string
from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename
from Crypto.Cipher import AES

# Flask setup
app = Flask(__name__)
# Use environment variable for secret key, fallback to generated key
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Configuration
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
ALLOWED_EXTENSIONS = {
    # Images
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'tif', 'webp', 'svg', 'ico', 'raw', 'heic', 'heif',
    # Documents
    'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'rtf', 'odt', 'ods', 'odp',
    # Archives
    'zip', 'rar', '7z', 'tar', 'gz', 'bz2',
    # Media
    'mp4', 'mp3', 'wav', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'm4a', 'aac', 'ogg', 'flac',
    # Code
    'py', 'js', 'html', 'css', 'json', 'xml', 'csv', 'sql',
    # Encrypted files
    'enc',
    # Other
    'exe', 'msi', 'dmg', 'iso', 'bin'
}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB max file size


def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_secure_password(length=16):
    """Generate a cryptographically secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def derive_key(password: str) -> bytes:
    """Derive AES key from password using SHA-256"""
    return hashlib.sha256(password.encode()).digest()


def cleanup_old_files():
    """Clean up old files to prevent storage bloat"""
    import time
    current_time = time.time()
    
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        try:
            for filename in os.listdir(folder):
                # Skip .gitkeep files
                if filename == '.gitkeep':
                    continue
                    
                file_path = os.path.join(folder, filename)
                # Remove files older than 1 hour
                if os.path.getctime(file_path) < current_time - 3600:
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass
        except OSError:
            # Directory doesn't exist or can't be accessed
            pass


@app.route("/")
def index():
    """Main page"""
    cleanup_old_files()  # Clean up old files on each visit
    return render_template("index.html", result=None)


@app.route("/process", methods=["POST"])
def process():
    """Process file encryption/decryption"""
    # Check if file was uploaded
    if "file" not in request.files:
        flash("❌ No file uploaded. Please select a file.")
        return redirect(url_for('index'))

    file = request.files["file"]
    if file.filename == "":
        flash("❌ No file selected. Please choose a file to upload.")
        return redirect(url_for('index'))

    # Debug: Print file information
    print(f"📁 Uploading file: {file.filename}")
    
    # Validate file type
    if not allowed_file(file.filename):
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'no extension'
        print(f"❌ File extension '{file_ext}' not in allowed list")
        flash(f"❌ File type '{file_ext}' not allowed. Supported formats: images, documents, archives, media files, and more.")
        return redirect(url_for('index'))
    
    print(f"✅ File '{file.filename}' accepted for processing")

    action = request.form.get("action")
    print(f"🔧 Action received: '{action}'")
    print(f"🔧 Form data: {dict(request.form)}")
    
    if action not in ["encrypt", "decrypt"]:
        print(f"❌ Invalid action: '{action}'")
        flash("❌ Invalid action specified.")
        return redirect(url_for('index'))

    # Secure filename and save uploaded file
    filename = secure_filename(file.filename)
    if not filename:
        flash("❌ Invalid filename. Please rename your file and try again.")
        return redirect(url_for('index'))

    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    
    try:
        file.save(upload_path)
    except Exception as e:
        flash(f"❌ Error saving file: {str(e)}")
        return redirect(url_for('index'))

    try:
        if action == "encrypt":
            # ENCRYPTION PROCESS - Auto-generate password
            password = generate_secure_password(20)  # Generate 20-character password automatically
            key = derive_key(password)
            
            # Read original file
            with open(upload_path, "rb") as f:
                data = f.read()
            
            # Encrypt using AES-GCM (Authenticated encryption)
            cipher = AES.new(key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(data)
            
            # Combine nonce + tag + ciphertext
            encrypted_data = cipher.nonce + tag + ciphertext
            
            # Save encrypted file
            output_filename = filename + ".enc"
            output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_filename)
            print(f"🔒 Encrypting '{filename}' -> '{output_filename}'")
            
            with open(output_path, "wb") as f:
                f.write(encrypted_data)
            
            # Clean up uploaded file
            os.remove(upload_path)
            
            return render_template(
                "index.html",
                result={
                    "filename": output_filename,
                    "type": "encrypted",
                    "password": password,
                },
            )

        elif action == "decrypt":
            # DECRYPTION PROCESS
            password = request.form.get("key", "").strip()
            if not password:
                flash("❌ Decryption key is required. Please enter your password.")
                os.remove(upload_path)  # Clean up
                return redirect(url_for('index'))
            
            key = derive_key(password)
            
            # Read encrypted file
            with open(upload_path, "rb") as f:
                encrypted_data = f.read()
            
            # Check minimum file size (nonce + tag + some data)
            if len(encrypted_data) < 32:
                flash("❌ Invalid encrypted file. File appears to be corrupted.")
                os.remove(upload_path)
                return redirect(url_for('index'))
            
            # Extract components
            nonce = encrypted_data[:16]      # First 16 bytes
            tag = encrypted_data[16:32]      # Next 16 bytes  
            ciphertext = encrypted_data[32:] # Rest is ciphertext
            
            # Decrypt using AES-GCM
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            
            try:
                decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
            except ValueError as e:
                flash("❌ Decryption failed. Invalid password or corrupted file.")
                os.remove(upload_path)
                return redirect(url_for('index'))
            
            # Determine output filename (remove .enc extension)
            if filename.endswith('.enc'):
                output_filename = filename[:-4]  # Remove .enc extension
                print(f"🔓 Decrypting '{filename}' -> '{output_filename}'")
            else:
                output_filename = filename + ".decrypted"
                print(f"🔓 Decrypting '{filename}' -> '{output_filename}'")
            
            # Save decrypted file
            output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_filename)
            with open(output_path, "wb") as f:
                f.write(decrypted_data)
            
            # Clean up uploaded file
            os.remove(upload_path)
            
            return render_template(
                "index.html",
                result={
                    "filename": output_filename,
                    "type": "decrypted"
                },
            )

    except Exception as e:
        # Clean up uploaded file in case of error
        if os.path.exists(upload_path):
            os.remove(upload_path)
        
        flash(f"❌ Processing error: {str(e)}")
        return redirect(url_for('index'))


@app.route("/download/<filename>")
def download(filename):
    """Download processed files"""
    filename = secure_filename(filename)  # Security check
    file_path = os.path.join(app.config["OUTPUT_FOLDER"], filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        flash("❌ File not found. It may have been automatically cleaned up.")
        return redirect(url_for('index'))
    
    try:
        return send_from_directory(
            app.config["OUTPUT_FOLDER"], 
            filename, 
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f"❌ Download error: {str(e)}")
        return redirect(url_for('index'))


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash("❌ File too large. Maximum size is 100MB.")
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    flash("❌ Page not found.")
    return redirect(url_for('index'))


@app.errorhandler(500)
def server_error(e):
    """Handle server errors"""
    flash("❌ Server error occurred. Please try again.")
    return redirect(url_for('index'))


if __name__ == "__main__":
    print("🔐 Cyberpunk Neural Encryptor Starting...")
    print("🌐 Access at: http://localhost:5000")
    print("🔒 Ready for encryption/decryption operations!")
    
    # Run with debug mode for development
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)