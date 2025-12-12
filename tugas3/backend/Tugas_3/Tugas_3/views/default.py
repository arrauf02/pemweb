from pyramid.view import view_config
from pyramid.response import Response
import requests
import json
from ..models import Review

def get_settings(request):
    return request.registry.settings

def call_huggingface_sentiment(text, token):
    if not token: return {'label': 'CONFIG_ERROR', 'score': 0.0}
    
    API_URL = "https://router.huggingface.co/hf-inference/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": text}
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ HF Error {response.status_code}: {response.text}")
            return {'label': 'NEUTRAL', 'score': 0.0}
            
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            if isinstance(first, list):
                best = max(first, key=lambda x: x['score'])
            elif isinstance(first, dict):
                best = max(result, key=lambda x: x['score'])
            else:
                return {'label': 'NEUTRAL', 'score': 0.0}

            label = best['label'].upper()
            if "LABEL_2" in label or "POSITIVE" in label: label = "POSITIVE"
            elif "LABEL_0" in label or "NEGATIVE" in label: label = "NEGATIVE"
            else: label = "NEUTRAL"
            
            return {'label': label, 'score': best['score']}
                 
        return {'label': 'NEUTRAL', 'score': 0.0}
        
    except Exception as e:
        print(f"❌ HF Exception: {e}")
      
        return {'label': 'NEUTRAL', 'score': 0.0}

def extract_key_points_gemini(text, api_key):
    if not api_key: return ["Config Error"]
    candidate_models = [
        "gemini-2.5-flash",       
        "gemini-2.5-flash-lite",  
        "gemini-2.0-flash",       
        "gemini-1.5-flash-latest" 
    ]
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Extract 3 short key points from this review. Return ONLY a JSON array of strings (e.g. ['point 1', 'point 2']). Review: {text}"
            }]
        }]
    }

    for model in candidate_models:
        URL = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            print(f"🔄 Trying Gemini Model: {model}...")
            response = requests.post(URL, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                try:
                    raw_text = result['candidates'][0]['content']['parts'][0]['text']
                    clean_text = raw_text.replace("```json", "").replace("```", "").strip()
                    return json.loads(clean_text)
                except Exception:
                    return ["Analysis Done (Parsing Error)"]
            
            if response.status_code == 404:
                continue 
            else:
                print(f"❌ Gemini Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection Error ({model}): {e}")
            continue

    return ["Failed to extract points (All models failed)"]


@view_config(route_name='analyze_review', request_method='OPTIONS')
@view_config(route_name='get_reviews', request_method='OPTIONS')
@view_config(route_name='delete_reviews', request_method='OPTIONS')
def options_view(request):
    return Response(json_body={})

@view_config(route_name='analyze_review', request_method='POST', renderer='json')
def analyze_review(request):
    try:
        settings = get_settings(request)
        hf_token = settings.get('hf.token')
        gemini_key = settings.get('gemini.key')

        data = request.json_body
        product_name = data.get('product_name')
        review_text = data.get('review_text')
        
        if not product_name or not review_text:
            request.response.status = 400
            return {'error': 'Missing input'}

        print(f"🔄 Processing: {product_name}...")

        
        sentiment_res = call_huggingface_sentiment(review_text, hf_token)
        
        
        points_res = extract_key_points_gemini(review_text, gemini_key)
        
        new_review = Review(
            product_name=product_name,
            review_text=review_text,
            sentiment=sentiment_res['label'],
            confidence=sentiment_res['score'],
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
    try:
        request.dbsession.query(Review).delete()
        print("🗑️ All reviews deleted!")
        return {'message': 'Deleted'}
    except Exception as e:
        request.response.status = 500
        return {'error': str(e)}

@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def my_view(request):
    return {'project': 'Tugas_3'}