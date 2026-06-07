import uuid


def _random_email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _register_user(
    client, name: str, email: str, password: str, role: str | None = None
) -> dict:
    payload = {"name": name, "email": email, "password": password}
    if role:
        payload["role"] = role
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _login_user(client, email: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/token",
        data={
            "grant_type": "password",
            "username": email,
            "password": password,
            "scope": "",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    assert token
    return token


def test_auth_endpoints(client):
    admin_email = _random_email("admin")
    student_email = _random_email("student")
    admin_password = "StrongPass123!"
    student_password = "StudentPass123!"

    admin_user = _register_user(
        client, "Admin User", admin_email, admin_password, role="admin"
    )
    assert admin_user["email"] == admin_email
    assert admin_user["role"] == "admin"

    student_user = _register_user(
        client, "Student User", student_email, student_password
    )
    assert student_user["email"] == student_email
    assert student_user["role"] == "student"

    admin_token = _login_user(client, admin_email, admin_password)
    student_token = _login_user(client, student_email, student_password)

    admin_me = client.get("/api/v1/auth/me", headers=_auth_headers(admin_token))
    assert admin_me.status_code == 200
    assert admin_me.json()["email"] == admin_email

    student_me = client.get("/api/v1/auth/me", headers=_auth_headers(student_token))
    assert student_me.status_code == 200
    assert student_me.json()["email"] == student_email


def test_user_endpoints(client):
    admin_email = _random_email("admin")
    student_email = _random_email("student")
    admin_password = "StrongPass123!"
    student_password = "StudentPass123!"

    admin_user = _register_user(
        client, "Admin User", admin_email, admin_password, role="admin"
    )
    student_user = _register_user(
        client, "Student User", student_email, student_password
    )

    admin_token = _login_user(client, admin_email, admin_password)
    student_token = _login_user(client, student_email, student_password)

    # Student can view own user record
    student_me = client.get("/api/v1/users/me", headers=_auth_headers(student_token))
    assert student_me.status_code == 200
    assert student_me.json()["email"] == student_email

    # Admin can fetch any user by ID and list users
    user_by_id = client.get(
        f"/api/v1/users/{student_user['id']}", headers=_auth_headers(admin_token)
    )
    assert user_by_id.status_code == 200
    assert user_by_id.json()["email"] == student_email

    users_list = client.get("/api/v1/users/", headers=_auth_headers(admin_token))
    assert users_list.status_code == 200
    assert any(u["email"] == student_email for u in users_list.json())

    # Student can update their own profile
    updated_name = "Student User Updated"
    update_response = client.put(
        f"/api/v1/users/{student_user['id']}",
        json={"name": updated_name},
        headers=_auth_headers(student_token),
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == updated_name

    # Admin can delete a user
    delete_user = _register_user(
        client, "Delete Me", _random_email("delete"), "DeletePass123!"
    )
    delete_response = client.delete(
        f"/api/v1/users/{delete_user['id']}", headers=_auth_headers(admin_token)
    )
    assert delete_response.status_code == 204


def test_course_endpoints(client):
    admin_email = _random_email("admin")
    admin_password = "StrongPass123!"
    _register_user(client, "Admin User", admin_email, admin_password, role="admin")
    admin_token = _login_user(client, admin_email, admin_password)

    course_payload = {"title": "Intro to Testing", "code": "TEST101", "capacity": 5}
    create_response = client.post(
        "/api/v1/courses/", json=course_payload, headers=_auth_headers(admin_token)
    )
    assert create_response.status_code == 201
    course = create_response.json()
    assert course["code"] == course_payload["code"]

    public_list = client.get("/api/v1/courses/")
    assert public_list.status_code == 200
    assert any(
        item["code"] == course_payload["code"] for item in public_list.json()["items"]
    )

    get_course = client.get(f"/api/v1/courses/{course['id']}")
    assert get_course.status_code == 200
    assert get_course.json()["title"] == course_payload["title"]

    admin_list = client.get(
        "/api/v1/courses/admin/all", headers=_auth_headers(admin_token)
    )
    assert admin_list.status_code == 200
    assert any(
        item["code"] == course_payload["code"] for item in admin_list.json()["items"]
    )

    updated_title = "Intro to API Testing"
    update_course = client.put(
        f"/api/v1/courses/{course['id']}",
        json={"title": updated_title},
        headers=_auth_headers(admin_token),
    )
    assert update_course.status_code == 200
    assert update_course.json()["title"] == updated_title

    toggle_response = client.patch(
        f"/api/v1/courses/{course['id']}/toggle", headers=_auth_headers(admin_token)
    )
    assert toggle_response.status_code == 200
    assert toggle_response.json()["is_active"] is False

    delete_response = client.delete(
        f"/api/v1/courses/{course['id']}", headers=_auth_headers(admin_token)
    )
    assert delete_response.status_code == 204


def test_enrollment_endpoints(client):
    admin_email = _random_email("admin")
    student_email = _random_email("student")
    admin_password = "StrongPass123!"
    student_password = "StudentPass123!"

    _register_user(client, "Admin User", admin_email, admin_password, role="admin")
    student_user = _register_user(
        client, "Student User", student_email, student_password
    )
    admin_token = _login_user(client, admin_email, admin_password)
    student_token = _login_user(client, student_email, student_password)

    course_payload = {
        "title": "Enrollment Course",
        "code": _random_email("C").replace("@", ""),
        "capacity": 3,
    }
    course = client.post(
        "/api/v1/courses/", json=course_payload, headers=_auth_headers(admin_token)
    ).json()

    enroll_response = client.post(
        f"/api/v1/enrollments/{course['id']}", headers=_auth_headers(student_token)
    )
    assert enroll_response.status_code == 201
    enrollment = enroll_response.json()
    assert enrollment["course_id"] == course["id"]
    assert enrollment["user_id"] == student_user["id"]

    all_enrollments = client.get(
        "/api/v1/enrollments/", headers=_auth_headers(admin_token)
    )
    assert all_enrollments.status_code == 200
    assert any(
        item["id"] == enrollment["id"] for item in all_enrollments.json()["items"]
    )

    by_course = client.get(
        f"/api/v1/enrollments/course/{course['id']}", headers=_auth_headers(admin_token)
    )
    assert by_course.status_code == 200
    assert any(item["course_id"] == course["id"] for item in by_course.json()["items"])

    deregister_response = client.delete(
        f"/api/v1/enrollments/{course['id']}", headers=_auth_headers(student_token)
    )
    assert deregister_response.status_code == 204

    # Admin can remove another enrollment if one exists
    second_student_email = _random_email("student")
    _register_user(client, "Second Student", second_student_email, student_password)
    second_student_token = _login_user(client, second_student_email, student_password)
    enroll_again = client.post(
        f"/api/v1/enrollments/{course['id']}",
        headers=_auth_headers(second_student_token),
    )
    assert enroll_again.status_code == 201
    enrollment_id = enroll_again.json()["id"]

    remove_response = client.delete(
        f"/api/v1/enrollments/admin/{enrollment_id}", headers=_auth_headers(admin_token)
    )
    assert remove_response.status_code == 204


def test_health_endpoint(client):
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    data = health.json()
    assert data["status"] == "healthy"
    assert data["checks"]["database"] == "ok"
    assert data["checks"]["redis"] == "ok"
