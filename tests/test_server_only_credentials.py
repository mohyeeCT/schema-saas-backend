from credentials import hydrate_job_settings, strip_secret_fields


class _Response:
    def __init__(self, data):
        self.data = data


class _Query:
    def __init__(self, rows, fail=False):
        self.rows = rows
        self.fail = fail

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def execute(self):
        if self.fail:
            raise RuntimeError("table unavailable")
        return _Response(self.rows)


class _Supabase:
    def __init__(self, tables):
        self.tables = tables

    def table(self, name):
        value = self.tables.get(name, [])
        if isinstance(value, Exception):
            return _Query([], fail=True)
        return _Query(value)


def test_strip_secret_fields_removes_private_values():
    result = strip_secret_fields({
        "provider": "Claude",
        "api_key": "secret-ai",
        "dfs_login": "user@example.com",
        "dfs_password": "secret-dfs",
        "jina_api_key": "secret-jina",
        "firecrawl_api_key": "secret-fc",
        "schema_type": "Organization",
    })

    assert result == {
        "provider": "Claude",
        "dfs_login": "user@example.com",
        "schema_type": "Organization",
    }


def test_hydrate_job_settings_prefers_server_credentials():
    sb = _Supabase({
        "user_credentials": [{
            "provider_settings": {
                "api_key": "server-ai",
                "dfs_password": "server-dfs",
                "jina_api_key": "server-jina",
                "firecrawl_api_key": "server-fc",
            },
            "gsc_service_account": None,
        }],
        "user_settings": [],
    })

    hydrated = hydrate_job_settings(
        sb,
        "user-1",
        {
            "provider": "Claude",
            "api_key": "client-ai",
            "dfs_password": "client-dfs",
            "jina_api_key": "client-jina",
            "firecrawl_api_key": "client-fc",
        },
    )

    assert hydrated["api_key"] == "server-ai"
    assert hydrated["dfs_password"] == "server-dfs"
    assert hydrated["jina_api_key"] == "server-jina"
    assert hydrated["firecrawl_api_key"] == "server-fc"
