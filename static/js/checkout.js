$(function () {
    var IMP = window.IMP;
    IMP.init('imp11166264'); // 가맹정 코드
    $('.order-form').on('submit', function (e) { // 결제하기 버튼을 눌렀을때 function을 동작 시키겠다.
        var amount = parseFloat($('.order-form input[name="amount"]').val().replace(',', '')); // 형변환
        var type = $('.order-form input[name="type"]:checked').val(); // 결제 종류에 따른 다른 창을 띄울 수 있음
        // 폼 데이터를 기준으로 주문 생성
        var order_id = AjaxCreateOrder(e);
        if (order_id == false) {
            alert('주문 생성 실패\n다시 시도해주세요.');
            return false;
        }

        // 결제 정보 생성
        var merchant_id = AjaxStoreTransaction(e, order_id, amount, type);

        // 결제 정보가 만들어졌으면 iamport로 실제 결제 시도
        // iamport 메뉴얼에 따라서 한 것
        if (merchant_id !== '') { // !== 타입까지 같지 않으면
            IMP.request_pay({ // 결제 완료 전
                merchant_uid: merchant_id,
                name: 'E-Shop product',
                buyer_name:$('input[name="first_name"]').val()+" "+$('input[name="last_name"]').val(),
                buyer_email:$('input[name="email"]').val(),
                amount: amount
            }, function (rsp) { // 결제 완료된 후
                if (rsp.success) {
                    var msg = '결제가 완료되었습니다.';
                    msg += '고유ID : ' + rsp.imp_uid; // 결제 완료 후 보여줄 메세지
                    msg += '상점 거래ID : ' + rsp.merchant_uid;
                    msg += '결제 금액 : ' + rsp.paid_amount;
                    msg += '카드 승인번호 : ' + rsp.apply_num;
                    // 결제가 완료되었으면 비교해서 디비에 반영
                    ImpTransaction(e, order_id, rsp.merchant_uid, rsp.imp_uid, rsp.paid_amount);
                } else {
                    var msg = '결제에 실패하였습니다.';
                    msg += '에러내용 : ' + rsp.error_msg;
                    console.log(msg); // 크롬에서는 동작하고 다른 브라우저에서는 안될 수도 있음음                }
            });
        }
        return false;
    });
});

// 폼 데이터를 기준으로 주문 생성
function AjaxCreateOrder(e) { // 위에서 받은 이벤트 e를 받아서 동작
    e.preventDefault(); // 폼이 summit 되는걸 막음
    var order_id = '';
    var request = $.ajax({ // ajax처리
        method: "POST",
        url: order_create_url,
        async: false, // 하나일이 끝나면 다음일로
        data: $('.order-form').serialize()
    });
    request.done(function (data) {
        if (data.order_id) {
            order_id = data.order_id;
        }
    });
    request.fail(function (jqXHR, textStatus) { // 문제가 생겼을 때
        if (jqXHR.status == 404) {
            alert("페이지가 존재하지 않습니다.");
        } else if (jqXHR.status == 403) {
            alert("로그인 해주세요.");
        } else {
            alert("문제가 발생했습니다. 다시 시도해주세요.");
        }
    });
    return order_id;
}

// 결제 정보 생성
function AjaxStoreTransaction(e, order_id, amount, type) {
    e.preventDefault();
    var merchant_id = '';
    var request = $.ajax({
        method: "POST",
        url: order_checkout_url, //create html에 신호를 보냄
        async: false, // 동기화 작업
        data: {
            order_id : order_id,
            amount: amount,
            type: type,
            csrfmiddlewaretoken: csrf_token, // csrf 토큰
        }
    });
    request.done(function (data) {
        if (data.works) {
            merchant_id = data.merchant_id;
        }
    });
    request.fail(function (jqXHR, textStatus) {
        if (jqXHR.status == 404) {
            alert("페이지가 존재하지 않습니다.");
        } else if (jqXHR.status == 403) {
            alert("로그인 해주세요.");
        } else {
            alert("문제가 발생했습니다. 다시 시도해주세요.");
        }
    });
    return merchant_id;
}

// iamport에 결제 정보가 있는지 확인 후 결제 완료 페이지로 이동
function ImpTransaction(e, order_id, merchant_id, imp_id, amount) {
    e.preventDefault();
    var request = $.ajax({
        method: "POST",
        url: order_validation_url,
        async: false,
        data: { // 앞은 변수명, 뒤는 실제 값
            order_id:order_id,
            merchant_id: merchant_id,
            imp_id: imp_id,
            amount: amount,
            csrfmiddlewaretoken: csrf_token
        }
    });
    request.done(function (data) {
        if (data.works) { // 넘겨줄 페이지
            $(location).attr('href', location.origin+order_complete_url+'?order_id='+order_id)
        }
    });
    request.fail(function (jqXHR, textStatus) {
        if (jqXHR.status == 404) {
            alert("페이지가 존재하지 않습니다.");
        } else if (jqXHR.status == 403) {
            alert("로그인 해주세요.");
        } else {
            alert("문제가 발생했습니다. 다시 시도해주세요.");
        }
    });
}