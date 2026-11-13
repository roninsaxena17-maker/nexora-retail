import os
from dotenv import load_dotenv
from opensearchpy import OpenSearch

load_dotenv()

HOST = os.getenv("OPENSEARCH_HOST")
PORT = int(os.getenv("OPENSEARCH_PORT", "24516"))
USERNAME = os.getenv("OPENSEARCH_USER")
PASSWORD = os.getenv("OPENSEARCH_PASSWORD")

client = OpenSearch(
    hosts=[{
        "host": HOST,
        "port": PORT
    }],
    http_auth=(USERNAME, PASSWORD),
    use_ssl=True,
    verify_certs=True,
    ssl_show_warn=False,
    timeout=10
)


def test_connection():
    try:
        info = client.info()
        print("Connected to OpenSearch successfully!")
        print("Cluster:", info.get("cluster_name"))
        print("Version:", info.get("version", {}).get("number"))
        return True
    except Exception as error:
        print("OpenSearch connection failed:", repr(error))
        return False


if __name__ == "__main__":
    test_connection()
