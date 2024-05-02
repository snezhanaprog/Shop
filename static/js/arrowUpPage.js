const heightPointPage = 250;
const buttonPageUp = document.querySelector('.line-button-page-up').querySelector('button');

window.addEventListener('scroll', () => {
    let scrollHight = window.scrollY;

    if (scrollHight >= heightPointPage) {
        buttonPageUp.classList.remove('hide')
    } else {
        buttonPageUp.classList.add('hide')
    }
})

buttonPageUp.addEventListener('click', () => {
    window.scrollTo({
        top: 0,
        left: 0,
    });
})
