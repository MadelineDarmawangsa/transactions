import unittest
from app import app 

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        # Set up your test client
        app.testing = True
        self.client = app.test_client()

    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_summarize_route(self):
        response = self.client.post('/summarize', data={'Input': '{"creditLimit":1000,"events":[{"eventType":"TXN_AUTHED","eventTime":1,"txnId":"t1","amount":123},{"eventType":"TXN_SETTLED","eventTime":2,"txnId":"t1","amount":456},{"eventType":"PAYMENT_INITIATED","eventTime":3,"txnId":"p1","amount":-456}]}'})
        self.assertIn(b'$544', response.data)  
        self.assertIn(b'$0', response.data)  
        self.assertIn(b'Transaction ID: p1 - Amount: -456 @ Time: 3', response.data)  
        self.assertIn(b'Transaction ID: t1 - Amount: 456 @ Time: 2', response.data)  
