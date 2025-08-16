from flask import Flask, render_template, request, jsonify
from pinecone import Pinecone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('env.txt')  # Using env.txt since .env is blocked

app = Flask(__name__)

# Initialize Pinecone
try:
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    # Get the index for your knowledge base
    index_name = os.getenv("PINECONE_INDEX_NAME", "veterans-benefits")
    try:
        index = pc.Index(index_name)
        print("✅ Pinecone index connected successfully")
    except Exception as e:
        print(f"⚠️  Pinecone index not found: {e}")
        index = None
except Exception as e:
    print(f"❌ Error initializing Pinecone: {e}")
    index = None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    if not index:
        return jsonify({"error": "Pinecone index not available"}), 500
    
    try:
        prompt = request.json.get("prompt", "")
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # For now, return a placeholder response since we need to implement
        # the actual Pinecone query logic without pinecone-assistant
        # This will get your app running, then we can enhance it
        
        return jsonify({
            "content": f"I received your question: '{prompt}'. The Pinecone integration is being set up. This is a placeholder response while we configure the full assistant functionality.",
            "citations": []
        })
        
    except Exception as e:
        print(f"Error in ask endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "pinecone_available": index is not None,
        "environment": os.getenv("FLASK_ENV", "production")
    })

# Debug routes to help troubleshoot
@app.route("/debug")
def debug():
    return jsonify({
        "app_name": app.name,
        "template_folder": app.template_folder,
        "static_folder": app.static_folder,
        "routes": [str(rule) for rule in app.url_map.iter_rules()],
        "current_working_directory": os.getcwd(),
        "files_in_cwd": os.listdir(".") if os.path.exists(".") else "Directory not accessible",
        "pinecone_status": "connected" if index else "disconnected"
    })

@app.route("/test")
def test():
    return "Test route working! Flask is running correctly."

@app.route("/ping")
def ping():
    return jsonify({"message": "pong", "status": "ok"})

if __name__ == "__main__":
    print("🚀 Starting Veterans Benefits Assistant...")
    print(f"📁 Templates folder: {app.template_folder}")
    print(f"🔑 Pinecone API Key: {'✅ Set' if os.getenv('PINECONE_API_KEY') else '❌ Missing'}")
    print(f"📊 Pinecone Index: {os.getenv('PINECONE_INDEX_NAME', 'veterans-benefits')}")
    print(f"📍 Current working directory: {os.getcwd()}")
    print(f"📂 Files in current directory: {os.listdir('.') if os.path.exists('.') else 'Directory not accessible'}")
    
    # Get port from environment variable (for cloud deployment)
    port = int(os.environ.get("PORT", 5000))
    
    app.run(debug=True, host='0.0.0.0', port=port)
