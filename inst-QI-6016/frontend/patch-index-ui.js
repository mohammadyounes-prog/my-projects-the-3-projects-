const fs = require('fs');
const path = 'frontend/index.html';
const bak = 'frontend/index.html.bak';
let src = fs.readFileSync(path, 'utf8');
fs.writeFileSync(bak, src);

// 1) Toast container before </body>
if (!src.includes('<div id="toastContainer"')) {
  src = src.replace(/<\/body>/, \\`    <!-- Toast Container (RTL/LTR aware by logical end positioning) -->\n    <div id="toastContainer" class="position-fixed top-0 end-0 p-3" style="z-index: 1100;"></div>\n</body>\\`);
}

// 2) showToast helper after DOMContentLoaded start
if (!src.includes('function showToast(')) {
  src = src.replace("document.addEventListener('DOMContentLoaded', function() {",
    "document.addEventListener('DOMContentLoaded', function() {\n            // Simple toast helper (i18n-aware, RTL-safe)\n            function showToast(type, message) {\n                try {\n                    const text = (window.i18n && window.i18n.t && typeof message === 'string') ? (window.i18n.t(message) || message) : message;\n                    const bg = type === 'success' ? 'bg-success' : (type === 'warning' ? 'bg-warning text-dark' : 'bg-danger');\n                    const container = document.getElementById('toastContainer');\n                    const wrapper = document.createElement('div');\n                    wrapper.className = \\`toast align-items-center text-white \\${bg} border-0\\`;\n                    wrapper.setAttribute('role', 'alert');\n                    wrapper.setAttribute('aria-live', 'assertive');\n                    wrapper.setAttribute('aria-atomic', 'true');\n                    wrapper.innerHTML = \\`\n                        <div class=\"d-flex\">\n                          <div class=\"toast-body\">\\\${text}</div>\n                          <button type=\"button\" class=\"btn-close btn-close-white me-2 m-auto\" data-bs-dismiss=\"toast\" aria-label=\"Close\"></button>\n                        </div>\\`;\n                    container.appendChild(wrapper);\n                    const t = new bootstrap.Toast(wrapper, { delay: 3000 });\n                    t.show();\n                    wrapper.addEventListener('hidden.bs.toast', () => wrapper.remove());\n                } catch (e) { console.warn('Toast error', e); }\n            }\n" );
}

// 3) Batch render
src = src.replace("questionsDisplay.innerHTML = ''; // Clear previous questions", "let html = ''; // buffer for batch render");
src = src.replace(/questionDiv\.innerHTML = \\\`/g, 'html += \\`');
src = src.replace(/questionsDisplay\.appendChild\(questionDiv\);/g, '');
src = src.replace(/questionsDisplay\.innerHTML = \\`<p>No questions generated yet\.<\/p>\\`;/, "questionsDisplay.innerHTML = \\`<p>\\${(window.i18n && window.i18n.t && window.i18n.t('generate.noQuestions')) || 'No questions generated yet.'}</p>\\`;");
if (!src.includes('questionsDisplay.innerHTML = html;')) {
  src = src.replace('renderPaginationControls(generatedQuestions.length, page, ITEMS_PER_PAGE);', 'questionsDisplay.innerHTML = html;\n                renderPaginationControls(generatedQuestions.length, page, ITEMS_PER_PAGE);');
}

// 4) Inline validation feedback
src = src.replace(/field\.classList\.add\('is-invalid'\);\s*isValid = false;/, \\`field.classList.add('is-invalid');
                        let fb = field.nextElementSibling;
                        if (!fb || !fb.classList || !fb.classList.contains('invalid-feedback')) {
                            fb = document.createElement('div');
                            fb.className = 'invalid-feedback';
                            field.parentNode.appendChild(fb);
                        }
                        fb.textContent = (window.i18n && window.i18n.t && window.i18n.t('generate.validation.required')) || 'This field is required';
                        fb.style.display = 'block';
                        isValid = false;\\`);

src = src.replace(/if \(!isValid\) \{[\s\S]*?return; \/\/ Stop the form submission[\s\S]*?\}/, \\`if (!isValid) {
                    questionForm.querySelectorAll('.is-invalid').forEach(field => {
                        const eventType = field.tagName.toLowerCase() === 'select' ? 'change' : 'input';
                        field.addEventListener(eventType, () => {
                            if (field.value.trim() !== '') {
                                field.classList.remove('is-invalid');
                                const fb = field.nextElementSibling;
                                if (fb && fb.classList && fb.classList.contains('invalid-feedback')) fb.style.display = 'none';
                            }
                        }, { once: true });
                    });
                    showToast('error', (window.i18n && window.i18n.t && window.i18n.t('generate.validation.fillAll')) || 'Please fill all required fields.');
                    return; // Stop the form submission
                }\\`);

// 5) Submit button state and finally
src = src.replace(/questionsDisplay\.innerHTML = \\`<div class=\"d-flex justify-content-center\"><div class=\"spinner-border\" role=\"status\"><span class=\"visually-hidden\">Loading\.\.\.\<\/span\><\/div><\/div>\\`;/,
\\`const submitBtn = questionForm.querySelector('button[type="submit"]');
                const submitLabel = submitBtn ? submitBtn.innerHTML : '';
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = \\`<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>\\${(window.i18n && window.i18n.t && window.i18n.t('generate.generating')) || 'Generating…'}\\`;
                }
                questionsDisplay.innerHTML = \\`<div class=\"d-flex justify-content-center\"><div class=\"spinner-border\" role=\"status\"><span class=\"visually-hidden\">Loading...<\/span><\/div><\/div>\\`;\\`);

src = src.replace(/if \(Array\.isArray\(questions\) && questions\.length === 0\) \{[\s\S]*?return;[\s\S]*?\}/,
\\`if (Array.isArray(questions) && questions.length === 0) {
                        const msg = warn || (window.i18n && window.i18n.t && window.i18n.t('generate.noQuestions')) || 'No questions were generated. Try adjusting inputs and retry.';
                        questionsDisplay.innerHTML = \\`<div class="alert alert-info" role="alert">\\${msg}</div>\\`;
                        paginationControls.innerHTML = '';
                        if (submitBtn) { submitBtn.disabled = false; submitBtn.innerHTML = submitLabel || ((window.i18n && window.i18n.t && window.i18n.t('generate.submitButton')) || 'Generate Questions'); }
                        return;
                    }\\`);

src = src.replace(/\} catch \(error\) \{[\s\S]*?\}/,
\\`} catch (error) {
                    console.error('Error generating questions', error);
                    questionsDisplay.innerHTML = \\`<div class=\"alert alert-danger\" role=\"alert\">Error: \\${error.message}</div>\\`;
                    showToast('error', error.message || 'Error generating questions');
                } finally {
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = submitLabel || ((window.i18n && window.i18n.t && window.i18n.t('generate.submitButton')) || 'Generate Questions');
                    }
                }\\`);

// 6) Replace alerts in approve/reject
src = src.replace("alert('Question approved successfully');", "showToast('success', (window.i18n && window.i18n.t && window.i18n.t('generate.toast.approvedOne')) || 'Question approved successfully');");
src = src.replace(/alert\(\\`Error: \$\{error\.message\}\\`\);/g, "showToast('error', error.message || 'Operation failed');");
src = src.replace("alert('Question rejected successfully');", "showToast('success', (window.i18n && window.i18n.t && window.i18n.t('generate.toast.rejectedOne')) || 'Question rejected successfully');");

fs.writeFileSync(path, src, 'utf8');
console.log('Patched', path, 'Backup at', bak);
