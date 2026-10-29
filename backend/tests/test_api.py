from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r=client.get('/api/health'); assert r.status_code==200
    assert r.json()['status']=='ok'

def test_empty_resume_rejected():
    r=client.post('/api/analyze',json={'resume_text':'short'}); assert r.status_code==422

def test_demo_analysis():
    text='Python developer with React projects and SQL. Education: Computer Science. Internship at a software company.'
    r=client.post('/api/analyze',json={'resume_text':text}); assert r.status_code==200
    assert r.json()['resume_summary']['profile']
    assert r.json()['skills']

def test_json_export_shape():
    r=client.post('/api/analyze',json={'resume_text':'A'*100}); assert r.status_code==200
    assert isinstance(r.json()['learning_roadmap'],list)

def test_api_key_configuration_is_runtime_only():
    r=client.post('/api/configure-ai',json={'api_key':'test-key-not-a-real-secret'})
    assert r.status_code==200
    assert r.json()['configured'] is True
    cleared=client.delete('/api/configure-ai')
    assert cleared.status_code==200
    assert cleared.json()['demo_mode'] is True
