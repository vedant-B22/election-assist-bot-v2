$token = (gcloud auth print-access-token).Trim()
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}
$body = @{
    contents = @(
        @{
            role = "user"
            parts = @(
                @{
                    text = "Explain how AI works."
                }
            )
        }
    )
} | ConvertTo-Json -Depth 10

$url = "https://us-central1-aiplatform.googleapis.com/v1/projects/265912819375/locations/us-central1/publishers/google/models/gemini-2.0-flash:generateContent"
try {
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body
    $response | ConvertTo-Json -Depth 10
} catch {
    $_.Exception.Response.Content.ReadAsStringAsync().Result
}
