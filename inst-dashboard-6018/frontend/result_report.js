document.addEventListener('DOMContentLoaded', function() {


    const i18n = window.i18n; // Assuming i18n is available globally

    const resultReportContent = document.querySelector('#examsTable');
    const paginationControls = document.querySelector('#paginationControls');
    const filterButton = document.querySelector('#filterButton');
    const pageSizeSelect = document.querySelector('#pageSize');
    const startDateInput = document.querySelector('#startDate');
    const endDateInput = document.querySelector('#endDate');

    let currentPage = 1;

    if (!resultReportContent) {
        console.error('Could not find #examsTable element for result report.');
        return;
    }

    async function fetchAndDisplayExams(page = 1) {
        currentPage = page;
        const pageSize = pageSizeSelect.value;
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        const offset = (page - 1) * pageSize;

        resultReportContent.innerHTML = `<p>${i18n.t('resultReport.loadingExams') || 'Loading exams...'}</p>`;

        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
            window.location.href = 'login.html';
            return;
        }

        try {
            let url = `${window.BACKEND_BASE_URL}/my-exams?limit=${pageSize}&offset=${offset}`;
            if (startDate) url += `&start_date=${startDate}`;
            if (endDate) url += `&end_date=${endDate}`;
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    // Token expired or invalid, redirect to login
                    console.warn('Authentication failed for /my-exams. Redirecting to login.');
                    window.location.href = 'login.html';
                    return;
                }
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to fetch exams.');
            }

            const data = await response.json();
            renderExams(data.exams);
            renderPagination(data.total_count, pageSize, currentPage);

        } catch (error) {
            console.error('Error fetching exams:', error);
            resultReportContent.innerHTML = `<p class="text-danger">${i18n.t('resultReport.errorLoadingExams') || 'Error loading exams:'} ${error.message}</p>`;
        }
    }

    function renderExams(exams) {
        if (exams.length === 0) {
            resultReportContent.innerHTML = `<p>${i18n.t('resultReport.noExamsFound') || 'No exams found.'}</p>`;
            return;
        }

        let examsHtml = `<div class="table-responsive"><table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>${i18n.t('resultReport.examName') || 'Exam Name'}</th>
                    <th>${i18n.t('resultReport.examId') || 'Exam ID'}</th>
                    <th>${i18n.t('resultReport.duration') || 'Duration'}</th>
                    <th>${i18n.t('resultReport.createdAt') || 'Date'}</th>
                    <th>${i18n.t('resultReport.viewDetails') || 'View Details'}</th>
                </tr>
            </thead>
            <tbody>`;

        exams.forEach(exam => {
            const createdAt = new Date(exam.created_at).toLocaleString();
            examsHtml += `
                <tr>
                    <td>${exam.exam_name || i18n.t('resultReport.untitledExam') || 'Untitled Exam'}</td>
                    <td>${exam.id}</td>
                    <td>${exam.duration_minutes}</td>
                    <td>${createdAt}</td>
                    <td>
                        <button class="btn btn-sm btn-info me-1" onclick="viewExamDetails(${exam.id})" title="${i18n.t('resultReport.view') || 'View'}">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-success me-1" onclick="downloadExam(${exam.id})" title="${i18n.t('resultReport.download') || 'Download'}">
                            <i class="bi bi-download"></i>
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="printExam(${exam.id})" title="${i18n.t('resultReport.print') || 'Print'}">
                            <i class="bi bi-printer"></i>
                        </button>
                    </td>
                </tr>`;
        });

        examsHtml += `</tbody></table></div>`;
        resultReportContent.innerHTML = examsHtml;
    }

    function renderPagination(totalItems, pageSize, currentPage) {
        const totalPages = Math.ceil(totalItems / pageSize);
        paginationControls.innerHTML = '';

        if (totalPages <= 1) return;

        let paginationHtml = '<ul class="pagination">';

        // Previous button
        paginationHtml += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="fetchAndDisplayExams(${currentPage - 1})">&laquo;</a>
        </li>`;

        for (let i = 1; i <= totalPages; i++) {
            paginationHtml += `<li class="page-item ${currentPage === i ? 'active' : ''}">
                <a class="page-link" href="#" onclick="fetchAndDisplayExams(${i})">${i}</a>
            </li>`;
        }

        // Next button
        paginationHtml += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="fetchAndDisplayExams(${currentPage + 1})">&raquo;</a>
        </li>`;

        paginationHtml += '</ul>';
        paginationControls.innerHTML = paginationHtml;
    }

    // Function to fetch the report image from the backend
    async function fetchReportImage(examId) {
        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
            window.location.href = 'login.html';
            return;
        }

        try {
            // Call the new endpoint specifically for report images
            const response = await fetch(`${window.BACKEND_BASE_URL}/exam-report-image/${examId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                }
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Failed to fetch report image: ${response.status} ${response.statusText} - ${errorText}`);
            }

            // The backend now always returns the image file directly from this endpoint
            const imageBlob = await response.blob();
            const imageUrl = URL.createObjectURL(imageBlob);
            return imageUrl;

        } catch (error) {
            console.error('Error fetching report image:', error);
            alert(`${i18n.t('resultReport.errorFetchingReport') || 'Error fetching report image:'} ${error.message}`);
            return null;
        }
    }

    // Function to fetch the report HTML from the backend
    async function fetchReportHtml(examId) {
        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
            window.location.href = 'login.html';
            return;
        }

        try {
            const lang = window.i18n.getLang(); // Get the current language
            const response = await fetch(`${window.BACKEND_BASE_URL}/exam-report-html/${examId}?lang=${lang}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                }
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Failed to fetch report HTML: ${response.status} ${response.statusText} - ${errorText}`);
            }

            const htmlContent = await response.text(); // Get content as text
            return htmlContent;

        } catch (error) {
            console.error('Error fetching report HTML:', error);
            alert(`${i18n.t('resultReport.errorFetchingReport') || 'Error fetching report HTML:'} ${error.message}`);
            return null;
        }
    }

    window.viewExamDetails = function(examId) {
        window.location.href = `exam_detail_report.html?exam_id=${examId}`;
    };

    window.downloadExam = async function(examId) {
        const htmlContent = await fetchReportHtml(examId); // Use the new function
        if (htmlContent) {
            const blob = new Blob([htmlContent], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `exam_report_${examId}.html`; // Change to .html
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    };

    window.printExam = async function(examId) {
        const htmlContent = await fetchReportHtml(examId); // Use the new function
        if (htmlContent) {
            const printWindow = window.open('', '_blank');
            printWindow.document.open();
            printWindow.document.write(htmlContent);
            printWindow.document.close();
            printWindow.onload = () => {
                printWindow.print();
            };
        }
    };

    window.deleteExam = async function(examId) {
        if (!confirm(`${i18n.t('resultReport.confirmDeleteExam') || 'Are you sure you want to delete this exam report?'}`)) {
            return;
        }

        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
            window.location.href = 'login.html';
            return;
        }

        try {
            const response = await fetch(`${window.BACKEND_BASE_URL}/exams/${examId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to delete exam.');
            }

            alert(i18n.t('resultReport.examDeletedSuccessfully') || 'Exam report deleted successfully!');
            fetchAndDisplayExams(currentPage); // Refresh the list

        } catch (error) {
            console.error('Error deleting exam:', error);
            alert(`${i18n.t('resultReport.errorDeletingExam') || 'Error deleting exam:'} ${error.message}`);
        }
    };


    filterButton.addEventListener('click', () => fetchAndDisplayExams(1));
    pageSizeSelect.addEventListener('change', () => fetchAndDisplayExams(1));

    // Call fetchAndDisplayExams only after i18n has been applied
    document.addEventListener('i18n:applied', () => fetchAndDisplayExams(currentPage));
});