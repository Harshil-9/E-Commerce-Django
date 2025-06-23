var toastElList = [].slice.call(document.querySelectorAll('.toast'))
var toastList = toastElList.map(function (toastEl) {
  return new bootstrap.Toast(toastEl)
})

function showToast() {
    toastList[0].show()
}

var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

function gotoproductdetailpage() {
    window.location.href="/product_detial.html"
}

document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('.star-rating').forEach(function(starGroup) {
            starGroup.querySelectorAll('.bi-star').forEach(function(star, idx, stars) {
                star.addEventListener('click', function() {
                    stars.forEach(s => s.classList.remove('star-selected'));
                    for (let i = 0; i <= idx; i++) {
                        stars[i].classList.add('star-selected');
                    }
                });
            });
        });
    });