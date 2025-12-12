
# AI-Powered Product Review Analyzer

A Pyramid-based web application that automatically analyzes product reviews. It uses **Hugging Face** for sentiment analysis (Positive/Negative/Neutral) and **Google Gemini** to extract key summary points from the review text.

## 🚀 Features

* **Sentiment Analysis**: Determines if a review is Positive, Negative, or Neutral using the `twitter-roberta-base-sentiment` model.
* **Key Point Extraction**: Uses Google Gemini AI (`gemini-2.5-flash` with fallbacks) to summarize the review into 3 short key points.
* **Review Management**: Save, list, and delete reviews via REST API.
* **Robust Error Handling**: Includes fallback mechanisms for AI model timeouts or overload (Busy/503 errors).

## 🛠️ Tech Stack

* **Python 3.x**
* **Pyramid** (Web Framework)
* **SQLAlchemy** (Database ORM)
* **Hugging Face Inference API**
* **Google Gemini API**

## ⚙️ Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_folder>
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -e .
    pip install pyramid requests sqlalchemy zope.sqlalchemy
    ```

## 🔑 Configuration (API Keys)

You must configure your API keys in the `development.ini` file for the AI features to work.

1.  Open `development.ini`.
2.  Add the following lines under the `[app:main]` section:

```ini
[app:main]
use = egg:YourProjectName

# ... existing configuration ...

# API Configuration
hf.token = hf_xxxxxxxxxxxxxxxxxxxxxx
gemini.key = AIzaSyxxxxxxxxxxxxxxxxxxxx
## 🗄️ Database Setup

Initialize the database before running the app:

```bash
initialize_db development.ini
```

## ▶️ Running the Application

Start the server using `pserve`:

```bash
pserve development.ini --reload
```

The server will typically run at `http://localhost:6543`.

-----

## 📡 API Endpoints

### 1\. Analyze & Save Review

**Endpoint:** `POST /analyze_review`

Processes a review and saves it to the database.

**Request Body:**

```json
{
    "product_name": "Iphone 15 Pro",
    "review_text": "The battery life is amazing, but the charging speed is a bit slow. Camera is top notch!"
}
```

**Response:**

```json
{
    "id": 1,
    "product_name": "Iphone 15 Pro",
    "review_text": "The battery life is amazing...",
    "sentiment": "POSITIVE",
    "confidence": 0.98,
    "key_points": "[\"Amazing battery life\", \"Slow charging speed\", \"Top notch camera\"]",
    "created_at": "2023-10-27T10:00:00"
}
```

### 2\. Get All Reviews

**Endpoint:** `GET /get_reviews`

Retrieves all analysis history sorted by newest first.

**Response:**

```json
[
    {
        "id": 1,
        "product_name": "Iphone 15 Pro",
        "sentiment": "POSITIVE",
        ...
    },
    {
        "id": 2,
        ...
    }
]
```

### 3\. Delete All Reviews

**Endpoint:** `POST /delete_reviews`

Clears the entire database.

**Response:**

```json
{
    "message": "Deleted"
}
```

## ⚠️ Troubleshooting

  * **HF Error / Neutral Result:** If the Hugging Face model is "cold" (hasn't been used in a while), the first request might time out or return Neutral. Try sending the request again.
  * **Gemini Busy:** The code includes a fallback mechanism that tries multiple Gemini models (`flash`, `flash-lite`, etc.) if one is busy.

<!-- end list -->

```
```
