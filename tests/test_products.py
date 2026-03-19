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
        """
        Steps:
          1. Send GET /auth/products with valid Bearer token
          2. Assert status code is 200
        Expected result: HTTP 200 OK
        Validation: assert_status_code(response, 200)
        """
        response = auth_client.get_products(limit=5)
        assert_status_code(response, 200)

    def test_get_products_schema(self, auth_client):
        """
        Steps:
          1. Send GET /auth/products with valid Bearer token
          2. Parse response body
          3. Assert every product object has required fields
        Expected result: list of valid product objects with
                         id, title, price, stock, category
        Validation: assert_all_products_schema
        """
        response = auth_client.get_products(limit=5)
        assert_status_code(response, 200)
        products = response.json().get("products", [])
        assert_all_products_schema(products)

    def test_get_single_product_with_token_returns_200(self, auth_client):
        """
        Steps:
          1. Send GET /auth/products/1 with valid Bearer token
          2. Assert status code is 200
        Expected result: HTTP 200 OK
        Validation: assert_status_code(response, 200)
        """
        response = auth_client.get_product(1)
        assert_status_code(response, 200)

    def test_get_single_product_id_matches(self, auth_client):
        """
        Steps:
          1. Send GET /auth/products/1 with valid Bearer token
          2. Parse response body
          3. Assert returned id equals 1
        Expected result: correct product returned for the requested id
        Validation: assert_field_equals(data, "id", 1)
        """
        response = auth_client.get_product(1)
        assert_status_code(response, 200)
        assert_field_equals(response.json(), "id", 1)

    def test_get_products_without_token_returns_401(self, client):
        """
        Steps:
          1. Send GET /auth/products with NO Authorization header
          2. Assert status code is 401
        Expected result: HTTP 401 Unauthorised
        Validation: assert_unauthorised(response)
        """
        response = client.get_products()
        assert_unauthorised(response)

    def test_get_nonexistent_product_returns_404(self, auth_client):
        """
        Steps:
          1. Send GET /auth/products/999999 with valid Bearer token
          2. Assert status code is 404
        Expected result: HTTP 404 Not Found
        Validation: assert_status_code(response, 404)
        """
        response = auth_client.get_product(999999)
        assert_status_code(response, 404)


class TestCreateProduct:

    def test_create_product_returns_201(self, auth_client):
        """
        Steps:
          1. Send POST /auth/products/add with valid payload
          2. Assert status code is 201
        Expected result: HTTP 201 Created
        Validation: assert_status_code(response, 201)
        """
        payload = {
            "title": "Test Widget",
            "price": 9.99,
            "stock": 100,
            "category": "test",
        }
        response = auth_client.create_product(payload)
        assert_status_code(response, 201)

    def test_create_product_response_schema(self, auth_client):
        """
        Steps:
          1. Send POST /auth/products/add with valid payload
          2. Parse response body
          3. Assert all required fields are present
        Expected result: response is a valid product object
        Validation: assert_product_schema
        """
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
        """
        Steps:
          1. Send POST /auth/products/add with title='My Unique Product'
          2. Parse response body
          3. Assert response title equals sent title
        Expected result: server echoes back the title we sent
        Validation: assert_field_equals(data, "title", title)
        """
        title = "My Unique Product"
        response = auth_client.create_product(
            {"title": title, "price": 5.0, "stock": 20, "category": "test"}
        )
        assert_status_code(response, 201)
        assert_field_equals(response.json(), "title", title)

    def test_create_product_without_token_returns_401(self, client):
        """
        Steps:
          1. Send POST /auth/products/add with NO Authorization header
          2. Assert status code is 401
        Expected result: unauthenticated creation rejected
        Validation: assert_unauthorised(response)
        """
        response = client.create_product({"title": "Ghost", "price": 0})
        assert_unauthorised(response)

    @pytest.mark.parametrize(
        "title,price,category",
        [
            ("Laptop Pro",    999.99, "electronics"),
            ("Cozy Blanket",   29.99, "home"),
            ("Running Shoes",  79.99, "sports"),
        ],
    )
    def test_create_products_parametrized(self, auth_client, title, price, category):
        """
        Steps:
          1. Send POST /auth/products/add for each title/price/category combo
          2. Assert 201 and that title + price are echoed correctly
        Expected result: all 3 product types accepted, fields match payload
        Validation: parametrize × assert_field_equals on title and price
        """
        payload = {"title": title, "price": price, "stock": 50, "category": category}
        response = auth_client.create_product(payload)
        assert_status_code(response, 201)
        data = response.json()
        assert_field_equals(data, "title", title)
        assert_field_equals(data, "price", price)


class TestUpdateProduct:

    def test_update_product_returns_200(self, auth_client):
        """
        Steps:
          1. Send PUT /auth/products/1 with new title
          2. Assert status code is 200
        Expected result: HTTP 200 OK
        Validation: assert_status_code(response, 200)
        """
        response = auth_client.update_product(1, {"title": "Updated Title"})
        assert_status_code(response, 200)

    def test_update_product_title_is_changed(self, auth_client):
        """
        Steps:
          1. Send PUT /auth/products/1 with title='Freshly Updated'
          2. Parse response body
          3. Assert response title equals 'Freshly Updated'
        Expected result: server persists the new title
        Validation: assert_field_equals(data, "title", new_title)
        """
        new_title = "Freshly Updated"
        response = auth_client.update_product(1, {"title": new_title})
        assert_status_code(response, 200)
        assert_field_equals(response.json(), "title", new_title)

    def test_update_product_without_token_returns_401(self, client):
        """
        Steps:
          1. Send PUT /auth/products/1 with NO Authorization header
          2. Assert status code is 401
        Expected result: unauthenticated update rejected
        Validation: assert_unauthorised(response)
        """
        response = client.update_product(1, {"title": "Hack"})
        assert_unauthorised(response)


class TestDeleteProduct:

    def test_delete_product_returns_200(self, auth_client):
        """
        Steps:
          1. Send DELETE /auth/products/1 with valid Bearer token
          2. Assert status code is 200
        Expected result: HTTP 200 OK
        Validation: assert_status_code(response, 200)
        """
        response = auth_client.delete_product(1)
        assert_status_code(response, 200)

    def test_delete_product_response_has_deleted_flag(self, auth_client):
        """
        Steps:
          1. Send DELETE /auth/products/1 with valid Bearer token
          2. Parse response body
          3. Assert isDeleted is True
        Expected result: response confirms deletion with isDeleted: true
        Validation: data["isDeleted"] is True
        """
        response = auth_client.delete_product(1)
        assert_status_code(response, 200)
        data = response.json()
        assert data.get("isDeleted") is True, (
            f"Expected 'isDeleted: true' in delete response, got: {data}"
        )

    def test_delete_product_without_token_returns_401(self, client):
        """
        Steps:
          1. Send DELETE /auth/products/1 with NO Authorization header
          2. Assert status code is 401
        Expected result: unauthenticated deletion rejected
        Validation: assert_unauthorised(response)
        """
        response = client.delete_product(1)
        assert_unauthorised(response)