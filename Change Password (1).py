import requests
import json

number = input("Enter Your Number: ")
password = input("Enter Your Password: ")
newPass = input("Enter New Password: ")

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

# تنفيذ البرنامج
try:
    token = login(number, password)
    print("✅ تم تسجيل الدخول بنجاح، جاري تغيير كلمة المرور...")
    
    res = change_pass(number, token, password, newPass)
    print("🔹 استجابة الخادم:")
    
    # تحليل الاستجابة
    try:
        data = res.json()
        if data.get("reason") == "Repeated Password":
            print("❌ فشل التغيير: كلمة المرور الجديدة مستخدمة من قبل. استخدم كلمة مرور أخرى.")
        elif data.get("state") == "updated":
            print("✅ تم تغيير كلمة المرور بنجاح!")
        else:
            print("⚠️ استجابة غير متوقعة:", data)
    except:
        print("⚠️ لم نتمكن من تحليل الاستجابة:", res.text)
        
except Exception as e:
    print("❌ حدث خطأ:", e)