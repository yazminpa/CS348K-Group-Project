const imageInput = document.querySelector('#image_input');
const imgElement = document.querySelector('#display_image_img');
const uploadedImageElement = document.querySelector('#uploaded_image');
const segmentedImageElements = document.querySelectorAll('.segmented-image');

if (imageInput && imgElement) {
  imageInput.addEventListener('change', function(event) {
    const file = event.target.files[0];

    // Create a FileReader to read the image file
    const reader = new FileReader();
    reader.onload = function(e) {
      imgElement.src = e.target.result; // Set the source of the <img> element to the loaded image
    };
    reader.readAsDataURL(file); // Read the file as a data URL
  });
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
    console.log("In 1");

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
