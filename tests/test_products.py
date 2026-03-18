import pytest
from utils.validators import (
    assert_status_code,
    assert_product_schema,
    assert_all_products_schema,
    assert_field_equals,
    assert_unauthorised,
)

class TestGetProducts:
    def test_get_products_with_token_returns_200(self, auth_client):
        response = auth_client.get_products(limit=5)
        assert_status_code(response, 200)

    def test_get_products_schema(self, auth_client):
        response = auth_client.get_products(limit=5)
        assert_status_code(response, 200)
        products = response.json().get("products", [])
        assert_all_products_schema(products)

    def test_get_single_product_with_token_returns_200(self, auth_client):
        response = auth_client.get_product(1)
        assert_status_code(response, 200)

    def test_get_single_product_id_matches(self, auth_client):
        response = auth_client.get_product(1)
        assert_status_code(response, 200)
        assert_field_equals(response.json(), "id", 1)

    def test_get_products_without_token_returns_401(self, client):
        response = client.get_products()
        assert_unauthorised(response)

    def test_get_nonexistent_product_returns_404(self, auth_client):
        response = auth_client.get_product(999999)
        assert_status_code(response, 404)

class TestCreateProduct:
    def test_create_product_returns_201(self, auth_client):
        payload = {
            "title": "Test Widget",
            "price": 9.99,
            "stock": 100,
            "category": "test",
        }
        response = auth_client.create_product(payload)
        assert_status_code(response, 201)

    def test_create_product_response_schema(self, auth_client):
        payload = {
            "title": "Schema Test",
            "price": 1.0,
            "stock": 10,
            "category": "test",
        }
        response = auth_client.create_product(payload)
        assert_status_code(response, 201)
        assert_product_schema(response.json())

    def test_create_product_title_matches(self, auth_client):
        title = "My Unique Product"
        response = auth_client.create_product(
            {"title": title, "price": 5.0, "stock": 20, "category": "test"}
        )
        assert_status_code(response, 201)
        assert_field_equals(response.json(), "title", title)

    def test_create_product_without_token_returns_401(self, client):
        response = client.create_product({"title": "Ghost", "price": 0})
        assert_unauthorised(response)

    @pytest.mark.parametrize(
        "title,price,category",
        [
            ("Laptop Pro", 999.99, "electronics"),
            ("Cozy Blanket", 29.99, "home"),
            ("Running Shoes", 79.99, "sports"),
        ],
    )
    def test_create_products_parametrized(self, auth_client, title, price, category):
        payload = {"title": title, "price": price, "stock": 50, "category": category}
        response = auth_client.create_product(payload)
        assert_status_code(response, 201)
        data = response.json()
        assert_field_equals(data, "title", title)
        assert_field_equals(data, "price", price)

class TestUpdateProduct:
    def test_update_product_returns_200(self, auth_client):
        response = auth_client.update_product(1, {"title": "Updated Title"})
        assert_status_code(response, 200)

    def test_update_product_title_is_changed(self, auth_client):
        new_title = "Freshly Updated"
        response = auth_client.update_product(1, {"title": new_title})
        assert_status_code(response, 200)
        assert_field_equals(response.json(), "title", new_title)

    def test_update_product_without_token_returns_401(self, client):
       
        response = client.update_product(1, {"title": "Hack"})
        assert_unauthorised(response)

class TestDeleteProduct:
    def test_delete_product_returns_200(self, auth_client):
        response = auth_client.delete_product(1)
        assert_status_code(response, 200)

    def test_delete_product_response_has_deleted_flag(self, auth_client):

        response = auth_client.delete_product(1)
        assert_status_code(response, 200)
        data = response.json()
        assert data.get("isDeleted") is True, (
            f"Expected 'isDeleted: true' in delete response, got: {data}"
        )

    def test_delete_product_without_token_returns_401(self, client):
        response = client.delete_product(1)
        assert_unauthorised(response)
