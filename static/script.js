



const imageInput = document.querySelector('#image_input');
const imgElement = document.querySelector('#display_image_img');
const uploadedImageElement = document.querySelector('#uploaded_image');
const segmentedImageElements = document.querySelectorAll('.segmented-image');
const contrastSlider = document.getElementById('contrast_slider');
const blurSlider = document.getElementById('blur_slider');
const brightnessSlider = document.getElementById('brightness_slider');
const contrastSliderjs = document.getElementById('contrast_slider_js');
let file; // Declare the file variable here


if (imageInput && imgElement) {
 imageInput.addEventListener('change', function(event) {
   file = event.target.files[0]; // Assign the selected file to the file variable


   // Create a FileReader to read the image file
   const reader = new FileReader();
   reader.onload = function(e) {
     imgElement.src = e.target.result; // Set the source of the <img> element to the loaded image
   };
   reader.readAsDataURL(file); // Read the file as a data URL
 });
}
function dataURLtoFile(dataURL, filename) {
 const arr = dataURL.split(',');
 const mime = arr[0].match(/:(.*?);/)[1];
 const bstr = atob(arr[1]);
 let n = bstr.length;
 const u8arr = new Uint8Array(n);
 while (n--) {
   u8arr[n] = bstr.charCodeAt(n);
 }
 return new File([u8arr], filename, { type: mime });
}

//Dont need this function anymore
const SegmentationButton = document.querySelector('#test_button');
if (SegmentationButton) {
  SegmentationButton.addEventListener('click', function() {
   // Make an HTTP request to the Flask server
   var xhr = new XMLHttpRequest();
   xhr.open('GET', '/predict', true);
   xhr.onload = function() {
     if (xhr.readyState === 4 && xhr.status === 200) {
       var response = JSON.parse(xhr.responseText);
       console.log(response.message);
     }
   };
   xhr.send();
 });
}



const nextButtonStep1 = document.querySelector('#next_button_step1');
const statusElement = document.querySelector('#status');


if (nextButtonStep1) {
  nextButtonStep1.addEventListener('click', function() {
  statusElement.innerText = "Segmenting...";

  // Make an HTTP request to the Flask server
  var xhr1 = new XMLHttpRequest();
  xhr1.open('GET', '/predict', true);
  xhr1.onreadystatechange = function() {
    if (xhr1.readyState === 4 && xhr1.status === 200) {
      console.log("first function ready")

      secondFunctionCallback();
    }  
  };
  xhr1.send();
 });
}
  // Callback function to execute the second function
  function secondFunctionCallback() {
    var xhr2 = new XMLHttpRequest();
    console.log("second function")
    xhr2.open('POST', '/adjust-contrast-server', true);
    xhr2.setRequestHeader('Content-Type', 'multipart/form-data'); // Set the content type
    xhr2.onreadystatechange = function() {
      if (xhr2.readyState === 4 && xhr2.status === 200) {
        console.log("second function ready")
        // The second function (POST request) completed
        // Redirect to the next page
        window.location.href = '/next-page';
      }
    };
    xhr2.send();
  }

const CompleteSegButton = document.querySelector('#next_button_step2');


if (CompleteSegButton) {
 CompleteSegButton.addEventListener('click', function() {
   // Make an HTTP request to the Flask server
   var xhr = new XMLHttpRequest();
   xhr.open('GET', '/third-page', true);
   xhr.onreadystatechange = function() {
     if (xhr.readyState === 4 && xhr.status === 200) {
       // Redirect to the next page
       window.location.href = '/third-page';
     }
   };
   xhr.send();
 });
} else {
 console.log("Not complete segment button");
}
// Function to convert base64 string to Blob object
function dataURItoBlob(dataURI) {
 const byteString = atob(dataURI.split(',')[1]);
 const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
 const ab = new ArrayBuffer(byteString.length);
 const ia = new Uint8Array(ab);
 for (let i = 0; i < byteString.length; i++) {
   ia[i] = byteString.charCodeAt(i);
 }
 return new Blob([ab], { type: mimeString });
}
const currentPage = window.location.pathname; // Get the current page URL path


// if (currentPage.includes('next-page') || currentPage.includes('third-page')) {
if (currentPage.includes('forth-page')) {
 loadUploadedImage();
} else {
 console.log("Not in current path");
}


function loadUploadedImage() {
 const uploadedImage = sessionStorage.getItem('uploaded_image');
 if (uploadedImage) {
   uploadedImageElement.src = uploadedImage;
 } else {
   console.log("No image data found in sessionStorage");
 }


 // Load segmented images
 segmentedImageElements.forEach(function(imageElement) {
   imageElement.src = uploadedImage;
 });

const userInput_ = 5; // Replace with your actual user input

// Get the container where the image items will be appended
const imageGrid = document.getElementById('image-grid');

  // Check if the image items already exist

   // Get save button and add event listener
  //  const saveButton = document.getElementById('save_button');
  //  saveButton.addEventListener('click', function() {
  //    const canvas = document.createElement('canvas');
  //    const context = canvas.getContext('2d');
  //    const ImageElement = new Image();
  
  //    ImageElement.onload = function() {
  //      canvas.width = ImageElement.width;
  //      canvas.height = ImageElement.height;
  //      context.filter = ImageElement.style.filter;
  //      context.drawImage(ImageElement, 0, 0);
      
  //      const dataURL = canvas.toDataURL('image/png');
  //      const link = document.createElement('a');
  //      link.href = dataURL;
  //      link.download = 'edited_image.png';
  //      link.click();
  //    };
  
  //    ImageElement.src = uploadedImage;
  //  });
}

let grayscaleValue = 0;
let saturationValue = 100;
let brightnessValue = 100;
let hueRotateValue = 0;

function toggleButton(button, imageItem) {
  const menu = imageItem.querySelector('.menu-container');
  const grayscaleSlider = menu.querySelector('.grayscale-slider');
  const saturationSlider = menu.querySelector('.saturation-slider');
  const brightnessSlider = menu.querySelector('.brightness-slider');
  const hueRotateSlider = menu.querySelector('.hue-rotate-slider');
  const image = imageItem.querySelector('img');

  if (button.innerHTML === 'Pick') {
    button.innerHTML = 'Layer Picked';
    button.style.backgroundColor = 'gray';
    menu.style.display = 'block'; // Show the menu

    grayscaleSlider.value = grayscaleValue;
    saturationSlider.value = saturationValue;
    brightnessSlider.value = brightnessValue;
    hueRotateSlider.value = hueRotateValue;

    grayscaleSlider.addEventListener('input', function() {
      grayscaleValue = grayscaleSlider.value;
      applyImageAdjustments();
    });

    saturationSlider.addEventListener('input', function() {
      saturationValue = saturationSlider.value;
      applyImageAdjustments();
    });

    brightnessSlider.addEventListener('input', function() {
      brightnessValue = brightnessSlider.value;
      applyImageAdjustments();
    });

    hueRotateSlider.addEventListener('input', function() {
      hueRotateValue = hueRotateSlider.value;
      applyImageAdjustments();
    });
  } else {
    button.innerHTML = 'Pick';
    button.style.backgroundColor = 'white';
    menu.style.display = 'none'; // Hide the menu
  }

  function applyImageAdjustments() {
    image.style.filter = `grayscale(${grayscaleValue}%) saturate(${saturationValue}%) brightness(${brightnessValue}%) hue-rotate(${hueRotateValue}deg)`;
  }
}

const thirdPageNextButton = document.querySelector('#next_button_step3');

if (thirdPageNextButton) {
  thirdPageNextButton.addEventListener('click', function() {
   // Make an HTTP request to the Flask server
   var xhr = new XMLHttpRequest();
   xhr.open('GET', '/forth-page', true);
   xhr.onreadystatechange = function() {
     if (xhr.readyState === 4 && xhr.status === 200) {
       // Redirect to the next page
       window.location.href = '/forth-page';
     }
   };
   xhr.send();
 });
} else {
 console.log("Can not go to forth page");
}


document.getElementById('diffusion-model-form').addEventListener('submit', function(event) {
  event.preventDefault();
  var prompt = document.getElementById('diffusion-model-prompt').value;
  fetch('/run-diffusion-model', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'prompt=' + encodeURIComponent(prompt),
  })
  .then(response => response.text())
  .then(url => {
    // display the result image
    var img = document.createElement('img');
    img.src = url;
    document.getElementById('diffusion-model-result').appendChild(img);
  });
});

