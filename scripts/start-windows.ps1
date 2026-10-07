<#
.SYNOPSIS
    Yanımda'yı Windows'ta tek adımda çalıştırır.

.DESCRIPTION
    1. Docker kurulu değilse Docker Desktop'ı kurar (winget, yoksa resmi kurulum dosyası).
    2. Docker Desktop çalışmıyorsa başlatır ve hazır olmasını bekler.
    3. docker compose ile veritabanı, backend ve frontend'i sırayla ayağa kaldırır.
    4. Siteyi varsayılan tarayıcıda açar.

.PARAMETER NoBrowser
    Tarayıcıyı açmadan yalnızca servisleri başlatır.
#>
param([switch]$NoBrowser)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot

$AppUrl = 'http://localhost:5173'
$DockerDesktopExe = Join-Path $env:ProgramFiles 'Docker\Docker\Docker Desktop.exe'
$DockerCliDir = Join-Path $env:ProgramFiles 'Docker\Docker\resources\bin'
# Docker motorunun hazır olması için beklenecek en uzun süre (saniye).
$DockerWaitSeconds = 240

function Write-Step([string]$Message) {
    Write-Host ''
    Write-Host "==> $Message" -ForegroundColor Green
}

function Test-Command([string]$Name) {
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Add-DockerToPath {
    if ((Test-Path $DockerCliDir) -and -not ($env:Path -split ';' -contains $DockerCliDir)) {
        $env:Path = "$DockerCliDir;$env:Path"
    }
}

function Install-DockerDesktop {
    Write-Step 'Docker bulunamadı. Docker Desktop kuruluyor (yönetici onayı istenebilir)...'
    if (Test-Command 'winget') {
        winget install -e --id Docker.DockerDesktop --accept-source-agreements --accept-package-agreements
        if ($LASTEXITCODE -ne 0) { throw 'winget ile Docker Desktop kurulamadı.' }
    }
    else {
        $arch = if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') { 'arm64' } else { 'amd64' }
        $installer = Join-Path $env:TEMP 'DockerDesktopInstaller.exe'
        Write-Host "Kurulum dosyası indiriliyor ($arch)..."
        Invoke-WebRequest -UseBasicParsing -Uri "https://desktop.docker.com/win/main/$arch/Docker%20Desktop%20Installer.exe" -OutFile $installer
        $process = Start-Process -FilePath $installer -ArgumentList 'install', '--quiet', '--accept-license' -Verb RunAs -Wait -PassThru
        if ($process.ExitCode -ne 0) { throw "Docker Desktop kurulumu başarısız oldu (kod: $($process.ExitCode))." }
    }
    Add-DockerToPath
}

function Test-DockerReady {
    docker info *> $null
    return $LASTEXITCODE -eq 0
}

function Start-DockerEngine {
    if (Test-DockerReady) { return }
    Write-Step 'Docker Desktop başlatılıyor...'
    if (-not (Test-Path $DockerDesktopExe)) { throw "Docker Desktop bulunamadı: $DockerDesktopExe" }
    Start-Process -FilePath $DockerDesktopExe
    $deadline = (Get-Date).AddSeconds($DockerWaitSeconds)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 3
        if (Test-DockerReady) {
            Write-Host 'Docker hazır.'
            return
        }
        Write-Host -NoNewline '.'
    }
    throw ("Docker 4 dakika içinde hazır olmadı. İlk kurulumdan sonra Windows'u yeniden başlatmanız " +
        "(WSL 2 için) gerekebilir; ardından bu betiği tekrar çalıştırın.")
}

function Invoke-Main {
    <#
    .SYNOPSIS
        Docker'ı hazırlar, servisleri başlatır ve siteyi açar; hata durumunda istisna fırlatır.
    #>
    param([switch]$NoBrowser)

    Set-Location $ProjectRoot
    Add-DockerToPath
    if (-not (Test-Command 'docker')) { Install-DockerDesktop }
    Start-DockerEngine

    Write-Step 'Servisler sırayla başlatılıyor: veritabanı -> backend -> frontend (ilk açılış birkaç dakika sürebilir)...'
    docker compose up -d --build --wait
    if ($LASTEXITCODE -ne 0) { throw 'Servisler başlatılamadı. Ayrıntı için: docker compose logs' }

    Write-Step 'Yanımda hazır'
    Write-Host "  Site          : $AppUrl"
    Write-Host "  Admin paneli  : $AppUrl/admin"
    Write-Host '  API belgeleri : http://localhost:8000/api/docs/'
    Write-Host '  Admin girişi  : admin@yanimda.local / Yanimda-Admin-2026 (yalnızca yerel geliştirme)'
    Write-Host '  Durdurmak için: stop-windows.bat'

    if (-not $NoBrowser) { Start-Process $AppUrl }
}

# Testler betiği dot-source ile yükler; bu durumda ana akış çalıştırılmaz.
if ($MyInvocation.InvocationName -ne '.') {
    try {
        Invoke-Main -NoBrowser:$NoBrowser
    }
    catch {
        Write-Host ''
        Write-Host "HATA: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}
