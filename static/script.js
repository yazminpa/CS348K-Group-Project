const imageInput = document.querySelector('#image_input');
const imgElement = document.querySelector('#display_image_img');
const uploadedImageElement = document.querySelector('#uploaded_image');
const segmentedImageElements = document.querySelectorAll('.segmented-image');
const contrastSlider = document.getElementById('contrast_slider');
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


const testButton = document.querySelector('#test_button');
if (testButton) {
  testButton.addEventListener('click', function() {
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

if (nextButtonStep1) {
  nextButtonStep1.addEventListener('click', function() {
    // Store the image data in sessionStorage
    const uploadedImage = imgElement.src;
    sessionStorage.setItem('uploaded_image', uploadedImage);

    // Create a FormData object to send the image data as a file
    const formData = new FormData();
    const file = dataURLtoFile(uploadedImage, 'uploaded_image.png');
    formData.append('imageData', file);

    // Make an HTTP request to the Flask server
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/adjust-contrast-server', true);
    xhr.setRequestHeader('Content-Type', 'multipart/form-data'); // Set the content type
    xhr.onreadystatechange = function() {
      if (xhr.readyState === 4 && xhr.status === 200) {
        // Redirect to the next page
        window.location.href = '/next-page';
      }
    };
    xhr.send(formData);
  });
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

if (currentPage.includes('next-page') || currentPage.includes('third-page')) {
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
  // you can use the code below for when the images are all different 
  // Set the source of each segmented image element to the uploaded image 
  // segmentedImageElements.forEach(function(imageElement, index) {
  //   // const segmentedImageId = 'segmented_image' + (index + 1);
  //   // const segmentedImage = sessionStorage.getItem(segmentedImageId);
  //   const segmentedImage = sessionStorage.getItem('uploaded_image');
  //   if (segmentedImage) {
  //     imageElement.src = segmentedImage;
  //   } else {
  //     console.log("No segmented image " + (index + 1) + " data found in sessionStorage");
  //   }
  // });
  if (contrastSlider) {
    // Add an event listener to the contrast slider
    let contrastTimeout;
    contrastSlider.addEventListener('input', function() {
      const contrast = this.value;
    
      // Clear the previous timeout
      clearTimeout(contrastTimeout);
    
      // Set a new timeout of 2 seconds
      contrastTimeout = setTimeout(() => {
        // Create a FormData object
        // Convert base64 string to Blob object
        const imageData = dataURItoBlob(uploadedImage);
        const formData = new FormData();
        formData.append('imageData', imageData);
        formData.append('contrast', contrast);
        // Send the request to the server for contrast adjustment
        fetch('/adjust-contrast-server', {
          method: 'POST',
          body: formData
        })
          .then(response => response.text())
          .then(encodedImage => {
            console.log("Received encoded image:", encodedImage);
    
            // Handle the response containing the adjusted image
            // Set the source of the <img> element to the adjusted image
            if (encodedImage === "No image data received") {
              console.log("Error: No image data received");
            } else {
              uploadedImageElement.src = 'data:image/png;base64,' + encodedImage;
              console.log("Updated image source:", uploadedImageElement.src);
            }
          })
          .catch(error => {
            console.log('Error adjusting contrast:', error);
          });
      }, 2000); // 2-second delay
    });
    
    
  }

  if (currentPage.includes('third-page')) {
    // Get grayscale slider and add event listener
    // Get grayscale slider and add event listener
    const grayscaleSlider = document.getElementById('grayscale_slider');
    grayscaleSlider.addEventListener('input', function() {
      const value = this.value;

      // Apply grayscale filter to the image
      uploadedImageElement.style.filter = `grayscale(${value}%)`;
    });


    // Get save button and add event listener
    const saveButton = document.getElementById('save_button');
    saveButton.addEventListener('click', function() {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      const ImageElement = new Image();
    
      ImageElement.onload = function() {
        canvas.width = ImageElement.width;
        canvas.height = ImageElement.height;
        context.filter = ImageElement.style.filter;
        context.drawImage(ImageElement, 0, 0);
        
        const dataURL = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = dataURL;
        link.download = 'edited_image.png';
        link.click();
      };
    
      ImageElement.src = uploadedImage;
    });
    
  }
}

function toggleButton(button) {
  if (button.innerHTML === 'Pick') {
    button.innerHTML = 'Layer Picked';
    button.style.backgroundColor = 'gray';
  } else {
    button.innerHTML = 'Pick';
    button.style.backgroundColor = 'white';
    }

  
    
}
