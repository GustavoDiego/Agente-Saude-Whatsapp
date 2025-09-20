
$envFile = ".env"

if (-Not (Test-Path $envFile)) {
    Write-Host "ERRO: arquivo .env não encontrado."
    exit 1
}

Get-Content $envFile | ForEach-Object {
    if ($_ -match "^\s*#") { return }  
    if ($_ -match "^\s*$") { return } 
    $parts = $_.Split("=", 2)
    if ($parts.Length -eq 2) {
        $key = $parts[0].Trim()
        $value = $parts[1].Trim()
        [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
        Write-Host "Carregado: $key"
    }
}

Write-Host "Variáveis do .env carregadas no ambiente atual."
