import json
from flask_jwt_extended import create_access_token
from app import app
from src.models.user import UserModel
from tests.test_base import TestBase

item_category_dict = {'categoryname': 'categoryname'}


class TestRoleSystem(TestBase):

    def setUp(self):
        super(TestRoleSystem, self).setUp()
        with app.test_client() as client:
            with self.app_context():
                UserModel('username', 'firstname', 'lastname', 'residence', 'address', 'phonenumber', 'emailaddress',
                          'password').save_to_db()
                username = 'username'
                password = 'password'
                access_token = create_access_token(identity={"username": username, "password": password})
                auth_token = access_token
                self.access_token = f' Bearer {auth_token}'
    #get all item categories
    def test_get_itemcategory(self):
        with app.test_client() as client:
            with self.app_context():
                resp = client.get('/api/item/category', data=item_category_dict, headers={'Authorization': self.access_token})
                self.assertEqual(resp.status_code, 200)

    #get one item category given the name
    def test_get_one_itemcategory(self):
        with app.test_client() as client:
            with self.app_context():
                client.post('/api/item/category', data=item_category_dict,headers={'Authorization': self.access_token})
                resp = client.get('/api/item/category/categoryname',headers={'Authorization': self.access_token})
                self.assertEqual(resp.status_code, 200)

    #try to register the same item category
    def test_register_duplicate_itemcategory(self):
        with app.test_client() as client:
            with self.app_context():
                client.post('/api/item/category', data=item_category_dict,headers={'Authorization': self.access_token})
                response = client.post('/api/item/category', data=item_category_dict,headers={'Authorization': self.access_token})

                self.assertEqual(response.status_code, 400)
                self.assertDictEqual({'message': 'An Item Category with that name already exists'}, json.loads(response.data))


    #test deleting an item category given its name
    def test_delete_itemcategory(self):
        with app.test_client() as client:
            with self.app_context():
                client.post('/api/item/category', data=item_category_dict,headers={'Authorization': self.access_token})
                resp = client.delete('/api/item/category/categoryname',headers={'Authorization': self.access_token})
                self.assertEqual(resp.status_code, 200)
                self.assertDictEqual({'message': 'Item Category Deleted'},
                                     json.loads(resp.data))

