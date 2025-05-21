# Отчёт о покрытии тестами

Этот файл содержит информацию о покрытии кода тестами.

## Последние результаты покрытия

```
============================= test session starts =============================
platform win32 -- Python 3.12.6, pytest-8.3.5, pluggy-1.6.0
rootdir: C:\Users\romeo\PycharmProjects\FastAPI-assignment
plugins: anyio-4.9.0, cov-6.1.1
collected 28 items

tests\test_auth.py .....                                                 [ 17%]
tests\test_scenarios.py ...                                              [ 28%]
tests\test_tasks.py ....................                                 [100%]

============================== warnings summary ===============================
database.py:9
  C:\Users\romeo\PycharmProjects\FastAPI-assignment\database.py:9: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

..\FastAPI_project\venv\Lib\site-packages\pydantic\_internal\_config.py:295
..\FastAPI_project\venv\Lib\site-packages\pydantic\_internal\_config.py:295
  C:\Users\romeo\PycharmProjects\FastAPI_project\venv\Lib\site-packages\pydantic\_internal\_config.py:295: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

tests/test_auth.py: 1 warning
tests/test_scenarios.py: 4 warnings
tests/test_tasks.py: 17 warnings
  C:\Users\romeo\PycharmProjects\FastAPI-assignment\auth.py:34: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.12.6-final-0 _______________

Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
auth.py                          53      5    91%   20, 58-60, 63
database.py                      12      4    67%   12-16
main.py                          82      0   100%
models.py                        16      0   100%
schemas.py                       28      0   100%
tests\__init__.py                 0      0   100%
tests\conftest.py                47      0   100%
tests\test_auth.py               33      0   100%
tests\test_scenarios.py          98      0   100%
tests\test_tasks.py             170      0   100%
-----------------------------------------------------------
TOTAL                           580     50    91%
====================== 28 passed, 25 warnings in 32.45s =======================
```
