<?php
// Get the image data from the query parameters
$imageData = $_GET['image_data'];

// Generate a unique identifier for the image
$imageId = uniqid();

// Save the image data to a temporary location on the server
file_put_contents("temp/$imageId.jpg", base64_decode($imageData));

// Redirect to the next page with the image ID as a query parameter
header("Location: next-page.html?image_id=$imageId");
exit();
?>
