import os
import string

from flask import Flask, request, jsonify, redirect
import psycopg2
import redis


app = Flask(__name__)

# Define the 62 unique characters used for short codes (0-9, a-z, A-Z).
ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase

# connect to redis for fast lookup of short codes
cache = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'redis'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
    decode_responses=True,
    )

def get_db():
    """Connect to the PostgreSQL for permanent storage"""
    return psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'db'),
        user=os.environ.get('POSTGRES_USER', 'postgres'),
        password=os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        database=os.environ.get('POSTGRES_DB', 'urlshortener'),
    )

def base62_encode(num):
    """Convert a number to a base62 string"""
    if num == 0:
        return ALPHABET[0]
    arr = []
    base = len(ALPHABET)
    while num:
        num, rem = divmod(num, base)
        arr.append(ALPHABET[rem])
    arr.reverse()
    return ''.join(arr)

def base62_decode(string):
    """Convert a base62 string back to a number"""
    if not string or any(char not in ALPHABET for char in string):
        raise ValueError('Invalid base62 string')

    base = len(ALPHABET)
    strlen = len(string)
    num = 0

    for idx, char in enumerate(string):
        power = (strlen - (idx + 1))
        num += ALPHABET.index(char) * (base ** power)
    return num


@app.route('/shorten', methods=['POST'])
def shorten_url():
    # grap the long URL from the request body
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing URL in request body'}), 400
    
    long_url = data['url']
    
    # save to postgeres - the database assigns an auto-incrementing ID to each new URL
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO urls (long_url) VALUES (%s) RETURNING id", (long_url,))
    url_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    # encode the database ID into a short code
    short_code = base62_encode(url_id)
    
    
    # cache the mapping in redis for fast lookup
    cache.set(short_code, long_url)
    
    
    return jsonify({'short_url': f"http://localhost:5000/{short_code}", "short_code": short_code}), 201


@app.route('/<short_code>', methods=['GET'])
def redirect_url(short_code):
    # check the fast cache first
    long_url = cache.get(short_code)
    if long_url:
        print("CACHE HIT", flush=True)
        return redirect(long_url, code=302)
    
    # if not found in cache, look up in the database
    print("CACHE MISS", flush=True)
    try:
        url_id = base62_decode(short_code)
    except ValueError:
        return jsonify({'error': 'Short URL not found'}), 404

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT long_url FROM urls WHERE id = %s", (url_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    if not result:
        return jsonify({'error': 'Short URL not found'}), 404
    
    # found it in the database, cache it for future requests
    long_url = result[0]
    cache.set(short_code, long_url)
    
    return redirect(long_url, code=302)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the service is running"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
