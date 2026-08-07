from flask import Flask, render_template_string, request
import requests
import json

app = Flask(__name__)

# كود تسجيل الدخول الأصلي تماماً بدون أي تعديل
def login(number, password):
    url1 = 'https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Connection": "keep-alive",
        "silentLogin": "true",
        "x-agent-operatingsystem": "13",
        "clientId": "AnaVodafoneAndroid",
        "Accept-Language": "en",
        "x-agent-device": "Xiaomi M2102J20SG",
        "x-agent-version": "2025.11.1",
        "x-agent-build": "1063",
        "digitalId": "244BQYOGFM0IM",
        "device-id": "b83aab2d8fa633da",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "mobile.vodafone.com.eg",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/4.12.0"
    }
    data = {
        "username": number,
        "password": password,
        "grant_type": "password",
        "client_secret": "95fd95fb-7489-4958-8ae6-d31a525cd20a",
        "client_id": "ana-vodafone-app"
    }
    response = requests.post(url1, data=data, headers=headers)
    if response.status_code != 200:
        raise Exception(f"فشل تسجيل الدخول: {response.status_code} - {response.text}")
    return response.json()['access_token']

# كود تغيير كلمة المرور الأصلي تماماً بدون أي تعديل
def change_pass(number, token, password, newPass):
    url = "https://web.vodafone.com.eg/services/dxl/sam/serviceAccountManagement/v1/serviceAccount"
    
    payload = {
        "@type": "userPrefsUpdate",
        "customerAccount": {
            "authentication": {
                "password": password,
                "newPassword": newPass
            }
        },
        "resources": [
            {
                "resourceType": "MSISDN",
                "IDs": [
                    {
                        "value": number
                    }
                ]
            }
        ]
    }
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36",
        'Accept': "application/json",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'Content-Type': "application/json",
        'sec-ch-ua-platform': "\"Android\"",
        'Authorization': f"Bearer {token}",
        'Accept-Language': "AR",
        'msisdn': number,
        'sec-ch-ua': "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
        'clientId': "WebsiteConsumer",
        'sec-ch-ua-mobile': "?1",
        'Origin': "https://web.vodafone.com.eg",
        'Sec-Fetch-Site': "same-origin",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Dest': "empty",
        'Referer': "https://web.vodafone.com.eg/spa/profile",
    }
    
    response = requests.patch(url, data=json.dumps(payload), headers=headers)
    return response

# واجهة الموقع (HTML مدمجة داخل بايثون لتسهيل الرفع كملف واحد)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تغيير كلمة المرور</title>
    <style>
        body { font-family: Tahoma, sans-serif; background-color: #f4f4f9; text-align: center; padding: 50px; }
        .box { background: white; padding: 20px; border-radius: 10px; display: inline-block; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); width: 300px; }
        input { width: 90%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; }
        button { background: #e60000; color: white; border: none; padding: 10px 20px; width: 100%; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #cc0000; }
        .result { margin-top: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="box">
        <h2>تغيير كلمة المرور</h2>
        <form method="POST">
            <input type="text" name="number" placeholder="رقم الهاتف" required>
            <input type="password" name="password" placeholder="كلمة المرور الحالية" required>
            <input type="password" name="newPass" placeholder="كلمة المرور الجديدة" required>
            <button type="submit">تنفيذ</button>
        </form>
        {% if result %}
            <div class="result">{{ result }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    result_message = None
    if request.method == 'POST':
        number = request.form.get('number')
        password = request.form.get('password')
        newPass = request.form.get('newPass')
        
        try:
            token = login(number, password)
            res = change_pass(number, token, password, newPass)
            try:
                data = res.json()
                if data.get("reason") == "Repeated Password":
                    result_message = "❌ فشل التغيير: كلمة المرور الجديدة مستخدمة من قبل."
                elif data.get("state") == "updated":
                    result_message = "✅ تم تغيير كلمة المرور بنجاح!"
                else:
                    result_message = f"⚠️ استجابة غير متوقعة: {data}"
            except:
                result_message = f"⚠️ لم نتمكن من تحليل الاستجابة: {res.text}"
        except Exception as e:
            result_message = f"❌ حدث خطأ: {e}"
            
    return render_template_string(HTML_TEMPLATE, result=result_message)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

