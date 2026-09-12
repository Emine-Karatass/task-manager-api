from fastapi.testclient import TestClient
from task_manager_api import app
import uuid

client=TestClient(app)

def test_docs_erisilebilir():
    response=client.get("/docs")
    assert response.status_code == 200

def test_kullanici_kaydi_basarili():
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    response=client.post("/register",json={"username": unique_username,"password":"testpass123"})
    assert response.status_code==200
    assert response.json()["username"] == unique_username

def test_kullanici_kaydi_tekrar_basarisiz():
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    client.post("/register", json={"username": unique_username, "password": "testpass123"})
    response=client.post("/register",json={"username":"testuser1","password":"testpass123"})
    assert response.status_code == 400

def test_giris_basarili():
    unique_username=f"testuser_{uuid.uuid4().hex[:8]}"
    client.post("/register",json={"username": unique_username,"password":"testpass123"})
    
    response = client.post("/login",data={"username":unique_username,"password":"testpass123"})
    assert response.status_code==200
    assert "access_token" in response.json()

def test_gorev_olusturma():
    unique_username=f"testuser_{uuid.uuid4().hex[:8]}"
    client.post("/register",json={"username": unique_username,"password":"testpass123"})
    login_response= client.post("/login",data={"username":unique_username,"password":"testpass123"})
    token = login_response.json()["access_token"]

    headers = {"Authorization":f"Bearer {token}"}
    response = client.post("/tasks",json={"title":"test görevi","category":"test","priority":"normal"},headers=headers)

    assert response.status_code == 200
    assert response.json()["title"]== "test görevi"
    assert response.json()["owner"] == unique_username

def test_görev_oluşturma():
    #Kullanıcı A: kayıt ol,giriş yap,görev oluştur
    username_a=f"testuser_{uuid.uuid4().hex[:8]}"
    client.post("/register",json={"username":username_a,"password":"testpass123"})
    login_a=client.post("/login",data={"username":username_a,"password":"testpass123"})
    token_a =login_a.json()["access_token"]
    headers_a={"Authorization":f"Bearer {token_a}"}

    create_response=client.post("/tasks",json={"title":"A'nın görevi","category":"test","priority":"normal"},headers=headers_a)
    task_id = create_response.json()["id"]

    #kullanıcı B: kayıt ol,giriş yap
    username_b =f"testuser_{uuid.uuid4().hex[:8]}"
    client.post("/register",json={"username": username_b,"password":"testpass123"})
    login_b =client.post("/login",data ={"username":username_b,"password":"testpass123"})
    token_b= login_b.json()["access_token"]
    headers_b ={"Authorization":f"Bearer {token_b}"}

    #kullanıcı B,A'nın görevine erişmeye çalışıyor
    response=client.get(f"/tasks/{task_id}",headers=headers_b)
    assert response.status_code == 404

def test_gorev_guncelleme():
    username_a=f"testuser_{uuid.uuid4().hex[:8]}"
    client.post("/register",json={"username":username_a,"password":"testpass123"})
    login_a=client.post("/login",data={"username":username_a,"password":"testpass123"})
    token_a = login_a.json()["access_token"]
    headers_a={"Authorization":f"Bearer {token_a}"}

    create_response = client.post("/tasks", json={"title": "A'nın görevi", "category": "test", "priority": "normal"}, headers=headers_a)
    task_id = create_response.json()["id"]

    response=client.put(f"/tasks/{task_id}",json= {"completed": True},headers=headers_a)
    assert response.status_code == 200
    assert response.json()["completed"] == True

def test_gorev_silme():
    username_a=f"testuser_{uuid.uuid4().hex[:8]}"
    client.post("/register",json={"username":username_a,"password":"testpass123"})
    login_a=client.post("/login",data={"username":username_a,"password":"testpass123"})
    token_a = login_a.json()["access_token"]
    headers_a={"Authorization":f"Bearer {token_a}"}

    create_response = client.post("/tasks", json={"title": "A'nın görevi", "category": "test", "priority": "normal"}, headers=headers_a)
    task_id = create_response.json()["id"]

    delete_response=client.delete(f"/tasks/{task_id}",headers=headers_a)
    assert delete_response.status_code == 200

    get_response = client.get(f"/tasks/{task_id}", headers=headers_a)
    assert get_response.status_code == 404

def test_yanlis_sifre_ile_giris():
    username_a = f"testuser_{uuid.uuid4().hex[:8]}"
    client.post("/register", json={"username": username_a, "password": "testpass123"})
    response = client.post("/login", data={"username": username_a, "password": "yanlis_sifre"})
    assert response.status_code == 401


def test_olmayan_kullanici_ile_giris():
    response = client.post("/login", data={"username": "olmayan_kullanici_xyz", "password": "testpass123"})
    assert response.status_code == 401


def test_token_olmadan_erisim():
    response = client.get("/tasks")
    assert response.status_code == 401


def test_olmayan_gorevi_guncelleme():
    username_a = f"testuser_{uuid.uuid4().hex[:8]}"
    client.post("/register", json={"username": username_a, "password": "testpass123"})
    login_a = client.post("/login", data={"username": username_a, "password": "testpass123"})
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    response = client.put("/tasks/999999", json={"completed": True}, headers=headers_a)
    assert response.status_code == 404

def test_negatif_id_ile_erisim():
    username_a = f"testuser_{uuid.uuid4().hex[:8]}"
    client.post("/register", json={"username": username_a, "password": "testpass123"})
    login_a = client.post("/login", data={"username": username_a, "password": "testpass123"})
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    response = client.get("/tasks/-1", headers=headers_a)
    assert response.status_code == 404

def test_bos_kullanici_adi_ile_kayit():
    response= client.post("/register",json={"username":"","password":"testpass123"})
    assert response.status_code == 422






