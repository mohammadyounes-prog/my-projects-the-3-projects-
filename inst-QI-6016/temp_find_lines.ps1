$filePath = "D:\questionretrieval\new-q-bank\frontend\index.html"

# Check if file exists
if (-not (Test-Path $filePath)) {
    Write-Output "Error: File not found at $filePath"
    exit 1
}

$content = Get-Content $filePath

Write-Output "File loaded. Total lines: $($content.Length)"

$fieldMetadataOccurrences = @()
for ($i = 0; $i -lt $content.Length; $i++) {
    if ($content[$i] -match "^\s*const fieldMetadata = \{") {
        $fieldMetadataOccurrences += $i + 1 # +1 for 1-based line number
    }
}

$initializeFuncStart = -1
for ($i = 0; $i -lt $content.Length; $i++) {
    if ($content[$i] -match "^\s*async function initializeGenerateQuestionDropdowns\(\)") {
        $initializeFuncStart = $i + 1
        break
    }
}

$domContentLoadedStart = -1
for ($i = 0; $i -lt $content.Length; $i++) {
    if ($content[$i] -match "^\s*document.addEventListener\('DOMContentLoaded', async function\(\)") {
        $domContentLoadedStart = $i + 1
        break
    }
}

$i18nAppliedListenerStart = -1
for ($i = 0; $i -lt $content.Length; $i++) {
    if ($content[$i] -match "^\s*document.addEventListener\('i18n:applied', async \(\)") {
        $i18nAppliedListenerStart = $i + 1
        break
    }
}


Write-Output "Field Metadata occurrences on lines: $($fieldMetadataOccurrences -join ', ')"
Write-Output "initializeGenerateQuestionDropdowns starts on line: $initializeFuncStart"
Write-Output "DOMContentLoaded starts on line: $domContentLoadedStart"
Write-Output "i18n:applied listener starts on line: $i18nAppliedListenerStart"

# Output a small snippet around expected fieldMetadata locations for visual inspection
Write-Output "`n--- Snippet around line 2080 ---"
$startLine = [System.Math]::Max(0, 2080 - 10)
$endLine = [System.Math]::Min($content.Length - 1, 2080 + 10)
for ($i = $startLine; $i -le $endLine; $i++) {
    Write-Output "$($i + 1): $($content[$i])"
}
Write-Output "`n--- Snippet around line 2090 ---"
$startLine = [System.Math]::Max(0, 2090 - 10)
$endLine = [System.Math]::Min($content.Length - 1, 2090 + 10)
for ($i = $startLine; $i -le $endLine; $i++) {
    Write-Output "$($i + 1): $($content[$i])"
}