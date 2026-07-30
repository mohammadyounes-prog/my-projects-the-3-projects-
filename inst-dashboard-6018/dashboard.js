// Function to parse URL parameters
function getUrlParameter(name) {
    name = name.replace(/[\\\[\\\\]]/g, '\\$&'); // Correctly escape special regex characters [ and ]
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
};

document.addEventListener('DOMContentLoaded', () => {
    console.log('Online Exam Dashboard script loaded. Initializing i18next...');

    const i18n = window.i18next;
    const i18nextHttpBackend = window.i18nextHttpBackend;

    if (!i18n || !i18nextHttpBackend) {
        console.error('i18next or i18nextHttpBackend not found. The script tags in index.html may have failed to load or are blocked.');
        document.body.innerHTML = 'Error: A required translation library failed to load. Please check console for details.';
        return;
    }

    i18n
        .use(i18nextHttpBackend)
        .init({
            lng: 'en',
            fallbackLng: 'en',
            backend: {
                loadPath: './locales/{{lng}}.json',
            },
            interpolation: {
                escapeValue: false
            }
        }, (err, t) => {
            if (err) {
                return console.error('Error initializing i18next:', err);
            }
            console.log('i18next initialized successfully. Running application logic.');
            
            // --- App Initialization ---
            initializeApp();
        });

    function initializeApp() {
        // --- Translation and Content Update Functions ---
        function updateContent() {
            document.querySelectorAll('[data-i18n]').forEach(element => {
                const key = element.getAttribute('data-i18n');
                element.innerHTML = i18n.t(key);
            });
            document.documentElement.lang = i18n.language;
            document.documentElement.dir = i18n.dir(i18n.language);
            if (i18n.dir(i18n.language) === 'rtl') {
                document.body.classList.add('rtl');
            } else {
                document.body.classList.remove('rtl');
            }
        }

        async function updateAllContent() {
            updateContent();
            const activeTab = document.querySelector('.nav-tabs .nav-link.active');
            if (activeTab) {
                const tabId = activeTab.id;
                console.log(`Rendering active tab: ${tabId}`);
                switch (tabId) {
                    case 'summary-tab':
                        renderSummaryDashboard(await fetchDashboardData());
                        break;
                    case 'learning-outcomes-tab':
                        const activeSubTab = document.querySelector('#learningOutcomesSubTabs .nav-link.active');
                        if (activeSubTab) {
                            const subTabId = activeSubTab.id;
                            switch (subTabId) {
                                case 'exam-lo-tab':
                                    const selectedExamId = document.getElementById('lo-exam-select').value;
                                    if (selectedExamId) {
                                        document.getElementById('exam-lo-content').innerHTML = `<p>${i18n.t('loading_exam_lo')}</p>`;
                                        renderExamLearningOutcomes(await fetchExamLearningOutcomesByExamData(selectedExamId));
                                    } else {
                                        document.getElementById('exam-lo-content').innerHTML = `<p>${i18n.t('select_exam')}</p>`;
                                    }
                                    break;
                                case 'student-lo-tab':
                                    document.getElementById('student-lo-content').innerHTML = `<p>${i18n.t('loading_student_lo')}</p>`;
                                    // TODO: Implement fetch and render for Student Learning Outcomes
                                    break;
                                case 'student-total-lo-tab':
                                    document.getElementById('student-total-lo-content').innerHTML = `<p>${i18n.t('loading_total_lo')}</p>`;
                                    // TODO: Implement fetch and render for Student Total Learning Outcomes
                                    break;
                                case 'achievement-report-tab':
                                    document.getElementById('achievement-report-content').innerHTML = `<p>${i18n.t('loading_achievement_report')}</p>`;
                                    // TODO: Implement fetch and render for Achievement Report
                                    break;
                            }
                        } else {
                            const firstSubTabButton = document.getElementById('exam-lo-tab');
                            if (firstSubTabButton) {
                                const bsTab = new bootstrap.Tab(firstSubTabButton);
                                bsTab.show();
                            }
                            const selectedExamId = document.getElementById('lo-exam-select').value;
                            if (selectedExamId) {
                                document.getElementById('exam-lo-content').innerHTML = `<p>${i18n.t('loading_exam_lo')}</p>`;
                                renderExamLearningOutcomes(await fetchExamLearningOutcomesByExamData(selectedExamId));
                            } else {
                                document.getElementById('exam-lo-content').innerHTML = `<p>${i18n.t('select_exam')}</p>`;
                            }
                        }
                        break;
                    case 'exams-results-tab':
                        document.getElementById('exams-results-content').innerHTML = `<p>${i18n.t('loading_results')}</p>`;
                        renderExamsResultsReport(await fetchExamsResultsData(60, 12, null));
                        break;
                }
            }
        }
        
        // --- Event Listeners ---
        i18n.on('languageChanged', updateAllContent);
        document.getElementById('lang-en').addEventListener('click', () => i18n.changeLanguage('en'));
        document.getElementById('lang-ar').addEventListener('click', () => i18n.changeLanguage('ar'));
        
        // Main tabs
        document.getElementById('summary-tab').addEventListener('shown.bs.tab', async () => renderSummaryDashboard(await fetchDashboardData()));
        
        document.getElementById('learning-outcomes-tab').addEventListener('shown.bs.tab', async () => {
            await populateCourseDropdown();
            // This will trigger populateExamDropdown and populateFilterDropdowns via the course select change event
            document.getElementById('lo-course-select').dispatchEvent(new Event('change'));

            const firstSubTabButton = document.getElementById('exam-lo-tab');
            if (firstSubTabButton) {
                const bsTab = new bootstrap.Tab(firstSubTabButton);
                bsTab.show();
            }
            // The content will be loaded by the exam-lo-tab's shown.bs.tab listener
        });

        document.getElementById('exams-results-tab').addEventListener('shown.bs.tab', async () => {
            document.getElementById('exams-results-content').innerHTML = `<p>${i18n.t('loading_results')}</p>`;
            renderExamsResultsReport(await fetchExamsResultsData(60, 12, null));
        });

        // Sub-tabs for Learning Outcomes
        document.getElementById('exam-lo-tab').addEventListener('shown.bs.tab', async () => {
            const selectedExamId = document.getElementById('lo-exam-select').value;
            if (selectedExamId) {
                document.getElementById('exam-lo-content').innerHTML = `<p>${i18n.t('loading_exam_lo')}</p>`;
                renderExamLearningOutcomes(await fetchExamLearningOutcomesByExamData(selectedExamId));
            } else {
                document.getElementById('exam-lo-content').innerHTML = `<p>${i18n.t('select_exam')}</p>`;
            }
        });
        document.getElementById('student-lo-tab').addEventListener('shown.bs.tab', async () => {
            document.getElementById('student-lo-content').innerHTML = `<p>${i18n.t('loading_student_lo')}</p>`;
            // TODO: Implement fetch and render for Student Learning Outcomes
        });
        document.getElementById('student-total-lo-tab').addEventListener('shown.bs.tab', async () => {
            document.getElementById('student-total-lo-content').innerHTML = `<p>${i18n.t('loading_total_lo')}</p>`;
            // TODO: Implement fetch and render for Student Total Learning Outcomes
        });
        document.getElementById('achievement-report-tab').addEventListener('shown.bs.tab', async () => {
            document.getElementById('achievement-report-content').innerHTML = `<p>${i18n.t('loading_achievement_report')}</p>`;
            // TODO: Implement fetch and render for Achievement Report
        });

        // Event listeners for filter dropdowns
        document.getElementById('lo-course-select').addEventListener('change', async (event) => {
            const selectedCourseId = event.target.value;
            await populateExamDropdown(selectedCourseId);
            await populateFilterDropdowns(selectedCourseId);

            // Re-render LO content if exam is selected
            const selectedExamId = document.getElementById('lo-exam-select').value;
            if (selectedExamId) {
                document.getElementById('exam-lo-content').innerHTML = `<p>${i18n.t('loading_exam_lo')}</p>`;
                renderExamLearningOutcomes(await fetchExamLearningOutcomesByExamData(selectedExamId));
            } else {
                document.getElementById('exam-lo-content').innerHTML = `<p>${i18n.t('select_exam')}</p>`;
            }
        });

        document.getElementById('lo-exam-select').addEventListener('change', async (event) => {
            const selectedExamId = event.target.value;
            if (selectedExamId) {
                document.getElementById('exam-lo-content').innerHTML = `<p>${i18n.t('loading_exam_lo')}</p>`;
                renderExamLearningOutcomes(await fetchExamLearningOutcomesByExamData(selectedExamId));
            } else {
                document.getElementById('exam-lo-content').innerHTML = `<p>${i18n.t('select_exam')}</p>`;
            }
        });

        // Event listener for dynamically created filter dropdowns
        document.getElementById('lo-filter-dropdowns-container').addEventListener('change', async (event) => {
            if (event.target.classList.contains('filter-select')) {
                const selectedCourseId = document.getElementById('lo-course-select').value;
                const filterParams = {};
                document.querySelectorAll('#lo-filter-dropdowns-container .filter-select').forEach(dropdown => {
                    if (dropdown.value) {
                        // Store the value using the dropdown's ID (which is derived from the filter name)
                        filterParams[dropdown.id.replace('filter-select-', '')] = dropdown.value; 
                    }
                });
                await populateExamDropdown(selectedCourseId, filterParams); // Re-populate exams based on filters

                const selectedExamId = document.getElementById('lo-exam-select').value;
                if (selectedExamId) {
                    document.getElementById('exam-lo-content').innerHTML = `<p>${i18n.t('loading_exam_lo')}</p>`;
                    renderExamLearningOutcomes(await fetchExamLearningOutcomesByExamData(selectedExamId));
                } else {
                    document.getElementById('exam-lo-content').innerHTML = `<p>${i18n.t('select_exam')}</p>`;
                }
            }
        });


        // --- Data Fetching & Rendering Functions ---
        async function fetchDashboardData() {
             try {
                let token = "debug_token"; // TEMPORARY: Use a dummy token since authentication is bypassed in backend

                const response = await fetch('http://questai.examforall.com:8000/api/v1/summary', { headers: { 'Authorization': `Bearer ${token}` }}});
                if (!response.ok) return { error: (response.status === 401 || response.status === 403 ? 'unauthorized_access' : 'error_fetching_data'), statusText: response.statusText };
                return await response.json();
            } catch (error) {
                return { error: 'network_error', message: error.message };
            }
        }
        function renderSummaryDashboard(data) {
            const summaryContent = document.getElementById('summary-content');
            if (!data || data.error) {
                const errorKey = data?.error || 'no_summary_data';
                const errorMessage = data?.message || data?.statusText || '';
                summaryContent.innerHTML = `<p>${i18n.t(errorKey)} ${errorMessage}</p>`;
                return;
            }
            summaryContent.innerHTML = `
                <div class="summary-cards">
                    <div class="card"><div class="card-body"><h2 class="card-title">${i18n.t('total_students')}</h2><p class="card-text">${data.total_students}</p></div></div>
                    <div class="card"><div class="card-body"><h2 class="card-title">${i18n.t('total_exams')}</h2><p class="card-text">${data.total_exams}</p></div></div>
                </div>
                <div class="section mt-4"><h2>${i18n.t('latest_exams')}</h2><ul id="latest-exams-list" class="list-group"></ul></div>
                <div class="section mt-4">
                    <h2>${i18n.t('student_performance_summary')}</h2>
                    <table id="student-performance-table" class="table table-striped">
                        <thead><tr><th>${i18n.t('student_name')}</th><th>${i18n.t('total_exams')}</th><th>${i18n.t('average_score')}</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>`;
            const latestExamsList = document.getElementById('latest-exams-list');
            if (latestExamsList && data.latest_exams) {
                data.latest_exams.forEach(exam => {
                    const li = document.createElement('li');
                    li.className = "list-group-item";
                    li.textContent = `${exam.name} (ID: ${exam.id}) - Date: ${new Date(exam.date).toLocaleDateString()}`;
                    latestExamsList.appendChild(li);
                });
            }
            const studentPerformanceTableBody = document.querySelector('#student-performance-table tbody');
            if (studentPerformanceTableBody && data.student_performance_summary) {
                data.student_performance_summary.forEach(summary => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `<td>${summary.student_name}</td><td>${summary.total_exams}</td><td>${summary.average_score.toFixed(2)}</td>`;
                    studentPerformanceTableBody.appendChild(tr);
                });
            }
        }
        
        async function fetchLearningOutcomesData(courseId) {
            try {
               let token = "debug_token"; // TEMPORARY: Use a dummy token since authentication is bypassed in backend

               const response = await fetch(`http://questai.examforall.com:8000/api/v1/reports/learning-outcomes/${courseId}`, { headers: { 'Authorization': `Bearer ${token}` }}});
               if (!response.ok) return { error: (response.status === 401 || response.status === 403 ? 'unauthorized_access_lo' : 'error_fetching_lo'), statusText: response.statusText };
               return (await response.json()).data;
           } catch (error) {
               return { error: 'network_error_lo', message: error.message };
           }
       }
        // Placeholder render functions for the original LO report, which is now replaced by sub-tabs.
        // This function will likely be removed or refactored.
        function renderLearningOutcomesReport(reportData) {
             const learningOutcomesContent = document.getElementById('learning-outcomes-content');
             learningOutcomesContent.innerHTML = `<p>${i18n.t('select_lo_subtab')}</p>`;
        }


        function renderExamLearningOutcomes(data) {
            // Debugging logs
            console.log('Rendering Exam Learning Outcomes with data:', data);
            console.log('i18n object:', i18n);
            if (typeof i18n.t !== 'function') {
                console.error('i18n.t is not a function!');
            }

            const contentDiv = document.getElementById('exam-lo-content');
            if (!data || data.error || !data.length) {
                const errorKey = data?.error || 'no_lo_data'; // Reusing 'no_lo_data' for now, can be more specific
                const errorMessage = data?.message || data?.statusText || '';
                contentDiv.innerHTML = `<p>${i18n.t(errorKey)} ${errorMessage}</p>`;
                return;
            }
            
            let tableHtml = `<table class="table table-bordered table-striped table-sm mt-3"><thead><tr>`;
            
            // Pre-calculate translated strings
            const translated_question_id = i18n.t('question_id');
            const translated_question_title = i18n.t('question_title');
            const translated_question_mark = i18n.t('question_mark');
            const translated_objective = i18n.t('objective');

            tableHtml += `<th>${translated_question_id}</th>`;
            tableHtml += `<th>${translated_question_title}</th>`;
            tableHtml += `<th>${translated_question_mark}</th>`;
            tableHtml += `<th>${translated_objective}</th>`;

            // Add student result columns if student data is present (i.e., student_id was used in fetch)
            if (data[0] && data[0].hasOwnProperty('currentMark')) { // Added data[0] check
                const translated_student_mark = i18n.t('student_mark');
                const translated_student_answer = i18n.t('student_answer');
                const translated_answer_status = i18n.t('answer_status');
                const translated_answer_type = i18n.t('answer_type');

                tableHtml += `<th>${translated_student_mark}</th>`;
                tableHtml += `<th>${translated_student_answer}</th>`;
                tableHtml += `<th>${translated_answer_status}</th>`;
                tableHtml += `<th>${translated_answer_type}</th>`;
            }
            tableHtml += `</tr></thead><tbody>`;

            data.forEach(q => {
                tableHtml += `<tr>`;
                tableHtml += `<td>${q.id}</td>`;
                tableHtml += `<td>${q.question}</td>`;
                tableHtml += `<td>${q.examDataMark !== null ? q.examDataMark.toFixed(2) : i18n.t('not_applicable')}</td>`;
                tableHtml += `<td>${q.objectiveName || i18n.t('not_applicable')}</td>`;
                if (q.hasOwnProperty('currentMark')) {
                    tableHtml += `<td>${q.currentMark !== null ? q.currentMark.toFixed(2) : i18n.t('not_applicable')}</td>`;
                    tableHtml += `<td>${q.answer || i18n.t('not_applicable')}</td>`;
                    tableHtml += `<td>${q.status || i18n.t('not_applicable')}</td>`;
                    tableHtml += `<td>${q.answerType || i18n.t('not_applicable')}</td>`;
                }
                tableHtml += `</tr>`;
            });

            tableHtml += `</tbody></table>`;
            contentDiv.innerHTML = tableHtml;
        }
        
        async function fetchExamsResultsData(studentId, courseId, majorId) {
            try {
                let token = "debug_token"; // TEMPORARY: Use a dummy token since authentication is bypassed in backend

                let url = new URL('http://questai.examforall.com:8000/api/v1/reports/exams-results');
                if (studentId) url.searchParams.append('student_id', studentId);
                if (courseId) url.searchParams.append('course_id', courseId);
                if (majorId) url.searchParams.append('major_id', majorId);
                const response = await fetch(url.toString(), { headers: { 'Authorization': `Bearer ${token}` }}});
                if (!response.ok) return { error: (response.status === 401 || response.status === 403 ? 'unauthorized_access_er' : 'error_fetching_er'), statusText: response.statusText };
                return (await response.json()).data;
            } catch (error) {
                return { error: 'network_error_er', message: error.message };
            }
        }

        async function fetchExamLearningOutcomesByExamData(examId, studentId = null) {
            try {
                let token = "debug_token"; // TEMPORARY: Use a dummy token since authentication is bypassed in backend
                
                let url = new URL(`http://questai.examforall.com:8000/api/v1/reports/exam-learning-outcomes-by-exam/${examId}`);
                if (studentId) url.searchParams.append('student_id', studentId);

                const response = await fetch(url.toString(), { headers: { 'Authorization': `Bearer ${token}` }}});
                if (!response.ok) {
                    return { error: (response.status === 401 || response.status === 403 ? 'unauthorized_access' : 'error_fetching_data'), statusText: response.statusText };
                }
                return (await response.json()).data;
            } catch (error) {
                return { error: 'network_error', message: error.message };
            }
        }

        async function populateCourseDropdown() {
            try {
                const response = await fetch('http://questai.examforall.com:8000/api/v1/lookup/university_courses');
                if (!response.ok) throw new Error('Failed to fetch courses');
                const courses = await response.json();
                const dropdown = document.getElementById('lo-course-select');
                dropdown.innerHTML = '<option value="">-- ' + i18n.t('select_course_option') + ' --</option>';
                courses.forEach(course => {
                    const option = document.createElement('option');
                    option.value = course.id;
                    option.textContent = course.name;
                    dropdown.appendChild(option);
                });
            } catch (error) {
                console.error('Error populating course dropdown:', error);
                document.getElementById('lo-course-select').innerHTML = `<option value="">-- ${i18n.t('error_loading_courses')} --</option>`;
            }
        }

        async function populateExamDropdown(courseId, filterParams = {}) {
            const examDropdown = document.getElementById('lo-exam-select');
            examDropdown.innerHTML = '<option value="">-- ' + i18n.t('select_exam_option') + ' --</option>';
            examDropdown.disabled = true;

            if (!courseId) {
                return;
            }

            try {
                // Fetch exams for the selected course, potentially filtered by other parameters
                let url = new URL(`http://questai.examforall.com:8000/api/v1/lookup/exam-names-all`); // Using exam-names-all for now
                for (const key in filterParams) {
                    url.searchParams.append(key, filterParams[key]);
                }
                
                const response = await fetch(url.toString());
                if (!response.ok) throw new Error('Failed to fetch exams');
                const exams = await response.json();
                
                exams.forEach(exam => {
                    const option = document.createElement('option');
                    option.value = exam.id;
                    option.textContent = exam.name;
                    examDropdown.appendChild(option);
                });
                examDropdown.disabled = false;
            } catch (error) {
                console.error('Error populating exam dropdown:', error);
                examDropdown.innerHTML = `<option value="">-- ${i18n.t('error_loading_exams')} --</option>`;
            }
        }

        async function populateFilterDropdowns(courseId) {
            const container = document.getElementById('lo-filter-dropdowns-container');
            container.innerHTML = ''; // Clear previous filters

            if (!courseId) {
                return;
            }

            try {
                const response = await fetch(`http://questai.examforall.com:8000/api/v1/lookup/course-filter-values?course_id=${courseId}`); // New endpoint
                if (!response.ok) throw new Error('Failed to fetch filter values');
                const filters = await response.json();

                if (filters && filters.length > 0) {
                    filters.forEach(filter => {
                        const colDiv = document.createElement('div');
                        colDiv.className = 'col-md-3'; // Adjust column size as needed

                        const label = document.createElement('label');
                        label.htmlFor = `filter-select-${filter.name.toLowerCase().replace(/\s/g, '-')}`;
                        label.className = 'form-label';
                        label.textContent = filter.name; // Use filter name as label

                        const select = document.createElement('select');
                        select.className = 'form-select filter-select';
                        select.id = `filter-select-${filter.name.toLowerCase().replace(/\s/g, '-')}`;
                        
                        const defaultOption = document.createElement('option');
                        defaultOption.value = '';
                        defaultOption.textContent = `-- Select ${filter.name} --`; // TODO: Translate this
                        select.appendChild(defaultOption);

                        filter.values.forEach(value => {
                            const option = document.createElement('option');
                            option.value = value;
                            option.textContent = value;
                            select.appendChild(option);
                        });

                        colDiv.appendChild(label);
                        colDiv.appendChild(select);
                        container.appendChild(colDiv);
                    });
                }
            } catch (error) {
                console.error('Error populating filter dropdowns:', error);
                container.innerHTML = `<p class="text-danger">${i18n.t('error_loading_filters')}</p>`;
            }
        }

        function renderExamsResultsReport(reportData) {
            const examsResultsContent = document.getElementById('exams-results-content');
            if (!reportData || reportData.error) {
                const errorKey = reportData?.error || 'no_er_data';
                 const errorMessage = reportData?.message || '';
                examsResultsContent.innerHTML = `<p>${i18n.t(errorKey)} ${errorMessage}</p>`;
                return;
            }
            let tableBody = '';
            reportData.forEach(entry => {
                tableBody += `
                    <tr>
                        <td>${entry.studentName}</td><td>${entry.courseName}</td><td>${entry.examName}</td>
                        <td>${entry.examTotalMark.toFixed(2)}</td><td>${entry.successMark.toFixed(2)}</td>
                        <td>${entry.studentExamMark.toFixed(2)}</td><td>${entry.studentExamStatus}</td><td>${entry.objectiveCount}</td>
                    </tr>`;
            });
            examsResultsContent.innerHTML = `
                <h2>${i18n.t('exams_results_report')}</h2>
                <div class="table-responsive"><table class="table table-bordered table-striped table-sm">
                    <thead><tr>
                        <th>${i18n.t('student_name')}</th><th>${i18n.t('course_name')}</th><th>${i18n.t('exam_name')}</th>
                        <th>${i18n.t('total_mark')}</th><th>${i18n.t('success_mark')}</th><th>${i18n.t('student_mark')}</th>
                        <th>${i18n.t('status')}</th><th>${i18n.t('objective_count')}</th>
                    </tr></thead>
                    <tbody>${tableBody}</tbody>
                </table></div>`;
        }
        
        // Placeholder render functions for the new sub-tabs
        function renderStudentLearningOutcomes(data) {
            const contentDiv = document.getElementById('student-lo-content');
            if (!data) { /* Handle no data */ }
            contentDiv.innerHTML = `<p>${i18n.t('student_learning_outcomes_tab')} Content (TODO: Fetch and render data)</p>`;
        }

        function renderStudentTotalLearningOutcomes(data) {
            const contentDiv = document.getElementById('student-total-lo-content');
            if (!data) { /* Handle no data */ }
            contentDiv.innerHTML = `<p>${i18n.t('student_total_learning_outcomes_tab')} Content (TODO: Fetch and render data)</p>`;
        }

        function renderAchievementReport(data) {
            const contentDiv = document.getElementById('achievement-report-content');
            if (!data) { /* Handle no data */ }
            contentDiv.innerHTML = `<p>${i18n.t('achievement_report_tab')} Content (TODO: Fetch and render data)</p>`;
        }


        // --- Initial Load ---
        updateAllContent();
    }
});
