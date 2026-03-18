import pytest
from utils.validators import (
    assert_status_code,
    assert_product_schema,
    assert_all_products_schema,
    assert_field_equals,
    assert_unauthorised,
)


# ------------------------------------------------------------------
# TC-04a — GET (list + single)
# ------------------------------------------------------------------


class TestGetProducts:
    def test_get_products_with_token_returns_200(self, auth_client):
        """
        Steps:
          1. GET /auth/products (Bearer token set)
          2. Assert status 200
        Expected result: HTTP 200 OK
        Validation: assert_status_code(response, 200)
        """
        response = auth_client.get_products(limit=5)
        assert_status_code(response, 200)

    def test_get_products_schema(self, auth_client):
        """
        Steps:
          1. GET /auth/products
          2. Assert response contains 'products' list
          3. Assert each item has required fields
        Expected result: well-formed list of product objects
        Validation: assert_all_products_schema
        """
        response = auth_client.get_products(limit=5)
        assert_status_code(response, 200)
        products = response.json().get("products", [])
        assert_all_products_schema(products)

    def test_get_single_product_with_token_returns_200(self, auth_client):
        """
        Steps:
          1. GET /auth/products/1
          2. Assert status 200
        Expected result: HTTP 200 OK
        Validation: assert_status_code(response, 200)
        """
        response = auth_client.get_product(1)
        assert_status_code(response, 200)

    def test_get_single_product_id_matches(self, auth_client):
        """
        Steps:
          1. GET /auth/products/1
          2. Assert response id == 1
        Expected result: correct product returned for the requested id
        Validation: field equality on 'id'
        """
        response = auth_client.get_product(1)
        assert_status_code(response, 200)
        assert_field_equals(response.json(), "id", 1)

    def test_get_products_without_token_returns_401(self, client):
        """
        Steps:
          1. GET /auth/products with NO token
          2. Assert 401
        Expected result: auth guard rejects unauthenticated requests
        Validation: assert_unauthorised
        """
        response = client.get_products()
        assert_unauthorised(response)

    def test_get_nonexistent_product_returns_404(self, auth_client):
        """
        Steps:
          1. GET /auth/products/999999
          2. Assert 404
        Expected result: missing resource returns 404, not an empty 200
        Validation: assert_status_code(response, 404)
        """
        response = auth_client.get_product(999999)
        assert_status_code(response, 404)


# ------------------------------------------------------------------
# TC-04b — POST (create)
# ------------------------------------------------------------------


class TestCreateProduct:
    def test_create_product_returns_201(self, auth_client):
        """
        Steps:
          1. POST /auth/products/add with valid payload
          2. Assert status 201
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
          1. POST /auth/products/add
          2. Assert returned object has all required product fields
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
          1. POST with title='My Unique Product'
          2. Assert response title == 'My Unique Product'
        Expected result: server echoes the title we sent
        Validation: field equality on 'title'
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
          1. POST /auth/products/add with NO token
          2. Assert 401
        Expected result: unauthenticated creation rejected
        Validation: assert_unauthorised
        """
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
        """
        Steps:
          1. POST each title/price/category combination
          2. Assert 201 and that each field is echoed correctly
        Expected result: all 3 product types are accepted
        Validation: parametrize × field equality
        Why parametrize? Proves the create endpoint isn't hardcoded to
        accept only one category or price range.
        """
        payload = {"title": title, "price": price, "stock": 50, "category": category}
        response = auth_client.create_product(payload)
        assert_status_code(response, 201)
        data = response.json()
        assert_field_equals(data, "title", title)
        assert_field_equals(data, "price", price)


# ------------------------------------------------------------------
# TC-04c — PUT (update)
# ------------------------------------------------------------------


class TestUpdateProduct:
    def test_update_product_returns_200(self, auth_client):
        """
        Steps:
          1. PUT /auth/products/1 with new title
          2. Assert status 200
        Expected result: HTTP 200 OK
        Validation: assert_status_code(response, 200)
        """
        response = auth_client.update_product(1, {"title": "Updated Title"})
        assert_status_code(response, 200)

    def test_update_product_title_is_changed(self, auth_client):
        """
        Steps:
          1. PUT /auth/products/1 with title='Freshly Updated'
          2. Assert response title == 'Freshly Updated'
        Expected result: server persists the new title
        Validation: field equality on 'title'
        """
        new_title = "Freshly Updated"
        response = auth_client.update_product(1, {"title": new_title})
        assert_status_code(response, 200)
        assert_field_equals(response.json(), "title", new_title)

    def test_update_product_without_token_returns_401(self, client):
        """
        Steps:
          1. PUT /auth/products/1 with NO token
          2. Assert 401
        Expected result: auth guard blocks unauthenticated updates
        Validation: assert_unauthorised
        """
        response = client.update_product(1, {"title": "Hack"})
        assert_unauthorised(response)


# ------------------------------------------------------------------
# TC-04d — DELETE
# ------------------------------------------------------------------


class TestDeleteProduct:
    def test_delete_product_returns_200(self, auth_client):
        """
        Steps:
          1. DELETE /auth/products/1
          2. Assert status 200
        Expected result: HTTP 200 (DummyJSON returns 200 + deleted object)
        Validation: assert_status_code(response, 200)
        Note: DummyJSON is a mock API — data is NOT permanently deleted.
        """
        response = auth_client.delete_product(1)
        assert_status_code(response, 200)

    def test_delete_product_response_has_deleted_flag(self, auth_client):
        """
        Steps:
          1. DELETE /auth/products/1
          2. Assert response contains 'isDeleted: true'
        Expected result: server confirms the deletion in the response body
        Validation: field equality on 'isDeleted'
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
          1. DELETE /auth/products/1 with NO token
          2. Assert 401
        Expected result: unauthenticated deletion rejected
        Validation: assert_unauthorised
        """
        response = client.delete_product(1)
        assert_unauthorised(response)
