



const imageInput = document.querySelector('#image_input');
const imgElement = document.querySelector('#display_image_img');
const uploadedImageElement = document.querySelector('#uploaded_image');
const segmentedImageElements = document.querySelectorAll('.segmented-image');
const contrastSlider = document.getElementById('contrast_slider');
const blurSlider = document.getElementById('blur_slider');
const brightnessSlider = document.getElementById('brightness_slider');
const contrastSliderjs = document.getElementById('contrast_slider_js');
const thirdPage_NextButton = document.querySelector('next_button_step3');
var pickedImages = [];

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
      var vectorData = [];
  
      // Helper function to convert image Blob to Base64 data
      function blobToBase64(blob) {
        return new Promise(resolve => {
          const reader = new FileReader();
          reader.onloadend = () => resolve(reader.result);
          reader.readAsDataURL(blob);
        });
      }
  
      // Helper function to fetch image data from URL and convert it to Blob
      function fetchImage(url) {
        return new Promise((resolve, reject) => {
          fetch(url)
            .then(response => response.blob())
            .then(blob => resolve(blob))
            .catch(error => reject(error));
        });
      }
  
      // Iterate over the pickedImages array
      console.log("Number of pickedImages:", pickedImages.length);
      Promise.all(pickedImages.map(function(image) {
        console.log("pickedImages", pickedImages)
        if (typeof image === 'object' && image.imageUrl && image.imageUrl.startsWith('http')) {
          return fetchImage(image.imageUrl)
            .then(blob => blobToBase64(blob))
            .then(base64Data => {
              vectorData.push({
                data: base64Data,
                grayscale: image.grayscale,
                saturation: image.saturation,
                brightness: image.brightness,
                hueRotate: image.hueRotate
              });
            })
            .catch(error => {
              console.log('Error fetching image:', error);
              return Promise.reject();
            });
        } else {
          console.log('Invalid image object:', image);
          return Promise.reject();
        }
      }))
        .then(() => {
          console.log("Base64 data:", vectorData);
          console.log("vectorData", vectorData);
  
          // Make an HTTP request to the Flask server
          var xhr = new XMLHttpRequest();
          xhr.open('POST', '/save-images', true);
          xhr.setRequestHeader('Content-Type', 'application/json');
          xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
              if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success) {
                  // Images saved successfully, redirect to the next page
                  window.location.href = '/third-page';
                } else {
                  // Handle error case
                  console.log('Error: Images could not be saved');
                }
              } else {
                // Handle error case
                console.log('Error: ' + xhr.status);
              }
            }
          };
          xhr.send(JSON.stringify({ vector: vectorData }));
        })
        .catch(error => {
          console.log('Error: ' + error);
        });
    });
  } else {
    console.log("Not the complete segment button");
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


// function loadUploadedImage() {
//  const uploadedImage = sessionStorage.getItem('uploaded_image');
//  if (uploadedImage) {
//    uploadedImageElement.src = uploadedImage;
//  } else {
//    console.log("No image data found in sessionStorage");
//  }


//  // Load segmented images
//  segmentedImageElements.forEach(function(imageElement) {
//    imageElement.src = uploadedImage;
//  });

// const userInput_ = 5; // Replace with your actual user input

// // Get the container where the image items will be appended
// const imageGrid = document.getElementById('image-grid');
// }

function loadUploadedImage() {
  const uploadedImage = sessionStorage.getItem('uploaded_image');
  if (uploadedImage) {
    document.getElementById('uploaded_image').src = uploadedImage; // Set the source of the image to the uploaded image
  } else {
    console.log("No image data found in sessionStorage");
  }
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
  const imageUrl = imageItem.querySelector('img').src;

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

    // Apply the image adjustments initially
    applyImageAdjustments();

    // Add the image URL and its current style values to the pickedImages array
    pickedImages.push({
      imageUrl: imageUrl,
      grayscale: grayscaleValue,
      saturation: saturationValue,
      brightness: brightnessValue,
      hueRotate: hueRotateValue
    });

  } else {
    button.innerHTML = 'Pick';
    button.style.backgroundColor = 'white';
    menu.style.display = 'none'; // Hide the menu

    // Remove the image object from the pickedImages array based on its URL
    const index = pickedImages.findIndex(obj => obj.imageUrl === imageUrl);
    if (index > -1) {
      pickedImages.splice(index, 1);
    }
  }

  console.log("vector", pickedImages);

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


// document.getElementById('diffusion-model-form').addEventListener('submit', function(event) {
//   event.preventDefault();
//   var prompt = document.getElementById('diffusion-model-prompt').value;
//   fetch('/run-diffusion-model', {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/x-www-form-urlencoded',
//     },
//     body: 'prompt=' + encodeURIComponent(prompt),
//   })
//   .then(response => response.text())
//   .then(url => {
//     // display the result image
//     var img = document.createElement('img');
//     img.src = url;
//     document.getElementById('diffusion-model-result').appendChild(img);
//   });
// });


const nextButtonStep3 = document.getElementById('next_button_step3');
const promptInput = document.getElementById('prompt-input');

nextButtonStep3.addEventListener('click', function() {
  const promptData = {
    prompt: promptInput.value
  };

  fetch('/run-diffusion-model', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(promptData)
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      console.error(data.error);
    } else {
      window.location.href = '/forth-page?image_url=' + encodeURIComponent(data.image_url);
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
});

