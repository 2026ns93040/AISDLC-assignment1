Gate: lint
Failed rule or test:I001,FURB162
Expected behaviour:
Observed behaviour:
Relevant output:
I001 [*] Import block is un-sorted or un-formatted
  --> src\main.py:1:1
   |
 1 | / import os
 2 | | import re
 3 | | from contextlib import asynccontextmanager
 4 | | from datetime import UTC, date, datetime, timedelta
 5 | | from threading import Lock
 6 | |
 7 | | from fastapi import FastAPI, HTTPException, Request
 8 | | from fastapi.exceptions import RequestValidationError
 9 | | from fastapi.responses import JSONResponse
10 | | from pydantic import BaseModel, ConfigDict, Field
11 | | from sqlalchemy import (
12 | |     Date,
13 | |     DateTime,
14 | |     ForeignKey,
15 | |     Integer,
16 | |     String,
17 | |     create_engine,
18 | |     func,
19 | |     select,
20 | |     text,
21 | | )
22 | | from sqlalchemy.orm import (
23 | |     DeclarativeBase,
24 | |     Mapped,
25 | |     Session,
26 | |     mapped_column,
27 | |     relationship,
28 | |     sessionmaker,
29 | | )
30 | | from sqlalchemy.pool import StaticPool
   | |______________________________________^
help: Organize imports
   |
31 |
   -
32 | DATABASE_URL = os.getenv("LIBRARY_DATABASE_URL", "sqlite:///library.db")
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

Found 2 errors.
[*] 1 fixable with `--fix` (1 unsafe fix available with `--fix --unsafe-fixes`).
