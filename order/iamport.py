import requests
from django.conf import settings


def get_token(): # API와 secret 키를 가지고 iamport로 가서 로그인처리
    access_data={ # iamport 메뉴얼에 되어있음 key값 데이터
        'imp_key':settings.IAMPORT_KEY,
        'imp_secret':settings.IAMPORT_SECRET
    }
    url = "https://api.iamport.kr/users/getToken" # url에 접속해서 정보를 받아옴
    req = requests.post(url, data=access_data)
    access_res = req.json() # api는 일반적으로 json으로 받아옴

    if access_res['code'] is 0: # 제대로 응답이 왔다. 0이 기본임
        return access_res['response']['access_token'] # 이걸 가지고 서버랑 통신함
    else:
        return None


def payments_prepare(order_id, amount, *args, **kwargs): # 어떤 아이디로 얼마만큼의 결제를 할지 등록
    access_token = get_token()
    if access_token:
        access_data = {
            'merchant_uid':order_id,
            'amount':amount
        }
        url = "http://api.iamport.kr/payments/prepare"
        headers = { # header 정보가 있어야 통신 가능
            'Authorization':access_token
        }
        req = requests.post(url, data=access_data, headers=headers)
        res = req.json()
        if res['code'] != 0: # 응답 실패시
            raise ValueError("API 통신 오류")
    else:
        raise ValueError("토큰 오류")


def find_transaction(order_id, *args, **kwargs): # 사용자가 결제하면 iamport쪽에 정보가 남는데 실제로 결제가 됐는지 확인하는 과정
    # 결제가 되었는지 들어가서 확인하는 부분
    access_token = get_token()
    if access_token:
        url = "https://api.iamport.kr/payments/find"+order_id
        headers = {
            'Authorization': access_token
        }
        req = requests.post(url, headers=headers) # data가 없는 이유는 url에 order_id를 붙여서 그럼
        res = req.json()
        if res['code'] == 0:
            context = { # 가져온 데이터를 리턴해서 확인
                'imp_id': res['response']['imp_uid'],
                'merchant_order_id': res['response']['merchant_uid'],
                'amount': res['response']['amount'],
                'status': res['response']['status'],
                'type': res['response']['pay_method'],
                'receipt_url': res['response']['receipt_url']
            }
            return context
        else:
            return None
    else:
        raise ValueError("토큰 오류")

