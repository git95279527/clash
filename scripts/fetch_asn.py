import requests
import os
from netaddr import IPNetwork, cidr_merge

ASN_LIST = {
    "Apple": ["AS714", "AS6185", "AS36561"],
    "Akamai": ["AS20940", "AS12222"],
    "Amazon": ["AS16509"],
    "Fastly": ["AS54113"]
}

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_prefixes_from_ripestat(asn):
    url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            v4 = []
            v6 = []
            for item in data['data']['prefixes']:
                prefix = item['prefix']
                if ":" in prefix:
                    v6.append(prefix)
                else:
                    v4.append(prefix)
            return v4, v6
        else:
            print(f"[ERROR] Failed to fetch ASN {asn}, status {resp.status_code}")
    except Exception as e:
        print(f"[ERROR] Exception fetching ASN {asn}: {e}")
    return [], []

def merge_ip_list(ip_list):
    try:
        networks = [IPNetwork(ip.strip()) for ip in ip_list if ip.strip()]
        merged = cidr_merge(networks)
        return [str(net) for net in merged]
    except Exception as e:
        print(f"[ERROR] Merge failed: {e}")
        return ip_list

def write_merged_list(org, asn_list):
    v4_total, v6_total = [], []
    for asn in asn_list:
        v4, v6 = fetch_prefixes_from_ripestat(asn)
        print(f"[{org}] ASN {asn}: {len(v4)} IPv4, {len(v6)} IPv6")
        v4_total.extend(v4)
        v6_total.extend(v6)

    merged_v4 = merge_ip_list(v4_total)
    merged_v6 = merge_ip_list(v6_total)

    with open(f"{OUTPUT_DIR}/{org}_ipv4.txt", "w") as f:
        for ip in sorted(merged_v4):
            f.write(ip + "\n")

    with open(f"{OUTPUT_DIR}/{org}_ipv6.txt", "w") as f:
        for ip in sorted(merged_v6):
            f.write(ip + "\n")

if __name__ == "__main__":
    for org, asns in ASN_LIST.items():
        write_merged_list(org, asns)
