from __future__ import annotations
import json
import ipaddress
from typing import Any, Dict


def _base(src_ip, dst_ip, src_port, dst_port, protocol, bytes, packets, first, last, cloud, account=None, vpc_id=None, extra=None):
    return {
        "src_ip": str(ipaddress.ip_address(src_ip)),
        "dst_ip": str(ipaddress.ip_address(dst_ip)),
        "src_port": int(src_port),
        "dst_port": int(dst_port),
        "protocol": int(protocol),
        "bytes": int(bytes),
        "packets": int(packets),
        "first_seen": float(first),
        "last_seen": float(last),
        "cloud": cloud,
        "account": account,
        "vpc_id": vpc_id,
        "extra": extra or {},
    }


def normalise(record: Any) -> Dict[str, Any]:
    if isinstance(record, str):
        try:
            record = json.loads(record)
        except json.JSONDecodeError:
            parts = record.split()
            if len(parts) >= 14:
                # AWS VPC Flow Logs format
                return _base(
                    parts[3], parts[4], parts[5], parts[6], parts[7],
                    parts[9], parts[8], parts[10], parts[11],
                    "aws", account=parts[1], vpc_id=parts[2]
                )
            raise ValueError("Unknown record format")
    if "properties" in record and "flows" in record["properties"]:
        # Azure NSG Flow logs
        flow = record["properties"]["flows"][0]["flows"][0]
        tcp = flow["flowTuples"][0].split(",")
        return _base(tcp[1], tcp[2], tcp[3], tcp[4], tcp[5], tcp[8], tcp[7], tcp[6], tcp[6], "azure")
    if "src_ip" in record:
        return record
    # GCP
    if "logName" in record:
        payload = record.get("jsonPayload", {})
        return _base(
            payload.get("src_ip"), payload.get("dest_ip"), payload.get("src_port",0),
            payload.get("dest_port",0), payload.get("protocol",0),
            payload.get("bytes",0), payload.get("packets",0), payload.get("start_time",0),
            payload.get("end_time",0), "gcp")
    raise ValueError("Cannot normalise record")
