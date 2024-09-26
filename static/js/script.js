document.addEventListener('DOMContentLoaded', function() {

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