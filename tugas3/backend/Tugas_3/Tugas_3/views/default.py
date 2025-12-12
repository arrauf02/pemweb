from pyramid.view import view_config
from pyramid.response import Response
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from ..models import Review

# --- LIBRARY RESMI (SARAN TEMANMU) ---
from huggingface_hub import InferenceClient
import google.generativeai as genai

# ============================================================
# 1. SETUP ENV (WAJIB JALAN DULUAN)
# ============================================================
def setup_environment():
    # Cari file .env mundur 2 folder dari file ini
    current_file = Path(__file__).resolve()
    project_root = current_file.parents[2] # backend/Tugas_3
    env_path = project_root / '.env'
    
    print(f"\n🔌 SYSTEM CHECK:")
    print(f"   Target .env: {env_path}")
    
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
        print("   ✅ STATUS: File .env DITEMUKAN!")
    else:
        print("   ❌ FATAL: File .env TIDAK DITEMUKAN! Cek folder backend/Tugas_3")

# Jalankan setup saat file ini dimuat pertama kali
setup_environment()

# ============================================================
# 2. FUNGSI AI (PAKE LIBRARY RESMI)
# ============================================================

def call_huggingface_sentiment(text):
    # Ambil token
    token = os.getenv("HF_TOKEN")
    
    if not token:
        print("❌ HF ERROR: Token kosong/tidak terbaca dari .env")
        return {'label': 'CONFIG_ERROR', 'score': 0.0}

    try:
        # --- CARA TEMANMU (InferenceClient) ---
        client = InferenceClient(token=token)
        model_id = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        
        # Panggil API
        result = client.text_classification(text, model=model_id)
        
        # Ambil score tertinggi
        if result:
            best = max(result, key=lambda x: x.score)
            
            # Normalisasi Label (biar rapi di database)
            label = best.label.upper()
            if "LABEL_2" in label or "POSITIVE" in label: label = "POSITIVE"
            elif "LABEL_0" in label or "NEGATIVE" in label: label = "NEGATIVE"
            else: label = "NEUTRAL"
            
            return {'label': label, 'score': best.score}
            
    except Exception as e:
        print(f"❌ HF Exception: {e}")
    
    return {'label': 'NEUTRAL', 'score': 0.0}

def extract_key_points_gemini(text):
    api_key = os.getenv("GEMINI_KEY")
    
    if not api_key:
        print("❌ GEMINI ERROR: Key kosong/tidak terbaca dari .env")
        return ["Config Error"]

    try:
        # --- CARA TEMANMU (Google GenAI SDK) ---
        genai.configure(api_key=api_key)
        
        # Coba model terbaru dulu
        models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-latest"]
        
        for model_name in models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    f"Extract 3 key points from this review. Return ONLY a JSON array of strings. Review: {text}"
                )
                
                # Bersihkan hasil (kadang ada markdown ```json)
                if response.text:
                    clean = response.text.replace("```json", "").replace("```", "").strip()
                    return json.loads(clean)
            except:
                continue # Coba model berikutnya jika error
                
    except Exception as e:
        print(f"❌ Gemini Exception: {e}")

    return ["AI Busy/Failed"]

# ============================================================
# 3. ENDPOINTS (JANGAN DIUBAH)
# ============================================================

@view_config(route_name='analyze_review', request_method='OPTIONS')
@view_config(route_name='get_reviews', request_method='OPTIONS')
@view_config(route_name='delete_reviews', request_method='OPTIONS')
def options_view(request):
    return Response(json_body={})

@view_config(route_name='analyze_review', request_method='POST', renderer='json')
def analyze_review(request):
    try:
        # Debugging: Pastikan token ada sebelum proses
        if not os.getenv("HF_TOKEN"): setup_environment()

        data = request.json_body
        product_name = data.get('product_name')
        review_text = data.get('review_text')
        
        print(f"🔄 Analyzing: {product_name}...")

        sentiment_res = call_huggingface_sentiment(review_text)
        points_res = extract_key_points_gemini(review_text)
        
        new_review = Review(
            product_name=product_name, review_text=review_text,
            sentiment=sentiment_res['label'], confidence=sentiment_res['score'],
            key_points=json.dumps(points_res)
        )
        request.dbsession.add(new_review)
        request.dbsession.flush()
        
        print("✅ Success!")
        return new_review.to_json()

    except Exception as e:
        print(f"❌ Server Error: {e}")
        request.response.status = 500
        return {'error': str(e)}

@view_config(route_name='get_reviews', request_method='GET', renderer='json')
def get_reviews(request):
    reviews = request.dbsession.query(Review).order_by(Review.created_at.desc()).all()
    return [r.to_json() for r in reviews]

@view_config(route_name='delete_reviews', request_method='POST', renderer='json')
def delete_reviews(request):
    request.dbsession.query(Review).delete()
    return {'message': 'Deleted'}

@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def my_view(request):
    return {'project': 'Tugas_3'}