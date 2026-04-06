"""
测试店端 API 功能
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

# 测试登录
def test_login():
    # 门店登录
    response = requests.post(f"{BASE_URL}/api/auth/login", data={
        "username": "store1",
        "password": "store123"
    })
    print(f"门店登录状态码：{response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"门店登录成功，token: {data['access_token'][:50]}...")
        return data["access_token"]
    else:
        print(f"门店登录失败：{response.text}")
        return None

# 测试获取我的文档
def test_my_docs(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/store/my_docs", headers=headers)
    print(f"\n获取我的文档状态码：{response.status_code}")
    if response.status_code == 200:
        print(f"获取成功：{response.json()}")
    else:
        print(f"获取失败：{response.text}")

# 测试管理员登录
def test_admin_login():
    response = requests.post(f"{BASE_URL}/api/auth/login", data={
        "username": "admin",
        "password": "admin123"
    })
    print(f"\n管理员登录状态码：{response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"管理员登录成功")
        return data["access_token"]
    else:
        print(f"管理员登录失败：{response.text}")
        return None

# 测试管理员统计
def test_admin_stats(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
    print(f"\n获取管理员统计状态码：{response.status_code}")
    if response.status_code == 200:
        print(f"统计数据：{response.json()}")
    else:
        print(f"获取失败：{response.text}")

if __name__ == "__main__":
    print("=" * 60)
    print("开始测试店端和管理员端 API")
    print("=" * 60)
    
    # 测试门店功能
    store_token = test_login()
    if store_token:
        test_my_docs(store_token)
    
    # 测试管理员功能
    admin_token = test_admin_login()
    if admin_token:
        test_admin_stats(admin_token)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
