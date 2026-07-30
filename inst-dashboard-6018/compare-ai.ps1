# ===============================
# Compare OpenAI Nano vs Gemini
# ===============================

Write-Host "---- OpenAI Nano ----" -ForegroundColor Cyan

# Build OpenAI request
$headers = @{
  "Authorization" = "Bearer $env:OPENAI_API_KEY"
  "Content-Type"  = "application/json"
}

$body = @{
  model = "gpt-4.1-nano"
  messages = @(@{ role = "user"; content = "Write a short haiku about coding." })
} | ConvertTo-Json -Depth 3

$response_openai = Invoke-RestMethod -Uri "https://api.openai.com/v1/chat/completions" -Headers $headers -Method Post -Body $body
$openai_reply = $response_openai.choices[0].message.content
Write-Host $openai_reply -ForegroundColor Green

# -------------------------------
Write-Host "`n---- Google Gemini ----" -ForegroundColor Cyan

# Gemini body (must include role=user!)
$body_gemini = @{
  contents = @(
    @{
      role = "user"
      parts = @(
        @{ text = "Write a short haiku about coding." }
      )
    }
  )
} | ConvertTo-Json -Depth 5 -Compress

# Try Gemini models in order
$gemini_models = @("gemini-1.5-flash-latest", "gemini-1.5-pro-latest")
$response_gemini = $null

foreach ($model in $gemini_models) {
    try {
        $url = "https://generativelanguage.googleapis.com/v1/models/$model:generateContent?key=$($env:GOOGLE_API_KEY)"
        $response_gemini = Invoke-RestMethod -Uri $url -Method Post -ContentType "application/json" -Body $body_gemini -ErrorAction Stop
        Write-Host "[OK] Gemini model used: $model" -ForegroundColor DarkGray
        break
    } catch {
        Write-Host "[FAIL] Gemini call failed with model: $model" -ForegroundColor Red
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $reader.BaseStream.Position = 0
            $reader.DiscardBufferedData()
            $rawResponse = $reader.ReadToEnd()
            Write-Host $rawResponse -ForegroundColor Magenta
        } catch {
            Write-Host "Could not read error details." -ForegroundColor Magenta
        }
    }
}

if ($response_gemini -ne $null) {
    if ($response_gemini.candidates.Count -gt 0) {
        $gemini_reply = $response_gemini.candidates[0].content.parts[0].text
        Write-Host $gemini_reply -ForegroundColor Yellow
    } else {
        Write-Host "Gemini returned no candidates:" -ForegroundColor Red
        $response_gemini | ConvertTo-Json -Depth 10 | Write-Host
    }
} else {
    Write-Host "[ERROR] Gemini call failed for all tested models." -ForegroundColor Red
}
