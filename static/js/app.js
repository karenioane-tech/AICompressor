// =====================================================
// ELEMENTS
// =====================================================

const fileInput = document.getElementById("fileInput");
const browseButton = document.getElementById("browseButton");
const dropZone = document.getElementById("dropZone");

const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");
const removeFile = document.getElementById("removeFile");

const compressForm = document.getElementById("compressForm");
const compressButton = document.getElementById("compressButton");

const loading = document.getElementById("loading");
const result = document.getElementById("result");

const resetButton = document.getElementById("resetButton");
const quality = document.getElementById("quality");

const previewContainer =
    document.getElementById("previewContainer");

const imagePreview =
    document.getElementById("imagePreview");

const historyList =
    document.getElementById("historyList");

const clearHistory =
    document.getElementById("clearHistory");


// =====================================================
// FORMAT FILE SIZE
// =====================================================

function formatSize(bytes) {

    if (bytes === 0) {
        return "0 Bytes";
    }

    const units = [
        "Bytes",
        "KB",
        "MB",
        "GB"
    ];

    const index = Math.floor(
        Math.log(bytes) / Math.log(1024)
    );

    return (
        (bytes / Math.pow(1024, index)).toFixed(2)
        + " "
        + units[index]
    );
}


// =====================================================
// SHOW SELECTED FILE
// =====================================================

function showFile(file) {

    if (!file) {
        return;
    }

    fileName.textContent = file.name;

    fileSize.textContent =
        formatSize(file.size);

    fileInfo.classList.remove("hidden");

    compressButton.disabled = false;


    // Image preview
    if (file.type.startsWith("image/")) {

        const reader = new FileReader();

        reader.onload = function(event) {

            imagePreview.src =
                event.target.result;

            previewContainer.classList.remove(
                "hidden"
            );
        };

        reader.readAsDataURL(file);

    } else {

        previewContainer.classList.add(
            "hidden"
        );
    }
}


// =====================================================
// BROWSE BUTTON
// =====================================================

browseButton.addEventListener(
    "click",
    function() {

        fileInput.click();

    }
);


// =====================================================
// FILE INPUT
// =====================================================

fileInput.addEventListener(
    "change",
    function() {

        const file =
            fileInput.files[0];

        showFile(file);

    }
);


// =====================================================
// DRAG OVER
// =====================================================

dropZone.addEventListener(
    "dragover",
    function(event) {

        event.preventDefault();

        dropZone.classList.add(
            "dragging"
        );

    }
);


// =====================================================
// DRAG LEAVE
// =====================================================

dropZone.addEventListener(
    "dragleave",
    function() {

        dropZone.classList.remove(
            "dragging"
        );

    }
);


// =====================================================
// DROP FILE
// =====================================================

dropZone.addEventListener(
    "drop",
    function(event) {

        event.preventDefault();

        dropZone.classList.remove(
            "dragging"
        );

        const files =
            event.dataTransfer.files;

        if (!files || files.length === 0) {
            return;
        }

        const file = files[0];

        try {

            fileInput.files = files;

        } catch (error) {

            console.warn(
                "Could not assign dropped file.",
                error
            );

        }

        showFile(file);

    }
);


// =====================================================
// REMOVE FILE
// =====================================================

removeFile.addEventListener(
    "click",
    function() {

        fileInput.value = "";

        fileInfo.classList.add(
            "hidden"
        );

        previewContainer.classList.add(
            "hidden"
        );

        imagePreview.src = "";

        compressButton.disabled = true;

    }
);


// =====================================================
// COMPRESS FILE
// =====================================================

compressForm.addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();

        const file =
            fileInput.files[0];

        if (!file) {

            alert("Please select a file first.");

            return;
        }


        // Create form data
        const formData =
            new FormData();

        formData.append(
            "file",
            file
        );

        formData.append(
            "quality",
            quality.value
        );


        // Show loading
        compressButton.disabled = true;

        loading.classList.remove(
            "hidden"
        );

        result.classList.add(
            "hidden"
        );


        try {

            const response =
                await fetch(
                    "/compress",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const data =
                await response.json();


            // Server error
            if (!response.ok || !data.success) {

                alert(
                    data.error ||
                    "Compression failed."
                );

                return;
            }


            // =================================================
            // DISPLAY RESULTS
            // =================================================

            document.getElementById(
                "originalSize"
            ).textContent =
                formatSize(
                    data.original_size
                );


            document.getElementById(
                "compressedSize"
            ).textContent =
                formatSize(
                    data.compressed_size
                );


            document.getElementById(
                "savedPercentage"
            ).textContent =
                data.saved_percentage + "%";


            document.getElementById(
                "compressionRatio"
            ).textContent =
                data.compression_ratio + "×";


            document.getElementById(
                "engine"
            ).textContent =
                data.engine;


            // =================================================
            // ENGINE DESCRIPTION
            // =================================================

            const engineDescription =
                document.getElementById(
                    "engineDescription"
                );


            if (engineDescription) {

                if (
                    data.engine.includes("K-Means")
                ) {

                    engineDescription.textContent =
                        "AI analyzes image colors and reduces the color palette using K-Means clustering.";

                }

                else if (
                    data.engine.includes("Gzip")
                ) {

                    engineDescription.textContent =
                        "DEFLATE identifies repeated data patterns and stores them more efficiently.";

                }

                else if (
                    data.engine.includes("PDF")
                ) {

                    engineDescription.textContent =
                        "PDF content streams are optimized to reduce unnecessary data while preserving the document.";

                }

                else {

                    engineDescription.textContent =
                        "";

                }

            }


            // =================================================
            // DOWNLOAD
            // =================================================

            const downloadButton =
                document.getElementById(
                    "downloadButton"
                );

            downloadButton.href =
                data.download_url;


            // =================================================
            // SHOW RESULT
            // =================================================

            result.classList.remove(
                "hidden"
            );


            // =================================================
            // SAVE HISTORY
            // =================================================

            saveHistory({

                filename:
                    data.original_filename,

                saved:
                    data.saved_percentage,

                date:
                    new Date().toISOString()

            });

        }


        catch (error) {

            console.error(
                "Compression error:",
                error
            );

            alert(
                "Something went wrong while communicating with the server."
            );

        }


        finally {

            loading.classList.add(
                "hidden"
            );

            compressButton.disabled = false;

        }

    }
);


// =====================================================
// RESET
// =====================================================

resetButton.addEventListener(
    "click",
    function() {

        fileInput.value = "";

        fileInfo.classList.add(
            "hidden"
        );

        previewContainer.classList.add(
            "hidden"
        );

        imagePreview.src = "";

        result.classList.add(
            "hidden"
        );

        compressButton.disabled = true;

    }
);


// =====================================================
// HISTORY
// =====================================================

function getHistory() {

    try {

        return JSON.parse(
            localStorage.getItem(
                "compressionHistory"
            ) || "[]"
        );

    }

    catch (error) {

        console.warn(
            "Could not read compression history.",
            error
        );

        return [];

    }
}


// =====================================================
// SAVE HISTORY
// =====================================================

function saveHistory(item) {

    const history =
        getHistory();

    history.unshift(item);

    const limitedHistory =
        history.slice(0, 10);

    localStorage.setItem(
        "compressionHistory",
        JSON.stringify(
            limitedHistory
        )
    );

    displayHistory();
}


// =====================================================
// DISPLAY HISTORY
// =====================================================

function displayHistory() {

    if (!historyList) {
        return;
    }

    const history =
        getHistory();


    if (history.length === 0) {

        historyList.innerHTML =
            "<p>No compression history yet.</p>";

        return;
    }


    historyList.innerHTML =
        history.map(function(item) {

            return `
                <div class="history-item">

                    <strong>
                        ${escapeHTML(item.filename)}
                    </strong>

                    <span>
                        ${item.saved}% saved
                    </span>

                </div>
            `;

        }).join("");
}


// =====================================================
// BASIC HTML ESCAPING
// =====================================================

function escapeHTML(value) {

    const div =
        document.createElement("div");

    div.textContent =
        value;

    return div.innerHTML;
}


// =====================================================
// CLEAR HISTORY
// =====================================================

if (clearHistory) {

    clearHistory.addEventListener(
        "click",
        function() {

            localStorage.removeItem(
                "compressionHistory"
            );

            displayHistory();

        }
    );

}


// =====================================================
// INITIALIZE
// =====================================================

displayHistory();