import unittest

from françoise.mail import parse_to_header, parse_conversation_id_from_headers


class TestMail(unittest.TestCase):
    def test_parse_to_header(self):
        headers = '[["To","\"Boku.2\" <foo@bar.com>"]]'
        to = parse_to_header(headers)
        self.assertEqual(to, '"\"Boku.2\" <foo@bar.com>"')

    def test_parse_conversation_id_from_headers(self):
        headers = '[["To","\"Boku.2\" <foo@bar.com>"]]'
        conversation_id = parse_conversation_id_from_headers(headers)
        self.assertEqual(conversation_id, 2)


if __name__ == '__main__':
    unittest.main()
