import requests

def test_api_time():
    url = "http://localhost:8000/api/time"
    response = requests.get(url)
    assert response.status_code == 200, f"Status code: {response.status_code}"
    data = response.json()
    assert "dies" in data, "dies not in response"
    assert "milidies" in data, "milidies not in response"
    assert "progress" in data, "progress not in response"
    assert 0 <= data["milidies"] <= 999, f"milidies out of range: {data['milidies']}"
    assert 0 <= data["progress"] <= 100, f"progress out of range: {data['progress']}"
    print("/api/time test passed.")

if __name__ == "__main__":
    test_api_time()
