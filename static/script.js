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
  
  // Show progress bar when upload starts
  document.getElementById('progressBar').style.display = 'block';
  document.getElementById('progressText').style.display = 'block';

  fetch('/upload', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
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
    console.error('Error:', error);
    document.getElementById('progressBar').style.display = 'none';
    document.getElementById('progressText').style.display = 'none';
    alert('An error occurred during upload');
  });
}

function downloadFile(filename) {
  if (!filename) return;

  // Show progress bar when download starts
  document.getElementById('progressBar').style.display = 'block';
  document.getElementById('progressText').style.display = 'block';

  fetch('/download', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ filename: filename })
  })
  .then(response => response.json())
  .then(data => {
    // Hide progress bar when download completes
    document.getElementById('progressBar').style.display = 'none';
    document.getElementById('progressText').style.display = 'none';
    if (data.error) {
      alert('Error: ' + data.error);
    } else {
      alert(data.message);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    document.getElementById('progressBar').style.display = 'none';
    document.getElementById('progressText').style.display = 'none';
    alert('An error occurred during download');
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
              'txt': 'icons/text-file.png',
              'pdf': 'icons/pdf-file.png',
              'doc': 'icons/word-file.png',
              'docx': 'icons/word-file.png',
              'xls': 'icons/excel-file.png',
              'xlsx': 'icons/excel-file.png',
              'png': 'icons/image-file.png',
              'jpg': 'icons/image-file.png',
              'jpeg': 'icons/image-file.png',
              'gif': 'icons/image-file.png',
              'ppt': 'icons/ppt-file.png',
              'mp3': 'icons/audio-file.png',
              'html': 'icons/html-file.png',
              // Add more mappings as needed
            };

            const icon = document.createElement('img');
            icon.classList.add('file-icon');
            icon.src = iconMapping[extension] || 'icons/default-file.png';
            icon.alt = extension + ' file icon';

            const fileNameSpan = document.createElement('span');
            fileNameSpan.classList.add('file-name');
            fileNameSpan.textContent = file;

            // Create the download button within each file listing
            const downloadButton = document.createElement('button');
            downloadButton.classList.add('download-button');
            downloadButton.textContent = 'icons/download-file.png';
            downloadButton.addEventListener('click', () => {
              downloadFile(file);
            });

            li.appendChild(icon);
            li.appendChild(fileNameSpan);
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

// Optionally, if you have server-side progress tracking:
function fetchProgress() {
  // Assuming a fixed filename for demonstration; adjust as needed for multiple files
  const filename = 'default_file';
  fetch(`/get_progress/${filename}`)
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

// Automatically load the file list and start polling for progress on page load
window.onload = function() {
  listFiles();
  setInterval(fetchProgress, 1000);
};
