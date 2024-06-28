document.addEventListener('DOMContentLoaded', function() {

//setmood-page appears
    window.addEventListener('load', function() {
        document.body.classList.add('visible');
    });
//login-page animation
    const loginForm = document.getElementById('loginForm');
    if(loginForm) {
        const handleSubmit = function(event) {
            event.preventDefault();
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/', true);
            xhr.onload = function() {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    if (response.success) {
                        loginForm.removeEventListener('submit', handleSubmit);
                        document.querySelector('.index-waves').classList.toggle('anim-trans-w');
                        document.querySelector('.wave-background').classList.toggle('anim-trans-bg');
                        localStorage.setItem('loginSuccess', 'true');
                        setTimeout(function() {
                            window.location.href = '/setmood';
                        }, 1000);
                    } else {
                        const errorDiv = document.querySelector('.error');
                        if (errorDiv) {
                            console.log('Error div found:', errorDiv);
                            errorDiv.textContent = response.message;
                        }
                    }
                }
            };
            const formData = new FormData(loginForm);
            xhr.send(formData);
            };
        loginForm.addEventListener('submit', handleSubmit);
    };

//setmood-page succes login animation
    const loginSuccess = localStorage.getItem('loginSuccess');
    if (loginSuccess) {
        document.querySelector('.li-wave-bg').classList.toggle('anim-trans-li-bg');
        document.querySelector('.li-header .waves').classList.toggle('anim-trans-li');
        localStorage.removeItem('loginSuccess');
    }

//setmood-page stars animation
    const stars = document.querySelectorAll('.rate-radio');
    const smiley = document.getElementById('smiley');
    const moodInput = document.getElementById('mood-input');
    const form = document.getElementById('rating-form');

    stars.forEach(star => {
        star.addEventListener('click', function() {
            const rating = this.getAttribute('data-rating');
            moodInput.value = rating;

            switch (rating) {
                case '1':
                    smiley.src = 'static/pics/badmood.jpg';
                    break;
                case '2':
                    smiley.src = 'static/pics/midbadmood.jpg';
                    break;
                case '3':
                    smiley.src = 'static/pics/midmood.jpg';
                    break;
                case '4':
                    smiley.src = 'static/pics/midhappymood.jpg';
                    break;
                case '5':
                    smiley.src = 'static/pics/happymood.jpg';
                    break;
            }
            const formData = new FormData(form);
            fetch('/setmood', {
                method: 'POST',
                body: formData
            }).catch(error => {
                console.error('Error:', error);
            });
        });
    });
});