from fastapi import APIRouter, Query, HTTPException
from app.search.opensearch_client import client

router = APIRouter(prefix="/search", tags=["Search"])

INDEX_NAME = "nexora-products"


@router.get("/")
def search_products(
    q: str = Query(..., min_length=2),
    category: str | None = None
):
    try:
        filters = []

        if category:
            filters.append({
                "term": {
                    "category": category
                }
            })

        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": q,
                                "fields": [
                                    "name^3",
                                    "description",
                                    "category"
                                ],
                                "fuzziness": "AUTO"
                            }
                        }
                    ],
                    "filter": filters
                }
            }
        }

        response = client.search(
            index=INDEX_NAME,
            body=search_query
        )

        results = [
            hit["_source"]
            for hit in response["hits"]["hits"]
        ]

        return {
            "query": q,
            "total": response["hits"]["total"]["value"],
            "results": results
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(error)}"
        )
