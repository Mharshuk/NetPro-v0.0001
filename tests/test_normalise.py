import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from normalise import normalise

aws_line = "2 123456789012 eni-abc 10.0.0.1 10.0.0.2 12345 80 6 1 60 1627028412 1627028424 ACCEPT OK"

azure_record = {
    "properties": {
        "flows": [{"flows": [{"flowTuples": ["1627028412,10.0.0.1,10.0.0.2,12345,80,6,1627028424,1,60"]}]}]
    }
}

gcp_record = {
    "logName": "projects/test/logs/flows",
    "jsonPayload": {
        "src_ip": "10.0.0.1",
        "dest_ip": "10.0.0.2",
        "src_port": 12345,
        "dest_port": 80,
        "protocol": 6,
        "bytes": 60,
        "packets": 1,
        "start_time": 1627028412.0,
        "end_time": 1627028424.0
    }
}

def test_aws():
    rec = normalise(aws_line)
    assert rec["src_ip"] == "10.0.0.1"
    assert rec["dst_port"] == 80

def test_azure():
    rec = normalise(azure_record)
    assert rec["cloud"] == "azure"
    assert rec["dst_port"] == 80

def test_gcp():
    rec = normalise(gcp_record)
    assert rec["cloud"] == "gcp"
