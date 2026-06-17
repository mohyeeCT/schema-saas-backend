import base64

import requests

BASE = "https://api.dataforseo.com/v3"


def _auth_header(login: str, password: str) -> str:
    token = base64.b64encode(f"{login}:{password}".encode()).decode()
    return f"Basic {token}"


def _friendly_error(exc: Exception) -> str:
    if isinstance(exc, requests.Timeout):
        return "DataForSEO request timed out. Check your internet connection."
    if isinstance(exc, requests.ConnectionError):
        return "Cannot connect to DataForSEO API. Check your internet connection."
    return f"DataForSEO error: {exc}"


def _post(path: str, payload: list[dict], login: str, password: str) -> dict:
    try:
        response = requests.post(
            f"{BASE}/{path}",
            headers={
                "Content-Type": "application/json",
                "Authorization": _auth_header(login, password),
            },
            json=payload,
            timeout=45,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        raise RuntimeError(_friendly_error(exc)) from exc

    task = (data.get("tasks") or [{}])[0]
    status_code = task.get("status_code")
    if status_code and status_code != 20000:
        message = task.get("status_message") or "DataForSEO task failed."
        raise RuntimeError(f"DataForSEO error: {message}")
    return data


def get_serp_data(login: str, password: str, keyword: str) -> list[dict]:
    payload = [{
        "keyword": keyword,
        "language_code": "en",
        "location_name": "United States",
        "depth": 10,
    }]
    data = _post("serp/google/organic/live/advanced", payload, login, password)
    return (((data.get("tasks") or [{}])[0].get("result") or [{}])[0].get("items") or [])
