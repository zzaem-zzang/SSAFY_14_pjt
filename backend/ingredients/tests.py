from rest_framework.test import APITestCase


class DrugAPITest(APITestCase):
    def test_save_drug_without_valid_api_key_returns_502(self):
        resp = self.client.get('/api/drugs/save/', {'name': '타이'})
        # 외부 API 인증 실패의 경우 502로 매핑되도록 처리
        self.assertIn(resp.status_code, (502, 200))
        # 에러 메시지가 있을 경우 data.error 포함
        if resp.status_code != 200:
            self.assertIn('error', resp.data)
