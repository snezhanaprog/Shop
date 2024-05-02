const userProfile = document.querySelector('.header__profile-user');
const userElementsList = userProfile.querySelector('ul');
console.log(userElementsList);
console.log(userProfile)

userProfile.addEventListener('click', () => {
    userElementsList.classList.toggle('profile-user__hide');
})

const header = document.querySelector('header');
const heightShowHeader = 450; // Момент, с которого начинается фиксация




window.addEventListener('scroll', () => {
    let scrollHight = window.scrollY;

    if (scrollHight >= heightShowHeader) {
        header.classList.add('header-fix');

    } else {
        header.classList.remove('header-fix');

    }
})