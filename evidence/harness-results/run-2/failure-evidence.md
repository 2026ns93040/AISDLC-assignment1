Gate: lint
Failed rule or test:I001, UP017, FURB162
Expected behaviour:
Observed behaviour:
Relevant output:

I001 [*] Import block is un-sorted or un-formatted
  --> src\main.py:1:1
   |
 1 | / from datetime import date, datetime, timedelta, timezone
 2 | | import os
 3 | | import re
 4 | | from threading import Lock
 5 | | from contextlib import asynccontextmanager
 6 | |
 7 | | from fastapi import FastAPI, HTTPException, Request
 8 | | from fastapi.exceptions import RequestValidationError
 9 | | from fastapi.responses import JSONResponse
10 | | from pydantic import BaseModel, ConfigDict, Field
11 | | from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, create_engine, func, select, text
12 | | from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
13 | | from sqlalchemy.pool import StaticPool
   | |______________________________________^
help: Organize imports
   |
   - from datetime import date, datetime, timedelta, timezone
1  | import os
2  | import re
3  + from contextlib import asynccontextmanager
4  + from datetime import date, datetime, timedelta, timezone
5  | from threading import Lock
   - from contextlib import asynccontextmanager
6  |
--------------------------------------------------------------------------------
10 | from pydantic import BaseModel, ConfigDict, Field
   - from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, create_engine, func, select, text
   - from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
11 + from sqlalchemy import (
12 +     Date,
13 +     DateTime,
14 +     ForeignKey,
15 +     Integer,
16 +     String,
17 +     create_engine,
18 +     func,
19 +     select,
20 +     text,
21 + )
22 + from sqlalchemy.orm import (
23 +     DeclarativeBase,
24 +     Mapped,
25 +     Session,
26 +     mapped_column,
27 +     relationship,
28 +     sessionmaker,
29 + )
30 | from sqlalchemy.pool import StaticPool
   -
31 |
   |

UP017 [*] Use `datetime.UTC` alias
   --> src\main.py:133:25
    |
132 | def _utc_now() -> datetime:
133 |     return datetime.now(timezone.utc)
    |                         ^^^^^^^^^^^^
help: Convert to `datetime.UTC` alias
    |
    - from datetime import date, datetime, timedelta, timezone
1   + from datetime import date, datetime, timedelta, timezone, UTC
2   | import os
--------------------------------------------------------------------------------
132 | def _utc_now() -> datetime:
    -     return datetime.now(timezone.utc)
133 +     return datetime.now(UTC)
134 |
    |

FURB162 Unnecessary timezone replacement with zero offset
   --> tests\test_book_loan_api.py:115:40
    |
113 |     assert response.status_code == 201
114 |     body = response.json()
115 |     loaned_at = datetime.fromisoformat(body["loaned_at"].replace("Z", "+00:00"))
    |                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
116 |     due_date = date.fromisoformat(body["due_date"])
117 |     assert due_date == (loaned_at.date() + timedelta(days=14))
    |
help: Remove `.replace()` call
    |
114 |     body = response.json()
    -     loaned_at = datetime.fromisoformat(body["loaned_at"].replace("Z", "+00:00"))
115 +     loaned_at = datetime.fromisoformat(body["loaned_at"])
116 |     due_date = date.fromisoformat(body["due_date"])
    |
note: This is an unsafe fix and may change runtime behavior

Found 3 errors.
[*] 2 fixable with `--fix` (1 unsafe fix available with `--fix --unsafe-fixes`).



Gate: tests
Failed rule or test:test_ac14_overdue_returns_only_active_loans_before_today
Expected behaviour:
Observed behaviour:
Relevant output:
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0 -- C:\Users\Anupam's\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: C:\dev\Part-1A
configfile: pytest.ini
plugins: anyio-4.16.0, cov-7.1.0
collecting ... collected 14 items

tests/test_book_loan_api.py::test_ac1_create_book_returns_201_and_created_book PASSED [  7%]
tests/test_book_loan_api.py::test_ac2_invalid_book_returns_422 PASSED    [ 14%]
tests/test_book_loan_api.py::test_ac3_duplicate_isbn_returns_409 PASSED  [ 21%]
tests/test_book_loan_api.py::test_ac4_create_member_returns_201 PASSED   [ 28%]
tests/test_book_loan_api.py::test_ac5_invalid_email_returns_422 PASSED   [ 35%]
tests/test_book_loan_api.py::test_ac6_duplicate_email_returns_409 PASSED [ 42%]
tests/test_book_loan_api.py::test_ac7_create_loan_returns_201_with_fourteen_day_due_date PASSED [ 50%]
tests/test_book_loan_api.py::test_ac8_unavailable_book_returns_409 PASSED [ 57%]
tests/test_book_loan_api.py::test_ac9_member_with_three_active_loans_returns_409 PASSED [ 64%]
tests/test_book_loan_api.py::test_ac10_missing_book_or_member_returns_404 PASSED [ 71%]
tests/test_book_loan_api.py::test_ac11_return_active_loan_returns_200_and_sets_returned_at PASSED [ 78%]
tests/test_book_loan_api.py::test_ac12_return_already_returned_loan_returns_409 PASSED [ 85%]
tests/test_book_loan_api.py::test_ac13_get_book_returns_current_availability_and_unknown_returns_404 PASSED [ 92%]
tests/test_book_loan_api.py::test_ac14_overdue_returns_only_active_loans_before_today FAILED [100%]

================================== FAILURES ===================================
__________ test_ac14_overdue_returns_only_active_loans_before_today ___________

client = <starlette.testclient.TestClient object at 0x000001C5BD2E2870>
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001C5BD2E0530>

    def test_ac14_overdue_returns_only_active_loans_before_today(
        client, monkeypatch: pytest.MonkeyPatch
    ):
        import src.main as main_module
    
        class FrozenDate(date):
            @classmethod
            def today(cls):
                return date(2026, 11, 23)
    
        def freeze_service_datetime(target: datetime) -> None:
            class FrozenDateTime(datetime):
                @classmethod
                def now(cls, tz=None):
                    if tz is None:
                        return target
                    return target.astimezone(tz)
    
                @classmethod
                def utcnow(cls):
                    return target
    
            monkeypatch.setattr(main_module, "datetime", FrozenDateTime)
    
        monkeypatch.setattr(main_module, "date", FrozenDate)
        book = _create_book(client, total_copies=3)
        member = _create_member(client)
    
        freeze_service_datetime(datetime(2026, 11, 1))
        overdue_loan = _create_loan(client, book["id"], member["id"])
        freeze_service_datetime(datetime(2026, 11, 9))
        due_today_loan = _create_loan(client, book["id"], member["id"])
        freeze_service_datetime(datetime(2026, 11, 23))
        future_loan = _create_loan(client, book["id"], member["id"])
    
        response = client.get("/loans/overdue")
    
        assert response.status_code == 200
        overdue_ids = {item["id"] for item in response.json()}
        assert overdue_loan["id"] in overdue_ids
>       assert due_today_loan["id"] not in overdue_ids
E       assert 2 not in {1, 2}

tests\test_book_loan_api.py:247: AssertionError
============================== warnings summary ===============================
..\..\Users\Anupam's\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\fastapi\testclient.py:1
  C:\Users\Anupam's\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=============================== tests coverage ================================
______________ coverage: platform win32, python 3.12.10-final-0 _______________

Name          Stmts   Miss  Cover
---------------------------------
src\main.py     162      1    99%
---------------------------------
TOTAL           162      1    99%
Required test coverage of 80% reached. Total coverage: 99.38%
=========================== short test summary info ===========================
FAILED tests/test_book_loan_api.py::test_ac14_overdue_returns_only_active_loans_before_today
=================== 1 failed, 13 passed, 1 warning in 0.55s ===================
