let updateBtns = document.getElementsByClassName('update-cart')

for(let i = 0; i < updateBtns.length; i++){
    updateBtns[i].addEventListener('click', function (){
        let productId = this.dataset.product;
        let action = this.dataset.action;
        let isPremium = this.dataset.is_premium;

        console.log('productId:', productId, 'action:', action, 'is_premium:', isPremium);
        console.log('USER', user)

        if (user == 'AnonymousUser'){
            addCookieItem(productId, isPremium, action);
        } else {
            updateUserOrder(productId, isPremium, action);
        }
    })
}

function addCookieItem(productId, isPremium, action) {
    console.log('Not logged in');

    if(action == 'add') {
        cart[productId] = { is_premium: isPremium };
    }

    if(action == 'remove') {
        delete cart[productId];
    }

    console.log('Cart:', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    location.reload()
}

function updateUserOrder(productId, isPremium, action){
    console.log('User is authenticated')

    let url = '/update_item/'

    fetch(url, {
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'productId':productId, 'action':action, 'is_premium':isPremium})
    })

    .then((response) =>{
        return response.json()
    })

    .then((data) =>{
        console.log('data:', data)
        location.reload()
    });
}