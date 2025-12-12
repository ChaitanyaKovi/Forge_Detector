const dropArea = document.getElementById('drop-area');
const fileElem = document.getElementById('fileElem');
const previewContainer = document.getElementById('preview-container');
const previewImage = document.getElementById('preview-image');
const removeBtn = document.getElementById('remove-btn');
const analyzeBtn = document.getElementById('analyze-btn');
const resultCard = document.getElementById('result-card');
const resultIcon = document.getElementById('result-icon');
const resultTitle = document.getElementById('result-title');
const resultDesc = document.getElementById('result-description');
const meterFill = document.getElementById('meter-fill');
const confidenceText = document.getElementById('confidence-text');
const btnText = document.querySelector('.btn-text');
const loader = document.querySelector('.loader');

let selectedFile = null;

// Prevent default drag behaviors
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Highlight drop area when item is dragged over it
['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
    dropArea.classList.add('highlight');
}

function unhighlight(e) {
    dropArea.classList.remove('highlight');
}

// Handle dropped files
dropArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

// Handle click to browse
dropArea.addEventListener('click', () => {
    fileElem.click();
});

fileElem.addEventListener('change', function() {
    handleFiles(this.files);
});

function handleFiles(files) {
    if (files.length > 0) {
        selectedFile = files[0];
        if (selectedFile.type.startsWith('image/')) {
            showPreview(selectedFile);
        } else {
            alert("Please upload an image file.");
        }
    }
}

function showPreview(file) {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = function() {
        previewImage.src = reader.result;
        dropArea.classList.add('hidden');
        previewContainer.classList.remove('hidden');
        analyzeBtn.disabled = false;
        resultCard.classList.add('hidden');
    }
}

removeBtn.addEventListener('click', () => {
    selectedFile = null;
    fileElem.value = '';
    previewImage.src = '';
    previewContainer.classList.add('hidden');
    dropArea.classList.remove('hidden');
    analyzeBtn.disabled = true;
    resultCard.classList.add('hidden');
});

analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    // UI Loading State
    analyzeBtn.disabled = true;
    btnText.textContent = "Analyzing...";
    loader.classList.remove('hidden');
    resultCard.classList.add('hidden');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (response.ok) {
            showResult(data);
        } else {
            alert('Error: ' + (data.error || 'Something went wrong'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to connect to the server. Make sure the customized backend is running.');
    } finally {
        // Reset Button
        btnText.textContent = "Analyze Signature";
        loader.classList.add('hidden');
        analyzeBtn.disabled = false;
    }
});

function showResult(data) {
    resultCard.classList.remove('hidden');
    
    // Reset classes
    resultCard.classList.remove('success', 'danger');
    resultIcon.classList.remove('fa-check-circle', 'fa-times-circle');

    const isReal = data.result === 'Real';
    const percent = parseFloat(data.confidence).toFixed(1) + '%';
    
    // Sanitize confidence for width (0-100)
    const width = parseFloat(data.confidence);

    if (isReal) {
        resultCard.classList.add('success');
        resultIcon.classList.add('fa-check-circle');
        resultTitle.textContent = "Authentic Signature";
        resultDesc.textContent = "The system has verified this signature as authentic with high confidence.";
    } else {
        resultCard.classList.add('danger');
        resultIcon.classList.add('fa-exclamation-triangle');
        resultTitle.textContent = "Potential Forgery";
        resultDesc.textContent = "The system detected anomalies suggesting this signature may be forged.";
    }

    meterFill.style.width = '0%';
    setTimeout(() => {
        meterFill.style.width = percent;
    }, 100);
    
    confidenceText.textContent = `${percent} Confidence`;
}
