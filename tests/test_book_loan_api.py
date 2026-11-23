from datetime import date, datetime, timedelta

import pytest


def _book_payload(*, total_copies: int = 1, isbn: str = "9780132350884") -> dict:
    return {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": isbn,
        "total_copies": total_copies,
    }


def _member_payload(*, email: str = "member@example.com") -> dict:
    return {"name": "Ada Lovelace", "email": email}


def _create_book(client, *, total_copies: int = 1, isbn: str = "9780132350884"):
    response = client.post(
        "/books", json=_book_payload(total_copies=total_copies, isbn=isbn)
    )
    assert response.status_code == 201
    return response.json()


def _create_member(client, *, email: str = "member@example.com"):
    response = client.post("/members", json=_member_payload(email=email))
    assert response.status_code == 201
    return response.json()


def _create_loan(client, book_id: int, member_id: int):
    response = client.post(
        "/loans", json={"book_id": book_id, "member_id": member_id}
    )
    assert response.status_code == 201
    return response.json()


def _assert_error(response, status_code: int) -> None:
    assert response.status_code == status_code
    assert response.headers["content-type"].startswith("application/json")
    assert isinstance(response.json()["detail"], str)


def test_ac1_create_book_returns_201_and_created_book(client):
    response = client.post("/books", json=_book_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["title"] == "Clean Code"
    assert body["author"] == "Robert C. Martin"
    assert body["isbn"] == "9780132350884"
    assert body["total_copies"] == 1


def test_ac2_invalid_book_returns_422(client):
    missing_title = _book_payload()
    missing_title.pop("title")
    invalid_isbn = _book_payload(isbn="123")

    missing_title_response = client.post("/books", json=missing_title)
    invalid_isbn_response = client.post("/books", json=invalid_isbn)

    _assert_error(missing_title_response, 422)
    _assert_error(invalid_isbn_response, 422)


def test_ac3_duplicate_isbn_returns_409(client):
    _create_book(client)

    response = client.post("/books", json=_book_payload())

    _assert_error(response, 409)


def test_ac4_create_member_returns_201(client):
    response = client.post("/members", json=_member_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["name"] == "Ada Lovelace"
    assert body["email"] == "member@example.com"


def test_ac5_invalid_email_returns_422(client):
    response = client.post(
        "/members", json=_member_payload(email="not-an-email")
    )

    _assert_error(response, 422)


def test_ac6_duplicate_email_returns_409(client):
    _create_member(client)

    response = client.post("/members", json=_member_payload())

    _assert_error(response, 409)


def test_ac7_create_loan_returns_201_with_fourteen_day_due_date(client):
    book = _create_book(client)
    member = _create_member(client)

    response = client.post(
        "/loans", json={"book_id": book["id"], "member_id": member["id"]}
    )

    assert response.status_code == 201
    body = response.json()
    loaned_at = datetime.fromisoformat(body["loaned_at"])    
    due_date = date.fromisoformat(body["due_date"])
    assert due_date == (loaned_at.date() + timedelta(days=14))
    assert body["book_id"] == book["id"]
    assert body["member_id"] == member["id"]
    assert body["returned_at"] is None


def test_ac8_unavailable_book_returns_409(client):
    book = _create_book(client, total_copies=1)
    first_member = _create_member(client, email="first@example.com")
    second_member = _create_member(client, email="second@example.com")
    _create_loan(client, book["id"], first_member["id"])

    response = client.post(
        "/loans", json={"book_id": book["id"], "member_id": second_member["id"]}
    )

    _assert_error(response, 409)


def test_ac9_member_with_three_active_loans_returns_409(client):
    member = _create_member(client)
    books = [
        _create_book(client, isbn=f"9780132350{880 + index:03d}")
        for index in range(3)
    ]
    for book in books:
        _create_loan(client, book["id"], member["id"])

    fourth_book = _create_book(client, isbn="9780132350990")
    response = client.post(
        "/loans", json={"book_id": fourth_book["id"], "member_id": member["id"]}
    )

    _assert_error(response, 409)


def test_ac10_missing_book_or_member_returns_404(client):
    book = _create_book(client)
    member = _create_member(client)

    missing_book = client.post(
        "/loans", json={"book_id": 999999, "member_id": member["id"]}
    )
    missing_member = client.post(
        "/loans", json={"book_id": book["id"], "member_id": 999999}
    )

    _assert_error(missing_book, 404)
    _assert_error(missing_member, 404)


def test_ac11_return_active_loan_returns_200_and_sets_returned_at(client):
    book = _create_book(client)
    member = _create_member(client)
    loan = _create_loan(client, book["id"], member["id"])

    response = client.post(f"/loans/{loan['id']}/return")

    assert response.status_code == 200
    assert response.json()["returned_at"] is not None


def test_ac12_return_already_returned_loan_returns_409(client):
    book = _create_book(client)
    member = _create_member(client)
    loan = _create_loan(client, book["id"], member["id"])
    first_return = client.post(f"/loans/{loan['id']}/return")
    assert first_return.status_code == 200

    response = client.post(f"/loans/{loan['id']}/return")

    _assert_error(response, 409)


def test_ac13_get_book_returns_current_availability_and_unknown_returns_404(
    client,
):
    book = _create_book(client, total_copies=2)
    member = _create_member(client)
    _create_loan(client, book["id"], member["id"])

    response = client.get(f"/books/{book['id']}")
    unknown_response = client.get("/books/999999")

    assert response.status_code == 200
    assert response.json()["id"] == book["id"]
    assert response.json()["available_copies"] == 1
    _assert_error(unknown_response, 404)


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
    assert due_today_loan["id"] not in overdue_ids
    assert future_loan["id"] not in overdue_ids

    returned_response = client.post(f"/loans/{overdue_loan['id']}/return")
    assert returned_response.status_code == 200
    response_after_return = client.get("/loans/overdue")
    assert response_after_return.status_code == 200
    assert overdue_loan["id"] not in {
        item["id"] for item in response_after_return.json()
    }
