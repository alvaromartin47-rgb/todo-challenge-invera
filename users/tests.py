from rest_framework.test import APITestCase
from users.models import User
from rest_framework import status

class MeEndpointTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alvaro", password="1234")

    def test_me_endpoint_with_authentication(self):
        login_response = self.client.post("/api/v1/auth/login/", {
            "username": "alvaro",
            "password": "1234"
        }, format="json")

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        token = login_response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        me_response = self.client.get("/api/v1/users/me/")

        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["username"], "alvaro")
