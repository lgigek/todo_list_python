from unittest import TestCase
from flaskr import app
from unittest.mock import patch
from test.unit.test_utils import TestUtils

from routes.task_messages import TaskMessages


class TestTaskRoute(TestCase):

    def setUp(self):
        app.testing = True
        self.app = app
        self.test_client = app.test_client()

        self.add_route = '/task/add'
        self.get_by_name_route = '/task/get_by_name/'
        self.get_by_status_route = '/task/get_by_status/'
        self.get_all_route = '/task/get_all'
        self.update_route = '/task/update/'
        self.delete_route = '/task/delete/'

    """
    Add route tests
    """

    @patch('services.task_service.insert')
    @patch('services.task_service.is_registered')
    def test_add(self, mocked_task_service_is_registered, mocked_task_service_insert):
        """
        It should return 201 when a task is created
        """

        mocked_task_service_is_registered.return_value = False

        response = self.test_client.post(self.add_route,
                                         json=TestUtils.task_with_valid_body)
        response_json = response.get_json()

        self.assertTrue(mocked_task_service_insert.called)
        self.assertEqual(response_json['Message'], TaskMessages.created)
        self.assertEqual(response.status_code, 201)

    @patch('services.task_service.insert')
    def test_add_invalid_body(self, mocked_task_service_insert):
        """
        It should return 400 when trying to add a task with invalid body
        """

        response = self.test_client.post(self.add_route,
                                         json=TestUtils.task_with_invalid_body)
        response_json = response.get_json()

        self.assertFalse(mocked_task_service_insert.called)
        self.assertEqual(response_json['Message'], TaskMessages.incorrect_parameters)
        self.assertEqual(response.status_code, 400)

    @patch('services.task_service.insert')
    def test_add_invalid_status(self, mocked_task_service_insert):
        """
        It should return 400 when trying to add a task with invalid status
        """

        response = self.test_client.post(self.add_route,
                                         json=TestUtils.task_with_invalid_status)
        response_json = response.get_json()

        self.assertFalse(mocked_task_service_insert.called)
        self.assertEqual(response_json['Message'], TaskMessages.invalid_status)
        self.assertEqual(response.status_code, 400)

    @patch('services.task_service.insert')
    @patch('services.task_service.is_registered')
    def test_add_duplicated(self, mocked_task_service_is_registered, mocked_task_service_insert):
        """
        It should return 400 when trying to add a task that already exists
        """

        mocked_task_service_is_registered.return_value = True

        response = self.test_client.post(self.add_route,
                                         json=TestUtils.task_with_valid_body)
        response_json = response.get_json()

        self.assertFalse(mocked_task_service_insert.called)
        self.assertEqual(response_json['Message'], TaskMessages.duplicated)
        self.assertEqual(response.status_code, 400)

    @patch('services.task_service.insert')
    @patch('services.task_service.is_registered')
    def test_add_status_upper_case(self, mocked_task_service_is_registered, mocked_task_service_insert):
        """
        It should set status to lower case (.lower()) before saving the task
        """

        mocked_task_service_is_registered.return_value = False

        response = self.test_client.post(self.add_route,
                                         json=TestUtils.task_with_valid_body)

        task_used_by_mock = mocked_task_service_insert.call_args[0][0]

        self.assertEqual(task_used_by_mock.status,
                         TestUtils.task_with_status_upper_case['status'].lower())
        self.assertEqual(response.status_code, 201)

    """
    Get by name route tests
    """

    @patch('services.task_service.get_by_name')
    def test_get_by_name_existing(self, mocked_task_service_get_by_name):
        """
        It should return 200 if the task exists
        """

        mocked_task_service_get_by_name.return_value = TestUtils.task_with_valid_body

        response = self.test_client.get(self.get_by_name_route + 'it_exists')
        response_json = response.get_json()

        self.assertTrue(mocked_task_service_get_by_name.called)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['name'], TestUtils.task_with_valid_body['name'])
        self.assertEqual(response_json['description'], TestUtils.task_with_valid_body['description'])
        self.assertEqual(response_json['status'], TestUtils.task_with_valid_body['status'])

    @patch('services.task_service.get_by_name')
    def test_get_by_name_not_exists(self, mocked_task_service_get_by_name):
        """
        It should return 404 if the task does not exist
        """
        mocked_task_service_get_by_name.return_value = None

        response = self.test_client.get(self.get_by_name_route + 'it_does_not_exist')
        response_json = response.get_json()

        self.assertTrue(mocked_task_service_get_by_name.called)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json['Message'], TaskMessages.not_found)

    """
    Get by status route tests
    """

    @patch('services.task_service.get_by_status')
    def test_get_by_status_existing(self, mocked_task_service_get_by_status):
        """
        It should return 200 with a list
        """

        mocked_task_service_get_by_status.return_value = [TestUtils.task_with_valid_body]

        response = self.test_client.get(self.get_by_status_route + 'to_do')
        response_json = response.get_json()

        self.assertTrue(mocked_task_service_get_by_status.called)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_json, list))
        self.assertEqual(response_json[0], TestUtils.task_with_valid_body)

    @patch('services.task_service.get_by_status')
    def test_get_by_status_invalid(self, mocked_task_service_get_by_status):
        """
        It should return 400 if  the status is invalid
        """

        response = self.test_client.get(self.get_by_status_route + 'this_is_invalid')
        response_json = response.get_json()

        self.assertFalse(mocked_task_service_get_by_status.called)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['Message'], TaskMessages.invalid_status)

    @patch('services.task_service.get_by_status')
    def test_get_by_status_upper_case(self, mocked_task_service_get_by_status):
        """
        It should set status to lower case (.lower()) before returning tasks
        """

        response = self.test_client.get(self.get_by_status_route + 'TO_DO')

        status_used_by_mock = mocked_task_service_get_by_status.call_args[0][0]

        self.assertEqual(status_used_by_mock, 'to_do')
        self.assertEqual(response.status_code, 200)

    @patch('services.task_service.get_by_status')
    def test_get_by_status_invalid_task(self, mocked_task_service_get_by_status):
        """
        It should not return something that is not a Task
        """

        mocked_task_service_get_by_status.return_value = [TestUtils.task_with_valid_body,
                                                          TestUtils.task_with_invalid_body]

        response = self.test_client.get(self.get_by_status_route + 'to_do')
        response_json = response.get_json()

        self.assertEqual(len(response_json), 1)
        self.assertEqual(response.status_code, 200)

    """
    Get all route tests
    """

    @patch('services.task_service.get_all')
    def test_get_all(self, mocked_task_service_get_all):
        """
        It should return 200 with a list
        """

        mocked_task_service_get_all.return_value = [TestUtils.task_with_valid_body]

        response = self.test_client.get(self.get_all_route)
        response_json = response.get_json()

        self.assertTrue(mocked_task_service_get_all.called)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_json, list))
        self.assertEqual(response_json[0], TestUtils.task_with_valid_body)

    @patch('services.task_service.get_all')
    def test_get_all_invalid_task(self, mocked_task_service_get_all):
        """
        It should not return something that is not a Task
        """

        mocked_task_service_get_all.return_value = [TestUtils.task_with_valid_body,
                                                    TestUtils.task_with_invalid_body]

        response = self.test_client.get(self.get_all_route)
        response_json = response.get_json()

        self.assertEqual(len(response_json), 1)
        self.assertEqual(response.status_code, 200)

    """
    Update route tests
    """

    @patch('services.task_service.is_registered')
    @patch('services.task_service.update')
    def test_update(self, mocked_task_service_update, mocked_task_service_is_registered):
        """
        It should return 200 and update the task
        """

        mocked_task_service_is_registered.return_value = True

        response = self.test_client.put(self.update_route + TestUtils.task_with_valid_body['name'],
                                        json=TestUtils.task_with_valid_body)
        response_json = response.get_json()

        self.assertTrue(mocked_task_service_update.called)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['Message'], TaskMessages.updated)

    @patch('services.task_service.is_registered')
    @patch('services.task_service.update')
    def test_update_not_found(self, mocked_task_service_update, mocked_task_service_is_registered):
        """
        It should return 404 if the task does not exist
        """

        mocked_task_service_is_registered.return_value = False

        response = self.test_client.put(self.update_route + 'i_dont_exist',
                                        json=TestUtils.task_with_valid_body)
        response_json = response.get_json()

        self.assertFalse(mocked_task_service_update.called)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json['Message'], TaskMessages.not_found)

    @patch('services.task_service.is_registered')
    @patch('services.task_service.update')
    def test_update_invalid_body(self, mocked_task_service_update, mocked_task_service_is_registered):
        """
        It should return 400 if the body is invalid
        """

        mocked_task_service_is_registered.return_value = True

        response = self.test_client.put(self.update_route + 'i_have_an_invalid_body',
                                        json=TestUtils.task_with_invalid_body)
        response_json = response.get_json()

        self.assertFalse(mocked_task_service_update.called)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['Message'], TaskMessages.incorrect_parameters)

    @patch('services.task_service.is_registered')
    @patch('services.task_service.update')
    def test_update_invalid_status(self, mocked_task_service_update, mocked_task_service_is_registered):
        """
        It should return 400 if the status is invalid
        """

        mocked_task_service_is_registered.return_value = True

        response = self.test_client.put(self.update_route + TestUtils.task_with_invalid_status['name'],
                                        json=TestUtils.task_with_invalid_status)
        response_json = response.get_json()

        self.assertFalse(mocked_task_service_update.called)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['Message'], TaskMessages.invalid_status)

    @patch('services.task_service.is_registered')
    @patch('services.task_service.update')
    def test_update_duplicated(self, mocked_task_service_update, mocked_task_service_is_registered):
        """
        It should return 400 if there is a task with the new name
        """

        mocked_task_service_is_registered.return_value = True

        response = self.test_client.put(self.update_route + TestUtils.task_with_valid_body['name'] + '_new',
                                        json=TestUtils.task_with_valid_body)
        response_json = response.get_json()

        self.assertFalse(mocked_task_service_update.called)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['Message'], TaskMessages.duplicated)

    @patch('services.task_service.is_registered')
    @patch('services.task_service.update')
    def test_update_change_name(self, mocked_task_service_update, mocked_task_service_is_registered):
        """
        It should return 200 and update if there is not a task with the new name
        """

        # Returns True on first call and False on second one
        # Returns True when verifying if 'old_name' exists and returns False when verifying if new name exists
        mocked_task_service_is_registered.side_effect = [True, False]

        response = self.test_client.put(self.update_route + 'old_name',
                                        json=TestUtils.task_with_valid_body)
        response_json = response.get_json()

        self.assertTrue(mocked_task_service_update.called)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['Message'], TaskMessages.updated)

    @patch('services.task_service.is_registered')
    @patch('services.task_service.update')
    def test_update_upper_case(self, mocked_task_service_update, mocked_task_service_is_registered):
        """
        It should set status to lower case (.lower()) before updating the task
        """

        mocked_task_service_is_registered.return_value = True

        response = self.test_client.put(self.update_route + TestUtils.task_with_valid_body['name'],
                                        json=TestUtils.task_with_status_upper_case)

        task_used_by_mock = mocked_task_service_update.call_args[0][1]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(task_used_by_mock.status,
                         TestUtils.task_with_status_upper_case['status'].lower())

    """
    Delete route tests
    """

    @patch('services.task_service.delete')
    @patch('services.task_service.is_registered')
    def test_delete(self, mocked_task_service_is_registered, mocked_task_service_delete):
        """
        It should return 200 and delete the task
        """

        mocked_task_service_is_registered.return_value = True

        response = self.test_client.delete(self.delete_route + 'test_name')
        response_json = response.get_json()

        self.assertTrue(mocked_task_service_delete.called)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['Message'], TaskMessages.deleted)

    @patch('services.task_service.delete')
    @patch('services.task_service.is_registered')
    def test_delete_not_found(self, mocked_task_service_is_registered, mocked_task_service_delete):
        """
        It should return 404 if the task does not exist
        """

        mocked_task_service_is_registered.return_value = False

        response = self.test_client.delete(self.delete_route + 'test_task')
        response_json = response.get_json()

        self.assertFalse(mocked_task_service_delete.called)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json['Message'], TaskMessages.not_found)
