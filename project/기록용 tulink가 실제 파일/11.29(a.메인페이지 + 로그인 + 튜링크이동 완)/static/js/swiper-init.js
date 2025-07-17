const swiperWrapper = document.querySelector('.swiper-wrapper');
const prevButton = document.querySelector('.swiper_prev');
const nextButton = document.querySelector('.swiper_next');
const bullets = document.querySelectorAll('.swiper_circle');

let currentSlide = 0;
const slides = document.querySelectorAll('.swiper-slide');
const totalSlides = slides.length;

function showSlide(slideIndex) {
    if (slideIndex < 0) slideIndex = totalSlides - 1; // 첫 번째로 돌아가면 마지막으로
    if (slideIndex >= totalSlides) slideIndex = 0;  // 마지막에서 넘기면 첫 번째로

    // 슬라이드의 넓이 계산
    const slideWidth = slides[0].offsetWidth;
    const containerWidth = swiperWrapper.offsetWidth;

     // 슬라이드의 중심이 컨테이너 중심에 오도록 조정
     const translateX = -slideIndex * slideWidth + (containerWidth - slideWidth) / 2;

     // `swiper-wrapper` 이동
     swiperWrapper.style.transform = `translateX(${translateX}px)`;
 
     currentSlide = slideIndex;
 
     // 슬라이드 상태 업데이트
     slides.forEach((slide, index) => {
         slide.classList.toggle('active', index === currentSlide);
     });

    // 동그라미 활성화 상태 업데이트
    bullets.forEach((bullet, index) => {
        bullet.classList.toggle('active', index === currentSlide);
    });

    // 슬라이드 강조 상태 업데이트
    slides.forEach((slide, index) => {
        slide.classList.toggle('active', index === currentSlide);
    });
}

// 초기 슬라이드 설정 (첫 번째 슬라이드)
showSlide(0);

// 'Next' 버튼 클릭 시 다음 슬라이드로
nextButton.addEventListener('click', () => {
    showSlide(currentSlide + 1);  // 현재 슬라이드에서 +1
});

// 'Prev' 버튼 클릭 시 이전 슬라이드로
prevButton.addEventListener('click', () => {
    showSlide(currentSlide - 1);  // 현재 슬라이드에서 -1
});

// 동그라미 버튼 클릭 시 해당 슬라이드로 이동
bullets.forEach((bullet, index) => {
    bullet.addEventListener('click', () => {
        showSlide(index);  // 클릭한 동그라미에 해당하는 슬라이드로 이동
    });
});

// 초기 슬라이드 설정 (첫 번째 슬라이드)
showSlide(0);
