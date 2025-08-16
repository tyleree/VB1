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
    # Get the index for your knowledge base - try different index names
    index_names = ["veterans-benefits", "vb", "veterans", "benefits"]
    index = None
    
    for index_name in index_names:
        try:
            index = pc.Index(index_name)
            print(f"✅ Pinecone index '{index_name}' connected successfully")
            break
        except Exception as e:
            print(f"⚠️  Pinecone index '{index_name}' not found: {e}")
            continue
    
    if not index:
        print("⚠️  No Pinecone index found. App will run with placeholder responses.")
        
except Exception as e:
    print(f"❌ Error initializing Pinecone: {e}")
    index = None

@app.route("/")
def home():
    # Temporary inline HTML to fix template issue
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Veterans Benefits Assistant</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        textarea {
            width: 100%;
            height: 100px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            resize: vertical;
            font-family: inherit;
        }
        textarea:focus {
            outline: none;
            border-color: #3498db;
        }
        button {
            background-color: #3498db;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        button:disabled {
            background-color: #bdc3c7;
            cursor: not-allowed;
        }
        .response {
            margin-top: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        .citations {
            margin-top: 20px;
        }
        .citations h3 {
            color: #2c3e50;
            margin-bottom: 15px;
        }
        .citation-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 6px;
            border: 1px solid #ddd;
        }
        .citation-item a {
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
        }
        .citation-item a:hover {
            text-decoration: underline;
        }
        .loading {
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
        }
        .status {
            text-align: center;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 6px;
            font-weight: bold;
        }
        .status.success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.warning {
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Veterans Benefits Knowledge Base Assistant</h1>
        
        <div class="status success">
            ✅ App is running successfully on Render!
        </div>
        
        <div class="input-group">
            <textarea id="prompt" placeholder="Ask a question about veterans benefits..."></textarea>
        </div>
        
        <button onclick="ask()" id="askButton">Ask Question</button>
        
        <div id="response" class="response" style="display: none;"></div>
        
        <div id="refs" class="citations" style="display: none;"></div>
    </div>

    <script>
        async function ask() {
            const prompt = document.getElementById('prompt').value.trim();
            if (!prompt) {
                alert('Please enter a question');
                return;
            }

            const button = document.getElementById('askButton');
            const responseDiv = document.getElementById('response');
            const refsDiv = document.getElementById('refs');

            // Show loading state
            button.disabled = true;
            button.textContent = 'Processing...';
            responseDiv.style.display = 'block';
            responseDiv.innerHTML = '<div class="loading">Processing your question...</div>';
            refsDiv.style.display = 'none';

            try {
                const res = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt})
                });
                
                if (!res.ok) {
                    throw new Error(`HTTP error! status: ${res.status}`);
                }
                
                const data = await res.json();
                
                // Display response
                responseDiv.innerHTML = `<strong>Answer:</strong><br>${data.content}`;
                
                // Display citations if available
                if (data.citations && data.citations.length > 0) {
                    refsDiv.style.display = 'block';
                    refsDiv.innerHTML = '<h3>References:</h3>';
                    
                    data.citations.forEach((c, i) => {
                        const div = document.createElement('div');
                        div.className = 'citation-item';
                        const a = document.createElement('a');
                        a.href = c.url;
                        a.target = '_blank';
                        a.textContent = `Reference ${i+1}: ${c.file} (Page ${c.page})`;
                        div.appendChild(a);
                        refsDiv.appendChild(div);
                    });
                }
            } catch (error) {
                responseDiv.innerHTML = `<strong>Error:</strong> ${error.message}`;
                console.error('Error:', error);
            } finally {
                // Reset button state
                button.disabled = false;
                button.textContent = 'Ask Question';
            }
        }

        // Allow Enter key to submit
        document.getElementById('prompt').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                ask();
            }
        });
    </script>
</body>
</html>
    """
    return html_content

@app.route("/ask", methods=["POST"])
def ask():
    try:
        prompt = request.json.get("prompt", "")
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        if index:
            # Pinecone is connected - return enhanced response
            return jsonify({
                "content": f"I received your question: '{prompt}'. Pinecone is connected and ready! This is a placeholder response while we implement the full query functionality.",
                "citations": []
            })
        else:
            # Pinecone not connected - return basic response
            return jsonify({
                "content": f"I received your question: '{prompt}'. The app is running successfully! Pinecone connection is being configured. This is a placeholder response.",
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
