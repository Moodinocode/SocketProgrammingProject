// Trigger the hidden file input when the upload button is clicked
document.getElementById('uploadButton').addEventListener('click', function() {
  document.getElementById('fileInput').click();
});

// Automatically upload file once it's selected
document.getElementById('fileInput').addEventListener('change', function() {
  if (this.files.length > 0) {
    uploadFile();
  }
});

function uploadFile() {
  const fileInput = document.getElementById('fileInput');
  if (!fileInput.files.length) {
    alert('Please select a file first');
    return;
  }

  
  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append('file', file);

  fetch('/list')
    .then(response => response.json())
    .then(data => { 
      if (data.files && data.files.includes(file.name)) {
        if (currentUser === "admin") {
          const choice = confirm(`File "${file.name}" already exists. Click OK to overwrite, or Cancel to create a new version.`);
          if (choice) {
            // Delete the existing file first, then proceed with upload
            return fetch('/delete', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ filename: file.name })
            })
            .then(response => response.json())
            .then(data => {
              if (data.error) {
                throw new Error('Failed to delete existing file: ' + data.error);
              }
              // Add overwrite flag to form data
              formData.append('is_overwrite', 'true');
              // Continue with the upload after successful deletion
              return Promise.resolve();
            });
          }
        }
      }
    }).then(()=>{

    
  // Show progress bar when upload starts
  document.getElementById('progressBar').style.display = 'block';
  document.getElementById('progressText').style.display = 'block';
  
  // Start progress tracking for this specific file
  const progressInterval = setInterval(() => {
    fetch(`/get_progress/${file.name}`)
      .then(response => response.json())
      .then(data => {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const progress = data.progress || 0;
        progressBar.value = progress;
        progressText.innerText = `${progress}%`;
        
        // If upload is complete, clear the interval
        if (data.status === 'completed' || progress >= 100) {
          clearInterval(progressInterval);
        }
      })
      .catch(error => console.error('Error fetching progress:', error));
  }, 1000);
  

  fetch('/upload', {
    method: 'POST',
    body: formData
  })
  .then(response => {
    console.log(response);
    return response.json();
  })
  .then(data => {
    // Clear the progress interval
    clearInterval(progressInterval);
    
    // Hide progress bar when upload completes
    document.getElementById('progressBar').style.display = 'none';
    document.getElementById('progressText').style.display = 'none';
    if (data.error) {
      alert('Error: ' + data.error);
    } else {
      alert(data.message);
      listFiles(); // Refresh file list after successful upload
    }
  })
  .catch(error => {
    // Clear the progress interval
    clearInterval(progressInterval);
    
    console.error('Error:', error);
    document.getElementById('progressBar').style.display = 'none';
    document.getElementById('progressText').style.display = 'none';
    alert('An error occurred during upload');
  });
  })
}


function downloadFile(filename) {
  if (!filename) return;

  // Show progress bar when download starts
  document.getElementById('progressBar').style.display = 'block';
  document.getElementById('progressText').style.display = 'block';
  
  // Start progress tracking for this specific file
  const progressInterval = setInterval(() => {
    fetch(`/get_progress/${filename}`)
      .then(response => response.json())
      .then(data => {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const progress = data.progress || 0;
        progressBar.value = progress;
        progressText.innerText = `${progress}%`;
        
        // If download is complete, clear the interval
        if (data.status === 'completed' || progress >= 100) {
          clearInterval(progressInterval);
        }
      })
      .catch(error => console.error('Error fetching progress:', error));
  }, 1000);

  fetch('/download', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ filename: filename })
  })
  .then(response => {
    // Clear the progress interval
    clearInterval(progressInterval);
    
    // Check if the response is a file or an error
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      // It's a JSON error response
      return response.json().then(data => {
        throw new Error(data.error || 'Download failed');
      });
    } else {
      // It's a file download
      return response.blob().then(blob => {
        // Create a URL for the blob
        const url = window.URL.createObjectURL(blob);
        // Create a temporary link element
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename; // Set the filename
        document.body.appendChild(a);
        a.click(); // Trigger the download
        window.URL.revokeObjectURL(url); // Clean up
        document.body.removeChild(a);
        
        // Hide progress bar when download completes
        document.getElementById('progressBar').style.display = 'none';
        document.getElementById('progressText').style.display = 'none';
      });
    }
  })
  .catch(error => {
    // Clear the progress interval
    clearInterval(progressInterval);
    
    console.error('Error:', error);
    document.getElementById('progressBar').style.display = 'none';
    document.getElementById('progressText').style.display = 'none';
    alert('An error occurred during download: ' + error.message);
  });
}

function listFiles() {
  fetch('/list')
    .then(response => response.json())
    .then(data => {
      const fileList = document.getElementById('fileList');
      fileList.innerHTML = '';

      if (data.files && data.files.length) {
        const ul = document.createElement('ul');

        data.files.forEach(file => {
          if (file) { // Skip empty entries
            const li = document.createElement('li');
            li.classList.add('file-item');

            // Get the file extension (if any)
            const parts = file.split('.');
            const extension = parts.length > 1 ? parts.pop().toLowerCase() : '';

            // Icon mapping based on file extension
            const iconMapping = {
              'txt': '../static/icons/text-file.png',
              'pdf': '../static/icons/pdf-file.png',
              'doc': '../static/icons/word-file.png',
              'docx': '../static/icons/word-file.png',
              'xls': '../static/icons/excel-file.png',
              'xlsx': '../static/icons/excel-file.png',
              'png': '../static/icons/image-file.png',
              'jpg': '../static/icons/image-file.png',
              'jpeg': '../static/icons/image-file.png',
              'gif': '../static/icons/image-file.png',
              'ppt': '../static/icons/ppt-file.png',
              'mp3': '../static/icons/audio-file.png',
              'html': '../static/icons/html-file.png',
              'delete': '../static/icons/delete.png',
              // Add more mappings as needed
            };

            const icon = document.createElement('img');
            icon.classList.add('file-icon');
            icon.src = iconMapping[extension] || '../static/icons/default-file.png';
            icon.alt = extension + ' file icon';

            const fileNameSpan = document.createElement('span');
            fileNameSpan.classList.add('file-name');
            fileNameSpan.textContent = file;
            const delbtn = document.createElement('button');
             console.log("Logged in as:", currentUser);
            if (currentUser === "admin") {
                const delicon = document.createElement('img');
                delbtn.classList.add('delbtn');
                delicon.src = '../static/icons/delete.png'
                delbtn.appendChild(delicon)
                //delbtn.textContent = 'icons/delete.png' || 'icons/default-file.png';;
                delbtn.addEventListener('click', () => {
                  deletefile(file);
                });
            }
            // Create the download button within each file listing
            const downloadButton = document.createElement('button');
            const downloadicon = document.createElement('img');
            downloadButton.classList.add('download-button');
            downloadButton.appendChild(downloadicon)
            downloadicon.src = '../static/icons/download-file.png';
            downloadButton.addEventListener('click', () => {
              downloadFile(file);
            });

            li.appendChild(icon);
            li.appendChild(fileNameSpan);
            if (currentUser === "admin") {
              li.append(delbtn)
            }
            li.appendChild(downloadButton);
            ul.appendChild(li);
          }
        });

        fileList.appendChild(ul);
      } else {
        fileList.textContent = 'No files available';
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('An error occurred while listing files');
    });
}

function deletefile(filename) {
  if (!filename) {
    alert('No file selected for deletion');
    return;
  }

  // Confirm deletion with the user
  if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
    return;
  }

  // Show progress bar when deletion starts
  document.getElementById('progressBar').style.display = 'block';
  document.getElementById('progressText').style.display = 'block';
  
  fetch('/delete', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ filename: filename })
  })
  .then(response => response.json())
  .then(data => {
    // Hide progress bar when deletion completes
    document.getElementById('progressBar').style.display = 'none';
    document.getElementById('progressText').style.display = 'none';
    
    if (data.error) {
      alert('Error: ' + data.error);
    } else {
      alert(data.message || 'File deleted successfully');
      listFiles(); // Refresh file list after successful deletion
    }
  })
  .catch(error => {
    console.error('Error:', error);
    document.getElementById('progressBar').style.display = 'none';
    document.getElementById('progressText').style.display = 'none';
    alert('An error occurred during file deletion');
  });
}

// Optionally, if you have server-side progress tracking:
function fetchProgress() {
  // Get the current file being processed (if any)
  const currentFile = document.querySelector('.file-item.selected')?.querySelector('.file-name')?.textContent || 'default_file';
  
  fetch(`/get_progress/${currentFile}`)
    .then(response => response.json())
    .then(data => {
      const progressBar = document.getElementById('progressBar');
      const progressText = document.getElementById('progressText');
      const progress = data.progress;
      progressBar.value = progress;
      progressText.innerText = `${progress}%`;
      // Only show progress bar if progress is between 0 and 100
      if (progress > 0 && progress < 100) {
        progressBar.style.display = 'block';
        progressText.style.display = 'block';
      } else {
        progressBar.style.display = 'none';
        progressText.style.display = 'none';
      }
    })
    .catch(error => console.error('Error fetching progress:', error));
}

// Automatically load the file list 
window.onload = function() {
  listFiles();
};
