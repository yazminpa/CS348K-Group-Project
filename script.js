const image_input = document.querySelector('#image_input');
const image_display = document.querySelector('#display_image');
const next_button_step1 = document.querySelector('#next_button_step1');
var uploaded_image = "";

// Upload and display image
image_input.addEventListener('change', function() {
    const reader = new FileReader();
    reader.addEventListener('load', () => {
        uploaded_image = reader.result;
        document.querySelector('#display_image').style.backgroundImage = `url(${uploaded_image})`;
        const img = new Image();
        img.src = uploaded_image;
        img.onload = function() {
            const display_width = document.querySelector('#display_image').offsetWidth;
            const display_height = document.querySelector('#display_image').offsetHeight;
            const img_width = img.width;
            const img_height = img.height;
            const scale = Math.min(display_width / img_width, display_height / img_height);
            document.querySelector('#display_image').style.backgroundSize = `${scale * img_width}px ${scale * img_height}px`;
        }
    });
    reader.readAsDataURL(this.files[0]);
});

// Tried this quickly but get 501 error, just for reference
// function nextButton() {
//     // logic for navigating to the next page
//     window.location.href = 'next-page.html';
// };

// next_button_step1.addEventListener('click', nextButton);

