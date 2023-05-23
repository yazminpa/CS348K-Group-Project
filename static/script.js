const image_input = document.querySelector('#image_input');
const next_button_step1 = document.querySelector('#next_button_step1');
//const next_button_step2 = document.querySelector('#next_button_step2');
let uploaded_image = "";

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

next_button_step1.addEventListener('click', function() {
  // Store the image data in localStorage
  localStorage.setItem('uploaded_image', uploaded_image);

  // Make an HTTP request to the Flask server
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/next-page', true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      // Redirect to the next page
      window.location.href = '/next-page';
    }
  };
  xhr.send();
});
// next_button_step2.addEventListener('click', function() {
//   console.log("Button clicked"); // Check if this message is logged in the browser console
//   // Store the image data in localStorage
//   localStorage.setItem('uploaded_image', uploaded_image);

//   // Make an HTTP request to the Flask server
//   var xhr = new XMLHttpRequest();
//   xhr.open('GET', '/third-page', true);
//   xhr.onreadystatechange = function() {
//     if (xhr.readyState === 4 && xhr.status === 200) {
//       // Redirect to the next page
//       window.location.href = '/third-page';
//     }
//   };
//   xhr.send();
// });

function toggleButton(button) {
  if (button.innerHTML === 'Pick') {
    button.innerHTML = 'Layer Picked';
    button.style.backgroundColor = 'gray';
  } else {
    button.innerHTML = 'Pick';
    button.style.backgroundColor = 'white';
  }
}