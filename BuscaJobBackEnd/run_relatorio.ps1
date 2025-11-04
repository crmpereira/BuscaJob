param(
    [switch]$EnviarEmail
)

$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot

# Descobre Python do venv
$pythonPath = Join-Path $PSScriptRoot '.\.venv\Scripts\python.exe'
if (-not (Test-Path $pythonPath)) {
    Write-Host "Aviso: Python do venv não encontrado, tentando 'python' do sistema..."
    $pythonPath = 'python'
}

# Configura envio de email (usa variáveis de ambiente já suportadas pelo backend)
if ($EnviarEmail) {
    $env:EMAIL_ENABLED = 'true'
} else {
    $env:EMAIL_ENABLED = 'false'
}

# Cria script Python temporário que usa o Flask test client
$tmpPy = Join-Path ([System.IO.Path]::GetTempPath()) ("run_relatorio_tmp_" + [System.Guid]::NewGuid().ToString() + '.py')
$pyCode = @"
import json, sys, os
# Garante que o diretório do backend esteja no PYTHONPATH
backend_dir = r'${PSScriptRoot}'
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from api_server import app

if __name__ == '__main__':
    with app.test_client() as client:
        resp = client.get('/api/relatorio-fixo')
        data = resp.get_json()
        # Imprime somente JSON para facilitar o parse no PowerShell
        print(json.dumps(data, ensure_ascii=False))
"@
Set-Content -Path $tmpPy -Value $pyCode -Encoding UTF8

try {
    # Executa e captura a saída JSON
    $output = & $pythonPath $tmpPy
    $data = $output | ConvertFrom-Json

    if (-not $data.success) {
        Write-Error "Falha ao gerar relatório: $($data.error)"
        exit 1
    }

    Write-Host "Relatório gerado com sucesso" -ForegroundColor Green
    Write-Host ("Arquivo: {0}" -f $data.arquivo)
    Write-Host ("Total de vagas: {0}" -f $data.total)

    if ($data.email_enviado -eq $true) {
        Write-Host "Email enviado." -ForegroundColor Green
    } elseif ($data.email_erro) {
        Write-Host ("Falha no envio de email: {0}" -f $data.email_erro) -ForegroundColor Yellow
    }

    exit 0
}
finally {
    Remove-Item $tmpPy -ErrorAction SilentlyContinue
    Pop-Location
}