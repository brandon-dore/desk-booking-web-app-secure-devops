class TestPostAndGetEndpoints:
    def test_create_and_get_user(
        self, client_authenticated, request_data, response_data
    ):
        response = client_authenticated.post(
            "/register",
            json=request_data["user_request"],
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["user_response"]

        response = client_authenticated.get(f"/users/{1}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["user_response"]

    def test_create_and_get_room(
        self, client_authenticated, request_data, response_data
    ):
        response = client_authenticated.post(
            "/rooms",
            json=request_data["room_request"],
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["room_response"]

        response = client_authenticated.get(f"/rooms/{1}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["room_response"]

    def test_create_and_get_desk(
        self, client_authenticated, request_data, response_data
    ):
        response = client_authenticated.post(
            "/desks",
            json=request_data["desk_request"],
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["desk_response"]

        response = client_authenticated.get(f"/desks/{1}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["desk_response"]

    def test_create_and_get_booking(
        self, client_authenticated, request_data, response_data
    ):
        response = client_authenticated.post(
            "/bookings",
            json=request_data["booking_request"],
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["booking_response"]

        response = client_authenticated.get(f"/bookings/{1}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["booking_response"]

    def test_get_all_desks_in_room(
        self, client_authenticated, request_data, response_data
    ):
        for desk in request_data["desk_request_multiple"]:
            response = client_authenticated.post(
                "/desks",
                json=desk,
            )
            assert response.status_code == 200, response.text

        response = client_authenticated.get(f"/rooms/{1}/desks")
        data = response.json()

        assert data == response_data["room_response_multiple"]

    def test_get_all_booking_in_room(
        self, client_authenticated, request_data, response_data
    ):
        response = client_authenticated.post(
            "/register",
            json=request_data["user_request_2"],
        )
        assert response.status_code == 200, response.text

        response = client_authenticated.post(
            "/bookings",
            json=request_data["booking_request_2"],
        )
        assert response.status_code == 200, response.text

        response = client_authenticated.get(f"/rooms/{1}/bookings/2020-05-17")
        data = response.json()

        assert data == response_data["booking_response_multiple"]


class TestDeleteEndpointsAndGetErrors:
    def test_create_entities_for_deletion(self, client_authenticated, request_data):
        response = client_authenticated.post(
            "/register",
            json=request_data["user_request"],
        )
        assert response.status_code == 200, response.text

        response = client_authenticated.post(
            "/rooms",
            json=request_data["room_request"],
        )
        assert response.status_code == 200, response.text

        response = client_authenticated.post(
            "/desks",
            json=request_data["desk_request"],
        )
        assert response.status_code == 200, response.text

        response = client_authenticated.post(
            "/bookings",
            json=request_data["booking_request"],
        )
        assert response.status_code == 200, response.text

    def test_delete_booking(self, client_authenticated):
        response = client_authenticated.get(f"/bookings/{1}")
        assert response.status_code == 200, response.text

        response = client_authenticated.delete(f"/bookings/{1}")
        assert response.status_code == 204, response.text

        response = client_authenticated.get(f"/bookings/{1}")
        assert response.status_code == 404, response.text

    def test_delete_desk(self, client_authenticated):
        response = client_authenticated.get(f"/desks/{1}")
        assert response.status_code == 200, response.text

        response = client_authenticated.delete(f"/desks/{1}")
        assert response.status_code == 204, response.text

        response = client_authenticated.get(f"/desks/{1}")
        assert response.status_code == 404, response.text

    def test_delete_user(self, client_authenticated):
        response = client_authenticated.get(f"/users/{1}")
        assert response.status_code == 200, response.text

        response = client_authenticated.delete(f"/users/{1}")
        assert response.status_code == 204, response.text

        response = client_authenticated.get(f"/users/{1}")
        assert response.status_code == 404, response.text

    def test_delete_room(self, client_authenticated):
        response = client_authenticated.get(f"/rooms/{1}")
        assert response.status_code == 200, response.text

        response = client_authenticated.delete(f"/rooms/{1}")
        assert response.status_code == 204, response.text

        response = client_authenticated.get(f"/rooms/{1}")
        assert response.status_code == 404, response.text


class TestPatchEndpoints:
    def test_create_entities_for_patching(
        self, client_authenticated, response_data, request_data
    ):
        response = client_authenticated.post(
            "/register",
            json=request_data["user_request"],
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["user_response"]

        response = client_authenticated.post(
            "/rooms",
            json=request_data["room_request"],
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["room_response"]

        response = client_authenticated.post(
            "/desks",
            json=request_data["desk_request"],
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["desk_response"]

        response = client_authenticated.post(
            "/bookings",
            json=request_data["booking_request"],
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["booking_response"]

    def test_patch_user(self, client_authenticated, request_data, response_data):
        response = client_authenticated.get(f"/users/{1}")
        assert response.status_code == 200, response.text

        response = client_authenticated.patch(
            f"/users/{1}",
            json=request_data["user_request_edited"],
        )
        assert response.status_code == 200, response.text

        response = client_authenticated.get(f"/users/{1}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["user_patched_response"]

    def test_patch_room(self, client_authenticated, request_data, response_data):
        response = client_authenticated.get(f"/rooms/{1}")
        assert response.status_code == 200, response.text

        response = client_authenticated.patch(
            f"/rooms/{1}",
            json=request_data["room_request_edited"],
        )
        assert response.status_code == 200, response.text

        response = client_authenticated.get(f"/rooms/{1}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["room_patched_response"]

    def test_patch_desk(self, client_authenticated, request_data, response_data):
        response = client_authenticated.get(f"/desks/{1}")
        assert response.status_code == 200, response.text

        response = client_authenticated.patch(
            f"/desks/{1}",
            json=request_data["desk_request_edited"],
        )
        assert response.status_code == 200, response.text

        response = client_authenticated.get(f"/desks/{1}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["desk_patched_response"]

    def test_patch_booking(self, client_authenticated, request_data, response_data):
        response = client_authenticated.get(f"/bookings/{1}")
        assert response.status_code == 200, response.text

        response = client_authenticated.patch(
            f"/bookings/{1}",
            json=request_data["booking_request_edited"],
        )
        assert response.status_code == 200, response.text

        response = client_authenticated.get(f"/bookings/{1}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data == response_data["booking_patched_response"]

    def test_patch_user_with_error(self, client_authenticated, request_data):
        response = client_authenticated.patch(
            f"/users/{100}",
            json=request_data["user_request_edited"],
        )
        assert response.status_code == 404, response.text

    def test_patch_room_with_error(
        self,
        client_authenticated,
        request_data,
    ):
        response = client_authenticated.patch(
            f"/rooms/{100}",
            json=request_data["room_request_edited"],
        )
        assert response.status_code == 404, response.text

    def test_patch_desk_with_error(self, client_authenticated, request_data):
        response = client_authenticated.patch(
            f"/desks/{100}",
            json=request_data["desk_request_edited"],
        )
        assert response.status_code == 404, response.text

    def test_patch_booking_with_error(self, client_authenticated, request_data):
        response = client_authenticated.patch(
            f"/bookings/{100}",
            json=request_data["booking_request_edited"],
        )
        assert response.status_code == 404, response.text


class TestUserAuth:
    def test_register_and_login(self, client, headers, request_data):
        response = client.post(
            "/register",
            json=request_data["user_request_3"],
        )

        assert response.status_code == 200, response.text

        response = client.post(
            "/login", data=request_data["user_request_3"], headers=headers
        )

        assert response.status_code == 200, response.text

    def test_register_fail_login(self, client, headers, request_data):
        response = client.post(
            "/login", data=request_data["user_request_invalid"], headers=headers
        )

        assert response.status_code == 401, response.text
