document.addEventListener('DOMContentLoaded', async function() {


    const i18n = window.i18n; // Assuming i18n is available globally

    const reportTitleElement = document.getElementById('reportTitle');
    const reportDetailsElement = document.getElementById('reportDetails');
    const reportTableContainer = document.getElementById('reportTableContainer');
    const loadingMessage = document.getElementById('loadingMessage');

    // Extract exam_id from URL
    const urlParams = new URLSearchParams(window.location.search);
    const examId = urlParams.get('exam_id');

    if (!examId) {
        reportTableContainer.innerHTML = `<p class="text-danger">${i18n.t('examDetailReport.noExamId') || 'No exam ID provided.'}</p>`;
        if (loadingMessage) loadingMessage.remove();
        return;
    }

    // Function to fetch and display the detailed report
    async function fetchAndDisplayDetailedReport() {
        if (loadingMessage) loadingMessage.style.display = 'block'; // Show loading message
        reportTableContainer.innerHTML = ''; // Clear previous content

        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
            window.location.href = 'login.html';
            return;
        }

        try {
            const response = await fetch(`${window.BACKEND_BASE_URL}/exam-report/${examId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    console.warn('Authentication failed for /exam-report. Redirecting to login.');
                    window.location.href = 'login.html';
                    return;
                }
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to fetch detailed exam report.');
            }

            const report = await response.json();


            // 1. Set Report Title
            if (reportTitleElement) {
                reportTitleElement.textContent = report.report_title || i18n.t('examDetailReport.defaultTitle') || 'Exam Result Report';
            }

            // 2. Display Exam Details
            if (reportDetailsElement) {
                reportDetailsElement.innerHTML = `
                    <p><strong>${i18n.t('examDetailReport.examName') || 'Exam Name'}:</strong> ${report.exam_name || 'N/A'}</p>
                    <p><strong>${i18n.t('examDetailReport.username') || 'Username'}:</strong> ${report.username || 'N/A'}</p>
                    <p><strong>${i18n.t('examDetailReport.examDate') || 'Exam Date'}:</strong> ${new Date(report.exam_date).toLocaleString() || 'N/A'}</p>
                    <p><strong>${i18n.t('examDetailReport.reportGenerated') || 'Report Generated'}:</strong> ${new Date(report.report_generation_date).toLocaleString() || 'N/A'}</p>
                `;
            }

            // 3. Render Report Table
            renderReportTable(report.report_data);

        } catch (error) {
            console.error('Error fetching detailed exam report:', error);
            reportTableContainer.innerHTML = `<p class="text-danger">${i18n.t('examDetailReport.errorLoadingReport') || 'Error loading report:'} ${error.message}</p>`;
        } finally {
            if (loadingMessage) loadingMessage.style.display = 'none'; // Hide loading message
        }
    }

    function renderReportTable(reportData) {
        if (!reportData || reportData.length === 0) {
            reportTableContainer.innerHTML = `<p>${i18n.t('examDetailReport.noReportData') || 'No detailed report data available.'}</p>`;
            return;
        }

        let tableHtml = `<div class="table-responsive"><table class="table table-striped table-bordered table-hover">
            <thead class="table-dark">
                <tr>
                    <th>#</th>
                    <th>${i18n.t('examDetailReport.question') || 'Question'}</th>
                    <th>${i18n.t('examDetailReport.type') || 'Type'}</th>
                    <th>${i18n.t('examDetailReport.difficulty') || 'Difficulty'}</th>
                    <th>${i18n.t('examDetailReport.learningOutcome') || 'Learning Outcome'}</th>
                    <th>${i18n.t('examDetailReport.correctAnswer') || 'Correct Answer'}</th>
                    <th>${i18n.t('examDetailReport.yourAnswer') || 'Your Answer'}</th>
                    <th>${i18n.t('examDetailReport.status') || 'Status'}</th>
                    <th>${i18n.t('examDetailReport.score') || 'Score'}</th>
                </tr>
            </thead>
            <tbody>`;

        reportData.forEach((item, index) => {
            const statusClass = item.is_correct ? 'status-correct' : 'status-incorrect';
            const statusText = item.is_correct ? (i18n.t('examDetailReport.correct') || 'Correct') : (i18n.t('examDetailReport.incorrect') || 'Incorrect');
            const scoreDisplay = `${item.student_mark || 0}/${item.question_mark || 0}`;

            tableHtml += `
                <tr>
                    <td>${index + 1}</td>
                    <td>${item.question_text || 'N/A'}</td>
                    <td>${item.question_type || 'N/A'}</td>
                    <td>${item.difficulty_level_name || 'N/A'}</td>
                    <td>${item.learning_outcome_name || 'N/A'}</td>
                    <td>${item.correct_answer || 'N/A'}</td>
                    <td>${item.student_answer_choice || item.student_answer_text || 'N/A'}</td>
                    <td class="${statusClass}"><strong>${statusText}</strong></td>
                    <td>${scoreDisplay}</td>
                </tr>`;
        });

        tableHtml += `</tbody></table></div>`;
        reportTableContainer.innerHTML = tableHtml;
    }
    
    // Call the function to fetch and display the report when the page loads
    // Ensure i18n is ready before fetching data
    document.addEventListener('i18n:applied', fetchAndDisplayDetailedReport);

});