let actionBtns = document.querySelectorAll('.actionBtn');
let items = document.querySelector('.container__list-shop');
const sortList = document.querySelector('.sort-event').querySelector('ul')
const sortEventButton = document.querySelector('.sort-event').querySelector('button');

sortEventButton.addEventListener('click', () => {
    sortList.classList.toggle('.sort-list__hide');
})

const getCookie = (name) => {
    let cookieValue = null;
        if(document.cookie && document.cookie !== ''){
            var cookies = document.cookie.split(';');
            for(let i = 0; i < cookies.length; i++){
                let cookie = cookies[i].trim();
                if(cookie.substring(0, name.length + 1) === (name + '=')){
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                };
            };
        };
        return cookieValue;
};

var csrftoken = getCookie('csrftoken');

const addProductInOrder = (productId, action) => {
    let url = '/add_item/';

    fetch(url, {
        method: 'POST',
        headers: {'Content-Type':'application/json', 'X-CSRFToken':csrftoken},
        body:JSON.stringify({'productId':productId, 'action':action})
    })		.then((response) => {
		   return response.json();
		})
		.then((data) => {
		    location.reload();
		});
};

actionBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
        var productId = btn.dataset.product;
        var action = btn.dataset.action;
        console.log('productId:', productId, 'action:', action);
        addProductInOrder(productId, action);
    });
});

