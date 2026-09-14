import requests

from crawler.dummyjson import fetch_products


def test_fetch_products_retries_after_request_failure(monkeypatch):
    attempts = []

    def mock_get(*args, **kwargs):
        attempts.append(1)

        if len(attempts) < 3:
            raise requests.RequestException("模拟网络错误")

        class MockResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "products": [
                        {
                            "id": 1,
                            "title": "Test Product"
                        }
                    ],
                    "total": 1
                }

        return MockResponse()

    monkeypatch.setattr(
        "crawler.dummyjson.requests.get",
        mock_get
    )

    result = fetch_products(
        limit=30,
        skip=0,
        retries=3,
        timeout=10
    )

    assert result is not None
    assert result["total"] == 1
    assert len(attempts) == 3